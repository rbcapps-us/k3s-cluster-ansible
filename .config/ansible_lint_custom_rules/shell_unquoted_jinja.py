"""Flag Jinja expressions interpolated into shell/command strings without `| quote`."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.file_utils import Lintable

SHELL_MODULES = {"shell", "command", "raw"}
JINJA_EXPR = re.compile(r"\{\{-?(.*?)-?\}\}", re.DOTALL)
RAW_BLOCK = re.compile(r"\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}", re.DOTALL)
LAST_FILTER = re.compile(r"\|\s*([A-Za-z_][\w.]*)\s*(?:\([^()]*\))?\s*$")
# Filters whose output cannot carry shell metacharacters.
SAFE_FILTERS = {"quote", "int", "float", "bool", "b64encode"}


class ShellUnquotedJinjaRule(AnsibleLintRule):
    id = "shell-unquoted-jinja"
    description = "Jinja expressions in shell/command strings must end with `| quote`."
    severity = "HIGH"
    tags = ["security"]
    version_added = "v6.0.0"
    version_changed = "6.0.0"

    def matchtask(self, task: Any, file: Lintable | None = None) -> bool | str:
        module = str(task["action"].get("__ansible_module__", "")).split(".")[-1]
        if module not in SHELL_MODULES:
            return False

        args = task["action"]
        command = args.get("_raw_params") or args.get("cmd") or ""
        if not isinstance(command, str):
            return False

        command = RAW_BLOCK.sub("", command)
        unquoted = [expr.strip() for expr in JINJA_EXPR.findall(command) if not self._is_safe(expr)]
        if unquoted:
            return f"Add `| quote` to: {', '.join('{{ ' + e + ' }}' for e in unquoted)}".replace("[", "\\[")
        return False

    @staticmethod
    def _is_safe(expr: str) -> bool:
        match = LAST_FILTER.search(expr.strip())
        return bool(match) and match.group(1).split(".")[-1] in SAFE_FILTERS
