# 16 — Engineering Review

## Strengths

- Runtime objects are deeply immutable, not merely frozen at the dataclass shell.
- Rule fingerprints cover every behavior- and report-affecting field.
- Candidate selectors are composed and intersected without changing rule semantics.
- Indexed execution is differentially compared with a full-scan reference path for every maintained scenario.
- Every rule produces a deterministic execution trace, including zero-result rules.
- Maintained scenarios assert exact evidence windows, grouping values, severity, and response action.
- The execution ledger enforces stage order, types, digest shape, counts, chain continuity, and completion.
- Bundle verification recomputes internal identities and relationships; optional source-bound verification reproduces all three artifacts from the supplied scenario.
- JSON Schemas are validated and then used against real repository and generated instances.
- Benchmark workloads are deterministic while environment-dependent timing remains outside replay evidence identities.
- Wheel construction is checked for byte reproducibility under fixed build inputs.
- Runtime dependencies remain zero.
- The package has no live-I/O, credential, command-execution, or infrastructure-control authority.

## Deliberate trade-offs

### Small rule language

The eight operators are intentionally constrained. Arbitrary executable expressions would increase flexibility at the cost of inspectability, deterministic serialization, and security.

### In-memory index

The index is appropriate for bounded experiments and portfolio-scale replay. It is not a distributed stream processor. `max_events` remains the explicit volume guard.

### Differential rather than formal proof

The index-equivalence layer compares two implementations on maintained scenarios and deterministic expanded workloads. It does not exhaust the entire input domain or prove that a rule is operationally useful.

### Environment-bound benchmarks

Timing results depend on interpreter, host, load, and toolchain. CI uses the benchmark as a schema-valid smoke test and does not impose shared-runner latency thresholds.

### Exact deterministic scenarios

Exact assertions are powerful regression contracts but are not a substitute for production false-positive analysis, noisy-data evaluation, or probabilistic quality measurement.

### Internal and source-bound integrity without external attestation

Standalone verification makes internal contradiction and post-generation alteration observable. Source-bound verification additionally proves that the supplied scenario reproduces the complete bundle under the installed engine. A party able to replace both source and artifacts can still create a new consistent evidence set. External authorship and trusted time require signatures or an attestation service.

## Failure modes covered

- missing, malformed, or unknown input fields;
- invalid timestamps, IPs, ports, nested paths, operators, and aggregate contracts;
- duplicate event IDs;
- attempted nested mutation after validation;
- incomplete fingerprints;
- candidate selector intersections and empty pools;
- indexed/full-scan semantic divergence;
- optimization metadata accidentally treated as detection semantics;
- unhashable nested group/distinct values;
- repeated-window evidence reuse;
- zero-detection trace loss;
- aggregate expectation drift and exact detection drift;
- invalid ledger stages, types, digests, counts, sequence, chain, or root;
- ordinary artifact tampering;
- rehashed but internally contradictory bundles;
- coherent report rewrites that fail source-bound reproduction;
- non-scalar ledger stages or statuses and other malformed JSON-valid structures;
- schema/document/runtime version drift;
- non-reproducible wheel bytes;
- unknown or post-freeze adapter registration; and
- accidental live-I/O imports.

## Highest-value next proofs

1. Publish one complete measured physical-lab experiment with synchronized source telemetry, analyst decision, containment validation, rollback, and recovery evidence.
2. Add an optional signed external envelope around the deterministic unsigned bundle.
3. Publish benchmark history across event count, rule count, group cardinality, and selector selectivity using controlled hosts.
4. Add a second offline vendor adapter and conformance fixture.
