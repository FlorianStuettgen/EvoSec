# 21 — Threat Model

## Protected properties

SOC_Replay is designed to protect:

- deterministic replay behavior;
- integrity and traceability of generated evidence;
- the simulation-only response boundary;
- separation between stored telemetry and live infrastructure authority; and
- confidentiality of real lab credentials, management addresses, and incident data.

## Trust boundaries

| Boundary | Untrusted input | Primary controls |
| --- | --- | --- |
| Scenario loader | JSON and JSONL files | Strict model validation, duplicate checks, timezone and IP validation |
| Vendor adapter | Sanitized EVE records | Supported-type allowlist, shared event validation, atomic output |
| Rule engine | Scenario conditions and aggregation | Small declarative language, no expression evaluation, deterministic ordering |
| Report bundle | Local output directory | Atomic writes, manifest-last completion, hash and size verification |
| CI | Repository changes and dependencies | Read-only token, lint, strict typing, tests, verification, packaging |
| Physical lab | Network and device state | Human governance, segmentation, OOB recovery, no control connector in package |

## Considered threats

### Malformed or adversarial input

The loader rejects malformed JSON, unknown fields in machine schemas, duplicate event IDs, invalid timestamps, invalid IPs, unsafe response modes, unsupported operators, and inconsistent expectations.

### Path or command execution

Rules are data, not code. The engine performs no shell execution, dynamic imports, template evaluation, or device calls. Bundle verification reads only the three fixed artifact names from the requested directory.

### Evidence tampering

Artifact hashes and byte counts detect changes to `report.json` or `report.md` relative to `manifest.json`. This does not defend against an attacker replacing all three files.

### Sensitive-data disclosure

Public fixtures must be synthetic or sanitized. Credentials, keys, serial numbers, real personal data, sensitive management addresses, and production incident records are prohibited by the contribution and security policies.

### Capability inflation

The implementation-state register distinguishes installed, documented, partially evidenced, prototype, and roadmap capabilities. Replay evidence is not presented as proof of live containment or complete sensor coverage.

## Residual risks

- The bundle manifest is unsigned.
- JSON Schemas are published contracts but runtime validation is implemented in Python rather than delegated to a schema library.
- The adapter supports only a documented subset of Suricata EVE.
- Runtime performance depends on event volume, grouping cardinality, and rule count.
- A local operator can modify code and regenerate internally consistent artifacts.
