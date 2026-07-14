# 24 — Contract Validation

## Why this exists

Runtime validation and JSON Schemas can drift independently. A repository may contain valid schema documents while its real inputs or generated outputs violate them. SOC_Replay treats that as a build failure.

## Contract versions

| Contract | Current | Compatibility |
| --- | --- | --- |
| Scenario | 1.1 | Runtime also reads 1.0 |
| Report | 2.1 | Current generator/verifier contract |
| Manifest | 2.1 | Current generator/verifier contract |
| Ledger | 1.0 | Strict five-stage contract |

## Validation tool

```bash
python tools/validate_contracts.py
```

The tool:

1. loads every schema and checks it against Draft 2020-12;
2. constructs an offline registry for relative schema references;
3. validates every maintained `scenario.json`;
4. validates every event line;
5. executes every scenario;
6. validates generated report, manifest, and embedded ledger instances; and
7. normalizes the Suricata fixture and validates every emitted event.

## Runtime versus schema responsibilities

Schemas describe portable document shape. Runtime validation additionally enforces relational invariants such as:

- expectation counts must agree;
- referenced rule IDs must exist;
- duplicate rule and event IDs are forbidden;
- maintained 1.1 exact detection lists must match aggregate expectations;
- response mode must remain simulated; and
- ledger hashes must recalculate correctly.

## Repository audit

`tools/verify_repository.py` checks the architectural wiring around the contracts: shared versions, pipeline stages, registry freeze state, exact maintained scenarios, rule-trace accounting, ledger completeness, index fields, required documentation, and prohibited live-I/O imports.

## Determinism audit

`tools/verify_deterministic_bundles.py` verifies that two isolated executions of each maintained scenario produce identical JSON, Markdown, and manifest bytes.
