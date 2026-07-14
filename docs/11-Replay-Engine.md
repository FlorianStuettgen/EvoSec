# 11 — Replay Engine

SOC_Replay 3.1 is a deterministic, contract-complete execution pipeline rather than a collection of matching helpers.

## Public result

A scenario supplies immutable `scenario.json` and `events.jsonl` inputs. The engine returns a `ReplayResult` containing:

- validated input objects and provenance hashes;
- a compiled semantic execution plan;
- one execution trace for every rule;
- ordered detections;
- exact expectation checks;
- simulation-only recommendations; and
- a complete five-stage execution ledger.

## Core modules

| Module | Responsibility |
| --- | --- |
| `contracts.py` | Shared engine, stage, index, and schema-version vocabulary |
| `immutability.py` | Recursive conversion of JSON-like data into immutable structures |
| `model_common.py` | Shared validation vocabulary and field contracts |
| `event_models.py` | Events, conditions, aggregates, responses, and rules |
| `scenario_models.py` | Exact expectations and scenario contracts |
| `result_models.py` | Detections and verification records |
| `models.py` | Stable compatibility façade for public model imports |
| `operators.py` | Small inspectable predicate registry |
| `compiler.py` | Field accessors, operator binding, candidate selectors, and fingerprints |
| `indexing.py` | Immutable equality/tag indexes and selector intersections |
| `correlation.py` | Single-event and window evaluation plus rule traces |
| `verification.py` | Aggregate and exact detection-contract comparison |
| `pipeline.py` | Stage orchestration and ledger construction |
| `result.py` | Immutable result and public report representation |
| `report_render.py` | JSON and analyst-readable rendering |
| `bundle.py` | Manifest construction and internal-consistency verification |
| `report.py` | Stable reporting façade |

## Execution order

```text
load → compile → index → evaluate → verify
```

The order is shared by the pipeline, ledger builder, ledger verifier, schemas, CLI graph, repository auditor, and documentation.

## Deep immutability

Inputs are recursively frozen at the public model boundary. Mapping values become read-only mappings and JSON arrays become tuples. The serialization layer converts those structures back to normal JSON objects and arrays. This prevents a completed stage from being silently modified through a nested reference.

## Compilation

Every condition receives a pre-parsed field accessor and a bound operator callable. Aggregate grouping and distinct-value accessors are prepared once. The compiler extracts all safe index selectors and creates a complete rule fingerprint from every field capable of changing evaluation or report output.

## Candidate intersection

A rule may compile several selectors, for example:

```text
intersection[
  eq:category=network_connection,
  eq:outcome=blocked,
  tag:reconnaissance
]
```

The index intersects these pools in original event order. The complete rule predicate is still evaluated against every candidate; indexes cannot decide a match.

## Rule execution traces

The evaluation stage emits a `RuleExecution` even when no detection occurs. It records candidate count, matched count, group count, windows considered, and detection count. This makes negative controls and non-firing rules inspectable.

## Exact verification

Scenario schema 1.1 can specify the exact ordered detection set. The verifier compares rule ID, severity, evidence-event IDs, grouping values, and simulated response action. Aggregate count, rule-ID, severity, and action-count checks remain as independent diagnostics.

## Compatibility

- Scenario schema 1.0 remains accepted by the runtime.
- Maintained scenarios use 1.1 and exact detection contracts.
- `engine.run_scenario`, `engine.evaluate_rule`, `report.write_reports`, and `normalize-suricata` remain compatibility surfaces.
