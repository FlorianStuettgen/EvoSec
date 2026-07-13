# Replay report: Synthetic privileged group change

> **Verification: PASS** · Run ID `1f76fcf3b5221c68` · Engine `soc-replay 2.1.0`

## Decision summary

| Measure | Result |
| --- | ---: |
| Events processed | 3 |
| Detections | 1 |
| Simulated actions | 1 |
| Expectations verified | Yes |

## Provenance

- **Scenario SHA-256:** `9576611eddb3f3248a4fe9d74389a5f1ce1fbc7f59176cb3686d571a7372bd2d`
- **Events SHA-256:** `b0bdecbea452eff3538bb5d57ae33f60f9ca9dc292ad5d81b1dc0d9056f82b3d`
- **Deterministic run ID:** `1f76fcf3b5221c68`

## Verification checks

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| `detection_count` | `1` | `1` | PASS |
| `rule_ids` | `["IAM-PRIV-001"]` | `["IAM-PRIV-001"]` | PASS |
| `severity_counts` | `{"critical": 1}` | `{"critical": 1}` | PASS |
| `simulated_action_count` | `1` | `1` | PASS |

## Authorization boundary

Synthetic audit records only. No identity provider or host is modified.

## Expected outcome

One critical detection associated with the unauthorized group-change event.

## Detections

### IAM-PRIV-001:001 — Unexpected privileged group membership change

- **Severity:** critical
- **First seen:** 2026-07-02T09:12:20+00:00
- **Last seen:** 2026-07-02T09:12:20+00:00
- **Evidence events:** iam-002
- **Group:** `{}`
- **Correlation:** `{"event_count": 1, "type": "single_event"}`
- **Response:** `recommend_account_review` (simulated)
- **Purpose:** Recommend reviewing the synthetic actor and target accounts, preserving the audit record, and confirming change authorization.

## Safety note

All responses in this report are simulations. The replay engine does not connect to firewalls, hypervisors, endpoints, identity providers, or production services.
