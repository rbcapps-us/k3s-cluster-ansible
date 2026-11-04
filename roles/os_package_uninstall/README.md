# Role: os_package_uninstall

Remove a list of operating system packages using the host's package manager.
This role must be executed with superuser privileges.

## Inputs and requirements

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `package_names` | list of strings | Required | Package names to remove. |
| `update_cache` | bool | `false` | Whether to update the package manager cache before removal. |

Host facts must be available so the role can select a package manager. The
`community.general` collection is required for SUSE hosts.

## Behavior

Debian-family hosts use `apt` and purge package configuration. Red Hat-family
hosts use `dnf`, SUSE hosts use `community.general.zypper`, and other Linux
families use Ansible's generic `package` module; those paths remove packages
without requesting a purge.

## Example

```yaml
- name: Remove unused packages
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.os_package_uninstall
  vars:
    package_names:
      - example-package
    update_cache: true
```
