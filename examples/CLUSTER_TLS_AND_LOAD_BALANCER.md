# Adding a Local CA and HTTPS (TLS) to the Test Cluster

This optional, manual setup creates a private certificate authority (CA), uses cert-manager to issue a shared server certificate, distributes the public CA certificate with Reflector, and enables HTTPS and HTTP-to-HTTPS redirects on the K3s Traefik ingress controller.

The `install_cert_manager` and `install_emberstack_kubernetes_secrets_reflector` options must be enabled when setting up the cluster.

These instructions assume the default cert-manager namespace (`cert-manager`), Reflector deployment (`default/reflector`), and K3s Traefik v3 deployment (`kube-system/traefik`).  Run the cluster-side commands below on the first server:

Log into the first node of the cluster.  Replace the `k3s` username with the value of the `kube_api_user` variable, if you used a value other than the default for the Kubernetes API user.  Confirm that you can list the namespaces in the cluster.
```sh
ssh k3s-test-01.local
sudo su - k3s
kubectl get ns
```

## Create the CA Private Key and Certificate

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

# Copy the CA's private key and certificate to the first node in the cluster.
scp -p k3-test-root-ca.key k3-test-root-ca.crt k3s-test-01.local:/tmp/
```

SSH into the first node of the cluster, and add the secrets:
```sh
# SSH into the first node in the cluster.
ssh k3s-test-01.local

# Change the owner/group of the certificate and key files to the k3s user/group.
# Replace k3s:k3s with your custom user/group if you overrode `kube_api_user` or
# `kube_api_group` in your inventory.
sudo chown k3s:k3s /tmp/k3-test-root-ca.crt /tmp/k3-test-root-ca.key

# Become the Kubernetes API user.
# Replace k3s with your user if you overrode `kube_api_user` in your inventory.
sudo su - k3s

# Create a CA secret for cert-manager to use to issue new TLS certificates.
kubectl -n cert-manager create secret tls cluster-local-ca \
  --cert=/tmp/k3-test-root-ca.crt \
  --key=/tmp/k3-test-root-ca.key \
  --dry-run=client -o yaml | \
    kubectl apply -f -

# Create a secret containing the public CA certificate secret, which is replicated to all namespaces.
kubectl -n default create secret generic cluster-local-ca-cert \
  --from-file=ca.crt=/tmp/k3-test-root-ca.crt \
  --dry-run=client -o yaml | \
  kubectl annotate -f - \
    'reflector.v1.k8s.emberstack.com/reflection-allowed=true' \
    'reflector.v1.k8s.emberstack.com/reflection-auto-enabled=true' \
    --local \
    -o yaml | \
      kubectl apply -f -

# Wait a few seconds for the secret to replicate to the other namespaces, then confirm that it exists
# in a known namespace:
kubectl -n longhorn-system get secret cluster-local-ca-cert

# Remove the sensitive files from the first node of the cluster.
rm -f /tmp/k3-test-root-ca.crt /tmp/k3-test-root-ca.key
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

## Give cert-manager the Signing Secret

Still in the first node of the cluster, as the k3s user, create the cluster-wide issuer:
```sh
kubectl apply -f - <<'EOF'
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: cluster-local-ca
spec:
  ca:
    secretName: cluster-local-ca
EOF

kubectl wait --for=condition=Ready clusterissuer/cluster-local-ca --timeout=60s
```

## Test mounting the CA certificate in a pod

Back on your laptop, copy the `` file to the first node in the cluster:
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
kubectl exec -it busybox -- /bin/sh

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

Avoid a `subPath` mount if you want Kubernetes to propagate Secret updates.  Mounted Secret updates are eventual, and applications may still need a reload or restart to use a changed CA.  This is where Stakater Reloader comes to the rescue.  If you set `install_stakater_reloader` to true, Stakater Reloader will be installed on the cluster, and can be used to do rolling updates of pods when a mounted secret is updated.  This is accomplished by adding a `reloader.stakater.com/auto: "true"` annotation to a resource (Deployment, StatefulSet, DaemonSet, ReplicaSet, etc.) which creates pods.  See [Stakater Reloader GitHub](https://github.com/stakater/reloader) for documentation.

## Issue the Shared Traefik Server Certificate; Configure Traefik's Default Certificate and HTTPS Redirect

Back on the first node in the cluster, as the `k3s` user, request one TLS certificate containing all four DNS names.  Store it in the `kube-system` namespace, alongside Traefik.  Edit Traefik's configuration to use the TLS certificate for all incoming traffic, and to redirect HTTP to HTTPS.

```sh
kubectl apply -f - <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: k3s-test-ingress-tls
  namespace: kube-system
spec:
  secretName: k3s-test-ingress-tls
  duration: 2160h
  renewBefore: 360h
  privateKey:
    algorithm: RSA
    size: 2048
    rotationPolicy: Always
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: cluster-local-ca
    kind: ClusterIssuer
    group: cert-manager.io
  dnsNames:
    - k3s-test.local
    - k3s-test-01.local
    - k3s-test-02.local
    - k3s-test-03.local

---

apiVersion: traefik.io/v1alpha1
kind: TLSStore
metadata:
  name: default
  namespace: kube-system
spec:
  defaultCertificate:
    secretName: k3s-test-ingress-tls

---

apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    additionalArguments:
      - "--entrypoints.websecure.asdefault=true"
      - "--entrypoints.websecure.http.tls=true"
      - "--entrypoints.web.http.redirections.entrypoint.to=:443"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.web.http.redirections.entrypoint.permanent=false"
    ports:
      web:
        redirectTo:
          port: websecure
          permanent: false
EOF

kubectl -n kube-system wait --for=condition=Ready certificate/k3s-test-ingress-tls --timeout=60s
```

Cert-manager will automatically this certificate as necessary, before it expires.  It does **not** automatically rotate the manually created CA or redistribute laptop trust.  Monitor expiration of the `cluster-local-ca` and `cluster-local-ca-cert` secrets, and replace them with a newly generated CA private key and certificate pair before the CA private key and certificate expires.  Use the same commands from above to create a replacement CA private key and certificate pair, and update the secrets in the cluster.

Traefik uses only one TLS store named `default` cluster-wide.  Check `kubectl get tlsstores.traefik.io -A` first if you already have custom TLS stores: update the existing default store rather than creating a second one.

The server TLS Secret does not need reflection; Traefik can use this default certificate for routes in other namespaces.

These Traefik v3 arguments make `websecure` the default entrypoint for routers without explicit entrypoints, enable TLS there, and globally redirect port 80 requests to HTTPS on the **external port 443** (not Traefik's internal port 8443).  TLS terminates at Traefik; connections from Traefik to application backends remain unchanged.  The TLSStore supplies the certificate to routes without their own certificate configuration.

After the Helm upgrade completes, check the deployment and confirm the arguments were applied.  A rollout check made before the Helm controller starts the upgrade can report the old deployment as
ready.  Be sure that any running `traefik-*` pods are newly created, with a state of *Running*.  Confirm that the above arguments are showing in the `traefik` deployment.

```sh
kubectl -n kube-system get pods
kubectl -n kube-system rollout status deployment/traefik --timeout=60s
kubectl -n kube-system get deployment traefik -o jsonpath='{.spec.template.spec.containers[0].args}'
```

Existing Ingresses with no explicit entrypoint/TLS overrides, including the example Headlamp and Longhorn ingresses, can use the shared certificate without a per-application TLS Secret.  For apps that explicitly select `web` or disable TLS, you can update their declarative manifests or Helm values to use these annotations (and preserve their other annotations):

```yaml
metadata:
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
```

For `IngressRoute` resources, use `spec.entryPoints: [websecure]` and `spec.tls: {}` to use the default certificate.  An explicit `spec.tls.secretName` on an Ingress/IngressRoute selects a namespace-local certificate instead; remove or update conflicting certificate settings if the shared certificate is intended.  Keep existing routing hosts, paths, services, and middleware settings.

This enables HTTPS for apps routed through Traefik under the **four listed names**, not for arbitrary DNS names, direct Service/NodePort access, or the K3s API on port 6443.  Add other app hostnames to the Certificate's `dnsNames` (or issue separate certificates) before using them.  Do not add per-Ingress cert-manager issuer annotations unless you intentionally want separate certificates.

## Verify HTTPS and Redirects

On your laptop, exit all browser windows, quit the browser process, then re-open the browser and point it to [http://k3s-test-01.local/headlamp/](http://k3s-test-01.local/headlamp/).  You should see it automatically redirect to https, and show a secure URL.  Also try [http://k3s-test-01.local/longhorn/](http://k3s-test-01.local/longhorn/).

The HTTP request should return a temporary redirect with a `Location` beginning `https://k3s-test-01.local/`.  HTTPS must complete without a certificate error; an application authentication response such as Longhorn's `401 Unauthorized` is expected before login.  Repeat with each of the four hostnames.  Do not use `curl -k`, which would hide certificate/trust problems.  Once browser trust is installed, use <https://k3s-test-01.local/headlamp/> and <https://k3s-test-01.local/longhorn/>.

## Alternate CA Issuers for cert-manager

In an integrated environment where you are using an Amazon Web Services ACM Private Certificate Authority to issue private TLS certificates, it is possible to use [aws-privateca-issuer](https://github.com/cert-manager/aws-privateca-issuer) in combination with either AWS IAM Roles Anywhere or (in the case of a K3s cluster running on EC2 instances in the AWS account) an EC2 instance profile/role, to grant the cluster the required IAM permissions to issue certificates from the ACM PCA.  In the real world, this is an excellent way to issue certificates for the cluster.  In this type of configuration, still need to create the root CA certificate secret (`cluster-local-ca-cert` in this example), retrieving it from the ACM-PCA, and update it each time before it expires, but you don't need to create a CA private key / certificate secret (`cluster-local-ca-cert` in this example), as that will come from the ACM PCA itself.

## Custer Load Balancer with TLS

*This section is OPTIONAL, and requires a static IP address on your local network.*

Now that we have TLS working on the clsuter, we can configure the cluster load balancer, to enable accessing the cluster via a single IP address and corresponding hostname.

The four hostnames `k3s-test.local`, `k3s-test-01.local`, `k3s-test-02.local`, and `k3s-test-03.local` must resolve on clients to reachable cluster ingress addresses, with ports 80 and 443 accessible.  A certificate does not create DNS records.  In particular, configure `k3s-test.local` to resolve to a server or the cluster load-balancer address.  `.local` uses multicast DNS on many systems; for a real intranet, use names under an internal DNS domain controlled by your organization instead, and adjust the certificate names accordingly.

That said, in a local development environment on MacOS `avahi-daemon` will cause the three nodes of the cluster to resolve correctly in DNS.  Because of this, you should only need to get `k3s-test.local` resolving correctly.

The `k3s-test.local` domain will need to resolve to a free, unused IP address in your local network.  This IP address will need to be outside of the range of any DHCP server running on your local network (in other words, a static IP address).  For our example, we will use `192.168.64.153`, but this will be different for your internal network, so be sure to replace it with your IP address in all of the commands below.

Add a line at the bottom of your /etc/hosts file on your laptop, like this:
```text
192.168.64.153  k3s-test.local
```

Edit `inventories/k3s-test-cluster/group_vars/all.yml` and add the following section at the end (if the section exists already but is commented out, you might be able to uncomment it and just change the IP address):
```yaml
install_keepalived_cluster_load_balancer: true
cluster_load_balancer_services:
  - vrrp_instance_name: http_https
    network_interface: enp0s1
    virtual_router_id: 51
    ip_address: 192.168.64.153
    ports:
      - port_number: 80
        health_check_protocol: http
        health_check_path: /
        health_check_healthy_status_codes: 200-299,404
      - port_number: 443
        health_check_protocol: https
        health_check_path: /
        health_check_healthy_status_codes: 200-299,404
```

Save the changes.  DO NOT commit changes to this file to git.

Run the following commands to update the cluster load balancer configuration:
```sh
ansible-playbook -i "$INVPATH" -u ansible --become-password-file "$BECOMEPWFILE" roncemer.k3s_cluster_ansible.setup_k3s_cluster --tags keepalived_cluster_load_balancer
```

After the playbook completes, you should be able to access the Headlamp and Longhorn dashboards at the cluster's load-balanced endpoint.  Try the following URLs in your browser:
* [https://k3s-test.local/headlamp](https://k3s-test.local/headlamp)
* [https://k3s-test.local/longhorn](https://k3s-test.local/longhorn)

## References

References: [cert-manager CA issuers](https://cert-manager.io/docs/configuration/ca/), [Reflector automatic reflection](https://github.com/emberstack/kubernetes-reflector#usage), [K3s HelmChartConfig customization](https://docs.k3s.io/add-ons/helm#customizing-packaged-components-with-helmchartconfig), [Traefik TLSStore](https://doc.traefik.io/traefik/reference/routing-configuration/kubernetes/crd/tls/tlsstore/), and [Traefik entrypoints](https://doc.traefik.io/traefik/reference/install-configuration/entrypoints/).
