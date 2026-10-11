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

You can also access the Longhorn dashboard at <http://k3s-test-01.local/longhorn>.  The login credentials are set in the `longhorn_ui_credentials` setting in [../roles/longhorn/defaults/main.yml](../roles/longhorn/defaults/main.yml), and can be overridden in your inventory (or your calling role or playbook, if you're writing your own playbooks or roles).

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

## Adding a Local CA and HTTPS (TLS) to the Test Cluster

See [CLUSTER_TLS_AND_LOAD_BALANCER.md](CLUSTER_TLS_AND_LOAD_BALANCER.md) for a complete walk-through of how to create a CA private key and certificate pair, configure `cert-manager` to use it to issue a cluster-wide HTTPS (TLS) certificate which auto-renews, and configure the traefik ingress to use it for all incoming HTTP/HTTPS traffic.
