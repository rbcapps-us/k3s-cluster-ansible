# Role: headlamp_token

Create a token for the `headlamp-admin` service account in `kube-system` using
`kubectl create token --duration=12h`, and display it in Ansible output. Kubernetes
may adjust the requested token lifetime according to its configuration.

## Inputs and requirements

| Variable | Type | Source/default | Purpose |
| --- | --- | --- | --- |
| `kube_api_user` | str | `k3s` from `init` | User used to run `kubectl`. |

This role has no defaults file. See [argument specifications](meta/argument_specs.yml).
The selected host needs `kubectl`, working API access for `kube_api_user`, and an
existing `headlamp-admin` service account, normally created by
[headlamp](../headlamp/README.md).

## Results

Tasks run once with privilege escalation to `kube_api_user` and do not report a
change. `headlamp_token_result_headlamp_token.stdout` contains the generated token.
The debug task prints the token, so treat playbook output and logs as sensitive.

## Example

```yaml
- name: Generate a Headlamp token
  ansible.builtin.include_role:
    name: rbcapps_us.k3s_cluster_ansible.headlamp_token
```
