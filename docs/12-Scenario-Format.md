# 12 — Scenario format

## Directory layout

```text
scenario-name/
├── scenario.json
└── events.jsonl
```

## Minimal scenario

```json
{
  "id": "example",
  "title": "Example scenario",
  "objective": "Explain the decision being tested.",
  "authorization_boundary": "Synthetic telemetry only.",
  "expected_outcome": "One high-severity detection.",
  "rules": [
    {
      "id": "EX-001",
      "name": "Example rule",
      "severity": "high",
      "match": [
        {"field": "category", "operator": "eq", "value": "example"}
      ],
      "response": {
        "action": "recommend_review",
        "description": "Preserve evidence and review the event.",
        "mode": "simulated"
      }
    }
  ]
}
```

## Aggregate example

```json
{
  "group_by": ["source_ip", "destination_ip"],
  "count_gte": 5,
  "within_seconds": 60,
  "distinct_field": "destination_port",
  "distinct_gte": 5
}
```

## Validation

```bash
soc-replay validate scenarios/example
```

The JSON schemas under `schemas/` document the portable contract. Runtime validation is stricter around duplicate IDs, timestamps, ports, operators, and response mode.
