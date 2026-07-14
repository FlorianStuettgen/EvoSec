# 12 — Scenario Format

Each scenario directory contains:

```text
scenario-name/
├── scenario.json
└── events.jsonl
```

## Scenario schema versions

- `1.0` remains readable for backward compatibility.
- `1.1` is the maintained standard and requires exact detection contracts.

## Core scenario fields

A scenario declares its identity, title, objective, authorization boundary, expected outcome, expectations, and one or more rules.

## Rules

A rule contains:

- stable ID and display name;
- severity and description;
- one or more conditions;
- an optional aggregate contract; and
- a simulation-only response.

Supported operators are `eq`, `ne`, `in`, `not_in`, `contains`, `gte`, `lte`, and `exists`. Nested paths are permitted only beneath `details`.

## Aggregate rules

Aggregate rules declare:

- grouping fields;
- minimum event count;
- window duration;
- optional distinct field and threshold; and
- `first_per_group` or `all_non_overlapping` window policy.

## Exact expectations in 1.1

`expectations.detections` is ordered and identifies:

```json
{
  "rule_id": "NET-SCAN-001",
  "severity": "high",
  "event_ids": ["net-001", "net-002", "net-003", "net-004", "net-005"],
  "group": {
    "source_ip": "10.20.30.77",
    "destination_ip": "10.20.40.10"
  },
  "action": "recommend_segment_isolation"
}
```

The exact list must agree with detection count, rule-ID sequence, severity totals, and simulated-action count.

## Events

Every JSONL record requires event ID, timezone-aware timestamp, source, category, and action. Optional fields include IPs, destination port, host, user, outcome, tags, and nested details. Event IDs and tags must be unique within their respective scopes.

## Validation

```bash
soc-replay validate scenarios/network-scan
python tools/validate_contracts.py
```

The first command applies runtime validation. The second validates the repository and generated artifacts against the JSON Schemas.
