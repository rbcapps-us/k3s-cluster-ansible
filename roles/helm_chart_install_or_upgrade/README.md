# Role: helm_chart_install_or_upgrade

Install a Helm release or upgrade it when the chart version or rendered resources
differ from the live cluster. See [defaults](defaults/main.yml) and
[argument specifications](meta/argument_specs.yml).

## Inputs

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `helm_namespace` | str | Required | Release namespace. |
| `helm_release_name` | str | Required | Helm release name. |
| `helm_repo_name` | str | Required | Repository alias for non-OCI charts; supply `""` for OCI. |
| `helm_chart_name` | str | Required | Chart name, also used to identify its installed version. |
| `helm_chart_url` | str | Required | Repository URL, or full `oci://` chart URL. |
| `helm_chart_version` | str | Required | Exact chart version. |
| `helm_args` | list of str | Required | Extra command-line arguments; supply `[]` if none. |
| `helm_omit_namespace_argument_from_kubectl_diff` | bool | `false` | Omit `--namespace` from diff, useful for mixed namespaces. |
| `helm_diff_kustomize_patches_yaml` | str | `""` | YAML list of Kustomize patches used only for diff. |
| `helm_diff_yq_filter_expressions` | list of str | `[]` | Sequential Python `yq` filters used only for diff. |

The role also reads `kube_api_user` from [init](../init/README.md).
It runs once as that user using privilege escalation. The selected host needs
Helm, `kubectl`, `jq`, working cluster credentials, and access to the chart source.
Python `yq` is required when filters are supplied. The namespace must exist unless
`helm_args` includes `--create-namespace`.

## Upgrade decision and results

For non-OCI charts, add the repository if absent and update Helm repositories.
A nonzero release-status result triggers installation. For an existing release,
a chart-version mismatch triggers upgrade immediately. Otherwise, render the
chart, optionally apply Kustomize patches and `yq` filters, and run `kubectl diff`.
Diff exit code `1` triggers upgrade; codes other than `0` or `1` fail the task.

Patches and filters affect only the comparison, not what `helm install` or
`helm upgrade` deploys. Supply patch list items without a surrounding `patches:`
key. Prefer Kustomize for comparisons where `yq` round-tripping could alter values.
Temporary rendering files are removed in an `always` block.

`helm_chart_install_or_upgrade_result` contains `stdout`, `stderr`, and `rc`.
Code `0` means no installation or upgrade was needed; `99` means installation or
upgrade succeeded and reports a change. Other codes fail the task. Repository
updates and temporary-file operations do not independently report changes.

## Example

```yaml
- name: Install a chart from a Helm repository
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.helm_chart_install_or_upgrade
  vars:
    helm_namespace: monitoring
    helm_release_name: example
    helm_repo_name: example
    helm_chart_name: example
    helm_chart_url: https://charts.example.org
    helm_chart_version: "1.2.3"
    helm_args:
      - --create-namespace
```
