# Replay report: Synthetic privileged group change

## Decision summary

| Measure | Result |
| --- | ---: |
| Events processed | 3 |
| Detections | 1 |
| Simulated actions | 1 |

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
- **Response:** `recommend_account_review` (simulated)
- **Purpose:** Recommend reviewing the synthetic actor and target accounts, preserving the audit record, and confirming change authorization.

## Safety note

All responses in this report are simulations. The replay engine does not connect to firewalls, hypervisors, endpoints, or production services.
