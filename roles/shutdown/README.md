# Role: shutdown

Shut down each targeted node using `community.general.shutdown` with privilege
escalation. This stops the nodes and their workloads; the role does not restart
them or wait for them to return.

## Inputs and requirements

There are no role-specific inputs or defaults; see
[argument specifications](meta/argument_specs.yml). Configure connection and
become settings in the inventory or playbook. The `community.general` collection
must be installed on the control node. Limit the play's target hosts when only
part of the cluster should be stopped.

## Example

```yaml
- name: Shut down selected nodes
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.shutdown
```
