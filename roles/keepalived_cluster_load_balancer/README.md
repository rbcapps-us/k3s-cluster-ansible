# Role: keepalived_cluster_load_balancer

Configure Keepalived virtual IP failover and TCP load balancing across the cluster
nodes. An empty service list invokes the
[uninstall role](../keepalived_cluster_load_balancer_uninstall/README.md).

## Inputs and requirements

This role has no defaults file. Shared settings come from [init](../init/README.md).
See [argument specifications](meta/argument_specs.yml) for the nested service schema.
Cluster node IPv4 facts must be available in `hostvars` for every backend host.
The selected interfaces must exist and the network must support the configured
virtual IP addresses and VRRP traffic.

| Variable | Type | Source/default | Purpose |
| --- | --- | --- | --- |
| `superuser_name` | str | Discovered by `init` | Privileged user and configuration owner. |
| `superuser_group` | str | Discovered by `init` | Configuration group owner. |
| `k3s_hosts_group` | str | `k3s_nodes` from `init` | Ordered inventory group for VRRP election and backends. |
| `cluster_load_balancer_services` | list of dict | `[]` from `init` | Virtual services to configure. |

Each service requires `vrrp_instance_name` (str), `network_interface` (str),
`virtual_router_id` (int), `ip_address` (str), and `ports` (list of dict).
Each port requires `port_number` (int) and `health_check_protocol` (str: `http`,
`https`, or `tcp`). HTTP/HTTPS checks also need `health_check_path` (str) and
`health_check_healthy_status_codes` (str, for example `200-299,404`).

## Behavior

Install Keepalived, write `/etc/keepalived/keepalived.conf` and one
`conf.d/k3s-<vrrp_instance_name>.conf` per service, and delete stale K3s-managed
service files. Configuration changes notify a restart handler. Enable and start
Keepalived, then flush handlers. All management runs as `superuser_name`.

The first inventory host is configured as `MASTER`; others are `BACKUP`, with
priority decreasing by inventory position. Backends use each node's default IPv4
address and the configured port. The template uses TCP, NAT forwarding, and
round-robin balancing; health checks use HTTP, HTTPS, or TCP as selected.
The main Keepalived configuration is overwritten by this role.

## Example

```yaml
cluster_load_balancer_services:
  - vrrp_instance_name: web
    network_interface: eth0
    virtual_router_id: 51
    ip_address: 192.0.2.10
    ports:
      - port_number: 443
        health_check_protocol: https
        health_check_path: /
        health_check_healthy_status_codes: "200-299,404"
```
