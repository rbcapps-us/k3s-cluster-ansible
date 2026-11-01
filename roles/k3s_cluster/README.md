# Role: k3s_cluster

Install or upgrade a K3s cluster, configure server kubeconfig access, and optionally
relocate local storage. Run [init](../init/README.md) and [prereq](../prereq/README.md)
first. See [defaults](defaults/main.yml) and
[argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `k3s_version` | str | (see defaults/main.yml) | Exact K3s version to install. |
| `k3s_cluster_pod_network_cidr` | str | (see defaults/main.yml) | Server-side cluster pod CIDR. |
| `k3s_enable_wireguard_network_encryption` | bool | (see defaults/main.yml) | Use Flannel `wireguard-native` and external IPs. |

Shared inputs include `k3s_hosts_group`, `num_k3s_server_nodes`, `node_k3s_role`,
`k3s_storage_dir`, `superuser_name`, `superuser_group`, `superuser_home`,
`kube_api_user`, `kube_api_group`, and `kube_api_user_home`; their definitions are
documented by `init`. Cluster host IPv4 facts and installation-status facts must
be available when selecting a join server. The inventory group describes the
full topology; the installation loop targets hosts in the current play.
Nodes need privilege escalation, connectivity to the K3s download sources and
other cluster nodes, and WireGuard support when encryption is enabled.

## Installation and upgrades

Inspect the installed binary, version, and server/agent data directories. Install
or reinstall nodes in play order when K3s is missing, its version differs, or the
installed role differs from `node_k3s_role`. Configuration-only changes do not
trigger this installation decision.

Use another installed server's default IPv4 address and token to join the
cluster, or initialize a server with `--cluster-init` if none is available.
Servers enable secrets encryption and the configured pod CIDR. In a multi-server
cluster, reinstalling an existing node can cordon, drain, and delete it from the
cluster, run its uninstall script, and install K3s again. Draining uses
`--delete-emptydir-data --force`, so local ephemeral data can be lost. An existing
sole server is upgraded in place instead. Back up cluster and workload data and
follow K3s-supported version transitions before changing versions.

Wait for server port `6443` and successful API access. Set server kubeconfig group
ownership and mode `0640`, persist `K3S_KUBECONFIG_MODE=0640`, and link kubeconfigs
into the superuser and API user's home directories. When `k3s_storage_dir` is
non-empty, create its `k3s/storage` directory and link
`/var/lib/rancher/k3s/storage` to it; existing data is not migrated by these tasks.

## Results

`k3s_cluster_k3s_installed_info` records `is_installed`, `version`, `role`, and
`need_install_or_reinstall` for each node, and is updated after installation.
Join-server host/address/token facts are used internally; token retrieval and
installation commands are marked `no_log`. Temporary installer directories are
removed in `always` blocks.
