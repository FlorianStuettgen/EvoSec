# 12 — Scenario Format

A scenario is an executable experiment contract.

```text
scenario-name/
├── scenario.json
└── events.jsonl
```

## Required scenario fields

- `schema_version`: currently `1.0`
- `id`, `title`, and `objective`
- `authorization_boundary`
- `expected_outcome`
- `expectations`
- one or more rules

## Expectations

```json
{
  "detection_count": 1,
  "rule_ids": ["NET-SCAN-001"],
  "severity_counts": {"high": 1},
  "simulated_action_count": 1
}
```

These values are validated for internal consistency and checked after every replay.

## Rule conditions

Supported operators:

| Operator | Meaning |
| --- | --- |
| `eq`, `ne` | equality and inequality |
| `in`, `not_in` | membership against a declared list |
| `contains` | containment for strings, lists, tuples, sets, or objects |
| `gte`, `lte` | ordered comparison |
| `exists` | field presence; accepts `true`, `false`, or omission for `true` |

Nested data is addressed with paths such as `details.actor.role`.

## Aggregation

```json
{
  "group_by": ["source_ip", "destination_ip"],
  "count_gte": 5,
  "within_seconds": 60,
  "distinct_field": "destination_port",
  "distinct_gte": 5,
  "window_policy": "first_per_group"
}
```

The distinct fields must be supplied together. Window policies are `first_per_group` and `all_non_overlapping`.

## Response boundary

```json
{
  "action": "recommend_segment_isolation",
  "description": "Analyst-facing recommendation",
  "mode": "simulated"
}
```

Any other mode is rejected. Response action names are descriptive data, not executable commands.

## Event contract

Every JSONL record requires `event_id`, timezone-aware `timestamp`, `source`, `category`, and `action`. Optional normalized fields include IPs, destination port, host, user, outcome, tags, and arbitrary nested `details`.

See the machine-readable contracts in [`schemas/`](../schemas/).

## Positive and negative controls

A scenario may expect zero detections. Negative controls should exercise realistic benign activity against the same rule contract used by a positive scenario. This demonstrates false-positive discipline and prevents a catalog made only of guaranteed detections.
