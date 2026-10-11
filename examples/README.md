## Testing on Virtual Machines in UTM on MacOS

If you're not already there, change into the *examples* directory.  This entire document assumes that the current working directory is the *examples* directory.
```sh
cd examples
```

See the [VMS.md](VMS.md) file for instructions to prepare three UTM VMs on your Mac for deploying K3s.

NOTE: Regardless of whether you are using VMs on your desktop, hosted VMs, or real hardware, the prerequisite users and configuration changes detailed in the above-referenced document are necessary.  Please pay careful attention to setting these up correctly before proceeding.

If you're not running on MacOS, you can use a different virtual machine package (VirtualBox, etc.) to create the VMs, but once the VMs are created and accessible from your laptop, the instructions are about the same.

## Test using the examples directory

Install Ansible:
```sh
brew install ansible
```

Install the required Galaxy module(s):
```sh
ansible-galaxy install -r requirements.yml
```

Create a file named *inventories/k3s-test-cluster/ansible-become-password.txt*, and put the password for the *ansible* user which you created when you set up the VMs.

NOTE: If you want to use the local copy of this collection, you can run the following command from the *examples* directory:
```sh
./install-local
```
This is also useful when making changes to the collection's playbooks or roles.  In that case, you can run the *install-local* before each playbook run, and that will ensure that you're always using the latest copy of the local playbooks and roles from the collection.

## Set the Inventory Environment Variables; Set up the K3s cluster

Set environment variables for the example inventory:
```sh
. ./set-ansible-inventory-k3s-test-cluster.sh
```

Run the Alive Check playbook to confirm that the nodes are alive:
```sh
ansible-playbook -i "$INVPATH" -u ansible --become-password-file "$BECOMEPWFILE" roncemer.k3s_cluster_ansible.alive_check
```

Set up the K3s cluster:
```sh
ansible-playbook -i "$INVPATH" -u ansible --become-password-file "$BECOMEPWFILE" roncemer.k3s_cluster_ansible.setup_k3s_cluster
```

At the end of the playbook, there should be a Headlamp token.  Point a browser to <http://k3s-test-01.local/headlamp>, copy and paste the token into the token field, and click *Authenticate*.  Click on *Workloads* -> *Pods* to see all of the pods which are running on the cluster.

You can also access the Longhorn dashboard at <http://k3s-test-01.local/longhorn>.  The login credentials are set in the `longhorn_ui_credentials` setting in [../roles/init/defaults/main.yml](../roles/init/defaults/main.yml), and can be overridden in your inventory (or your calling role or playbook, if you're writing your own playbooks or roles).

## Testing a Longhorn Shared Volume Between Two Pods

After your k3s cluster has been built out and the Headlamp and Longhorn dashboards are working, you can deploy a test workload to the cluster.

In the examples directory, there is a file named [lhtest.yaml](lhtest.yaml).  Copy this file to the /tmp directory on the first node of the cluster:

```sh
scp lhtest.yaml k3s-test-01.local:/tmp/
```

Next, log into the first node run these commands:

```sh
ssh k3s-test-01.local
sudo kubectl apply -f /tmp/lhtest.yaml
```

Wait for the pods to start:
```sh
sudo kubectl -n lhtest get pod
```
Repeat the above command until both pods are running.

In the first pod, create a test file:
```sh
sudo kubectl -n lhtest exec -it alpine-pod-1 -- /bin/sh
echo "test test test" > /data/test.txt
exit
```

In the second pod, show the contents of the test file:
```sh
sudo kubectl -n lhtest exec -it alpine-pod-2 -- /bin/sh
cat /data/test.txt
exit
```

You should see the contents of the file: *test test test*

Delete the test pods and associated resources, and remove the temporary YAML manifest:
```sh
sudo kubectl delete -f /tmp/lhtest.yaml
rm -f /tmp/lhtest.yaml
```

## Creating a production project

Copy the *examples* directory to a new directory outside of this project.

Modify the requirements.yml to use a production tag of the *roncemer.k3s_cluster_ansible* Galaxy collection.

Remove any non-production copy of the *roncemer.k3s_cluster_ansible* collection, and reinstall the configured version:
```sh
rm -rf ~/.ansible/collections/ansible_collections/roncemer/k3s_cluster_ansible
ansible-galaxy install -r requirements.yml
```

Create a file named *inventories/k3s-test-cluster/ansible-become-password.txt*, and put the password for the *ansible* user on your cluster.

## Summary of Playboks in the Collection

This collection contains the following playbooks:

* [roncemer.k3s_cluster_ansible.setup_k3s_cluster](../playbooks/setup_k3s_cluster.yml): Builds out a K3s cluster across the nodes (hosts) in the inventory.
* [roncemer.k3s_cluster_ansible.headlamp_token](../playbooks/headlamp_token.yml): Creates a new token for logging into the Headlamp dashboard.
* [roncemer.k3s_cluster_ansible.uninstall_k3s](../playbooks/uninstall_k3s.yml): Uninstalls k3s from all nodes (hosts) in the inventory.
* [roncemer.k3s_cluster_ansible.alive_check](../playbooks/alive_check.yml): Confirms that all nodes are alive and reachable.
* [roncemer.k3s_cluster_ansible.reboot](../playbooks/reboot.yml): Reboots all nodes.
* [roncemer.k3s_cluster_ansible.shutdown](../playbooks/shutdown.yml): Shuts down all nodes.

## Playbook Defaults

The default values for the roles in the playbook are stored in [../roles/init/defaults/main.yml](../roles/init/defaults/main.yml), and each customizable default is documented in [../roles/init/meta/argument_specs.yml](../roles/init/meta/argument_specs.yml).  You can override these values by setting them in the inventory, or, if you are calling roles directly from your own playbooks, by explicitly setting facts or passing vars to the roles which you call.

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
* Run:
    ```sh
    ansible-galaxy collection build
    ```
* Publish the collection, either by CLI:
    ```sh
    ansible-galaxy collection publish roncemer-k3s_cluster_ansible-1.0.0.tar.gz --api-key <ansible-galaxy-token-goes-here>
    ```
  or by going to [https://galaxy.ansible.com/ui/my-namespaces/](https://galaxy.ansible.com/ui/my-namespaces/), clicking *View collections* under the correct namespace, clicking *Upload collection*, and selecting the collection tarball.

* Create and push a git tag with the same version as the collection version (replace 1.0.0 with the correct version everywhere in the commands below):
    ```sh
    git tag -a v1.0.0 -m "Release version 1.0.0"
    git push origin v1.0.0
    ``` 
* In GitHub, create a release from the new tag.  Upload the newly built tarball to the new release.
