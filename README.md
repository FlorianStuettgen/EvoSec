<div align="center">

# SOC_Replay

### A proof-oriented defensive telemetry engine with compiled rules, exact scenario contracts, differential correctness checks, deterministic execution traces, and verifiable evidence bundles

[![CI](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml/badge.svg)](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11–3.13-3776AB?logo=python&logoColor=white)
![Coverage](https://img.shields.io/badge/branch%20coverage-90%25%2B-16a34a)
![Runtime](https://img.shields.io/badge/runtime-zero%20dependencies-0f766e)
![Contracts](https://img.shields.io/badge/contracts-schema%20validated-7c3aed)
![Correctness](https://img.shields.io/badge/indexing-differentially%20proved-2563eb)
![Boundary](https://img.shields.io/badge/response-simulation%20only-b45309)
![License](https://img.shields.io/badge/license-MIT-0f172a)

</div>

![SOC_Replay platform overview](docs/assets/soc-replay-hero.svg)

SOC_Replay joins two systems that security portfolios usually present separately:

1. a **real segmented cyber range** with enterprise compute, storage, network enforcement, telemetry, and out-of-band recovery; and
2. a **deterministic evidence engine** that compiles inspectable detection rules, evaluates synthetic or sanitized telemetry, verifies exact declared outcomes, and publishes integrity-checkable report bundles.

The project is built around one principle:

> **A diagram proves architecture. A screenshot proves visibility. A reproducible experiment proves behavior. A differential proof shows that an optimization did not change meaning.**

## The 90-second proof

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e .

soc-replay doctor
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan
python tools/verify_index_equivalence.py
```

Expected result:

```text
replayed 7 events; detections=1
verification: PASS
plan: <64-character semantic fingerprint>
ledger: <64-character execution root>
bundle: <64-character bundle identity>
bundle verification: PASS
PASS network-scan: ... proof=<64-character proof identity>
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

| Stage | Responsibility | Deterministic output |
| --- | --- | --- |
| **Load** | Validate and deeply freeze scenario and JSONL event inputs | Provenance hashes and run ID |
| **Compile** | Bind accessors/operators and compile candidate selectors | Plan and per-rule fingerprints |
| **Index** | Build immutable indexes and intersect safe selectors | Stable candidate sets and index digest |
| **Evaluate** | Execute every rule and preserve positive or zero-detection traces | Ordered detections and rule executions |
| **Verify** | Compare results with exact declared detection contracts | Machine-readable PASS/FAIL |

Every stage appends an entry to a strictly typed, cryptographically linked execution ledger. The verifier enforces exact stage order, digest formats, count types, metadata shape, hash continuity, completion state, and root identity.

## The proof layer

Candidate indexes are useful only if they preserve rule semantics. SOC_Replay therefore treats the unoptimized full-scan path as a reference implementation and compares it with indexed execution for every maintained scenario.

For each rule, the proof records:

- indexed and full-scan candidate counts;
- indexed strategy;
- matched, grouped, window, and detection counts;
- normalized semantic detection output;
- a semantic digest; and
- a pass/fail verdict with explicit failure reasons.

Optimization-only fields such as candidate strategy and candidate count are excluded from the semantic comparison. Detection identity, severity, evidence events, grouping, response, correlation thresholds, and timestamps remain part of the comparison.

```bash
python tools/verify_index_equivalence.py
python tools/verify_index_equivalence.py --json > build/index-equivalence.json
```

This is a differential correctness proof relative to the full-scan implementation. It is not a mathematical proof of the detection rules themselves and does not establish the origin of telemetry.

## Performance evidence without performance theatre

Benchmark inputs are deterministic; elapsed time is not. SOC_Replay keeps benchmark measurements outside the replay ledger and evidence bundle so environment noise cannot contaminate deterministic identities.

```bash
python tools/benchmark_scenarios.py \
  --copies 100 \
  --iterations 15 \
  --warmups 3 \
  --output build/benchmarks
```

Each benchmark artifact records:

- source and expanded event counts;
- deterministic workload ID;
- plan and rule fingerprints;
- environment metadata;
- index-build, indexed-evaluation, and full-scan timing summaries;
- candidate-reduction ratios;
- measured median speedup; and
- an embedded semantic-equivalence proof.

The benchmark schema validates structure, not speed. CI deliberately avoids brittle latency thresholds on shared runners.

## Reproducible package construction

The project verifies that two independent clean source copies produce byte-identical wheels when supplied the same build backend, wheel builder, fixed build epoch, and hash seed:

```bash
python tools/verify_reproducible_wheel.py
```

The verifier preserves build-frontend logs and entry-level ZIP diagnostics on failure, and CI uploads those diagnostics even when the build check fails. This establishes reproducibility under the tested toolchain and environment; it does not replace artifact signing, trusted timestamps, or independent provenance attestation.

## Contract-complete internals

### Deeply immutable runtime state

Nested event details, condition values, expectations, detection groups, correlation metadata, verification values, and ledger metadata are recursively frozen. Serialized output remains ordinary JSON.

### Complete semantic fingerprints

A rule fingerprint commits to identity, display text, severity, conditions, aggregate behavior, and the simulated response contract. Changing behavior or report-visible meaning changes the fingerprint.

### Composite candidate plans

The compiler extracts every safe indexed selector. The index intersects equality and tag pools deterministically, then applies the complete compiled predicate set. Candidate selection changes cost, never truth conditions.

### Every rule leaves a trace

A zero-detection rule records the same candidate, match, group, window, and detection accounting as a firing rule. Zero detections are therefore visible evidence rather than an unexplained absence.

### Exact scenario assertions

Maintained scenario schema `1.1` declares exact expected detections: rule, severity, evidence-event IDs, group values, and simulated action. Schema `1.0` remains readable only for compatibility.

### Runtime and schemas agree

CI validates real scenario, event, report, manifest, ledger, proof, benchmark, and normalized-adapter instances against Draft 2020-12 JSON Schemas.

## Evidence identity hierarchy

```text
input bytes
  └── run ID
       └── semantic execution plan
            ├── indexed/full-scan equivalence proof
            └── per-rule execution traces
                 └── ordered detections
                      └── expectation verdict
                           └── stage ledger root
                                └── artifact hashes
                                     └── bundle ID
```

A bundle is accepted only when these identities agree. The verifier rejects ordinary file tampering and rehashed bundles whose report, traces, ledger, summary, actions, or manifest contradict one another.

## Included experiments

| Scenario | Role | Exact expected result |
| --- | --- | --- |
| [Network scan](scenarios/network-scan) | Positive correlation control | One high detection backed by `net-001` through `net-005` |
| [Privileged group change](scenarios/privileged-group-change) | Positive nested-field control | One critical detection backed by `iam-002` |
| [Failed authentication burst](scenarios/failed-authentication-burst) | Repeated-window control | Two medium detections with non-overlapping evidence windows |
| [Approved privileged maintenance](scenarios/benign-privileged-change) | Negative control | Zero detections and a preserved zero-result rule trace |

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

## Repository architecture

```text
SOC_Replay/
├── src/soc_replay/
│   ├── contracts.py            # shared schema and pipeline vocabulary
│   ├── immutability.py         # recursive freeze boundary
│   ├── event_models.py         # events, conditions, aggregates, rules
│   ├── scenario_models.py      # exact expectations and scenarios
│   ├── compiler.py             # executable plans and semantic fingerprints
│   ├── indexing.py             # immutable composite candidate routing
│   ├── correlation.py          # detections and per-rule execution traces
│   ├── proofs.py               # indexed/full-scan differential correctness
│   ├── pipeline.py             # five-stage orchestration
│   ├── ledger.py               # strict deterministic hash chain
│   ├── bundle.py               # manifests and consistency verification
│   └── adapters/               # frozen offline normalization registry
├── scenarios/                  # exact positive, repeated-window, and negative controls
├── schemas/                    # runtime, evidence, proof, and benchmark contracts
├── tests/                      # behavior, corruption, immutability, proof, and CLI tests
├── tools/                      # contract, proof, benchmark, build, and repository auditors
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
python tools/verify_index_equivalence.py
python tools/verify_deterministic_bundles.py
python tools/verify_repository.py
python tools/verify_reproducible_wheel.py
python tools/benchmark_scenarios.py --copies 4 --iterations 2 --warmups 1
```

The gate verifies code quality, exact scenario behavior, schema-instance validity, differential index correctness, deterministic bundle bytes, strict ledger consistency, repository invariants, reproducible package bytes, and a schema-valid benchmark smoke run. CI preserves diagnostics and benchmark artifacts even when an earlier quality gate fails.

## Documentation

Start with:

- [Documentation map](docs/README.md)
- [System architecture](docs/01-Architecture.md)
- [Replay engine](docs/11-Replay-Engine.md)
- [Engineering review](docs/16-Engineering-Review.md)
- [Execution core](docs/22-Execution-Core.md)
- [Execution ledger](docs/23-Execution-Ledger.md)
- [Contract validation](docs/24-Contract-Validation.md)
- [Differential correctness](docs/25-Differential-Correctness.md)
- [Performance methodology](docs/26-Performance-Methodology.md)
- [Reproducible builds](docs/27-Reproducible-Builds.md)

The version-controlled `docs/` directory is canonical. Wiki copy is secondary and must not overrule implementation-state records or measured evidence.

## Scope and non-claims

SOC_Replay is a personally operated defensive research and demonstration environment. It does not generate traffic, deploy payloads, bypass controls, modify accounts, operate infrastructure, or execute response commands.

The execution ledger and bundle manifest provide tamper evidence relative to their hashes. Differential proofs establish equivalence to the full-scan reference implementation for tested inputs. Benchmarks describe measured execution in a recorded environment. None of these establishes authorship, trusted time, external custody, or production telemetry origin.

## Current state

**Version:** 3.2.1  
**Execution engine:** deeply immutable, compiled, composite-indexed, traced, and packaged  
**Correctness assurance:** indexed execution differentially checked against full scan  
**Experiment evidence:** four exact deterministic contracts, including a zero-detection control  
**Schema assurance:** inputs, outputs, proofs, and benchmark artifacts validated as real Draft 2020-12 instances  
**Build assurance:** deterministic bundle generation plus two-clean-source wheel reproducibility verification  
**Adapter surface:** frozen, offline, sanitized Suricata EVE normalization  
**Live response:** deliberately outside the package
