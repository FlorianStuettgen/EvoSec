# Replay report: Synthetic multi-port scan

> **Verification: PASS** · Run ID `686f91bca3c385b6` · Engine `soc-replay 3.2.1`

## Decision summary

| Measure | Result |
| --- | ---: |
| Events processed | 7 |
| Rules executed | 1 |
| Detections | 1 |
| Simulated actions | 1 |
| Expectations verified | Yes |

## Provenance and execution identity

- **Scenario SHA-256:** `defa19d6af50f8335bae607271c780f1b7aea998b47baee3f605a9693d431817`
- **Events SHA-256:** `e7421a5093e510b41f013c8cef4e4d5014764ddfa578cb03352c3415f46dc6dd`
- **Deterministic run ID:** `686f91bca3c385b6`
- **Execution-plan fingerprint:** `1a8be1ed446db27f0bd5bf7306165b53f0f67c0ff4e4934638e33ad27e339e94`
- **Execution-ledger root:** `2e051d78d6adfac1e71af2debbe525258bb4ca97815daa902b02dbb4edb7f84a`

## Execution ledger

| # | Stage | In | Out | Entry hash |
| ---: | --- | ---: | ---: | --- |
| 1 | `load` | 2 | 7 | `2957549f6ff905b2…` |
| 2 | `compile` | 1 | 1 | `1c797376a137c4f1…` |
| 3 | `index` | 7 | 7 | `6a84cb843c084f64…` |
| 4 | `evaluate` | 7 | 1 | `061f9670dfb56967…` |
| 5 | `verify` | 1 | 5 | `2e051d78d6adfac1…` |

Each ledger entry commits to the prior entry, stage inputs, stage outputs, record counts, and deterministic metadata.

## Rule execution trace

| Rule | Candidates | Matched | Groups | Windows | Detections | Strategy |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `NET-SCAN-001` | 6 | 6 | 1 | 5 | 1 | `intersection[eq:category=network_connection,eq:outcome=blocked,tag:reconnaissance]` |

The trace records every rule, including rules that correctly produced zero detections.

## Verification checks

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| `detection_count` | `1` | `1` | PASS |
| `rule_ids` | `["NET-SCAN-001"]` | `["NET-SCAN-001"]` | PASS |
| `severity_counts` | `{"high": 1}` | `{"high": 1}` | PASS |
| `simulated_action_count` | `1` | `1` | PASS |
| `detection_contracts` | `[{"action": "recommend_segment_isolation", "event_ids": ["net-001", "net-002", "net-003", "net-004", "net-005"], "group": {"destination_ip": "10.20.40.10", "source_ip": "10.20.30.77"}, "rule_id": "NET-SCAN-001", "severity": "high"}]` | `[{"action": "recommend_segment_isolation", "event_ids": ["net-001", "net-002", "net-003", "net-004", "net-005"], "group": {"destination_ip": "10.20.40.10", "source_ip": "10.20.30.77"}, "rule_id": "NET-SCAN-001", "severity": "high"}]` | PASS |

## Authorization boundary

Synthetic telemetry only. No packets are generated and no network device is contacted.

## Expected outcome

One high-severity detection backed by at least five events and five distinct destination ports within sixty seconds.

## Detections

### NET-SCAN-001:001 — Multi-port connection burst

- **Severity:** high
- **First seen:** 2026-07-01T12:00:00+00:00
- **Last seen:** 2026-07-01T12:00:31+00:00
- **Evidence events:** net-001, net-002, net-003, net-004, net-005
- **Group:** `{"destination_ip": "10.20.40.10", "source_ip": "10.20.30.77"}`
- **Correlation:** `{"candidate_events": 6, "candidate_strategy": "intersection[eq:category=network_connection,eq:outcome=blocked,tag:reconnaissance]", "distinct_count": 5, "distinct_field": "destination_port", "distinct_threshold": 5, "event_count": 5, "matched_events": 6, "rule_fingerprint": "8950e9b4ceaeb4076ffa90a980994c435147c12a1c08b35936891ba6de45dc7d", "threshold": 5, "type": "time_window", "window_policy": "first_per_group", "within_seconds": 60}`
- **Response:** `recommend_segment_isolation` (simulated)
- **Purpose:** Recommend isolating the synthetic source segment and preserving the matched event set for analyst review.

## Safety note

All responses are simulations. The package does not contact infrastructure, execute commands, or change accounts.
