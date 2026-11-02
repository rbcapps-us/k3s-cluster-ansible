# Role: helm_chart_uninstall

Uninstall a Helm release if it exists, without reporting a change for an absent release.
The calling user must have access to the Kubernetes API.

## Inputs and requirements

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `helm_namespace` | str | Required | Namespace containing the release. |
| `helm_release_name` | str | Required | Release to uninstall. |

The calling user must have access to the Kubernetes API.

## Behavior and results

Run `helm status` for the release. If installed, run `helm uninstall`. A status
exit code of `1` containing `release: not found` is treated as an unchanged success;
other status failures are reported and fail the task. Uninstalling a release
removes its Helm-managed resources and may interrupt workloads.

`helm_chart_uninstall_result` contains `stdout`, `stderr`, and `rc`. Code `0` means
the release was absent; `99` means uninstallation succeeded and reports a change.
Other return codes fail the task.

## Example

```yaml
- name: Uninstall a release
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.helm_chart_uninstall
  vars:
    helm_namespace: monitoring
    helm_release_name: example
```
