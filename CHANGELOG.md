# Changelog

## 2.1.0 — 2026-07-13

- Added manifest-backed JSON/Markdown evidence bundles and offline tamper verification.
- Added a sanitized Suricata EVE adapter for stored `alert` and `flow` records.
- Added an approved privileged-maintenance negative control with an expected zero-detection result.
- Added a bundle-manifest JSON Schema and committed manifest references for every scenario.
- Added a measured experiment template and explicit threat model.
- Expanded tests across adapter behavior, negative controls, bundle determinism, and tamper detection.
- Raised the branch-coverage gate and extended repository coherence checks.

## 2.0.0 — 2026-07-13

- Added machine-verifiable scenario expectations and a `verify` CLI command.
- Added SHA-256 input provenance and deterministic run identifiers to every report.
- Added explicit correlation-window policies, including non-overlapping repeated detections.
- Added a third executable scenario demonstrating repeated authentication-failure windows.
- Hardened event, condition, aggregate, IP-address, timestamp, and response validation.
- Added atomic report writes, a report schema, deterministic reference-report checks, and a local benchmark harness.
- Expanded the test suite across models, engine semantics, CLI behavior, reports, mismatch handling, and safety boundaries.
- Reframed the README around the system thesis, end-to-end proof, engineering decisions, and evidence hierarchy.
- Added a version-controlled wiki source and architecture-decision record.

## 1.1.0 — 2026-07-13

- Restored the physical lab documentation and integrated the replay utility as supporting evidence tooling.

## 1.0.0 — 2026-07-13

- Added the initial deterministic replay engine, scenarios, reports, schemas, tests, and CI.
