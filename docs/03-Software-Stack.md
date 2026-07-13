# 03 — Software stack

The SOC_Replay software stack spans secure desktop virtualization, server virtualization, network detection, infrastructure management, logging and evidence tooling.

## Confirmed and documented platform stack

| Layer | Technology | Role | State |
| --- | --- | --- | --- |
| Secure compute | Qubes OS | Compartmentalized domains on the Dell R710 | Documented operating role |
| Storage/service virtualization | Proxmox VE | Storage-centric VMs, containers and snapshots | Documented operating role |
| VM foundation | KVM/libvirt | Underlying virtualization technologies | Platform dependency |
| SOC distribution | SELKS | Dedicated security-monitoring environment | Installed/documented |
| Network IDS/IPS | Suricata | Packet inspection, alerting and network evidence | Installed/documented |
| Firewall platforms | Cisco ASA software, SonicWall firmware | Segmentation, policy and remote-access experiments | Hardware-backed platform role |
| Virtual switching | Qubes/Proxmox networking and optional OVS | Workload segmentation and trunks | Configuration-dependent |
| Packet analysis | Wireshark/TShark | Investigation and capture review | Documented toolset |
| Configuration management | SaltStack | Intended orchestration and state enforcement | Prototype/design track |
| Central logging | Elastic-family stack / syslog pipeline | Event aggregation and search | Partially evidenced/documented |
| Dashboards | Grafana and SOC interfaces | Infrastructure and security visualization | Partially evidenced/documented |
| Evidence replay | Python 3.11+ standard-library package | Deterministic stored-event validation | Implemented and tested |

## Hypervisor responsibilities

### Qubes OS on the R710

Qubes is the trust-oriented compute layer. Management and experiment workloads can be separated by security domain, reducing the chance that a lab workload shares the same trust level as privileged administration.

### Proxmox VE on the storage platform

Proxmox provides a practical service and storage workload layer. The repository documents VM/container provisioning, snapshots and recovery as its core responsibilities. It should not be described as supporting live migration unless the specific cluster/storage configuration is measured and documented.

## SOC and telemetry software

SELKS packages Suricata and analyst tooling into the dedicated SOC node. Firewall logs, packet-derived alerts and host/service telemetry may be correlated through centralized logging. The monitoring chapter distinguishes installed sensors from planned integrations.

## Automation stack

Historical documentation named LLM-driven orchestration, SaltStack, Ansible/Terraform concepts and CI/CD. The corrected model is:

- **SaltStack/LLM orchestration:** project-specific prototype/design track.
- **Ansible playbooks and helper scripts:** conceptual/sanitized contribution areas under `docs/infra/`.
- **GitHub Actions:** implemented repository CI for the Python replay utility.
- **Live network changes:** require an explicit adapter, approval model, dry-run capability, audit log and rollback validation before being described as operational.

## Replay utility

The package under `src/soc_replay/` accepts scenario definitions and normalized JSONL events. It evaluates inspectable conditions and time-window correlations, then writes JSON and Markdown reports. It has no network client or command-execution path.

See [Replay Engine](11-Replay-Engine.md).
