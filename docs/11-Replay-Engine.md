# 11 — Evidence replay engine

The replay engine is a supporting utility inside SOC_Replay. It provides a repeatable way to evaluate stored defensive telemetry without pretending to operate the physical lab.

## Public API

```python
from soc_replay import run_scenario

result = run_scenario("scenarios/network-scan")
print(result.to_dict())
```

## Capabilities

- JSONL event loading
- Scenario validation
- Inspectable field conditions
- Count and distinct-value correlation windows
- Stable ordering and deterministic output
- JSON and Markdown reports
- Simulation-only response recommendations

## Determinism

Events sort by timestamp and event ID. Rules evaluate in scenario order. Reports omit wall-clock generation timestamps and sort keys. Identical inputs therefore produce identical report content.

## Platform integration boundary

A physical experiment may export sanitized events into the replay format. Import adapters should remain read-only and normalize data before evaluation. The engine contains no firewall, switch, hypervisor, endpoint or identity connector.

## Why it belongs here

The physical lab creates real topology, sensor and recovery questions. The replay utility provides a controlled baseline for testing detection logic and evidence structure before or after a physical exercise. It is one tool in the platform, not the platform itself.
