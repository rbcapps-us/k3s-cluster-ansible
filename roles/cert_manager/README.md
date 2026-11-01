# Role: cert_manager

Install Cert-Manager and optionally configure a cluster-local certificate authority
and a default TLS certificate for Traefik. See [defaults](defaults/main.yml) and
[argument specifications](meta/argument_specs.yml).

## Inputs

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `cert_manager_helm_chart_version` | str | `v1.19.2` | Cert-Manager chart version. |
| `cert_manager_helm_extra_args` | list of str | `[]` | Arguments appended to the base Helm arguments. |
| `cert_manager_cluster_local_ca_cert` | str | `""` | Literal PEM CA certificate; empty skips all local CA resources. |
| `cert_manager_cluster_local_ca_private_key` | str | `""` | Literal PEM CA private key; requires the certificate to create issuer resources. |
| `cert_manager_cluster_local_ca_private_key_and_cert_secret_name` | str | `cluster-local-ca-private-key-and-cert` | CA key/certificate Secret in `cert-manager`. |
| `cert_manager_cluster_local_ca_cert_secret_name` | str | `cluster-local-ca-cert` | Public CA Secret in `default`. |
| `cert_manager_cluster_local_ca_cluster_issuer_name` | str | `cluster-local-ca-issuer` | CA-backed ClusterIssuer name. |
| `cert_manager_issue_trafik_ingress_global_tls_cert` | bool | `true` | Issue the global Traefik certificate when both CA values are supplied. |
| `cert_manager_traefik_ingress_global_tls_cert_name` | str | `cluster-ingress-global-tls-cert` | Certificate and TLS Secret name. |
| `cert_manager_traefik_ingress_global_tls_cert_domains` | list of str | `[]` | DNS names prepended to the full inventory host group for the certificate. |

Shared inputs are `kube_api_user` and `k3s_hosts_group`, normally provided by
[init](../init/README.md). Tasks run once as the Kubernetes API user.

## Behavior and results

Install release `cert-manager` in namespace `cert-manager`, creating the namespace
and enabling CRDs.

With a CA certificate, create a public `ca.crt` Secret in `default` annotated for
automatic replication by [Reflector](../reflector/README.md). Replication requires
Reflector to be installed. With the private key as well, create a TLS Secret in
`cert-manager` and a CA ClusterIssuer. When the global TLS flag is also enabled,
create a Certificate in `kube-system`, configure Traefik's default TLSStore, and
write a Traefik HelmChartConfig enabling HTTPS and HTTP-to-HTTPS redirects.

The local manifest is applied only when `kubectl diff` returns `1`.
`cert_manager_local_ca_resources_apply_result` records the result: `0` means
unchanged, `99` means successfully applied, and other codes fail. Temporary files
are removed in an `always` block. Disabling an option does not explicitly delete
resources created by an earlier run.

Store the CA private key securely, for example in Ansible Vault. The manifest and
diff output can contain Secret data; this role does not mark those tasks `no_log`.
