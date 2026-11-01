# Role: helm

Install or replace the Helm CLI on K3s server nodes. Agent nodes are skipped.
See [defaults](defaults/main.yml) and [argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Default/source | Purpose |
| --- | --- | --- | --- |
| `helm_version` | str | `v4.3.0` | Exact Helm version, including the `v` prefix. |
| `node_k3s_role` | str | Derived by `init` | Installation runs only when the value is `server`. |

Run [init](../init/README.md) first or provide `node_k3s_role` explicitly. Gathered
architecture facts are required. The role selects Linux `arm64` for `aarch64` and
Linux `amd64` otherwise, and downloads from `https://get.helm.sh`. Installing to
`/usr/local/bin/helm` requires privilege escalation.

## Behavior and results

Check whether `/usr/local/bin/helm` is executable and compare `helm version --short`
without build metadata against `helm_version`. If missing or different, download
and extract the release tarball in a temporary directory and replace the binary.
The temporary directory is removed in an `always` block. Only binary replacement
reports a change; `helm_check_installed_result` contains the check result.

## Example

```yaml
- name: Install Helm on server nodes
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.helm
```
