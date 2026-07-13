<div align="center">

# SOC_Replay

### A self-hosted, segmented cyber range and SOC experimentation platform built from enterprise infrastructure

[![CI](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml/badge.svg)](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml)
![Platform](https://img.shields.io/badge/platform-physical%20lab-0f766e)
![Evidence](https://img.shields.io/badge/evidence-replay%20core-2563eb)
![Boundary](https://img.shields.io/badge/live%20response-human%20governed-b45309)
![License](https://img.shields.io/badge/license-MIT-0f172a)

</div>

![SOC_Replay platform overview](docs/assets/soc-replay-hero.svg)

SOC_Replay documents an existing home cyber range assembled from enterprise servers, storage, network-security appliances, out-of-band management, segmented virtual workloads, and a dedicated SOC node. Its purpose is to make the lab understandable, reproducible, recoverable, and useful for controlled defensive experimentation.

The repository has two connected responsibilities:

1. **Platform record:** the rack, hardware, hypervisors, trust zones, telemetry paths, operating procedures, photographs, diagrams, and configuration baselines.
2. **Evidence tooling:** a small deterministic Python replay utility that evaluates synthetic or sanitized telemetry and produces inspectable reports.

The replay utility supports the lab; it does not replace the lab as the project’s identity.

## What exists

| Layer | Documented platform | Primary role |
| --- | --- | --- |
| Secure compute | Dell PowerEdge R710 running Qubes OS | Compartmentalized management and experiment domains |
| Storage and secondary virtualization | Dual EqualLogic FS7610 controllers with Avid storage chassis and Proxmox VE | Storage-backed services, VM/container workloads, snapshots and recovery |
| Core networking | Dell X1052P managed PoE switch | VLAN trunks, segmentation and controlled inter-zone paths |
| Security edge | Cisco ASA 5510, Cisco ASA 5515-X, SonicWall SRA 4200 | Policy enforcement, remote-access experiments, logging and boundary control |
| SOC and network detection | Panasonic Toughbook running SELKS and Suricata | IDS/IPS analysis, packet visibility and analyst console |
| Out-of-band recovery | OpenGear CM4148, StarTech KVM and HP TFT5600 rack console | Console access when the production path is unavailable |
| Evidence replay | Python package under `src/soc_replay/` | Deterministic evaluation of stored defensive telemetry |

## Architecture at a glance

![SOC_Replay physical and logical architecture](docs/assets/platform-topology.svg)

The platform is organized around six trust zones:

| Zone | Colour | Purpose |
| --- | --- | --- |
| Management | Blue | Administrative workstations, console access and privileged operations |
| Core | Green | Switching, storage and critical platform services |
| DMZ | Yellow | Deliberately exposed or boundary-facing services |
| Lab | Orange | Application workloads, development and controlled experiments |
| Honeypot | Red | Decoy services, honeypots and tar-pit workloads |
| Guest | Black | Temporary, visitor or otherwise non-critical access |

The historical workload mapping uses VLAN 10 for lab application VMs, VLAN 20 for honeypots and VLAN 30 for tar-pit workloads. The trust-zone model is broader than those three workload VLANs and includes management, core, DMZ and guest boundaries. See [Network Topology](docs/04-Network-Topology.md).

## Platform state without marketing fog

SOC_Replay deliberately separates physical existence from software maturity.

| Capability | State | Evidence |
| --- | --- | --- |
| Rack, servers, storage, switch, firewalls and OOB hardware | **Installed / documented** | Component photographs and inventory |
| Qubes OS compute role | **Documented operating role** | Architecture and software-stack records |
| Proxmox-backed storage/service role | **Documented operating role** | Hardware and software-stack records |
| SELKS/Suricata SOC node | **Installed / documented** | SOC photographs and monitoring records |
| VLAN/trust-zone architecture | **Documented design** | Diagrams, topology chapter and firewall-policy library |
| Centralized telemetry and dashboards | **Partially evidenced** | Monitoring captures and documented integration path |
| Deterministic replay engine | **Implemented and tested** | Source, scenarios, reports and CI |
| SaltStack/LLM-assisted orchestration | **Prototype/design track** | Architecture and automation documentation; requires scenario-specific validation |
| Autonomous containment | **Not claimed as generally operational** | Any implementation must publish measured evidence, approval boundaries and rollback results |
| Predictive maintenance and multi-site expansion | **Roadmap** | Roadmap only |

This matrix is the controlling statement when older diagrams or wiki prose use broader language.

## Physical build evidence

<table>
<tr>
<td width="50%"><img src="assets/photos/test2.jpeg" alt="SOC_Replay rack overview"></td>
<td width="50%"><img src="assets/photos/R710.jpg" alt="Dell PowerEdge R710"></td>
</tr>
<tr>
<td align="center"><strong>Rack and integrated platform</strong></td>
<td align="center"><strong>Primary Qubes OS compute host</strong></td>
</tr>
<tr>
<td width="50%"><img src="assets/photos/EqualLogic.png" alt="EqualLogic storage"></td>
<td width="50%"><img src="assets/photos/Dell X1052P.jpg" alt="Dell X1052P switch"></td>
</tr>
<tr>
<td align="center"><strong>Storage platform</strong></td>
<td align="center"><strong>Core managed switch</strong></td>
</tr>
</table>

The full component gallery is indexed in [Hardware](docs/02-Hardware.md) and [Appendix](docs/10-Appendix.md).

## Traffic, telemetry and control

![SOC_Replay telemetry and control flow](docs/assets/telemetry-flow.svg)

The intended operating loop is:

1. A bounded lab workload or decoy service produces activity.
2. The switch and firewall path preserve segmentation and forward relevant logs or mirrored traffic.
3. SELKS/Suricata and supporting telemetry layers provide detection evidence.
4. An analyst or governed automation layer evaluates the evidence.
5. Any network-state change is recorded, validated and recoverable through the OOB path.
6. Sanitized events can be replayed through the repository’s deterministic evidence utility.

The replay engine never contacts the switch, firewall, hypervisor or identity systems. It is a validation tool, not a hidden live-response path.

## Repository map

```text
SOC_Replay/
├── assets/
│   ├── diagrams/                  # original architecture and capability diagrams
│   └── photos/                    # rack and component evidence
├── docs/
│   ├── 01-Architecture.md         # full physical/logical system model
│   ├── 02-Hardware.md             # exact inventory and photo index
│   ├── 03-Software-Stack.md       # hypervisors, SOC and automation stack
│   ├── 04-Network-Topology.md     # trust zones, VLANs and traffic paths
│   ├── 05-CI-CD-Automation.md     # platform automation and repository CI
│   ├── 06-Monitoring-Telemetry.md # sensors, logging and evidence flow
│   ├── 07-Security-Model.md       # boundaries, recovery and policy controls
│   ├── 08-Use-Cases.md            # controlled defensive experiments
│   ├── 09-Roadmap.md              # sequenced platform evolution
│   ├── 10-Appendix.md             # glossary, status model and asset index
│   ├── 11-Replay-Engine.md        # evidence utility internals
│   ├── 12-Scenario-Format.md       # replay data contract
│   ├── 13-Experiment-Lifecycle.md # experiment evidence standard
│   ├── 14-Implementation-State.md # source-of-truth maturity register
│   └── infra/                     # restored firewall policy baselines
├── src/soc_replay/                # deterministic replay utility
├── scenarios/                     # synthetic example exercises
├── examples/reports/              # committed reference outputs
├── schemas/                       # event and scenario contracts
├── tests/                         # replay utility tests
└── .github/workflows/ci.yml       # compile, test, validate and replay
```

## Start with the platform

- [Architecture](docs/01-Architecture.md)
- [Hardware Inventory](docs/02-Hardware.md)
- [Software Stack](docs/03-Software-Stack.md)
- [Network Topology](docs/04-Network-Topology.md)
- [Monitoring and Telemetry](docs/06-Monitoring-Telemetry.md)
- [Implementation State](docs/14-Implementation-State.md)

The restored firewall configuration library is under [`docs/infra/lab-firewall-policies/`](docs/infra/lab-firewall-policies/). It is a sanitized lab baseline, not a claim that every example is currently deployed unchanged.

## Optional: run the evidence replay utility

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e .

soc-replay catalog
soc-replay validate scenarios/network-scan
soc-replay run scenarios/network-scan --output build/network-scan
```

Expected output:

```text
replayed 7 events; detections=1
json: build/network-scan/report.json
markdown: build/network-scan/report.md
```

The utility supports stored events, inspectable matching and time-window correlation, simulated recommendations, deterministic reports and CI across Python 3.11–3.13. See [Replay Engine](docs/11-Replay-Engine.md).

## Operating principles

- **Document the real system first.** Hardware, interfaces, zones and recovery paths are not decorative context.
- **Separate evidence classes.** A photograph proves installation; configuration proves intent; measured telemetry proves behaviour.
- **Preserve human authority.** Automation that can alter network state requires explicit scope, validation and rollback.
- **Keep OOB recovery independent.** Console access must remain available when an experiment disrupts normal networking.
- **Use sanitized examples.** Public files must not expose credentials, keys, live public addresses or sensitive incident data.
- **Treat the wiki as history, not the only source.** The file-based documentation in this repository is the maintained source of truth.

## Boundaries

SOC_Replay is a personally operated research and demonstration environment. It is not a commercial SOC, a production security guarantee, or authorization for testing systems outside the owner’s controlled environment. Broad historical claims about autonomous response or millisecond-scale orchestration require named, measured experiments before they are treated as verified capabilities.

## Status

**Physical platform:** installed and documented  
**Repository:** platform documentation restored; replay utility retained  
**Primary purpose:** self-hosted cyber range, SOC lab and reproducible defensive experimentation  
**Source of truth:** [`docs/14-Implementation-State.md`](docs/14-Implementation-State.md)

See [CHANGELOG](CHANGELOG.md) for the restoration record.
