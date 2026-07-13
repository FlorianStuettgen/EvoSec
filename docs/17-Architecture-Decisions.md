# 17 — Architecture Decisions

## ADR-001 — Standard-library runtime

**Decision:** Keep the runtime dependency-free.

**Why:** The engine remains easy to inspect, install, package, and run in constrained or isolated environments. Development tools remain optional dependencies.

## ADR-002 — Compile rules before evaluation

**Decision:** Convert rule fields, operators, aggregates, and candidate hints into immutable compiled structures.

**Why:** It removes repeated interpretation from the hot path and creates a stable semantic fingerprint.

## ADR-003 — Candidate indexes cannot decide matches

**Decision:** Indexes may narrow candidate events but may never bypass compiled conditions.

**Why:** Performance hints must not become hidden detection semantics.

## ADR-004 — Deterministic stage ledger

**Decision:** Record load, compile, index, evaluate, and verify in a hash-linked ledger without wall-clock timestamps or durations.

**Why:** Non-deterministic timing would make equivalent runs produce different evidence. Performance belongs in separate benchmark records.

## ADR-005 — Manifest-last bundle commit

**Decision:** Write JSON and Markdown artifacts atomically, then write the manifest last.

**Why:** The manifest acts as the completion marker for the bundle.

## ADR-006 — Offline adapter boundary

**Decision:** Adapters consume stored synthetic or sanitized files and expose no collection credentials or live connections.

**Why:** Vendor normalization can evolve independently without giving the replay package infrastructure authority.

## ADR-007 — Simulation-only response model

**Decision:** Reject every response mode except `simulated` at validation time.

**Why:** Detection evaluation and infrastructure control are different trust domains.
