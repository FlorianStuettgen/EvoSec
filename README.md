<div align="center">

# SOC_Replay

### An evidence-first cyber range with a compiled detection engine, deterministic execution ledger, and verifiable experiment bundles

[![CI](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml/badge.svg)](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11–3.13-3776AB?logo=python&logoColor=white)
![Coverage](https://img.shields.io/badge/branch%20coverage-90%25%2B-16a34a)
![Runtime](https://img.shields.io/badge/runtime-zero%20dependencies-0f766e)
![Boundary](https://img.shields.io/badge/response-simulation%20only-b45309)
![License](https://img.shields.io/badge/license-MIT-0f172a)

</div>

![SOC_Replay platform overview](docs/assets/soc-replay-hero.svg)

SOC_Replay joins two systems that security portfolios usually present separately:

1. a **real segmented cyber range** with enterprise compute, storage, network enforcement, telemetry, and out-of-band recovery; and
2. a **deterministic evidence engine** that compiles inspectable detection rules, evaluates synthetic or sanitized telemetry, verifies declared outcomes, and publishes integrity-checkable report bundles.

The project is built around one principle:

> **A diagram proves architecture. A screenshot proves visibility. A reproducible experiment proves behavior.**

SOC_Replay preserves those evidence classes without pretending they are interchangeable.

## The 90-second proof

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e .

soc-replay doctor
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan
```

Expected result:

```text
replayed 7 events; detections=1
verification: PASS
plan: <64-character semantic fingerprint>
ledger: <64-character execution root>
bundle: <64-character bundle identity>
bundle verification: PASS
```

The generated bundle contains:

```text
build/network-scan/
├── report.json      # machine-readable evidence
├── report.md        # analyst-readable evidence
└── manifest.json    # artifact hashes, execution identity, and bundle ID
```

## The execution fabric

![SOC_Replay execution core](docs/assets/execution-core.svg)

The engine is not a chain of loosely connected helper functions. It is an explicit five-stage pipeline:

| Stage | Responsibility | Deterministic output |
| --- | --- | --- |
| **Load** | Validate immutable scenario and JSONL event inputs | Input provenance and run ID |
| **Compile** | Convert field paths and operators into an execution plan | Plan and per-rule fingerprints |
| **Index** | Build semantics-preserving candidate indexes | Stable index digest |
| **Evaluate** | Execute single-event and time-window rules | Ordered detection set |
| **Verify** | Compare detections with declared expectations | Machine-readable PASS/FAIL |

Every stage appends an entry to a cryptographically linked execution ledger. Each entry commits to:

- the previous entry hash;
- stage input and output digests;
- record counts;
- deterministic stage metadata; and
- the exact execution order.

The final ledger root is embedded in both the report and bundle manifest. Post-generation modification of the report, manifest, or internal stage chain is detectable offline.

See [Execution Core](docs/22-Execution-Core.md) and [Execution Ledger](docs/23-Execution-Ledger.md).

## What the redesign changes underneath

### Compiled rules

Field paths are parsed once. Operator functions are resolved once. Aggregate strategies and candidate hints are prepared before the first event is evaluated. Each rule receives a semantic fingerprint derived from the behavior it will execute—not from object identity or runtime timing.

### Candidate indexing without semantic shortcuts

The engine builds immutable indexes for common equality selectors and tags. A rule can begin from a smaller candidate set, but every candidate still passes through every compiled condition. Indexes change cost, never meaning.

### Deterministic observability

The report records candidate strategy, candidate count, matched count, correlation semantics, rule fingerprint, evidence-event IDs, and stage ledger. A reviewer can see not only **what fired**, but **how the engine reached the result**.

### Extension surfaces with hard boundaries

- The **adapter registry** normalizes stored synthetic or sanitized vendor telemetry.
- The **operator registry** contains a deliberately small inspectable predicate set.
- The **pipeline contract** remains independent of live collection and response systems.
- The **response model** rejects every mode except `simulated`.

The package contains no socket client, subprocess runner, firewall connector, endpoint agent, credential store, or live-response executor.

## Engineering decisions and proof

| Decision | Reason | Evidence |
| --- | --- | --- |
| Compile before evaluation | Remove repeated path parsing and centralize rule semantics | Compiler tests and plan fingerprints |
| Index once per run | Reduce unnecessary scans without altering matches | Candidate-strategy metadata and equivalence tests |
| Hash-chain the stages | Make internal execution tampering observable | Ledger verification and corruption tests |
| Verify exact expectations | Turn scenarios into regression contracts | Four executable positive/repeated/negative controls |
| Keep runtime dependency-free | Maximize portability and inspectability | Standard-library package and wheel |
| Separate adapters from core | Isolate vendor parsing and permissions | Adapter protocol and registry |
| Manifest-last bundle commit | Distinguish complete bundles from partial writes | Atomic writes and bundle verification |
| Preserve simulation-only responses | Prevent detection testing from acquiring authority | Runtime and schema validation |

## Included experiments

| Scenario | Role | Expected result |
| --- | --- | --- |
| [Network scan](scenarios/network-scan) | Positive correlation control | One high-severity detection |
| [Privileged group change](scenarios/privileged-group-change) | Positive nested-field control | One critical detection |
| [Failed authentication burst](scenarios/failed-authentication-burst) | Repeated-window control | Two medium detections |
| [Approved privileged maintenance](scenarios/benign-privileged-change) | Negative control | Zero detections |

Every scenario contains a precise authorization boundary, synthetic telemetry, inspectable rules, exact expectations, and repeatably verified bundle generation.

## Sanitized telemetry adapters

The adapter surface is offline and registry-driven:

```bash
soc-replay adapters
soc-replay normalize \
  --adapter suricata-eve \
  examples/adapters/suricata-eve.jsonl \
  build/suricata-normalized.jsonl
```

The Suricata adapter supports stored `alert` and `flow` records, validates every emitted event through the same public model as scenarios, reports skipped record types, writes atomically, and emits a deterministic output hash.

## Physical platform

![SOC_Replay physical and logical architecture](docs/assets/platform-topology.svg)

| Layer | Representative components | Role |
| --- | --- | --- |
| Secure compute | Dell PowerEdge R710 with Qubes OS | Compartmentalized management and experiment domains |
| Storage and virtualization | EqualLogic/Avid platform with Proxmox VE | Storage-backed workloads, snapshots, and recovery |
| Network enforcement | Dell X1052P and Cisco ASA appliances | VLAN segmentation and controlled inter-zone paths |
| Detection and analysis | SELKS/Suricata on a dedicated SOC node | Network evidence and analyst workflows |
| Recovery | OpenGear console and KVM path | Out-of-band access when normal networking is unavailable |

Photographs prove installation. Configurations prove intended policy. Replay bundles prove deterministic rule behavior. Measured lab records prove end-to-end platform behavior.

## Command surface

```text
soc-replay validate <scenario>
soc-replay explain <scenario> [--json]
soc-replay run <scenario> --output <directory>
soc-replay verify <scenario>
soc-replay verify-bundle <directory>
soc-replay catalog [--json]
soc-replay adapters [--json]
soc-replay normalize --adapter <name> <source> <destination>
soc-replay graph --format text|json|mermaid
soc-replay doctor [--json]
```

`doctor` checks the pipeline contract, operator registry, adapter registry, and scenario catalog. `graph` exposes the execution wiring rather than leaving architecture implicit.

## Repository architecture

```text
SOC_Replay/
├── src/soc_replay/
│   ├── compiler.py             # executable rule plans and fingerprints
│   ├── indexing.py             # immutable candidate routing
│   ├── correlation.py          # single-event and window evaluation
│   ├── pipeline.py             # five-stage orchestration
│   ├── ledger.py               # deterministic hash chain
│   ├── report.py               # bundles and offline verification
│   ├── adapters/               # offline vendor normalization registry
│   └── cli.py                  # operational command surface
├── scenarios/                  # positive, repeated-window, and negative controls
├── schemas/                    # event, scenario, report, manifest, and ledger contracts
├── tests/                      # behavior, corruption, boundary, and CLI tests
├── tools/                      # repository and reference self-auditors
├── assets/                     # physical build evidence
└── docs/                       # architecture, operations, decisions, and threat model
```

## Quality gate

```bash
python -m pip install -e ".[dev]"
ruff check src tests tools
mypy
python -m compileall -q src tests tools
coverage run -m unittest discover -s tests -v
coverage report
soc-replay doctor
python tools/check_reference_reports.py
python tools/verify_repository.py
python -m pip wheel . --no-deps -w dist
```

The gate enforces strict typing, lint, compilation, at least 90% branch coverage, scenario verification, repeated deterministic bundle generation, ledger validity, schema presence, repository invariants, absence of live-I/O imports, and wheel construction.

## Documentation

Start with:

- [Documentation map](docs/README.md)
- [System architecture](docs/01-Architecture.md)
- [Replay engine](docs/11-Replay-Engine.md)
- [Implementation state](docs/14-Implementation-State.md)
- [Engineering review](docs/16-Engineering-Review.md)
- [Architecture decisions](docs/17-Architecture-Decisions.md)
- [Execution core](docs/22-Execution-Core.md)
- [Execution ledger](docs/23-Execution-Ledger.md)

The version-controlled `docs/` directory is canonical. Wiki copy under `docs/wiki/` is secondary and must not overrule implementation-state records or measured evidence.

## Scope and non-claims

SOC_Replay is a personally operated defensive research and demonstration environment. It does not generate traffic, deploy payloads, bypass controls, modify accounts, operate infrastructure, or execute response commands.

The execution ledger and bundle manifest provide tamper evidence relative to their hashes. They do **not** establish authorship, trusted time, or an external chain of custody.

## Current state

**Physical platform:** installed and documented  
**Execution engine:** compiled, indexed, expectation-verified, and packaged  
**Execution identity:** semantic plan fingerprint plus five-stage hash ledger  
**Experiment evidence:** four deterministic controls, including a zero-detection control  
**Adapter surface:** offline sanitized Suricata EVE normalization  
**Quality gate:** strict typing, lint, 90%+ branch coverage, self-audit, and wheel build  
**Live response:** deliberately outside the package
