# Role: whereabouts

Install the Whereabouts IPAM plugin as release `whereabouts` in `kube-system`.
It can allocate addresses for secondary CNI networks. See
[defaults](defaults/main.yml) and [argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `whereabouts_ipam_plugin_helm_chart_version` | str | (see defaults/main.yml) | Whereabouts chart version. |
| `whereabouts_ipam_plugin_helm_extra_args` | list of str | (see defaults/main.yml) | Arguments passed to Helm. |

The role also reads `kube_api_user` from [init](../init/README.md),
and runs once as that user with privilege escalation. The selected host needs
Helm, `kubectl`, `jq`, cluster credentials, and access to
`oci://ghcr.io/k8snetworkplumbingwg/whereabouts-chart`. Configure the chart's host
CNI paths through extra arguments if required by your environment.

## Behavior and results

Check for a legacy `whereabouts` release in `default` and uninstall it if found.
Then use the shared [Helm role](../helm_chart_install_or_upgrade/README.md) to
install or upgrade `whereabouts-chart` in `kube-system`. Removing the legacy release
can interrupt its IPAM components; plan namespace migrations accordingly.

`whereabouts_old_location_removal_result` contains `rc: 99` when a legacy release
was removed and `0` when the status check did not find an installed release.
`helm_chart_install_or_upgrade_result` records the chart operation: `0` means
unchanged and `99` means successfully installed or upgraded.

The role does not create address pools or NetworkAttachmentDefinitions for your
workloads. Configure secondary networks to use Whereabouts IPAM separately,
typically with [Multus](../multus_cni/README.md).

## Example

```yaml
- name: Install Whereabouts IPAM
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.whereabouts
```
