# Changelog

## Unreleased

## 3.3.0 — 2026-07-15

- Added source-bound bundle verification through `verify_bundle(..., source_directory=...)`, with deterministic re-execution and exact byte comparison of JSON, Markdown, and manifest artifacts.
- Strengthened standalone verification by recomputing run IDs, plan fingerprints, candidate strategies, verification outcomes, rule/detection accounting, and load/compile/evaluate/verify ledger digests.
- Added correlation-to-trace checks, sequential detection identity checks, exact schema 1.1 contract verification, and adversarial tests for rehashed semantic tampering and coherent report-only rewrites.
- Hardened execution-ledger verification so JSON-valid non-scalar stage and status values fail cleanly instead of raising uncaught runtime exceptions.
- Added concise, verbose, and JSON output modes to `soc-replay verify-bundle`; successful default output is now summary-first.
- Required source-bound verification in deterministic bundle auditing and the CI smoke path.
- Reworked the repository landing page and documentation map around visitor goals, evidence guarantees, and explicit non-claims.
- Updated the security policy, threat model, implementation register, engineering review, and contributor guidance to match standalone and source-bound verification.
- Pinned GitHub Actions by commit, aligned isolated and no-isolation build tooling, cancelled superseded workflow runs, and expanded cache/build-output exclusions.

## 3.2.1 — 2026-07-14

- Resolved all Ruff failures across the recursive immutability, serialization, and compatibility-wrapper surfaces.
- Made CI preserve and upload lint, test, coverage, build, benchmark, bundle, and proof diagnostics even when an earlier gate fails.
- Confirmed the Python 3.11 and 3.12 matrices pass every quality, contract, proof, schema, bundle, adapter, determinism, audit, and package-build gate.
- Confirmed the Python 3.13 benchmark smoke run produces schema-valid artifacts with embedded passing semantic-equivalence proofs.
- Corrected the reproducible-wheel verifier to build from two independent clean source copies rather than one mutable source tree.
- Added persistent build-frontend logs and entry-level wheel diagnostics for forensic failures.
- Declared the setuptools backend and wheel builder as development dependencies for deliberate no-isolation builds.
- Retained environment-labelled benchmark measurements without introducing brittle latency thresholds or unsupported speed claims.

## 3.2.0 — 2026-07-14

- Added differential correctness proofs comparing indexed execution with a full-scan reference path.
- Added per-rule semantic proof digests and candidate-reduction accounting.
- Added deterministic workload expansion and environment-labelled benchmark artifacts.
- Added public JSON Schemas for index-equivalence proofs and benchmark results.
- Added CI gates for indexed/full-scan equivalence, benchmark smoke execution, and reproducible wheel bytes.
- Added a reproducible-build auditor using fixed build epoch and hash seed inputs.
- Documented correctness-proof methodology, performance interpretation, and supply-chain boundaries.

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
