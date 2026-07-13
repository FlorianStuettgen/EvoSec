<div align="center">

# SOC_Replay

### An evidence-first cyber range: real segmented infrastructure, deterministic detection replay, and auditable experiment records

[![CI](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml/badge.svg)](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11–3.13-3776AB?logo=python&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-dependency%20free-0f766e)
![Boundary](https://img.shields.io/badge/response-simulation%20only-b45309)
![License](https://img.shields.io/badge/license-MIT-0f172a)

</div>

![SOC_Replay platform overview](docs/assets/soc-replay-hero.svg)

SOC_Replay connects two things that security portfolios often leave separate:

1. a **physical, segmented cyber range** with compute, storage, enforcement, telemetry, and out-of-band recovery; and
2. a **deterministic replay engine** that turns synthetic or sanitized telemetry into inspectable detections, simulated response recommendations, and machine-verifiable evidence reports.

The project thesis is simple:

> **A lab diagram proves architecture. A screenshot proves visibility. A reproducible experiment proves behavior.**

SOC_Replay is built to preserve all three evidence classes without confusing one for another.

## The 90-second proof

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e .

soc-replay catalog
soc-replay explain scenarios/network-scan
soc-replay run scenarios/network-scan --output build/network-scan
```

Expected terminal result:

```text
replayed 7 events; detections=1
verification: PASS
  PASS detection_count: expected=1 actual=1
  PASS rule_ids: expected=['NET-SCAN-001'] actual=['NET-SCAN-001']
  PASS severity_counts: expected={'high': 1} actual={'high': 1}
  PASS simulated_action_count: expected=1 actual=1
```

The generated report includes:

- the exact matching rule and evidence-event IDs;
- the correlation window and distinct-value threshold;
- a simulation-only response recommendation;
- SHA-256 hashes of both input files;
- a deterministic run ID; and
- a PASS/FAIL verdict against scenario expectations.

Published reference: [network-scan report](examples/reports/network-scan.md)

## What makes this an engineering project

| Design decision | Why it matters | Evidence |
| --- | --- | --- |
| Deterministic offline replay | The same inputs produce the same ordered detections and report bytes | Tests and committed reference reports |
| Machine-verifiable expectations | Scenarios fail CI when rules stop producing the intended result | `soc-replay verify` and scenario contracts |
| Cryptographic provenance | Reports identify the exact scenario and event inputs that produced them | SHA-256 hashes and deterministic run IDs |
| Explicit window semantics | Correlation behavior is declared rather than hidden in implementation detail | `first_per_group` and `all_non_overlapping` policies |
| Simulation-only responses | Detection testing cannot silently become infrastructure control | Contract validation rejects every non-simulated mode |
| Standard-library runtime | The core remains easy to inspect, package, and execute in constrained environments | Zero runtime dependencies |
| Physical/replay separation | Installed hardware, documented design, measured behavior, and roadmap work remain distinct | Implementation-state register |

## End-to-end system

![SOC_Replay telemetry and evidence pipeline](docs/assets/telemetry-flow.svg)

```text
bounded lab activity or sanitized telemetry
                    │
                    ▼
        normalized JSONL event contract
                    │
                    ▼
      inspectable match and correlation rules
                    │
                    ▼
 detections + simulated analyst recommendations
                    │
                    ▼
 provenance + expectations + JSON/Markdown report
```

The replay engine never contacts a switch, firewall, hypervisor, endpoint, or identity provider. Live changes remain outside the package and require separate human-governed operating procedures.

## Implemented and testable today

| Capability | State | Verification path |
| --- | --- | --- |
| Normalized JSONL ingestion | Implemented | `src/soc_replay/io.py` and model tests |
| Strict scenario validation | Implemented | Python contract plus JSON schemas |
| Nested-field matching | Implemented | `details.*` path resolution tests |
| Match operators | Implemented | `eq`, `ne`, `in`, `not_in`, `contains`, `gte`, `lte`, `exists` |
| Time-window correlation | Implemented | Threshold, grouping, distinct values, and policy tests |
| Expected-outcome verification | Implemented | `soc-replay verify` and CI failure codes |
| Input provenance | Implemented | SHA-256 hashes and deterministic run IDs |
| Atomic JSON/Markdown reports | Implemented | Reporting tests and reference-output checks |
| Static analysis and packaging | Implemented | Ruff, strict mypy, branch coverage gate, Python 3.11–3.13, and wheel build |
| Physical lab integration | Documented platform | Architecture, inventory, topology, and operations docs |
| Autonomous containment | Deliberately not claimed | Simulation-only contract boundary |

## Included experiments

| Scenario | Detection concept | Correlation behavior | Expected result |
| --- | --- | --- | --- |
| [Network scan](scenarios/network-scan) | Blocked multi-port connection burst | Five events and five distinct ports inside 60 seconds | One high detection |
| [Privileged group change](scenarios/privileged-group-change) | Unauthorized privileged membership change with no ticket | Single-event rule with nested detail lookup | One critical detection |
| [Failed authentication burst](scenarios/failed-authentication-burst) | Repeated failed logons for one user and host | Two non-overlapping three-event windows | Two medium detections |

Every scenario contains synthetic events, an authorization boundary, inspectable rules, machine-readable expectations, and committed reference reports.

## Physical platform

![SOC_Replay physical and logical architecture](docs/assets/platform-topology.svg)

The cyber range is built around enterprise hardware repurposed for controlled defensive research:

| Layer | Representative components | Role |
| --- | --- | --- |
| Secure compute | Dell PowerEdge R710 with Qubes OS | Compartmentalized management and experiment domains |
| Storage and virtualization | EqualLogic/Avid platform with Proxmox VE | Storage-backed services, workloads, snapshots, and recovery |
| Network enforcement | Dell X1052P and Cisco ASA appliances | VLAN trunks, segmentation, and controlled inter-zone paths |
| Detection and analysis | SELKS/Suricata on a dedicated SOC node | Network evidence and analyst workflows |
| Recovery | OpenGear console and KVM path | Out-of-band access when normal networking is unavailable |

Photographs prove installation. Configurations prove intended policy. Replay reports and measured experiments prove behavior. See [Hardware](docs/02-Hardware.md), [Network Topology](docs/04-Network-Topology.md), and [Implementation State](docs/14-Implementation-State.md).

## Repository architecture

```text
SOC_Replay/
├── src/soc_replay/                 # contracts, engine, provenance, CLI, reports
├── scenarios/                      # executable synthetic experiments
├── examples/reports/               # deterministic reference evidence
├── schemas/                        # event, scenario, and report contracts
├── tests/                          # model, engine, CLI, reporting, and repository-contract tests
├── tools/                          # reference verification and benchmark harness
├── assets/                         # physical build photographs and legacy diagrams
├── docs/                           # versioned architecture and operating documentation
│   └── wiki/                       # canonical source for future GitHub Wiki synchronization
└── .github/workflows/ci.yml        # compile, test, verify, compare, package
```

## Quality gates

```bash
python -m pip install -e ".[dev]"
ruff check src tests tools
mypy
python -m compileall -q src tests tools
coverage run -m unittest discover -s tests -v
coverage report
soc-replay catalog
soc-replay verify scenarios/network-scan
soc-replay verify scenarios/privileged-group-change
soc-replay verify scenarios/failed-authentication-burst
python tools/verify_repository.py
python -m pip wheel . --no-deps -w dist
```

A local throughput harness is available without publishing machine-dependent performance claims:

```bash
python tools/benchmark.py --events 100000
```

## Architecture and operating documentation

Start with:

- [Documentation map](docs/README.md)
- [Architecture](docs/01-Architecture.md)
- [Replay engine](docs/11-Replay-Engine.md)
- [Scenario contract](docs/12-Scenario-Format.md)
- [Experiment lifecycle](docs/13-Experiment-Lifecycle.md)
- [Implementation-state register](docs/14-Implementation-State.md)
- [Demo playbook](docs/15-Demo-Playbook.md)
- [Engineering review](docs/16-Engineering-Review.md)
- [Architecture decisions](docs/17-Architecture-Decisions.md)

The version-controlled material under `docs/` is the maintained source of truth. The legacy GitHub Wiki contains historical prose that can drift; a clean synchronization source now lives under [`docs/wiki/`](docs/wiki/).

## Scope and safety boundary

SOC_Replay is a personally operated defensive research and demonstration environment. Public scenarios use synthetic or sanitized telemetry. The replay package does not generate traffic, deploy payloads, bypass controls, modify accounts, operate network devices, or execute response commands.

## Current status

**Physical platform:** installed and documented  
**Replay engine:** implemented, expectation-verified, provenance-aware, and packaged  
**Experiment evidence:** three deterministic reference scenarios  
**Live response:** human-governed and outside the replay package  
**Canonical documentation:** version-controlled `docs/`
