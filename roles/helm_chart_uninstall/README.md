# Role: helm_chart_uninstall

Uninstall a Helm release if it exists, without reporting a change for an absent
release. See [argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `helm_namespace` | str | Required | Namespace containing the release. |
| `helm_release_name` | str | Required | Release to uninstall. |

There is no defaults file. The role also reads `kube_api_user`
from [init](../init/README.md). It runs once as that user with privilege escalation.
The selected host needs Helm and working Kubernetes credentials.

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
