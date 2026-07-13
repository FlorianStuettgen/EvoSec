# 16 — Engineering Review

## Strengths

- Clear separation between physical infrastructure and evidence evaluation.
- Deterministic behavior suitable for regression testing and technical review.
- Strict simulation-only boundary enforced in the data model.
- Machine-verifiable expected outcomes rather than narrative-only demos.
- No runtime dependency chain.
- Atomic reports with input provenance, manifest-backed integrity checks, and byte-for-byte reference comparison.
- Sanitized Suricata normalization kept outside the deterministic core.
- Positive, repeated-window, and negative controls that test both detection and expected non-detection.
- Strict typing, linting, branch coverage, multi-version CI, repository-coherence checks, and wheel construction.

## Deliberate tradeoffs

### Small rule language

The engine supports common field comparisons and time-window aggregation, not arbitrary expressions. This limits flexibility but keeps rules inspectable and reduces hidden execution risk.

### Exact expectations

Scenario expectations are exact rather than probabilistic. This is appropriate for deterministic fixtures but not sufficient for noisy production telemetry or detection-quality measurement at scale.

### Input hashes without signatures

SHA-256 identifies exact input and artifact bytes but does not establish who created them. Signed envelopes, trusted timestamps, and external custody controls remain separate future work.

### Offline adapters

Adapters consume stored sanitized telemetry rather than live sensors. This keeps credentials, collection permissions, network availability, and vendor-specific failure behavior outside the deterministic replay boundary.

### Standard-library runtime

The zero-dependency core improves portability and inspectability. The tradeoff is that runtime validation intentionally mirrors the published JSON Schemas instead of depending on a schema-validation library.

## Failure modes considered

- malformed JSON and missing files;
- duplicate event IDs;
- naive timestamps and invalid IP addresses;
- mistyped nested paths;
- unsafe containment checks on non-iterable values;
- inconsistent distinct aggregation fields;
- repeated-window evidence reuse;
- expectation drift;
- partial report writes;
- post-generation artifact modification;
- unsupported vendor-record types; and
- silent invalid scenarios in the catalog.

## Highest-value next proofs

1. Publish one complete measured physical-lab experiment tied to source telemetry, synchronized timestamps, containment validation, rollback, and the experiment-record template.
2. Add signed report envelopes or an external attestation path while retaining deterministic unsigned bundles.
3. Build benchmark history across event volume, group cardinality, rule count, and adapter throughput without turning machine-specific results into universal claims.
4. Add property-based or mutation testing for correlation boundaries, expectation mismatches, and adapter normalization.
5. Add another vendor adapter with a conformance fixture and explicit support matrix.
6. Automate synchronization or retirement of the legacy GitHub Wiki so historical prose cannot contradict the versioned documentation.
