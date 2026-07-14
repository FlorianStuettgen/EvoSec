# 17 — Architecture Decisions

## ADR-001 — Standard-library runtime

**Decision:** Keep runtime dependencies at zero.

**Reason:** The engine remains portable, inspectable, packageable, and usable in isolated environments. Schema tooling is a development dependency.

## ADR-002 — Deep freeze at model boundaries

**Decision:** Recursively freeze JSON-like values when constructing public runtime models.

**Reason:** A frozen dataclass containing mutable dictionaries is not immutable. Stage invariants must survive nested references.

## ADR-003 — Complete semantic fingerprints

**Decision:** Fingerprints commit to every rule field capable of changing evaluation or report output.

**Reason:** Execution identity must not treat two meaningfully different rules as equivalent.

## ADR-004 — Composite selectors are performance plans, not truth conditions

**Decision:** Compile all safe equality/tag selectors and intersect their candidate pools. Always evaluate the full compiled predicate afterward.

**Reason:** The execution plan should be genuinely useful while indexes remain incapable of changing semantics.

## ADR-005 — Preserve zero-result execution traces

**Decision:** Emit one trace for every rule, regardless of whether it detects anything.

**Reason:** Negative controls and non-firing rules are evidence about engine behavior and should be inspectable.

## ADR-006 — Exact contracts for maintained scenarios

**Decision:** Introduce scenario schema 1.1 with ordered exact detection assertions while retaining 1.0 read compatibility.

**Reason:** Aggregate counts alone can pass when the wrong events, groups, or actions are produced.

## ADR-007 — Strict deterministic stage ledger

**Decision:** Enforce the exact load/compile/index/evaluate/verify sequence, typed fields, digest formats, counts, statuses, and hash chain.

**Reason:** A rehashed but structurally invalid ledger must not be considered valid.

## ADR-008 — Validate real instances against schemas

**Decision:** CI validates repository inputs and generated outputs using Draft 2020-12 validators and a local schema registry.

**Reason:** A syntactically valid schema file is not evidence that runtime artifacts conform to it.

## ADR-009 — Verify internal bundle agreement

**Decision:** Bundle verification recomputes run and plan identities, verification outcomes, candidate strategies, rule/detection relationships, ledger stage digests, artifact hashes, and manifest identity.

**Reason:** Recomputing a file hash must not conceal contradictions inside the evidence set.

## ADR-010 — Freeze the global adapter registry

**Decision:** Register built-in adapters during startup and then freeze the shared registry.

**Reason:** Runtime extension should be explicit; global behavior must not mutate after initialization.

## ADR-011 — Simulation-only response model

**Decision:** Reject every response mode except `simulated`.

**Reason:** Detection evaluation and infrastructure control are separate trust domains.

## ADR-012 — Separate standalone consistency from source-bound identity

**Decision:** Retain standalone bundle verification for offline internal-consistency checks and add an optional source-bound mode that reruns the scenario and byte-compares all generated artifacts.

**Reason:** Some report fields cannot be independently reconstructed from a bundle that does not contain its original inputs. Source-bound reproduction makes that limitation explicit and provides a stronger verification path without embedding potentially sensitive telemetry in every bundle.

## ADR-013 — Fail closed on malformed evidence structures

**Decision:** Treat report bundles and execution ledgers as untrusted structured data. Invalid scalar types, object/array boundaries, stages, statuses, counts, or digest fields must produce a controlled failed verdict or `ValidationError`, never an uncaught runtime exception.

**Reason:** The verifier is an integrity boundary. Robust rejection behavior is part of the public contract, not merely defensive implementation detail.
