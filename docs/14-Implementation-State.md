# 14 — Implementation state

This register is the source of truth for capability language across the README, docs, diagrams and wiki.

## Physical platform

| Capability | State | Notes |
| --- | --- | --- |
| Enterprise rack and console equipment | Installed/documented | Photographs restored under `assets/photos/` |
| Dell R710 secure compute platform | Installed; Qubes role documented | Current configuration export remains private |
| EqualLogic/Avid storage platform | Installed/documented | Proxmox role documented; detailed storage topology should be refreshed |
| Dell X1052P core switch | Installed/documented | VLAN design documented; sanitized running configuration is a near-term evidence goal |
| Cisco ASA 5510 and 5515-X | Installed/documented | Policy baselines restored; current deployment state may differ by experiment |
| SonicWall SRA 4200 | Installed/documented | Remote-access/boundary experiment role documented |
| OpenGear/KVM/OOB path | Installed/documented | Recovery procedure evidence should be added |
| Toughbook SELKS/Suricata SOC node | Installed/documented | Monitoring captures restored |

## Logical platform

| Capability | State | Notes |
| --- | --- | --- |
| Management/Core/DMZ/Lab/Honeypot/Guest model | Documented architecture | Current config evidence required for operational claims |
| VLAN 10/20/30 workload mapping | Historical documented mapping | Validate against current switch/firewall state |
| Central log aggregation | Partially evidenced/documented | Publish sanitized source-to-index map |
| Grafana/visual dashboards | Partially evidenced/documented | Screenshots do not prove full integration |
| Snapshot and rollback model | Documented operating practice | Publish one measured recovery record |

## Automation

| Capability | State | Notes |
| --- | --- | --- |
| Repository CI | Implemented | GitHub Actions compiles/tests/replays scenarios |
| Configuration-management concepts | Documented | SaltStack direction; Ansible/script folders are conceptual baselines |
| LLM-assisted interpretation | Prototype/design track | Must name model, inputs, outputs and authority boundary |
| Dynamic VLAN reassignment | Prototype/design claim | No general latency or autonomy claim without measured experiment |
| Automated honeypot/tar-pit activation | Prototype/design claim | Requires adapter and validation evidence |
| Autonomous containment | Not generally claimed | Human-governed until bounded implementation is proven |
| Predictive maintenance | Roadmap | Future work only |

## Evidence replay utility

| Capability | State | Evidence |
| --- | --- | --- |
| Event ingestion and validation | Implemented | Source and tests |
| Rule matching and aggregation | Implemented | Source and tests |
| Deterministic reports | Implemented | Committed examples |
| Simulation-only recommendations | Implemented | Runtime validation |
| Physical telemetry adapters | Not implemented | Read-only adapter contract is roadmap work |
| Live response | Deliberately absent | Outside replay-core boundary |

## Language rule

A capability may only be described at or below the maturity recorded here. New evidence should update this page first, then propagate to the README and relevant chapter.
