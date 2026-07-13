# 06 — Monitoring and telemetry

Observability is the connection between the physical lab and defensible experiment results.

![SOC_Replay telemetry flow](assets/telemetry-flow.svg)

## Sensor and evidence layers

| Layer | Sources | Evidence produced |
| --- | --- | --- |
| Network boundary | Cisco ASA, SonicWall, core switch | Policy events, connection records and boundary logs |
| Network detection | SELKS / Suricata on the Toughbook | IDS alerts, flow context and packet-derived evidence |
| Hypervisor and workload | Qubes domains, Proxmox workloads | Service, system and VM/container events |
| Storage and infrastructure | EqualLogic/Avid, compute and switch | Health, capacity and availability metrics |
| Central collection | Syslog/Elastic-family pipeline | Searchable cross-source timeline |
| Visualization | SELKS/Kibana/Grafana-style views | Analyst navigation and status views |
| Replay utility | Normalized JSONL events | Deterministic detection and report output |

## Dedicated SOC node

The Panasonic Toughbook provides a physically distinct monitoring and analysis surface. SELKS and Suricata are documented as its central network-detection stack. This separation reduces the chance that an experiment workload and the primary analyst console fail together.

## Telemetry path

1. Workload or boundary activity occurs inside a defined zone.
2. Relevant traffic or logs reach the detection/collection layer.
3. Alerts retain source timestamps and contextual fields.
4. The analyst correlates events with topology and policy state.
5. Response and validation records are added to the experiment record.
6. Sanitized exports may be normalized for deterministic replay.

## Normalized replay contract

The repository’s replay utility requires stable event IDs, timestamps, source, category and action. Common optional fields include addresses, ports, host, user, outcome, tags and vendor-specific details.

A replay detection preserves:

- rule ID and name;
- severity;
- first and last matching time;
- exact supporting event IDs;
- grouping values; and
- simulated response recommendation.

## Evidence limits

A dashboard screenshot demonstrates that an interface existed at capture time. It does not prove sensor completeness, detection accuracy, response latency or containment effectiveness. Those claims require source records and measured experiments.
