# 21 — Threat Model

## Protected properties

SOC_Replay is designed to protect:

- deterministic replay behavior;
- integrity and traceability of generated evidence;
- controlled rejection of malformed evidence;
- the simulation-only response boundary;
- separation between stored telemetry and live infrastructure authority; and
- confidentiality of real lab credentials, management addresses, and incident data.

## Trust boundaries

| Boundary | Untrusted input | Primary controls |
| --- | --- | --- |
| Scenario loader | JSON and JSONL files | Strict model validation, duplicate checks, timezone and IP validation, event-volume guard |
| Vendor adapter | Stored sanitized vendor records | Supported-type allowlist, shared event validation, atomic output |
| Rule engine | Scenario conditions and aggregation | Small declarative language, no expression evaluation, deterministic ordering |
| Report bundle | Local output directory | Fixed artifact names, strict structure, standalone consistency checks, source-bound reproduction |
| Execution ledger | Report-supplied ledger JSON | Exact stages, typed scalar fields, digest validation, hash-chain and count verification |
| CI | Repository changes and dependencies | Read-only token, pinned actions, lint, strict typing, tests, contract verification, packaging |
| Physical lab | Network and device state | Human governance, segmentation, OOB recovery, no control connector in package |

## Considered threats

### Malformed or adversarial input

The loader rejects malformed JSON, unknown fields in machine contracts, duplicate event IDs, invalid timestamps, invalid IPs, unsafe response modes, unsupported operators, and inconsistent expectations.

Bundle verification treats JSON-valid structures as untrusted. Non-scalar ledger stages or statuses, invalid object/array boundaries, unknown verification checks, and inconsistent report relationships must fail in a controlled manner rather than escaping as raw runtime exceptions.

### Path or command execution

Rules are data, not code. The engine performs no shell execution, dynamic imports, template evaluation, device calls, or credential access. Bundle verification reads only the fixed artifact names in the requested directory. Source-bound verification invokes the same local replay pipeline against an explicitly supplied scenario directory.

### Evidence tampering

Standalone verification detects ordinary file changes and rehashed internal contradictions by recomputing run and plan identities, verification results, detection/trace relationships, ledger stage digests, artifact hashes, byte counts, and bundle identity.

A coherently rewritten bundle can still be internally consistent. Source-bound verification addresses that narrower gap by regenerating `report.json`, `report.md`, and `manifest.json` from the supplied scenario and comparing their bytes. It does not prove that the supplied source itself is authoritative.

### Sensitive-data disclosure

Public fixtures must be synthetic or sanitized. Credentials, keys, serial numbers, real personal data, sensitive management addresses, and production incident records are prohibited by the contribution and security policies.

### Capability inflation

The implementation-state register distinguishes installed, documented, partially evidenced, prototype, and roadmap capabilities. Replay evidence is not presented as proof of live containment, complete sensor coverage, or production detection quality.

## Residual risks

- Bundles are unsigned and have no trusted timestamp.
- A local operator can modify code, source scenarios, and artifacts together.
- Source-bound verification is tied to the installed engine and deterministic rendering behavior.
- JSON Schemas are published contracts, while runtime validation is implemented in Python.
- The adapter supports only a documented subset of Suricata EVE.
- Runtime performance depends on event volume, grouping cardinality, and rule count.
- The physical platform is documented separately and is not controlled by the package.
