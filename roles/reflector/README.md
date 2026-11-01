# Role: reflector

Install Emberstack Reflector as release `reflector` in `default`. Reflector can
replicate annotated Secrets and ConfigMaps across namespaces. See
[defaults](defaults/main.yml) and [argument specifications](meta/argument_specs.yml).

## Inputs and requirements

| Variable | Type | Default | Purpose |
| --- | --- | --- | --- |
| `emberstack_kubernetes_secrets_reflector_helm_chart_version` | str | (see defaults/main.yml) | Reflector chart version. |
| `emberstack_kubernetes_secrets_reflector_helm_extra_args` | list of str | (see defaults/main.yml) | Arguments passed to Helm. |

The role also reads `kube_api_user` from [init](../init/README.md),
and runs once as that user with privilege escalation. The selected host needs
Helm, `kubectl`, `jq`, working cluster credentials, and access to
`oci://ghcr.io/emberstack/helm-charts/reflector`.

## Behavior and results

Use the shared [Helm role](../helm_chart_install_or_upgrade/README.md) to install
or upgrade the chart when its version or rendered resources differ.
`helm_chart_install_or_upgrade_result` contains `stdout`, `stderr`, and `rc`;
`0` means unchanged, `99` means successfully installed or upgraded, and other
return codes fail.

This role installs the controller but does not annotate arbitrary resources for
replication. Set reflection annotations on the resources you want to share. The
[Cert-Manager role](../cert_manager/README.md) annotates its public CA Secret for
automatic reflection; consider namespace boundaries before allowing Secret
replication.

## Example

```yaml
- name: Install Reflector
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.reflector
```
