# Role: uninstall_k3s

Uninstall K3s servers or agents and delete residual cluster files on each targeted
host. This is destructive: K3s state, kubelet state, Longhorn data, and the selected
users' `.kube` directories are removed. Back up required data before running it.

## Inputs

There is no role defaults file. Run [init](../init/README.md) first or supply these
shared settings. See [argument specifications](meta/argument_specs.yml).

| Variable | Type | Source/default | Purpose |
| --- | --- | --- | --- |
| `superuser_home` | str | Discovered by `init` | Remove this user's `.kube` directory. |
| `kube_api_user_home` | str | `/home/{{ kube_api_user }}` from `init` | Remove the API user's `.kube` directory. |
| `k3s_storage_dir` | str | defaulted in the `init` role | Also remove its `k3s` and `longhorn` subdirectories when non-empty. |

## Behavior and results

With privilege escalation, execute any executable `/usr/local/bin/k3s-uninstall.sh`
and `/usr/local/bin/k3s-agent-uninstall.sh`. Remove `/etc/rancher/k3s`,
`/etc/rancher/node`, `/var/lib/rancher/k3s`, `/var/lib/kubelet`, the K3s binary and
installer, `/usr/local/bin/helm`, `/opt/cni`, `/etc/cni`, `/dev/longhorn`, and
`/var/lib/longhorn`, along with the configured kubeconfig and custom-storage paths.
Finally, attempt to remove `/etc/rancher` and `/var/lib/rancher` only if empty.

`uninstall_k3s_dirs_and_files_to_remove` records the deletion list.
`uninstall_k3s_result_k3s_server_agent_uninstall` records the uninstall script
result (`rc: 99` means an uninstall ran; `0` means neither script ran).
`uninstall_k3s_result_rmdir` contains the loop results for empty-directory removal.
This role does not remove Keepalived; use its
[uninstall role](../keepalived_cluster_load_balancer_uninstall/README.md) separately.
