# 11 — Replay Engine

SOC_Replay 3.0 is a deterministic execution pipeline, not a collection of ad hoc matching functions.

## Public contract

A scenario supplies immutable `scenario.json` and `events.jsonl` inputs. The engine returns a `ReplayResult` containing:

- the validated inputs and provenance hashes;
- a compiled execution plan;
- ordered detections;
- exact expectation checks;
- simulated analyst recommendations; and
- a five-stage execution ledger.

## Internal modules

| Module | Responsibility |
| --- | --- |
| `models.py` | Strict public data contracts and simulation-only response boundary |
| `operators.py` | Small inspectable operator registry |
| `compiler.py` | Field accessors, operator binding, aggregate plans, and fingerprints |
| `indexing.py` | Immutable candidate indexes for common selectors and tags |
| `correlation.py` | Single-event and time-window detection semantics |
| `verification.py` | Exact result-to-expectation comparison |
| `pipeline.py` | Stage orchestration and deterministic ledger construction |
| `result.py` | Immutable result and report representation |
| `report.py` | JSON/Markdown rendering, manifests, and offline bundle verification |

## Execution order

```text
load → compile → index → evaluate → verify
```

The order is part of the public execution contract and is checked by the repository verifier.

## Why compile rules

Without compilation, every event evaluation repeatedly splits field paths, resolves operators, and reconstructs aggregation behavior. Compilation moves that work into a single deterministic preparation stage. The resulting plan has a fingerprint derived from rule semantics.

## Why index candidates

Indexes reduce avoidable scans for common equality and tag conditions. They are only candidate selectors: every selected event must still satisfy every compiled condition. A missing hint falls back to a full scan.

## Correlation guarantees

- Inputs are sorted by timestamp and event ID.
- Groups are processed in deterministic representation order.
- Detection IDs are stable within a rule.
- `first_per_group` emits the first qualifying window.
- `all_non_overlapping` consumes evidence after each qualifying window.
- Candidate strategy and counts are preserved in detection metadata.

## Compatibility

`engine.run_scenario`, `engine.evaluate_rule`, `report.write_reports`, and `normalize-suricata` remain available as compatibility surfaces. New code should prefer `ReplayPipeline`, `write_bundle`, and the generic adapter registry.
