# Role: init

Initialize shared cluster settings, determine the privileged user's identity, and
validate the server count and optional CNI dependencies. Run this role before
other cluster setup or cleanup roles.

## Inputs

See [defaults](defaults/main.yml) and [argument specifications](meta/argument_specs.yml).

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `superuser_name` | str | (see defaults/main.yml) | Privileged user; when empty, discover the configured become user. |
| `k3s_hosts_group` | str | (see defaults/main.yml) | Unfiltered inventory group containing all cluster nodes. |
| `k3s_storage_dir` | str | (see defaults/main.yml) | Optional existing custom storage directory for other roles. |
| `kube_api_user` | str | (see defaults/main.yml) | Kubernetes API access user. |
| `kube_api_user_id` | int | (see defaults/main.yml) | Optional UID; null lets the OS allocate it. |
| `kube_api_user_home` | str | (see defaults/main.yml) | API user's home directory. |
| `kube_api_group` | str | (see defaults/main.yml) | Kubernetes API access group. |
| `kube_api_group_id` | int | (see defaults/main.yml) | Optional GID; null lets the OS allocate it. |
| `num_k3s_server_nodes` | int | (see defaults/main.yml) for at least three nodes, otherwise `1` | Number of server nodes. |
| `install_headlamp` | bool | (see defaults/main.yml) | Enable Headlamp in the setup workflow. |
| `install_longhorn` | bool | (see defaults/main.yml) | Enable Longhorn. |
| `install_cni_plugins` | bool | (see defaults/main.yml) | Enable the standard CNI plugins. |
| `install_multus_cni` | bool | (see defaults/main.yml) | Enable Multus; requires `install_cni_plugins`. |
| `install_whereabouts_ipam_plugin` | bool | (see defaults/main.yml) | Enable Whereabouts IPAM. |
| `install_emberstack_kubernetes_secrets_reflector` | bool | (see defaults/main.yml) | Enable Reflector. |
| `install_stakater_reloader` | bool | (see defaults/main.yml) | Enable Reloader. |
| `install_cert_manager` | bool | (see defaults/main.yml) | Enable Cert-Manager. |
| `install_keepalived_cluster_load_balancer` | bool | (see defaults/main.yml) | Enable Keepalived. |
| `cluster_load_balancer_services` | list of dict | (see defaults/main.yml) | Keepalived services; see the [load balancer role](../keepalived_cluster_load_balancer/README.md). |

These defaults are shared with subsequent roles; `init` itself does not install
the optional components. The provided playbooks target `k3s_nodes`, so changing
`k3s_hosts_group` also requires adapting the playbooks. The server count must be
positive, odd, and no greater than the full group size. Do not change an assigned
API user UID or group GID on an existing cluster.

## Derived settings

The first `num_k3s_server_nodes` hosts in inventory group order have
`node_k3s_role: server`; the remaining hosts have `node_k3s_role: agent`.
The role discovers `superuser_name`, `superuser_group`, and `superuser_home`,
preserving non-empty supplied group/home values. Its role variables also define
`k3s_data_current_symlink`, `k3s_cni_bin_dir`, and `k3s_cni_net_dir` for other roles.
Discovery commands use privilege escalation and do not report changes.

## Example

```yaml
- name: Initialize cluster settings
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.init
  vars:
    num_k3s_server_nodes: 3
```
