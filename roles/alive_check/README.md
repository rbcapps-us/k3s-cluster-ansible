# Role: alive_check

Check that a node can execute commands with privilege escalation. The role prints
an alive message and the effective user and group returned by `id`.

## Inputs

There are no role-specific inputs or defaults. Connection and privilege-escalation
settings come from the inventory or calling playbook. See
[argument specifications](meta/argument_specs.yml).

## Behavior and results

The commands run on every host with `become: true` and never report a change.
`alive_check_result_get_my_id` contains the registered shell result; its
`stdout_lines` are displayed by the following debug task.

## Example

```yaml
- name: Check node connectivity
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.alive_check
```
