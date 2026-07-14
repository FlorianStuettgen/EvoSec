<div align="center">

# SOC_Replay

### A contract-complete defensive telemetry engine with compiled rules, exact scenario assertions, deterministic execution traces, and verifiable evidence bundles

[![CI](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml/badge.svg)](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11–3.13-3776AB?logo=python&logoColor=white)
![Coverage](https://img.shields.io/badge/branch%20coverage-90%25%2B-16a34a)
![Runtime](https://img.shields.io/badge/runtime-zero%20dependencies-0f766e)
![Contracts](https://img.shields.io/badge/contracts-schema%20validated-7c3aed)
![Boundary](https://img.shields.io/badge/response-simulation%20only-b45309)
![License](https://img.shields.io/badge/license-MIT-0f172a)

</div>

![SOC_Replay platform overview](docs/assets/soc-replay-hero.svg)

SOC_Replay joins two systems that security portfolios usually present separately:

1. a **real segmented cyber range** with enterprise compute, storage, network enforcement, telemetry, and out-of-band recovery; and
2. a **deterministic evidence engine** that compiles inspectable detection rules, evaluates synthetic or sanitized telemetry, verifies exact declared outcomes, and publishes integrity-checkable report bundles.

The project is built around one principle:

> **A diagram proves architecture. A screenshot proves visibility. A reproducible, contract-validated experiment proves behavior.**

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
├── report.json      # machine-readable evidence and per-rule traces
├── report.md        # analyst-readable evidence
└── manifest.json    # artifact hashes, execution identity, and bundle ID
```

## The execution fabric

![SOC_Replay execution core](docs/assets/execution-core.svg)

The engine is an explicit five-stage pipeline:

| Stage | Responsibility | Deterministic output |
| --- | --- | --- |
| **Load** | Validate and deeply freeze scenario and JSONL event inputs | Provenance hashes and run ID |
| **Compile** | Bind accessors/operators and compile candidate selectors | Plan and per-rule fingerprints |
| **Index** | Build immutable indexes and intersect safe selectors | Stable candidate sets and index digest |
| **Evaluate** | Execute every rule and preserve positive or zero-detection traces | Ordered detections and rule executions |
| **Verify** | Compare results with exact declared detection contracts | Machine-readable PASS/FAIL |

Every stage appends an entry to a strictly typed, cryptographically linked execution ledger. The verifier enforces the exact stage order, digest formats, count types, metadata shape, hash continuity, completion state, and root identity.

See [Execution Core](docs/22-Execution-Core.md), [Execution Ledger](docs/23-Execution-Ledger.md), and [Contract Validation](docs/24-Contract-Validation.md).

## What “contract-complete” means

### Deeply immutable runtime state

Frozen dataclasses alone do not make nested mappings and lists immutable. SOC_Replay recursively freezes event details, condition values, expectation maps, detection groups, correlation metadata, verification values, and ledger metadata. Serialized output remains conventional JSON.

### Complete semantic fingerprints

A rule fingerprint commits to every output-affecting field:

- identity, display name, severity, and description;
- all match conditions and values;
- aggregate grouping, threshold, duration, distinct-value, and window policy;
- simulated response action, description, and mode.

Changing behavior or report-visible meaning changes the fingerprint.

### Composite candidate plans

The compiler extracts every safe indexed selector, not merely the first one. The index intersects equality and tag pools deterministically, then applies the complete compiled predicate set. Candidate selection changes cost, never truth conditions.

### Every rule leaves a trace

Each rule execution records:

- candidate strategy and candidate count;
- matched-event count;
- group count;
- windows considered; and
- detection count.

A zero-detection rule is therefore visible evidence, not an absence of evidence.

### Exact scenario assertions

Maintained scenario schema `1.1` declares the exact expected detections: rule, severity, evidence-event IDs, group values, and simulated action. Schema `1.0` remains readable for compatibility, but `doctor` rejects legacy scenarios from the maintained catalog.

### Runtime and schemas agree

CI validates actual scenario, event, report, manifest, and ledger instances against Draft 2020-12 JSON Schemas. Runtime validation, schema validation, bundle verification, and repository auditing use the same contract vocabulary.

## Evidence identity hierarchy

```text
input bytes
  └── run ID
       └── semantic execution plan
            └── per-rule execution traces
                 └── ordered detections
                      └── expectation verdict
                           └── stage ledger root
                                └── artifact hashes
                                     └── bundle ID
```

A bundle can be internally consistent only when these identities agree. The verifier rejects ordinary file tampering and rehashed bundles whose report, traces, ledger, summary, actions, or manifest contradict one another.

## Included experiments

| Scenario | Role | Exact expected result |
| --- | --- | --- |
| [Network scan](scenarios/network-scan) | Positive correlation control | One high detection backed by `net-001` through `net-005` |
| [Privileged group change](scenarios/privileged-group-change) | Positive nested-field control | One critical detection backed by `iam-002` |
| [Failed authentication burst](scenarios/failed-authentication-burst) | Repeated-window control | Two medium detections with non-overlapping evidence windows |
| [Approved privileged maintenance](scenarios/benign-privileged-change) | Negative control | Zero detections and a preserved zero-result rule trace |

Every maintained scenario contains synthetic telemetry, a precise authorization boundary, inspectable rules, exact detection contracts, and repeatably verified bundle generation.

## Offline telemetry adapters

```bash
soc-replay adapters
soc-replay normalize \
  --adapter suricata-eve \
  examples/adapters/suricata-eve.jsonl \
  build/suricata-normalized.jsonl
```

The global adapter registry is frozen after startup. The Suricata adapter consumes stored `alert` and `flow` records, validates every emitted event through the public model, reports skipped records, writes atomically, and emits a deterministic output hash. It contains no sensor connection or credentials.

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

`doctor` audits the pipeline, contract versions, registries, and maintained scenario maturity. `explain` exposes the compiled selector plan and observed execution counts. `graph` exposes the stage wiring rather than leaving architecture implicit.

## Repository architecture

```text
SOC_Replay/
├── src/soc_replay/
│   ├── contracts.py            # shared schema and pipeline vocabulary
│   ├── immutability.py         # recursive freeze boundary
│   ├── model_common.py         # shared validation vocabulary
│   ├── event_models.py         # events, conditions, aggregates, rules
│   ├── scenario_models.py      # exact expectations and scenarios
│   ├── result_models.py        # detections and verification records
│   ├── compiler.py             # executable plans and semantic fingerprints
│   ├── indexing.py             # immutable composite candidate routing
│   ├── correlation.py          # detections and per-rule execution traces
│   ├── pipeline.py             # five-stage orchestration
│   ├── ledger.py               # strict deterministic hash chain
│   ├── report_render.py        # JSON and analyst-readable rendering
│   ├── bundle.py               # manifests and internal-consistency verification
│   ├── report.py               # stable reporting façade
│   ├── adapters/               # frozen offline normalization registry
│   └── cli.py                  # operational command surface
├── scenarios/                  # exact positive, repeated-window, and negative controls
├── schemas/                    # event, scenario, report, manifest, and ledger contracts
├── tests/                      # behavior, corruption, immutability, schema, and CLI tests
├── tools/                      # contract, determinism, and repository auditors
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
python tools/validate_contracts.py
python tools/verify_deterministic_bundles.py
python tools/verify_repository.py
python -m pip wheel . --no-deps -w dist
```

The gate enforces strict typing, lint, compilation, at least 90% branch coverage, exact scenario verification, real schema-instance validation, repeated deterministic bundle generation, strict ledger validity, deep immutability tests, repository invariants, absence of live-I/O imports, and wheel construction.

## Documentation

Start with:

- [Documentation map](docs/README.md)
- [System architecture](docs/01-Architecture.md)
- [Replay engine](docs/11-Replay-Engine.md)
- [Implementation state](docs/14-Implementation-State.md)
- [Engineering review](docs/16-Engineering-Review.md)
- [Architecture decisions](docs/17-Architecture-Decisions.md)
- [Evidence bundles](docs/18-Evidence-Bundles.md)
- [Execution core](docs/22-Execution-Core.md)
- [Execution ledger](docs/23-Execution-Ledger.md)
- [Contract validation](docs/24-Contract-Validation.md)

The version-controlled `docs/` directory is canonical. Wiki copy under `docs/wiki/` is secondary and must not overrule implementation-state records or measured evidence.

## Scope and non-claims

SOC_Replay is a personally operated defensive research and demonstration environment. It does not generate traffic, deploy payloads, bypass controls, modify accounts, operate infrastructure, or execute response commands.

The execution ledger and bundle manifest provide tamper evidence relative to their hashes. They do **not** establish authorship, trusted time, external custody, or that telemetry originated from a live production system.

## Current state

**Version:** 3.1.0  
**Physical platform:** installed and documented  
**Execution engine:** deeply immutable, compiled, composite-indexed, traced, and packaged  
**Execution identity:** complete semantic plan fingerprint plus strict five-stage hash ledger  
**Experiment evidence:** four exact deterministic contracts, including a zero-detection control  
**Schema assurance:** maintained inputs and generated outputs validated as real Draft 2020-12 instances  
**Adapter surface:** frozen, offline, sanitized Suricata EVE normalization  
**Quality gate:** 42 tests, 93% branch coverage, strict typing, contract audit, determinism audit, and wheel build  
**Live response:** deliberately outside the package
