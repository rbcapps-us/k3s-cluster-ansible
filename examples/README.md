# Testing on Virtual Machines in UTM on MacOS

If you're not already there, change into the *examples* directory.  This entire document assumes that the current working directory is the *examples* directory.
```sh
cd examples
```

See the [VMS.md](VMS.md) file for instructions to prepare three UTM VMs on your Mac for deploying K3s.

NOTE: Regardless of whether you are using VMs on your desktop, hosted VMs, or real hardware, the prerequisite users and configuration changes detailed in the above-referenced document are necessary.  Please pay careful attention to setting these up correctly before proceeding.

If you're not running on MacOS, you can use a different virtual machine package (VirtualBox, etc.) to create the VMs, but once the VMs are created and accessible from your laptop, the instructions are about the same.

## Install Ansible and dependencies

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
ansible-playbook -i "$INVPATH" -u ansible --become-password-file "$BECOMEPWFILE" rbcapps_us.k3s_cluster_ansible.alive_check
```

Set up the K3s cluster:
```sh
ansible-playbook -i "$INVPATH" -u ansible --become-password-file "$BECOMEPWFILE" rbcapps_us.k3s_cluster_ansible.setup_k3s_cluster
```

At the end of the playbook, there should be a Headlamp token.  Point a browser to <http://k3s-test-01.local/headlamp>, copy and paste the token into the token field, and click *Authenticate*.  Click on *Workloads* -> *Pods* to see all of the pods which are running on the cluster.

You can also access the Longhorn dashboard at <http://k3s-test-01.local/longhorn>.  The login credentials are set in the `longhorn_ui_credentials` setting in [../roles/longhorn/defaults/main.yml](../roles/longhorn/defaults/main.yml), and can be overridden in your inventory (or your calling role or playbook, if you're writing your own playbooks or roles).

## Test a Longhorn Shared Volume Between Two Pods

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

## Add a Local CA and HTTPS (TLS) to the Cluster

This optional setup creates a private Certificate Authority (CA), uses cert-manager to issue a shared server certificate, distributes the public CA certificate to all Kubernetes namespaces with Reflector, and enables HTTPS and HTTP-to-HTTPS redirects on the K3s Traefik ingress controller.

The `install_cert_manager` and `install_emberstack_kubernetes_secrets_reflector` options must be enabled when setting up the cluster.

These instructions assume the default cert-manager namespace (`cert-manager`), Reflector deployment (`default/reflector`), and K3s Traefik v3 deployment (`kube-system/traefik`).  Run the cluster-side commands below on the first server:

### Create the CA Private Key and Certificate

On your laptop, outside of this Git repository, create the CA key and certificate:

```sh
# Ensure that we're working in our local home directory.
cd "$HOME"

# Generate the CA's private key.
openssl genrsa -out k3-test-root-ca.key 4096

# Generate the CA's public certificate.
openssl req -x509 -new -nodes \
  -key k3-test-root-ca.key \
  -sha256 \
  -days 3650 \
  -subj "/CN=K3s Cluster Root CA/O=My Home Lab" \
  -out k3-test-root-ca.crt
```

Back up the `k3-test-root-ca.key` CA key file securely, restrict access to it, and never commit it to Git or copy it to laptops or application namespaces.  The key is unencrypted because cert-manager must use it unattended.  Anyone who obtains it can issue certificates trusted by devices that trust this CA.  Use this CA only for a test environment you control; production intranet PKI should be designed and operated with internal IT/security staff, preferably using an organizational CA rather than a lab root.

Import the `k3-test-root-ca.crt` certificate into the System keychain using Keychain Access and explicitly trust it.  On MacOS, you can do this with the following steps:
* Press *Command + Spacebar* to open Spotlight, type Keychain Access, and launch it.
* Click *System* in the left pane.
* On the menu bar at the top of the screen, click *File -> Unlock Keychain "System"*; enter your password.
* Click *File -> Import Items*.
* Select the `k3-test-root-ca.crt` file to import it; enter your password.
* Find *K3s Cluster Root CA* in the list, and double-click it.
* Expand the *Trust* section.
* To the right of *When using this certificate*, select *Always Trust*.
* Close the certificate window; enter your password.

Restart browsers if necessary.  Some browsers, CLI tools, and language runtimes use separate trust stores and need separate configuration.

For **intranet infrastructure and managed laptops**, internal IT staff need to automatically install the approved internal root CA certificate on **all internal laptops** and relevant internal clients, using MDM/configuration profiles on macOS, Group Policy on Windows, or equivalent managed trust-store policies.  Distribute only the public certificate, verify its provenance, and plan renewal, rotation, and removal centrally.  Do not deploy this lab CA organization-wide without IT approval.  Pod trust and laptop trust are separate: Reflector does not install trust on laptops.

### Edit the inventory; run the playbook

WARNING: This section uses substandard handling of encryption keys.  This is just an example of how to get TLS working on the cluster.  In a real-world scenario, the `k3-test-root-ca.key` file would be encrypted in the inventory using Ansible Vault, or retrieved from a secret store, such as *AWS Secrets Manager*, possibly using an ansible `lookup`.  Sensitive secrets should *NEVER* be stored unencrypted in Ansible inventories.

Edit `inventories/k3s-test-cluster/group_vars/all.yml`.  Make the following changes:

* Uncomment the settings under the section comment titled *Example configuration for enabling cluster-wide TLS for HTTP/HTTPS...*.
* Replace the lines below the `cert_manager_cluster_local_ca_cert` setting with the contents of the newly generated `k3-test-root-ca.crt` file, indenting each line two spaces.
* Replace the lines below the `cert_manager_cluster_local_ca_private_key` setting with the contents of the newly generated `k3-test-root-ca.key` file, indenting each line two spaces.
* Run the following playbook:
    ```sh
    ansible-playbook -i "$INVPATH" -u ansible --become-password-file "$BECOMEPWFILE" rbcapps_us.k3s_cluster_ansible.setup_k3s_cluster --tags cert_manager
    ```
* Wait a minute or so for the dust to settle, then proceed to the next section.

### Verify HTTPS and Redirects

On your laptop, exit all browser windows, quit the browser process, then re-open the browser and point it to [http://k3s-test-01.local/headlamp/](http://k3s-test-01.local/headlamp/).  You should see it automatically redirect to https, and show a secure URL.  Also try [http://k3s-test-01.local/longhorn/](http://k3s-test-01.local/longhorn/).

The HTTP request should return a temporary redirect with a `Location` beginning `https://k3s-test-01.local/`.  HTTPS must complete without a certificate error; an application authentication response such as Longhorn's `401 Unauthorized` is expected before login.  Repeat with each of the four hostnames.  Do not use `curl -k`, which would hide certificate/trust problems.  Once browser trust is installed, use <https://k3s-test-01.local/headlamp/> and <https://k3s-test-01.local/longhorn/>.

### Notes on cert-manager and cluster-wide TLS certificate

Cert-manager will automatically renew the TLS certificate as necessary, before it expires.  It does **not** automatically rotate the manually created CA or redistribute laptop trust.  Monitor expiration of the `cluster-local-ca` and `cluster-local-ca-cert` secrets, and replace them with a newly generated CA private key and certificate pair before the CA private key and certificate expires.  Use the same commands from above to create a replacement CA private key and certificate pair, and update the secrets in the cluster.

Traefik uses only one TLS store named `default` cluster-wide.  Check `kubectl get tlsstores.traefik.io -A` first if you already have custom TLS stores: update the existing default store rather than creating a second one.

The server TLS Secret does not need reflection; Traefik can use this default certificate for routes in other namespaces.

These Traefik v3 arguments make `websecure` the default entrypoint for routers without explicit entrypoints, enable TLS there, and globally redirect port 80 requests to HTTPS on the **external port 443** (not Traefik's internal port 8443).  TLS terminates at Traefik; connections from Traefik to application backends remain unchanged.  The TLSStore supplies the certificate to routes without their own certificate configuration.

Existing Ingresses with no explicit entrypoint/TLS overrides, including the example Headlamp and Longhorn ingresses, can use the shared certificate without a per-application TLS Secret.  For apps that explicitly select `web` or disable TLS, you can update their declarative manifests or Helm values to use these annotations (and preserve their other annotations):
```yaml
metadata:
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
```

For `IngressRoute` resources, use `spec.entryPoints: [websecure]` and `spec.tls: {}` to use the default certificate.  An explicit `spec.tls.secretName` on an Ingress/IngressRoute selects a namespace-local certificate instead; remove or update conflicting certificate settings if the shared certificate is intended.  Keep existing routing hosts, paths, services, and middleware settings.

This enables HTTPS for apps routed through Traefik under the **four listed names**, not for arbitrary DNS names, direct Service/NodePort access, or the K3s API on port 6443.  Add other app hostnames to the Certificate's `dnsNames` (or issue separate certificates) before using them.  Do not add per-Ingress cert-manager issuer annotations unless you intentionally want separate certificates.

### Alternate CA Issuers for cert-manager

In an integrated environment where you are using an Amazon Web Services ACM Private Certificate Authority to issue private TLS certificates, it is possible to use [aws-privateca-issuer](https://github.com/cert-manager/aws-privateca-issuer) in combination with either AWS IAM Roles Anywhere or (in the case of a K3s cluster running on EC2 instances in the AWS account) an EC2 instance profile/role, to grant the cluster the required IAM permissions to issue certificates from the ACM PCA.  In the real world, this is an excellent way to issue certificates for the cluster.  In this type of configuration, still need to create the root CA certificate secret (`cluster-local-ca-cert` in this example), retrieving it from the ACM-PCA, and update it each time before it expires, but you don't need to create a CA private key / certificate secret (`cluster-local-ca-cert` in this example), as that will come from the ACM PCA itself.

### Test mounting the CA certificate in a pod

Back on your laptop, copy the `busybox-pod-with-cluster-local-ca-cert.yaml` Kubernetes manifest file to the first node in the cluster:
```sh
scp -p busybox-pod-with-cluster-local-ca-cert.yaml k3s-test-01.local:/tmp/
```

SSH into the first node of the cluster, and apply the busybox test manifest, then confirm that the CA certificate is mounted in the pod:
```sh
# SSH into the first node in the cluster.
ssh k3s-test-01.local

# Change the owner/group of the manifest to the k3s user/group.
# Replace k3s:k3s with your custom user/group if you overrode `kube_api_user` or
# `kube_api_group` in your inventory.
sudo chown k3s:k3s /tmp/busybox-pod-with-cluster-local-ca-cert.yaml

# Become the Kubernetes API user.
# Replace k3s with your user if you overrode `kube_api_user` in your inventory.
sudo su - k3s

# Apply the manifest, wait for the pod to come up:
kubectl apply -f /tmp/busybox-pod-with-cluster-local-ca-cert.yaml
kubectl wait --for=condition=Ready pod/busybox --timeout=60s

# Get a shell prompt inside the pod:
kubectl exec -it busybox-0 -- /bin/sh

# Confirm that the CA certificate file exists in the pod, and is readable:
ls -la /etc/ssl/certs/k3-test-root-ca.crt
cat /etc/ssl/certs/k3-test-root-ca.crt

# Exit the pod, then delete it:
exit
kubectl delete -f /tmp/busybox-pod-with-cluster-local-ca-cert.yaml

# Delete the test manifest:
rm -f /tmp/busybox-pod-with-cluster-local-ca-cert.yaml
```

To get an idea of how secret mounting works, have a look at the contents of the [busybox-pod-with-cluster-local-ca-cert.yaml](busybox-pod-with-cluster-local-ca-cert.yaml) YAML manifest which we just tested.

When using a `subPath` mount to mount Kubernetes secrets, it is necessary to annotate the manifest to cause Stakater Reloader to do a rolling update on the pods whenever a mounted secret changes.  This is accomplished by adding a `reloader.stakater.com/auto: "true"` annotation to a resource (Deployment, StatefulSet, DaemonSet, ReplicaSet, etc.) which creates pods.  See [Stakater Reloader GitHub](https://github.com/stakater/reloader) for documentation.

If you set `install_stakater_reloader` to true, Stakater Reloader will be installed on the cluster, and can be used to do rolling updates of pods when a mounted secret is updated.

## Cluster Load Balancer

*This section is OPTIONAL, and requires a static IP address on your local network.*

Now that we (optionaly) have TLS working on the cluster, we can configure the cluster load balancer, to enable accessing the cluster's HTTP/HTTPS services via a single IP address and corresponding hostname.

The four hostnames `k3s-test.local`, `k3s-test-01.local`, `k3s-test-02.local`, and `k3s-test-03.local` must resolve on clients to reachable cluster ingress addresses, with ports 80 and 443 accessible.  The nodes in the test cluster (comprised of UTM VMs) are running avahi-daemon to ensure that their hostnames are resolvable on the local network via DNS.  So we just need to configure `k3s-test.local` to resolve to the cluster load balancer's IP address.

For a real intranet, use names under an internal DNS domain controlled by your organization instead, and adjust the certificate names accordingly.

The `k3s-test.local` domain will need to resolve to a free, unused IP address in your local network.  This IP address will need to be outside of the range of any DHCP server running on your local network (in other words, a static IP address).  For our example, we will use `192.168.64.153`, but this will be different for your internal network, so be sure to replace it with your IP address in all of the commands below.

Add a line at the bottom of your /etc/hosts file on your laptop, like this:
```text
192.168.64.153  k3s-test.local
```

Edit `inventories/k3s-test-cluster/group_vars/all.yml`.  Make the following changes:

* Uncomment the settings under the section comment titled *Example configuration for enabling a keepalived-based cluster load balance...*, but LEAVE the cnpg1 vrrp instance block commented out.
* Replace the `ip_address` setting for `vrrp_instance_name: http_https` with your reserved IP address.
* Run the following playbook:
    ```sh
    ansible-playbook -i "$INVPATH" -u ansible --become-password-file "$BECOMEPWFILE" rbcapps_us.k3s_cluster_ansible.setup_k3s_cluster --tags keepalived_cluster_load_balancer
    ```
* Wait a minute or so for the dust to settle, then proceed to the next section.

After the playbook completes, you should be able to access the Headlamp and Longhorn dashboards at the cluster's load-balanced endpoint.  Try the following URLs in your browser:
* [https://k3s-test.local/headlamp](https://k3s-test.local/headlamp)
* [https://k3s-test.local/longhorn](https://k3s-test.local/longhorn)

## References

References: [cert-manager CA issuers](https://cert-manager.io/docs/configuration/ca/), [Reflector automatic reflection](https://github.com/emberstack/kubernetes-reflector#usage), [K3s HelmChartConfig customization](https://docs.k3s.io/add-ons/helm#customizing-packaged-components-with-helmchartconfig), [Traefik TLSStore](https://doc.traefik.io/traefik/reference/routing-configuration/kubernetes/crd/tls/tlsstore/), and [Traefik entrypoints](https://doc.traefik.io/traefik/reference/install-configuration/entrypoints/).

