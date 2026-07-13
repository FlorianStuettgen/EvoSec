# Replay report: Synthetic multi-port scan

> **Verification: PASS** · Run ID `7c3405055d55db4b` · Engine `soc-replay 2.0.0`

## Decision summary

| Measure | Result |
| --- | ---: |
| Events processed | 7 |
| Detections | 1 |
| Simulated actions | 1 |
| Expectations verified | Yes |

## Provenance

- **Scenario SHA-256:** `68f1ef584374e0f360d4a7d498a542ddfe7591a4fdca8157936fa9e026a059b4`
- **Events SHA-256:** `e7421a5093e510b41f013c8cef4e4d5014764ddfa578cb03352c3415f46dc6dd`
- **Deterministic run ID:** `7c3405055d55db4b`

## Verification checks

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| `detection_count` | `1` | `1` | PASS |
| `rule_ids` | `["NET-SCAN-001"]` | `["NET-SCAN-001"]` | PASS |
| `severity_counts` | `{"high": 1}` | `{"high": 1}` | PASS |
| `simulated_action_count` | `1` | `1` | PASS |

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
- **Correlation:** `{"distinct_count": 5, "distinct_field": "destination_port", "distinct_threshold": 5, "event_count": 5, "threshold": 5, "type": "time_window", "window_policy": "first_per_group", "within_seconds": 60}`
- **Response:** `recommend_segment_isolation` (simulated)
- **Purpose:** Recommend isolating the synthetic source segment and preserving the matched event set for analyst review.

## Safety note

All responses in this report are simulations. The replay engine does not connect to firewalls, hypervisors, endpoints, identity providers, or production services.
