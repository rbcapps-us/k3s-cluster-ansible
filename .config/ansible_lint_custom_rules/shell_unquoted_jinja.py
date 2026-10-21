"""Flag Jinja expressions interpolated into shell/command strings without `| quote`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ansiblelint.rules import AnsibleLintRule
from jinja2 import Environment, nodes

if TYPE_CHECKING:
    from ansiblelint.file_utils import Lintable

SHELL_MODULES = {"shell", "command", "raw"}
JINJA_ENVIRONMENT = Environment()
# Filters whose output cannot carry shell metacharacters.
SAFE_FILTERS = {"quote", "int", "float", "bool", "b64encode"}


class ShellUnquotedJinjaRule(AnsibleLintRule):
    id = "shell-unquoted-jinja"
    description = "Jinja expressions in shell/command strings must end with `| quote`."
    severity = "HIGH"
    tags = ["security"]
    version_added = "v6.0.0"
    version_changed = "v6.0.0"

    def matchtask(self, task: Any, file: Lintable | None = None) -> bool | str:
        module = str(task["action"].get("__ansible_module__", "")).split(".")[-1]
        if module not in SHELL_MODULES:
            return False

        args = task["action"]
        command = args.get("_raw_params") or args.get("cmd") or ""
        if not isinstance(command, str):
            return False

        unquoted = []
        expression_parts: list[str] | None = None
        for _, token_type, value in JINJA_ENVIRONMENT.lex(command):
            if token_type == "variable_begin":
                expression_parts = []
            elif token_type == "variable_end" and expression_parts is not None:
                expression = "".join(expression_parts).strip()
                if not self._is_safe(expression):
                    unquoted.append(expression)
                expression_parts = None
            elif expression_parts is not None:
                expression_parts.append(value)
        if unquoted:
            return f"Add `| quote` to: {', '.join('{{ ' + e + ' }}' for e in unquoted)}".replace("[", "\\[")
        return False

    @staticmethod
    def _is_safe(expr: str) -> bool:
        def is_safe_node(node: nodes.Expr | None) -> bool:
            if isinstance(node, nodes.Filter):
                return node.name.split(".")[-1] in SAFE_FILTERS
            if isinstance(node, nodes.CondExpr):
                return is_safe_node(node.expr1) and is_safe_node(node.expr2)
            return False

        output = JINJA_ENVIRONMENT.parse("{{ " + expr + " }}").find(nodes.Output)
        return output is not None and all(is_safe_node(node) for node in output.nodes)
