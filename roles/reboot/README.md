# Role: reboot

Reboot each targeted node using `ansible.builtin.reboot` with privilege escalation.
The module waits for the node to return and pass its readiness test using the
module's default timeouts and test command.

## Inputs and requirements

There are no role-specific inputs or defaults; see
[argument specifications](meta/argument_specs.yml). Configure connection and
become settings in the inventory or playbook. Control node ordering and concurrency
in the playbook, for example with `serial: 1`, to avoid rebooting the whole cluster
at once. Rebooting a node interrupts its workloads.

## Example

```yaml
- name: Reboot cluster nodes one at a time
  hosts: k3s_nodes
  serial: 1
  roles:
    - rbcapps_us.k3s_cluster_ansible.reboot
```
