# 23 — Execution Ledger

## Contract

The ledger is a deterministic five-entry hash chain:

```text
load → compile → index → evaluate → verify
```

Each entry contains sequence, stage, status, input/output digest, record counts, immutable metadata, prior hash, and entry hash.

## Builder enforcement

The builder rejects:

- an unexpected stage;
- a stage after completion;
- a stage after a failed entry;
- invalid status;
- non-hex or incorrectly sized digests;
- booleans or negative values used as counts; and
- non-mapping metadata.

## Verification enforcement

The verifier checks:

- the exact top-level field set;
- ledger schema and zero genesis hash;
- exactly five entries for a completed run;
- exact sequence and stage at each position;
- `ok` status for a completed evidence bundle;
- SHA-256 shape for every digest and hash;
- integer, nonnegative record counts;
- object metadata;
- prior-hash continuity;
- each recalculated entry hash; and
- final root identity.

A ledger with altered fields cannot become valid merely by recalculating its hashes if its structure violates the stage contract.

## Determinism

The ledger deliberately excludes wall-clock timestamps, durations, hostnames, process IDs, and machine-dependent measurements. Performance evidence belongs in separate benchmark records.

## Meaning

The root commits to the engine’s recorded stage transitions. It does not prove authorship, trusted time, source authenticity, or physical execution.
