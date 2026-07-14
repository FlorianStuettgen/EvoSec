# Changelog

## 3.1.0 — 2026-07-13

- Made all nested runtime state deeply immutable while preserving ordinary JSON serialization.
- Expanded rule fingerprints to commit to every behavior- and report-affecting field.
- Replaced single candidate hints with deterministic intersections of all safe selectors.
- Added per-rule execution traces, including explicit zero-detection evidence.
- Added scenario schema 1.1 with exact detection contracts while retaining 1.0 input compatibility.
- Strengthened ledger construction and verification with exact stage order, type, digest, count, and completion checks.
- Added report and manifest contract version 2.1 with rule traces and stronger internal-consistency verification.
- Added real Draft 2020-12 validation of scenarios, events, reports, manifests, ledgers, and normalized adapter output.
- Froze the global adapter registry after startup.
- Expanded the local gate to 42 tests and 93% branch coverage.

## 3.0.0 — 2026-07-13

- Replaced the monolithic replay path with an explicit load/compile/index/evaluate/verify pipeline.
- Added immutable compiled rules, field accessors, operator binding, and semantic plan fingerprints.
- Added candidate indexing for common equality selectors and tags without changing rule semantics.
- Added a deterministic hash-chained execution ledger and public ledger schema.
- Added report and manifest schema version 2.0 with plan, ledger, and bundle identities.
- Added a generic offline adapter registry while preserving the Suricata compatibility command.
- Added `doctor`, `graph`, and adapter-discovery CLI surfaces.
- Added repository self-auditing for scenario, ledger, schema, version, and live-I/O invariants.

## 2.1.0 — 2026-07-13

- Added manifest-backed evidence bundles, offline Suricata normalization, a negative control, threat model, and experiment template.

## 2.0.0 — 2026-07-13

- Added machine-verifiable expectations, input provenance, explicit correlation policies, strict typing, CI, and deterministic reference reports.
