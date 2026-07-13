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
2. a **deterministic evidence plane** that normalizes sanitized telemetry, evaluates inspectable rules, verifies declared outcomes, and emits integrity-checkable report bundles.

The project thesis is simple:

> **A lab diagram proves architecture. A screenshot proves visibility. A reproducible experiment proves behavior.**

SOC_Replay preserves all three evidence classes without confusing one for another.

## The 90-second proof

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e .

soc-replay catalog
soc-replay explain scenarios/network-scan
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan
```

Expected result:

```text
replayed 7 events; detections=1
verification: PASS
manifest: build/network-scan/manifest.json
bundle verification: PASS
```

The bundle contains:

- `report.json` for machine processing;
- `report.md` for human review; and
- `manifest.json` with SHA-256 hashes and byte counts for both artifacts.

The report also records the scenario and event-file hashes, deterministic run ID, exact evidence-event IDs, correlation semantics, simulated response, and PASS/FAIL verdict against declared expectations.

Published reference: [network-scan report](examples/reports/network-scan.md) · [bundle manifest](examples/reports/network-scan.manifest.json)

## What makes this an engineering project

| Design decision | Why it matters | Evidence |
| --- | --- | --- |
| Deterministic offline replay | Identical inputs produce identical ordered detections and report bytes | Tests and committed reference bundles |
| Machine-verifiable expectations | Semantic drift fails CI instead of silently changing demos | `soc-replay verify` and scenario contracts |
| Tamper-evident bundles | Reviewers can detect report modification after generation | `manifest.json` and `soc-replay verify-bundle` |
| Cryptographic input provenance | Every report identifies the exact scenario and event bytes used | SHA-256 hashes and deterministic run IDs |
| Explicit window semantics | Correlation behavior is declared rather than buried in code | `first_per_group` and `all_non_overlapping` |
| Negative controls | The project demonstrates expected non-detection, not only positive demos | Approved-maintenance control scenario |
| Adapter/core separation | Vendor normalization can evolve without coupling the engine to live sensors | Sanitized Suricata EVE adapter |
| Simulation-only responses | Detection testing cannot silently acquire infrastructure authority | Contract rejects every non-simulated mode |
| Standard-library runtime | The core remains inspectable and portable | Zero runtime dependencies |
| Physical/replay separation | Installed hardware, design, measured behavior, and roadmap remain distinct | Implementation-state register |

## End-to-end system

![SOC_Replay telemetry and evidence pipeline](docs/assets/telemetry-flow.svg)

```text
bounded lab activity or sanitized telemetry
                    │
                    ▼
      vendor adapter / normalized JSONL
                    │
                    ▼
      inspectable match and correlation rules
                    │
                    ▼
 detections + simulated analyst recommendations
                    │
                    ▼
 expectations + provenance + report bundle
                    │
                    ▼
       offline bundle integrity verification
```

The replay package never contacts a switch, firewall, hypervisor, endpoint, or identity provider. Live changes remain outside the package and require separate human-governed procedures, approvals, and rollback controls.

## Sanitized Suricata bridge

The included adapter converts supported Suricata EVE `alert` and `flow` records into the normalized SOC_Replay event contract:

```bash
soc-replay normalize-suricata \
  examples/adapters/suricata-eve.jsonl \
  build/suricata-normalized.jsonl
```

It validates every emitted record through the same event model used by scenarios, preserves supported/skipped counts, writes atomically, and makes no live sensor connection. See [Suricata Adapter](docs/19-Suricata-Adapter.md).

## Implemented and testable today

| Capability | State | Verification path |
| --- | --- | --- |
| Normalized JSONL ingestion | Implemented | `src/soc_replay/io.py` and validation tests |
| Sanitized Suricata EVE normalization | Implemented | Adapter fixtures and byte-for-byte reference output |
| Strict scenario validation | Implemented | Python contract plus JSON schemas |
| Nested-field matching | Implemented | `details.*` path-resolution tests |
| Match operators | Implemented | `eq`, `ne`, `in`, `not_in`, `contains`, `gte`, `lte`, `exists` |
| Time-window correlation | Implemented | Threshold, grouping, distinct-value, and policy tests |
| Expected-outcome verification | Implemented | `soc-replay verify` and CI failure codes |
| Input provenance | Implemented | SHA-256 hashes and deterministic run IDs |
| Tamper-evident output bundles | Implemented | Artifact manifest and offline verification |
| Atomic JSON/Markdown/manifest writes | Implemented | Reporting and tamper tests |
| Static analysis and packaging | Implemented | Ruff, strict mypy, branch coverage, Python 3.11–3.13, wheel build |
| Physical lab integration | Documented platform | Architecture, inventory, topology, and operations docs |
| Autonomous containment | Deliberately not claimed | Simulation-only contract boundary |

## Included experiments

| Scenario | Role | Detection concept | Expected result |
| --- | --- | --- | --- |
| [Network scan](scenarios/network-scan) | Positive control | Five blocked events across five ports inside 60 seconds | One high detection |
| [Privileged group change](scenarios/privileged-group-change) | Positive control | Unauthorized privileged membership change without a ticket | One critical detection |
| [Failed authentication burst](scenarios/failed-authentication-burst) | Repeated-window control | Two non-overlapping failed-logon bursts | Two medium detections |
| [Approved privileged maintenance](scenarios/benign-privileged-change) | Negative control | Ticketed and authorized administrative activity | Zero detections |

Every scenario contains synthetic events, a precise authorization boundary, inspectable rules, machine-readable expectations, and a committed JSON/Markdown/manifest reference bundle.

## Physical platform

![SOC_Replay physical and logical architecture](docs/assets/platform-topology.svg)

The cyber range uses enterprise hardware repurposed for controlled defensive research:

| Layer | Representative components | Role |
| --- | --- | --- |
| Secure compute | Dell PowerEdge R710 with Qubes OS | Compartmentalized management and experiment domains |
| Storage and virtualization | EqualLogic/Avid platform with Proxmox VE | Storage-backed services, workloads, snapshots, and recovery |
| Network enforcement | Dell X1052P and Cisco ASA appliances | VLAN trunks, segmentation, and controlled inter-zone paths |
| Detection and analysis | SELKS/Suricata on a dedicated SOC node | Network evidence and analyst workflows |
| Recovery | OpenGear console and KVM path | Out-of-band access when normal networking is unavailable |

Photographs prove installation. Configurations prove intended policy. Replay bundles prove deterministic rule behavior. Measured experiments prove end-to-end platform behavior. See [Hardware](docs/02-Hardware.md), [Network Topology](docs/04-Network-Topology.md), and [Implementation State](docs/14-Implementation-State.md).

## Repository architecture

```text
SOC_Replay/
├── src/soc_replay/                 # contracts, engine, adapters, CLI, reports
│   └── adapters/                   # offline vendor normalization
├── scenarios/                      # positive, repeated-window, and negative controls
├── examples/
│   ├── adapters/                   # sanitized input and normalized reference output
│   └── reports/                    # deterministic reference bundles
├── schemas/                        # event, scenario, report, and manifest contracts
├── tests/                          # model, engine, adapter, CLI, reporting, repository tests
├── tools/                          # repository verification and benchmark harness
├── templates/                      # measured experiment record template
├── assets/                         # physical build photographs and legacy diagrams
├── docs/                           # versioned architecture and operating documentation
│   └── wiki/                       # concise source for GitHub Wiki synchronization
└── .github/workflows/ci.yml        # lint, type, test, verify, package
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
soc-replay verify scenarios/benign-privileged-change
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
- [Evidence bundles](docs/18-Evidence-Bundles.md)
- [Suricata adapter](docs/19-Suricata-Adapter.md)
- [Measured experiment record](docs/20-Experiment-Record.md)
- [Threat model](docs/21-Threat-Model.md)

The version-controlled material under `docs/` is the maintained source of truth. Concise wiki copy lives under [`docs/wiki/`](docs/wiki/) so public documentation can be synchronized without becoming the only canonical record.

## Scope and safety boundary

SOC_Replay is a personally operated defensive research and demonstration environment. Public scenarios and adapter fixtures use synthetic or sanitized telemetry. The package does not generate traffic, deploy payloads, bypass controls, modify accounts, operate network devices, or execute response commands.

A bundle manifest proves artifact integrity relative to its recorded hashes. It does **not** prove authorship, trusted time, or external chain of custody.

## Current status

**Physical platform:** installed and documented  
**Replay engine:** implemented, expectation-verified, provenance-aware, and packaged  
**Adapter surface:** sanitized Suricata EVE `alert` and `flow` normalization  
**Experiment evidence:** four deterministic controls, including one zero-detection control  
**Output integrity:** manifest-backed bundles with offline verification  
**Live response:** human-governed and outside the replay package  
**Canonical documentation:** version-controlled `docs/`
