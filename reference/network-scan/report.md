# Replay report: Synthetic multi-port scan

> **Verification: PASS** · Run ID `a593cecd501f5d1a` · Engine `soc-replay 3.3.0`

## Decision summary

| Measure | Result |
| --- | ---: |
| Events processed | 7 |
| Rules executed | 1 |
| Detections | 1 |
| Simulated actions | 1 |
| Expectations verified | Yes |

## Provenance and execution identity

- **Scenario SHA-256:** `094766adbee70e9378f485140668d4a60f802132dc1aabf04cd331a4e250bc09`
- **Events SHA-256:** `97f67c5acaf07d7792d0e32305802c0ebeaf7941a48883c666015b0f300682c4`
- **Deterministic run ID:** `a593cecd501f5d1a`
- **Execution-plan fingerprint:** `1a8be1ed446db27f0bd5bf7306165b53f0f67c0ff4e4934638e33ad27e339e94`
- **Execution-ledger root:** `2d709f79a2bdee2fa6105234aeee63b2478447107cbd089a8f428fc49e84c937`

## Execution ledger

| # | Stage | In | Out | Entry hash |
| ---: | --- | ---: | ---: | --- |
| 1 | `load` | 2 | 7 | `1e88699192b227ca…` |
| 2 | `compile` | 1 | 1 | `3e415069f9b7de62…` |
| 3 | `index` | 7 | 7 | `ecc404b559ecc50c…` |
| 4 | `evaluate` | 7 | 1 | `618bf12604f17bc5…` |
| 5 | `verify` | 1 | 5 | `2d709f79a2bdee2f…` |

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
