# 22 — Execution Core

![SOC_Replay execution core](assets/execution-core.svg)

## Purpose

The execution core converts immutable scenario inputs into a deterministic, inspectable decision trail. Every stage has explicit inputs, outputs, invariants, and a ledger entry.

## 1. Load

The loader:

- parses the scenario and JSONL stream;
- validates runtime contracts;
- rejects duplicate event IDs;
- recursively freezes nested values;
- sorts events by timestamp and event ID;
- enforces the event limit; and
- hashes both input files.

## 2. Compile

Each rule becomes an immutable compiled rule containing:

- field accessors;
- bound operator callables;
- aggregate accessors;
- all safe candidate selectors; and
- a complete semantic fingerprint.

The plan fingerprint commits to the schema version, scenario ID, ordered rules, and their fingerprints.

## 3. Index

Indexes exist for category, action, outcome, source, host, user, and tags. Selector pools are intersected deterministically. Events remain in original normalized order.

Example strategy:

```text
intersection[eq:category=network_connection,eq:outcome=blocked,tag:reconnaissance]
```

The full compiled predicate remains authoritative.

## 4. Evaluate

Each rule produces a `RuleExecution`. Aggregate groups use canonical JSON keys so nested JSON values remain deterministic and hashable. Correlation records candidate strategy, candidate/matched counts, thresholds, window policy, distinct values, and rule fingerprint.

## 5. Verify

The verifier performs independent aggregate checks and, for schema 1.1 scenarios, compares the exact ordered detection contract. A mismatch in evidence IDs can fail even when the detection count is correct.

## Pipeline invariants

1. Inputs are deeply immutable after load.
2. Rules are compiled before evaluation.
3. Candidate indexes never change rule semantics.
4. Every compiled rule yields one execution trace.
5. Maintained scenarios declare exact detections.
6. Responses remain simulation-only.
7. Every stage is represented exactly once in the ledger.
8. Equivalent input bytes and engine version produce equivalent bundle bytes.
