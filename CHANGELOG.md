# Changelog

## 3.0.0 — 2026-07-13

- Replaced the monolithic replay path with an explicit load/compile/index/evaluate/verify pipeline.
- Added immutable compiled rules, field accessors, operator binding, and semantic plan fingerprints.
- Added candidate indexing for common equality selectors and tags without changing rule semantics.
- Added a deterministic hash-chained execution ledger and public ledger schema.
- Added report and manifest schema version 2.0 with plan, ledger, and bundle identities.
- Added a generic offline adapter registry while preserving the Suricata compatibility command.
- Added `doctor`, `graph`, and adapter-discovery CLI surfaces.
- Added repository self-auditing for scenario, ledger, schema, version, and live-I/O invariants.
- Expanded branch coverage above 90% across validation, corruption, adapter, CLI, and pipeline paths.

## 2.1.0 — 2026-07-13

- Added manifest-backed evidence bundles, offline Suricata normalization, a negative control, threat model, and experiment template.

## 2.0.0 — 2026-07-13

- Added machine-verifiable expectations, input provenance, explicit correlation policies, strict typing, CI, and deterministic reference reports.
