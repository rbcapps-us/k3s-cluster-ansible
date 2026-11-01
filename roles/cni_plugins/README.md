# Role: cni_plugins

Install additional standard CNI binaries into K3s's active data directory on every
targeted node. See [defaults](defaults/main.yml) and
[argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Purpose |
| --- | --- | --- | |
| `cni_plugins_version` | str | Exact CNI plugin release version. |
| `k3s_data_current_symlink` | str | Existing K3s data symlink used to resolve the binary directory. |

K3s must already be installed and its current data symlink must exist.
The role downloads release archives from `containernetworking/plugins` on GitHub
and requires privilege escalation. The collection's Multus workflow requires
these plugins; enable `install_cni_plugins` in shared setup settings.

## Behavior and results

Resolve the symlink target and set `cni_plugins_bin_dir` to its `bin` directory.
Check that all of the require CNI plugins are executable and report the requested
version. A missing plugin, version mismatch, or failed check triggers archive
download and replacement of all listed binaries.

During installation, create `/var/lib/rancher/k3s/data/cni` and symlink the listed
plugins there. This role installs binaries, not NetworkAttachmentDefinitions or
a DHCP daemon. `cni_plugins_result_check_installed_cni_plugins` contains the check
result. Temporary download/extraction directories are always removed; download,
extraction, and checks do not report changes, while binary replacement does.
