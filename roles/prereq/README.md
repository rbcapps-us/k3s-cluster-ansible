# Role: prereq

Install packages needed by the cluster and create the Kubernetes API access user
and group on server nodes. Run [init](../init/README.md) first, or supply its shared
settings explicitly. See [argument specifications](meta/argument_specs.yml).

## Inputs

This role has no defaults file. The defaults below are inherited from `init`.

| Variable | Type | Source/default | Purpose |
| --- | --- | --- | --- |
| `superuser_name` | str | Discovered by `init` | User used for package management. |
| `install_longhorn` | bool | (see defaults/main.yml) | Remove conflicting multipath software when enabled. |
| `node_k3s_role` | str | Derived by `init` | Create the API user/group only for `server` nodes. |
| `kube_api_group` | str | (see defaults/main.yml) | API access group name. |
| `kube_api_group_id` | int | (see defaults/main.yml) | Optional explicit GID. |
| `kube_api_user` | str | (see defaults/main.yml) | API access user name. |
| `kube_api_user_id` | int | (see defaults/main.yml) | Optional explicit UID. |
| `kube_api_user_home` | str | (see defaults/main.yml) | API user's home directory. |

## Behavior

Install required packages.
Python package names are selected for Arch Linux or other OS families using
gathered facts. Pip is run with `PIP_BREAK_SYSTEM_PACKAGES=1`.

When Longhorn is enabled, remove `multipath-tools` and attempt to terminate
running multipath processes. The termination task ignores failures and does not
report changes. On server nodes, create the API group and a system user with a
Bash shell and home directory. Null UID/GID values let the OS allocate IDs.
Package installation needs access to the configured package and Python indexes.
