# 25 — Differential Correctness

## Purpose

SOC_Replay uses candidate indexes to reduce the number of events passed into rule evaluation. An optimization is acceptable only when it preserves the semantic output of the unoptimized full-scan path.

## Reference and optimized paths

For every compiled rule, the proof runner executes two paths over the same immutable event tuple:

1. **Indexed path** — candidate pools are selected and intersected by the event index.
2. **Reference path** — every event is supplied to the same compiled predicate and correlation engine.

Both paths use the same compiled rule object, field accessors, operator functions, grouping logic, window policy, and detection construction.

## Semantic comparison

The comparison includes:

- matched-event count;
- group count;
- windows considered;
- detection count;
- detection ID, rule, severity, timestamps, event IDs, group values, response, and correlation semantics.

The comparison excludes only optimization metadata:

- candidate strategy; and
- candidate-event count.

Those fields must differ when indexing is effective and are recorded separately.

## Proof identity

Each rule proof receives a semantic digest. The scenario proof commits to:

- engine name and version;
- scenario and run identity;
- execution-plan fingerprint;
- event count;
- ordered rule proofs;
- candidate accounting; and
- final verdict.

Equivalent inputs and engine version produce the same proof identity.

## Failure interpretation

A failed proof means indexed and full-scan execution disagreed for the tested input. The indexed result must not be trusted until the selector, index, predicate, or correlation defect is resolved.

## Limits

The proof establishes equivalence between two implementations for the supplied scenarios and expanded benchmark workloads. It does not prove that the detection rule is operationally useful, that the source telemetry is authentic, or that every possible event value has been explored.
