# Role: keepalived_cluster_load_balancer_uninstall

Remove K3s-managed Keepalived configuration while preserving externally managed
configuration in `/etc/keepalived/conf.d`. See
[argument specifications](meta/argument_specs.yml).

## Inputs

This role has no defaults file. Shared settings normally come from
[init](../init/README.md).

| Variable | Type | Source/default | Purpose |
| --- | --- | --- | --- |
| `superuser_name` | str | Discovered by `init` | User used to manage Keepalived and its files. |
| `cluster_load_balancer_services` | list of dict | `[]` from `init` | An empty list allows the service to be stopped and disabled. |

## Behavior

Delete `k3s-*.conf` files from `/etc/keepalived/conf.d`. If other `*.conf` files
remain there, restart Keepalived and preserve the package and configuration
directory. Otherwise, gather service facts, stop and disable an existing
`keepalived.service` when the service list is empty, uninstall the package, and
remove `/etc/keepalived` recursively. The role uses privilege escalation.

Preservation is based only on non-K3s `*.conf` files in `conf.d`; back up other
custom configuration before running this role. Uninstalling the load balancer
interrupts access through its virtual IP addresses.
