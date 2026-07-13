# 11 — Replay Engine

## Purpose

The replay engine provides a deterministic evidence plane for defensive experiments. It consumes a scenario contract and normalized JSONL events, evaluates inspectable rules, verifies declared expectations, and emits JSON and Markdown reports.

It is intentionally not a SIEM, packet generator, endpoint agent, or response orchestrator.

## Processing model

```text
scenario.json + events.jsonl
          │
          ▼
strict contract validation
          │
          ▼
chronological normalization + SHA-256 provenance
          │
          ▼
field matching + optional time-window correlation
          │
          ▼
ordered detections + simulated recommendations
          │
          ▼
expectation verification + deterministic reports
```

## Determinism

For identical input bytes and engine version:

- events are sorted by UTC timestamp and event ID;
- rule order is preserved;
- detection order is stable;
- run IDs are derived from scenario and event hashes;
- no wall-clock timestamp is embedded in report content; and
- committed reference reports can be compared byte for byte.

## Correlation semantics

An aggregate rule declares:

- grouping fields;
- a minimum event count;
- a time window;
- an optional distinct-value threshold; and
- a window policy.

`first_per_group` emits the first qualifying window for each group. `all_non_overlapping` emits repeated qualifying windows while preventing evidence events from being reused across detections.

## Verification

Each scenario declares exact expectations for:

- detection count;
- rule IDs;
- severity counts; and
- simulated-action count.

`soc-replay verify` exits with code `3` when the output does not match. This converts example scenarios from prose demonstrations into executable regression tests.

## Provenance

Reports preserve:

- scenario SHA-256;
- event-file SHA-256;
- deterministic run ID;
- engine name and version; and
- evidence event IDs for every detection.

The hashes establish input identity, not authenticity. Signing and external chain-of-custody controls remain outside the current scope.

## Failure behavior

The engine rejects malformed JSON, missing files, duplicate event IDs, naive timestamps, invalid IP addresses, inconsistent aggregation fields, unsupported operators, unknown expected rule IDs, and any response mode other than `simulated`.

Report writes use atomic replacement so a partially written file is not presented as complete evidence.
