# Role: headlamp

Install Headlamp in `kube-system` with an administrator service account and optional
Traefik ingress. See [defaults](defaults/main.yml) and
[argument specifications](meta/argument_specs.yml).

## Inputs

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `headlamp_helm_chart_version` | str | (see defaults/main.yml) | Headlamp chart version. |
| `headlamp_helm_base_args` | list of str | Service account and cluster-role creation settings | Create `headlamp-admin` and configure `cluster-admin` access. |
| `headlamp_ingress_enabled` | bool | (see defaults/main.yml) | Enable chart ingress. |
| `headlamp_ingress_path` | path | (see defaults/main.yml) | Ingress path and Headlamp base URL. |
| `headlamp_ingress_path_type` | str | (see defaults/main.yml) | Ingress path matching type. |
| `headlamp_ingress_middlewares` | list of str | (see defaults/main.yml) | Traefik middleware references. |
| `headlamp_ingress_extra_annotations` | dict | (see defaults/main.yml) | Extra annotations, overriding matching generated keys. |
| `headlamp_ingress_annotations_combined` | dict | Middleware annotation merged with extra annotations | Advanced override for all ingress annotations. |
| `headlamp_helm_ingress_args` | list of str | Generated from ingress settings | Advanced override for ingress Helm arguments. |
| `headlamp_helm_extra_args` | list of str | (see defaults/main.yml) | Arguments appended after base and ingress arguments. |

## Requirements and behavior

The cluster must have Traefik's Middleware CRD: a trailing-slash middleware in
`kube-system` is templated and applied even when `headlamp_ingress_enabled` is
false. Those ancillary tasks run once and their `kubectl` command uses the default
become user, which therefore needs cluster credentials. Temporary files are
removed in an `always` block.

The chart installation uses `kube_api_user`, from [init](../init/README.md), via
the shared [Helm role](../helm_chart_install_or_upgrade/README.md).
Base, ingress, and extra argument lists are concatenated and passed to helm.

`kubectl_apply_result` records ancillary diff/apply results:
`0` is unchanged, `99` is a successful apply, and other codes fail.
`helm_chart_install_or_upgrade_result` records the chart operation.
Use [headlamp_token](../headlamp_token/README.md) to generate a login token after
installation. The default administrator credentials grant broad cluster access;
restrict exposure of the dashboard and tokens accordingly.

## Example

```yaml
- name: Install Headlamp without ingress
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.headlamp
  vars:
    headlamp_ingress_enabled: false
```
