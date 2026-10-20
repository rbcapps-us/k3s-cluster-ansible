# Ansible Collection - rbcapps_us.k3s_cluster_ansible

A no-nonsense Ansible collection to easily provision or upgrade a K3s cluster.

Handles edge cases, and has some significant built-in cluster planning logic, such as:
* When a node's role (server versus agent) changes in the configuration
* When the k3s version to be installed on a node is different than the version which is currently installed on the node (might fail if there is a version difference of more than one minor version, per the Kubernetes documentation)
* Adding new nodes to a cluster
* Automatically calculates the number of server nodes (can be overridden by setting a variable in the inventory) to an odd number, in order to establish quorum for the cluster state
* If there are at least 3 nodes in the cluster, the first 3 nodes will be server nodes, and the rest will be agents
* If there are fewer than 3 nodes in the cluster, the first node will be a server node, and the other node (if it exists) will be an agent node
* If a node needs to have k3s reinstalled on it (due to a change in k3s version or the node's role), the node will be automatically cordoned, drained, and removed from the cluster, k3s will be uninstalled from the node, the new k3s package (with the correct version) will be installed on the node with the correct role, and the node will be rejoined to the cluster under its new role
* Automatically installs Helm, Headlamp, Longhorn block storage, the CNI plugins, and Multus-CNI (each of these can be selectively installed or not installed, based on booleans which can be set from the calling class, or in the inventory)


## Testing on Virtual Machines in UTM on MacOS

For a full walkthrough of the example VM setup and K3s test workflow, see [examples/README.md](examples/README.md).

This guide covers preparing three UTM virtual machines on macOS and walking through the example inventory and cluster validation steps.

## Creating a production project

Copy the *examples* directory to a new directory outside of this project.

Modify the requirements.yml to use a production tag of the *rbcapps_us.k3s_cluster_ansible* Galaxy collection.

Remove any non-production copy of the *rbcapps_us.k3s_cluster_ansible* collection, and reinstall the configured version:
```sh
rm -rf ~/.ansible/collections/ansible_collections/rbcapps_us/k3s_cluster_ansible
ansible-galaxy install -r requirements.yml
```

Create a file named *inventories/k3s-test-cluster/ansible-become-password.txt*, and put the password for the *ansible* user on your cluster.

## Summary of Playboks in the Collection

This collection contains the following playbooks:

* [rbcapps_us.k3s_cluster_ansible.setup_k3s_cluster](../playbooks/setup_k3s_cluster.yml): Builds out a K3s cluster across the nodes (hosts) in the inventory.
* [rbcapps_us.k3s_cluster_ansible.headlamp_token](../playbooks/headlamp_token.yml): Creates a new token for logging into the Headlamp dashboard.
* [rbcapps_us.k3s_cluster_ansible.uninstall_k3s](../playbooks/uninstall_k3s.yml): Uninstalls k3s from all nodes (hosts) in the inventory.
* [rbcapps_us.k3s_cluster_ansible.alive_check](../playbooks/alive_check.yml): Confirms that all nodes are alive and reachable.
* [rbcapps_us.k3s_cluster_ansible.reboot](../playbooks/reboot.yml): Reboots all nodes.
* [rbcapps_us.k3s_cluster_ansible.shutdown](../playbooks/shutdown.yml): Shuts down all nodes.

## Playbook Defaults

Shared defaults and component installation switches are stored in [roles/init/defaults/main.yml](roles/init/defaults/main.yml) and documented in [roles/init/meta/argument_specs.yml](roles/init/meta/argument_specs.yml).  Role-specific defaults and their documentation are stored in each role's `defaults/main.yml` and `meta/argument_specs.yml` under [roles](roles).  For example, Longhorn settings are in [roles/longhorn/defaults/main.yml](roles/longhorn/defaults/main.yml) and [roles/longhorn/meta/argument_specs.yml](roles/longhorn/meta/argument_specs.yml).  You can override these values by setting them in the inventory, or, if you are calling roles directly from your own playbooks, by explicitly setting facts or passing vars to the roles which you call.

## Re-using Roles in your own Playbooks

If you need to write your own playbooks, as opposed to just using the playbooks which are provided in this collection, you can simply make a local copy of any of the above-referenced playbooks in your own project, and do your customizations.

## Developing this Project

Install `ansible-lint` on MacOS:
```sh
brew install ansible-lint
```

Validate playbooks and roles for lint errors:
```sh
./validate-lint
```

## Publishing a new version of the Galaxy collection

* Update the version in galaxy.yml
* Commit and push the change
* Run:
    ```sh
    ansible-galaxy collection build
    ```
* Publish the collection, either by CLI:
    ```sh
    ansible-galaxy collection publish rbcapps_us-k3s_cluster_ansible-1.0.0.tar.gz --api-key <ansible-galaxy-token-goes-here>
    ```
  or by going to [https://galaxy.ansible.com/ui/my-namespaces/](https://galaxy.ansible.com/ui/my-namespaces/), clicking *View collections* under the correct namespace, clicking *Upload collection*, and selecting the collection tarball.

* Create and push a git tag with the same version as the collection version (replace 1.0.0 with the correct version everywhere in the commands below):
    ```sh
    git tag v1.0.0
    git push origin v1.0.0
    ```
* In GitHub, create a release from the new tag.  Upload the newly built tarball to the new release.

## Known, Unhandled Edge Cases

Upgrading a single-node cluster to a different K3s version, while simultaneously adding nodes to the cluster in the same play, may result in complete loss of the cluster state.  Don't do this.  If you need to add nodes to a single-node cluster, ensure that `k3s_version` is set to the same K3s version which the single-node cluster is running before running the play to add nodes to the cluster.  If you need to upgrade to a different K3s version, it is easiest to upgrade the single-node cluster to the new K3s version first, then add the nodes to the cluster in a separate play.  However, if you want maximum safety, it might be safer to add the new nodes to the cluster, running the same exact K3s version as the existing node, then upgrade the entire cluster to the new K3s version in a subsequent play.

## Where to go from here?

Have a look at the [k3s-cloud-native-pg-ansible](https://github.com/rbcapps-us/k3s-cloud-native-pg-ansible) project, which provides Ansible playbooks for installing CloudNativePG high-availability PostgreSQL to a K3s cluster which was provisioned using the `rbcapps_us.k3s_cluster_ansible` Galaxy collection.
