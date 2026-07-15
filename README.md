<div align="center">

# SOC_Replay

### Deterministic defensive telemetry replay with verifiable evidence bundles

[![CI](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml/badge.svg)](https://github.com/FlorianStuettgen/SOC_Replay/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11–3.13-3776AB?logo=python&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-zero%20dependencies-0f766e)
![Coverage](https://img.shields.io/badge/branch%20coverage-90%25%2B-16a34a)
![Boundary](https://img.shields.io/badge/response-simulation%20only-b45309)
![License](https://img.shields.io/badge/license-MIT-0f172a)

</div>

SOC_Replay compiles inspectable detection rules, evaluates stored synthetic or sanitized telemetry, verifies exact expected outcomes, and produces deterministic JSON/Markdown evidence bundles.

The repository also documents the segmented physical lab that provides the project context. The shipped Python package remains deliberately offline: it does not collect live telemetry, generate traffic, execute commands, or control infrastructure.

**Start here:** [See the reference evidence](reference/network-scan/report.md) · [Run the demo](#quickstart) · [Read the project guide](docs/00-Start-Here.md) · [Review implementation state](docs/14-Implementation-State.md) · [Read the security boundary](SECURITY.md)

![SOC_Replay execution core](docs/assets/execution-core.svg)

```text
Segmented physical lab
  └─ produces and contextualizes stored, sanitized telemetry
       └─ SOC_Replay evidence engine
            ├─ validates exact scenario contracts
            ├─ replays detections deterministically
            ├─ compares indexed and full-scan execution
            └─ publishes verifiable evidence bundles
```

The physical platform is the research context. The Python package is the offline evidence engine; it has no live collection or infrastructure-control authority.

## What is in this repository

| Surface | Purpose | State |
| --- | --- | --- |
| Replay engine | Deterministic load → compile → index → evaluate → verify pipeline | Implemented and tested |
| Scenario catalog | Exact positive, repeated-window, and zero-detection controls | Implemented and tested |
| Evidence bundles | JSON, Markdown, manifest, execution ledger, and integrity verification | Implemented and tested |
| Correctness proof | Indexed execution compared with a full-scan reference path | Implemented for maintained scenarios |
| Offline adapters | Stored and sanitized vendor telemetry normalization | Suricata EVE implemented |
| Physical lab documentation | Hardware, trust zones, monitoring, and recovery context | Installed/documented with explicit maturity labels |

## What it does not do

SOC_Replay does **not**:

- connect to sensors, firewalls, switches, hypervisors, identity providers, or endpoints;
- generate packets, payloads, exploits, or adversarial traffic;
- execute containment, account changes, or infrastructure commands;
- prove authorship, trusted time, external custody, or production telemetry origin; or
- claim that a deterministic scenario is a production detection-quality assessment.

All response objects are validation-locked to `simulated`.

## Quickstart

```bash
git clone https://github.com/FlorianStuettgen/SOC_Replay.git
cd SOC_Replay

python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e .

soc-replay doctor
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan --source scenarios/network-scan
python tools/verify_index_equivalence.py
```

Expected summary:

```text
doctor: PASS
replayed 7 events; detections=1
verification: PASS
bundle verification: PASS (... checks, 0 failed)
PASS network-scan: ...
```

The generated bundle is intentionally small and inspectable:

```text
build/network-scan/
├── report.json      # machine-readable evidence and per-rule traces
├── report.md        # analyst-readable evidence
└── manifest.json    # artifact hashes and execution identity
```

Use `soc-replay verify-bundle ... --verbose` for every check or `--json` for machine-readable verification output.

## See the evidence before reading the theory

A complete bundle for the maintained network-scan scenario is committed under [`reference/network-scan/`](reference/network-scan). Open the human-readable [`report.md`](reference/network-scan/report.md) first, then inspect the exact [`report.json`](reference/network-scan/report.json) and [`manifest.json`](reference/network-scan/manifest.json).

```bash
soc-replay verify-bundle reference/network-scan --source scenarios/network-scan
```

This reference bundle is checked in so a visitor can inspect a real result without installing anything. CI and the repository auditor require it to reproduce byte for byte from the maintained source scenario.

## Evidence guarantees

SOC_Replay separates different kinds of evidence instead of treating every hash as proof of everything.

| Mechanism | Establishes | Does not establish |
| --- | --- | --- |
| Exact scenario verification | Produced detections match declared counts, rules, severity, evidence events, groups, and simulated actions | Production usefulness or false-positive rate |
| Standalone bundle verification | Internal agreement among report, plan, traces, detections, actions, ledger, manifest, hashes, and byte counts | That the bundle came from a particular source directory |
| Source-bound reproduction | The supplied scenario regenerates all three bundle artifacts exactly under the installed engine | Authorship, trusted time, or independent custody |
| Differential index proof | Indexed execution matches the full-scan reference implementation for tested inputs | A formal proof over every possible input |
| Reproducible wheel check | Two clean source copies produce byte-identical wheels under the defined toolchain | Trustworthiness of the build host |

See [Evidence Bundles](docs/18-Evidence-Bundles.md), [Differential Correctness](docs/25-Differential-Correctness.md), and [Reproducible Builds](docs/27-Reproducible-Builds.md).

## Execution model

| Stage | Responsibility | Deterministic evidence |
| --- | --- | --- |
| Load | Validate and deeply freeze scenario and JSONL input | Input hashes and run ID |
| Compile | Bind accessors/operators and create candidate selectors | Rule and plan fingerprints |
| Index | Build immutable equality/tag indexes | Candidate strategy and index digest |
| Evaluate | Execute every rule, including zero-result rules | Ordered detections and rule traces |
| Verify | Compare output with exact declared contracts | Machine-readable PASS/FAIL checks |

Every stage appends a typed entry to a hash-linked execution ledger. Candidate selection can change cost but must not change detection semantics.

## Maintained scenarios

| Scenario | Purpose | Exact result |
| --- | --- | --- |
| [Network scan](scenarios/network-scan) | Positive correlation control | One high-severity detection backed by `net-001` through `net-005` |
| [Privileged group change](scenarios/privileged-group-change) | Nested-field control | One critical detection backed by `iam-002` |
| [Failed authentication burst](scenarios/failed-authentication-burst) | Repeated non-overlapping windows | Two medium-severity detections |
| [Approved privileged maintenance](scenarios/benign-privileged-change) | Negative control | Zero detections and a preserved zero-result trace |

## Repository map

```text
SOC_Replay/
├── src/soc_replay/
│   ├── compiler.py                 # executable plans and semantic fingerprints
│   ├── indexing.py                 # immutable candidate routing
│   ├── correlation.py              # detections and per-rule traces
│   ├── pipeline.py                 # five-stage orchestration
│   ├── ledger.py                   # strict hash-linked stage ledger
│   ├── bundle.py                   # deterministic bundle construction
│   ├── bundle_verify*.py           # standalone and source-bound verification
│   ├── proofs.py                   # indexed/full-scan equivalence evidence
│   └── adapters/                   # frozen offline normalization registry
├── scenarios/                      # maintained exact controls
├── schemas/                        # public Draft 2020-12 contracts
├── tests/                          # behavior, corruption, proof, and CLI tests
├── tools/                          # repository, schema, proof, build, and benchmark audits
├── docs/                           # canonical architecture and governance record
└── assets/                         # physical-lab evidence
```

## Physical lab context

The documented platform includes Qubes OS and Proxmox compute, enterprise switching and firewall appliances, SELKS/Suricata monitoring, storage, and independent console recovery. That platform is the research context for SOC_Replay, not an authority granted to the Python package.

Start with [Architecture](docs/01-Architecture.md), [Hardware](docs/02-Hardware.md), [Network Topology](docs/04-Network-Topology.md), and [Monitoring and Telemetry](docs/06-Monitoring-Telemetry.md). Capability maturity is controlled by [Implementation State](docs/14-Implementation-State.md).

## Quality gate

```bash
python -m pip install -e ".[dev]"
ruff check src tests tools
mypy
python -m compileall -q src tests tools
coverage run -m unittest discover -s tests -v
coverage report
python tools/validate_contracts.py
python tools/verify_index_equivalence.py
python tools/verify_deterministic_bundles.py
python tools/verify_repository.py
python tools/verify_reproducible_wheel.py
```

CI runs the gate on Python 3.11, 3.12, and 3.13 and preserves diagnostics and generated evidence as workflow artifacts.

## Documentation paths

| Goal | Start with |
| --- | --- |
| Evaluate the project quickly | [Start Here](docs/00-Start-Here.md), [Reference Report](reference/network-scan/report.md), and [Implementation State](docs/14-Implementation-State.md) |
| Run a demonstration | [Demo Playbook](docs/15-Demo-Playbook.md) |
| Understand the engine | [Execution Core](docs/22-Execution-Core.md) and [Execution Ledger](docs/23-Execution-Ledger.md) |
| Review evidence integrity | [Evidence Bundles](docs/18-Evidence-Bundles.md) and [Threat Model](docs/21-Threat-Model.md) |
| Extend scenarios or adapters | [Scenario Format](docs/12-Scenario-Format.md), [Suricata Adapter](docs/19-Suricata-Adapter.md), and [Contributing](CONTRIBUTING.md) |
| Understand the physical platform | [Architecture](docs/01-Architecture.md) and [Network Topology](docs/04-Network-Topology.md) |

The version-controlled `docs/` directory is canonical. Wiki material is secondary and must not overrule implementation state or measured evidence.

## Current state

- **Version:** 3.3.0
- **Runtime:** standard-library only
- **Supported Python:** 3.11–3.13
- **Maintained scenarios:** four exact controls
- **Evidence assurance:** standalone semantic consistency plus optional source-bound byte reproduction
- **Correctness assurance:** indexed/full-scan differential comparison
- **Response authority:** simulation only

## License

[MIT](LICENSE)
