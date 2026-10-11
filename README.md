# Ansible Collection - roncemer.k3s_cluster_ansible

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
