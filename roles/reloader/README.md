# Role: reloader

Install Stakater Reloader as release `reloader` in `default`. Reloader can trigger
workload rollouts when referenced Secrets or ConfigMaps change. See
[defaults](defaults/main.yml) and [argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `stakater_reloader_helm_chart_version` | str | (see defaults/main.yml) | Reloader chart version. |
| `stakater_reloader_helm_extra_args` | list of str | (see defaults/main.yml) | Arguments passed to Helm. |

The role also reads `kube_api_user` from [init](../init/README.md),
and runs once as that user with privilege escalation. The selected host needs
Helm, `kubectl`, `jq`, cluster credentials, and access to
`https://stakater.github.io/stakater-charts`.

## Behavior and results

Use the shared [Helm role](../helm_chart_install_or_upgrade/README.md), which adds
or updates the Stakater repository and installs or upgrades the release when its
version or rendered resources differ. `helm_chart_install_or_upgrade_result`
contains `stdout`, `stderr`, and `rc`; `0` means unchanged, `99` means successfully
installed or upgraded, and other return codes fail.

This role does not add reload annotations to application workloads. Configure
workload annotations or chart settings separately to select what Reloader watches.
Rollouts caused by configuration changes can restart application pods.

## Example

```yaml
- name: Install Reloader
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.reloader
```
