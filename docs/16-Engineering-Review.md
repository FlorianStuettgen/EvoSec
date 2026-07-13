# 16 — Engineering Review

## Strengths

- The execution model is explicit, staged, and inspectable.
- Rules are compiled once into semantic execution plans.
- Candidate indexes improve cost without changing rule truth conditions.
- Every stage is represented in a deterministic hash chain.
- Positive, repeated-window, and negative controls verify both firing and non-firing behavior.
- Bundle verification checks artifacts, cross-document identity, plan fingerprint, ledger root, and bundle ID.
- Runtime remains dependency-free while development quality gates remain strict.
- The package has no live-I/O or command-execution authority.

## Deliberate trade-offs

### Small rule language

The operator set is intentionally constrained. Arbitrary expressions would increase flexibility but weaken inspectability and create an execution surface that is harder to secure and reason about.

### In-memory event index

The current index is optimized for bounded experiments and portfolio-scale replay. It is not a distributed stream processor. The `max_events` guard prevents accidental unbounded ingestion.

### Deterministic ledger without trusted attestation

The ledger proves internal consistency relative to its hashes. It does not prove who produced the bundle or when it was produced.

### Exact fixtures

Scenario expectations are exact. That is appropriate for regression controls but insufficient for production detection quality, noisy telemetry, or probabilistic analysis.

## Failure modes covered

- malformed or missing JSON;
- unknown contract fields;
- duplicate event IDs;
- invalid timestamps, IP addresses, ports, and nested paths;
- operator type mismatches;
- invalid aggregate configurations;
- repeated-window evidence reuse;
- expectation drift;
- partial report writes;
- artifact tampering;
- ledger-chain corruption;
- unknown adapters and unsupported vendor records;
- event-volume limit violations; and
- accidental live-I/O imports.

## Highest-value next proofs

1. Publish one complete measured physical-lab experiment with synchronized timestamps, source telemetry, analyst decision, containment validation, rollback, and recovery.
2. Add an optional signed envelope or external attestation path around the deterministic unsigned bundle.
3. Publish benchmark history across event count, group cardinality, rule count, and adapter throughput.
4. Add another offline vendor adapter with a conformance fixture.
5. Automate synchronization or retirement of the legacy GitHub Wiki.
