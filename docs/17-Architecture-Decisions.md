# 17 — Architecture Decisions

## ADR-001: deterministic offline replay

**Decision:** consume stored normalized events instead of coupling the core to live sensors.

**Rationale:** reproducibility, inspectability, and safe public examples matter more than ingestion breadth in the core package.

**Consequence:** adapters are separate work and synthetic success does not prove live detection coverage.

## ADR-002: simulation-only responses

**Decision:** reject every response mode except `simulated`.

**Rationale:** rule evaluation should not silently gain infrastructure authority. Live changes require a different trust boundary, approval model, and rollback design.

**Consequence:** response actions are evidence and analyst guidance, never commands.

## ADR-003: versioned scenario expectations

**Decision:** scenarios declare exact machine-readable expected results.

**Rationale:** examples become executable regression contracts and CI can identify semantic drift.

**Consequence:** expectations must be intentionally updated when rule semantics change.

## ADR-004: input-derived provenance

**Decision:** hash scenario and event files and derive a stable run ID.

**Rationale:** reviewers must be able to distinguish reports created from different inputs without introducing nondeterministic timestamps.

**Consequence:** hashes prove identity, not authorship or chain of custody.

## ADR-005: physical platform and replay plane remain separate

**Decision:** document the lab as the project context while keeping the package independent from device control.

**Rationale:** installed hardware is a differentiator, but unsupported automation claims damage credibility. Separation allows both layers to be evaluated honestly.

**Consequence:** end-to-end platform claims require named measured experiments beyond replay fixtures.
