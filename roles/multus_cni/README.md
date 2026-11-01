# Role: multus_cni

Install Multus CNI using its upstream DaemonSet, patched for K3s's CNI paths and
Flannel delegation. See [defaults](defaults/main.yml) and
[argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Default/source | Purpose |
| --- | --- | --- | --- |
| `multus_cni_version` | str | (see defaults/main.yml) | Upstream Multus release tag. |
| `multus_cni_protocol_version` | str | (see defaults/main.yml) | CNI protocol version in the configuration and DaemonSet arguments. |
| `superuser_name` | str | Discovered by `init` | Privileged user used for download, apply, and symlinks. |
| `k3s_data_current_symlink` | str | `/var/lib/rancher/k3s/data/current` from `init` | Existing K3s data symlink. |
| `k3s_cni_bin_dir` | str | `/var/lib/rancher/k3s/data/current/bin` from `init` | Host binary directory mounted into the DaemonSet. |
| `k3s_cni_net_dir` | str | `/var/lib/rancher/k3s/agent/etc/cni/net.d` from `init` | Host network configuration and Multus kubeconfig directory. |
| `cni_plugins_cni_dir` | str | default from `cni_plugins` role | Directory for the Multus binary symlink. |

Run [init](../init/README.md), install K3s, and run
[cni_plugins](../cni_plugins/README.md) first. Shared setup requires
`install_cni_plugins: true` when `install_multus_cni: true`. The selected apply host
needs `kubectl` with Kustomize support and cluster credentials for `superuser_name`.
Nodes need GitHub access and the cluster needs access to the upstream container
image. The patched default network assumes Flannel and `portmap` are available.

## Behavior and results

Resolve the current K3s binary directory, download and extract the release source
archive on each host, and template a Kustomization using the upstream
`multus-daemonset.yml`. Patches configure Flannel/portmap delegation, the CNI
protocol, Multus kubeconfig location, and host network/binary mounts.

Run `kubectl diff -k` once and apply only when its exit code is `1`.
`multus_cni_apply_result` records `0` for unchanged, `99` for a successful apply,
and any other code fails. Create a `multus` binary symlink in
`cni_plugins_cni_dir` on each host. Temporary source directories are always
removed. Downloads and rendering are repeated on each run but do not report
changes; diff/apply and symlink changes determine the reported changes.

This role installs Multus infrastructure, not application-specific secondary
network definitions. Create NetworkAttachmentDefinitions and pod network
annotations separately; [Whereabouts](../whereabouts/README.md) can supply IPAM
for secondary networks.
