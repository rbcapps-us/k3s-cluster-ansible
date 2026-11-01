# kubectl_apply

Diff and apply Kubernetes resources on one host as `kube_api_user`, which must be defined by the inventory or calling playbook. The target host must have `kubectl` configured to access the cluster.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `kubectl_apply_become_user` | str | value of the `kube_api_user` fact | User to become when running kubectl commands. |
| `kubectl_apply_manifest_description` | str | Required | Manifest description displayed in the diff and apply task name. |
| `kubectl_apply_manifest_path` | str | `""` | Target-host manifest file, or kustomization directory when `kubectl_apply_use_kustomize` is true. |
| `kubectl_apply_manifest_yaml_text` | str | `""` | Literal YAML passed to kubectl commands via stdin using `-f -`. |
| `kubectl_apply_use_kustomize` | bool | `false` | Use `-k`; requires `kubectl_apply_manifest_path` and disallows `kubectl_apply_manifest_yaml_text`. |
| `kubectl_apply_namespace` | str | `""` | Add `--namespace` to kubectl commands when non-empty. |

Exactly one of `kubectl_apply_manifest_path` and `kubectl_apply_manifest_yaml_text` must be non-empty.

The registered host variable `kubectl_apply_result` contains the shell result, including `stdout`, `stderr`, and `rc`. Exit code `0` means no differences; `99` means resources were successfully applied and the task reports changed. Unexpected diff errors and apply errors fail the task and retain their exit codes.

```yaml
- name: "Apply a manifest"
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.kubectl_apply
  vars:
    kubectl_apply_become_user: "{{ kube_api_user }}"
    kubectl_apply_manifest_description: "Application resources"
    kubectl_apply_manifest_path: "/tmp/resources.yaml"
    kubectl_apply_manifest_yaml_text: ""
    kubectl_apply_use_kustomize: false
    kubectl_apply_namespace: "default"
```
