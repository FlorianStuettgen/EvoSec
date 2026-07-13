# Replay report: Synthetic repeated authentication failures

> **Verification: PASS** · Run ID `eb34e2c23cc54541` · Engine `soc-replay 2.1.0`

## Decision summary

| Measure | Result |
| --- | ---: |
| Events processed | 7 |
| Detections | 2 |
| Simulated actions | 2 |
| Expectations verified | Yes |

## Provenance

- **Scenario SHA-256:** `44fea2ea3ac00be9d6003249f312b9bb53667d272ae32c513e5c76354e5ef850`
- **Events SHA-256:** `3d6e10b45b05fc16655b4c285b286856233b92127719e517696850ceb80ef779`
- **Deterministic run ID:** `eb34e2c23cc54541`

## Verification checks

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| `detection_count` | `2` | `2` | PASS |
| `rule_ids` | `["AUTH-BURST-001", "AUTH-BURST-001"]` | `["AUTH-BURST-001", "AUTH-BURST-001"]` | PASS |
| `severity_counts` | `{"medium": 2}` | `{"medium": 2}` | PASS |
| `simulated_action_count` | `2` | `2` | PASS |

## Authorization boundary

Synthetic authentication records only. No account, endpoint, or identity service is contacted.

## Expected outcome

Two medium-severity detections, each backed by three failed events inside a ninety-second window.

## Detections

### AUTH-BURST-001:001 — Repeated authentication failures

- **Severity:** medium
- **First seen:** 2026-07-03T10:00:00+00:00
- **Last seen:** 2026-07-03T10:00:45+00:00
- **Evidence events:** auth-001, auth-002, auth-003
- **Group:** `{"host": "lab-app-01", "user": "analyst.demo"}`
- **Correlation:** `{"event_count": 3, "threshold": 3, "type": "time_window", "window_policy": "all_non_overlapping", "within_seconds": 90}`
- **Response:** `recommend_authentication_review` (simulated)
- **Purpose:** Recommend reviewing the synthetic account and source context before taking any identity action.

### AUTH-BURST-001:002 — Repeated authentication failures

- **Severity:** medium
- **First seen:** 2026-07-03T10:05:00+00:00
- **Last seen:** 2026-07-03T10:05:50+00:00
- **Evidence events:** auth-004, auth-005, auth-006
- **Group:** `{"host": "lab-app-01", "user": "analyst.demo"}`
- **Correlation:** `{"event_count": 3, "threshold": 3, "type": "time_window", "window_policy": "all_non_overlapping", "within_seconds": 90}`
- **Response:** `recommend_authentication_review` (simulated)
- **Purpose:** Recommend reviewing the synthetic account and source context before taking any identity action.

## Safety note

All responses in this report are simulations. The replay engine does not connect to firewalls, hypervisors, endpoints, identity providers, or production services.
