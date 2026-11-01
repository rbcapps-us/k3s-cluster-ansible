# Role: longhorn

Install Longhorn distributed block storage, an additional RWX StorageClass, and
optional authenticated Traefik ingress for its dashboard. See
[defaults](defaults/main.yml) and [argument specifications](meta/argument_specs.yml).

## Inputs

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `longhorn_helm_chart_version` | str | (see defaults/main.yml) | Longhorn chart version. |
| `longhorn_default_volume_replica_count` | int | (see defaults/main.yml) | Default volume and StorageClass replica count. |
| `longhorn_helm_base_args` | list of str | Best-effort locality, non-default StorageClass, replica counts, migratable volumes | Base chart settings; exact arguments are in defaults. |
| `longhorn_helm_storage_dir_args` | list of str | Data/log paths under `k3s_storage_dir/longhorn` when non-empty, otherwise `[]` | Advanced storage-path override. |
| `longhorn_ingress_enabled` | bool | (see defaults/main.yml) | Expose the dashboard through ingress. |
| `longhorn_ingress_path` | path | (see defaults/main.yml) | Dashboard ingress path. |
| `longhorn_ingress_path_type` | str | (see defaults/main.yml) | Ingress path matching type. |
| `longhorn_ingress_middlewares` | list of str | Basic auth, trailing slash, and strip prefix in `longhorn-system` | Traefik references; exact names are in defaults. |
| `longhorn_ingress_extra_annotations` | dict | (see defaults/main.yml) | Extra annotations overriding matching generated keys. |
| `longhorn_ingress_annotations_combined` | dict | Middleware annotation merged with extras | Advanced annotation override. |
| `longhorn_helm_ingress_args` | list of str | Generated from ingress settings | Advanced ingress argument override. |
| `longhorn_helm_extra_args` | list of str | (see defaults/main.yml) | Arguments appended after base, storage, and ingress arguments. |
| `longhorn_ui_credentials` | list of dict | (see defaults/main.yml) | Entries with string `username` and `password`; required when ingress is enabled. |

Shared inputs are `superuser_name`, `kube_api_user`, `k3s_hosts_group`, and
`k3s_storage_dir`, normally supplied by [init](../init/README.md). The replica-count
default uses the full inventory group size. Store UI passwords in Ansible Vault
or another protected variable source.

## Requirements and behavior

Install `apache2-utils` and NFS client packages on each host as `superuser_name`;
the latter is `nfs-common` on Debian or `nfs-utils` otherwise. Nodes must also meet
Longhorn's storage and host prerequisites; [prereq](../prereq/README.md) removes
conflicting multipath software when Longhorn is enabled.

Cluster tasks run once as `kube_api_user`, requiring Helm, `kubectl`, `jq`, Python
`yq`, `htpasswd`, cluster credentials, and access to `https://charts.longhorn.io`.
Read the existing dashboard Secret, compare usernames, and verify passwords to
reuse existing htpasswd content when it matches. Otherwise generate new hashes.
Create `longhorn-system` if needed, then diff/apply ancillary resources and use
the shared [Helm role](../helm_chart_install_or_upgrade/README.md) for release
`longhorn`, excluding upgrade/uninstall hook Jobs from its diff.

The ancillary manifest always creates `longhorn-rwx`, with volume expansion,
`reclaimPolicy: Delete`, and non-migratable shared RWX settings. When ingress is
enabled, also create Traefik middleware and `longhorn-dashboard-users` for basic
authentication. Traefik CRDs are required for those resources. Disabling ingress
does not explicitly delete previously created ancillary resources.

## Results

`longhorn_system_namespace_create_result` and
`longhorn_ingress_middleware_apply_result` use `rc: 0` for unchanged and `99` for
successful changes; other codes fail. `helm_chart_install_or_upgrade_result`
records the chart operation. Password verification/generation uses `no_log`, but
ancillary manifest diff output can include Secret data. Temporary files are
removed in `always` blocks.

## Example

Supply credentials from a protected variable source when enabling ingress:

```yaml
longhorn_ingress_enabled: true
longhorn_ui_credentials:
  - username: admin
    password: "{{ vault_longhorn_ui_password }}"
```
