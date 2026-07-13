# 16 — Engineering Review

## Strengths

- Clear separation between physical infrastructure and evidence evaluation.
- Deterministic behavior suitable for regression testing and review.
- Strict simulation-only boundary enforced in the data model.
- Machine-verifiable expected outcomes rather than narrative-only demos.
- No runtime dependency chain.
- Atomic reports with input provenance, manifest-backed integrity checks, and reference-output comparison.
- Sanitized Suricata normalization kept outside the deterministic core.
- Positive and negative controls that test both detection and expected non-detection.

## Deliberate tradeoffs

### Small rule language

The engine supports common field comparisons and time-window aggregation, not arbitrary expressions. This limits flexibility but keeps rules inspectable and reduces hidden execution risk.

### Exact expectations

Scenario expectations are exact rather than probabilistic. This is appropriate for deterministic fixtures but not sufficient for noisy production telemetry.

### Input hashes without signatures

SHA-256 identifies exact input bytes but does not establish who created them. Signed envelopes and external custody controls are possible future work.

### Offline normalized events

The core does not ingest live vendor formats. Adapter code should remain separate so normalization, permissions, and failure behavior can be reviewed independently.

## Failure modes considered

- malformed JSON and missing files;
- duplicate event IDs;
- naive timestamps and invalid IP addresses;
- mistyped nested paths;
- unsafe containment checks on non-iterable values;
- inconsistent distinct aggregation fields;
- repeated-window evidence reuse;
- expectation drift;
- partial report writes; and
- silent invalid scenarios in the catalog.

## What would make the project stronger next

1. A sanitized adapter for one real telemetry format with fixture-based contract tests.
2. A complete physical-lab experiment record tied to source telemetry and measured timestamps.
3. Signed report envelopes and external attestation.
4. Benchmark history across scenario size, group cardinality, and rule count.
5. Mutation or property-based testing for correlation edge cases.
6. Additional vendor adapters with conformance fixtures and explicit support matrices.
