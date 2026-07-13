# Replay report: Synthetic multi-port scan

## Decision summary

| Measure | Result |
| --- | ---: |
| Events processed | 7 |
| Detections | 1 |
| Simulated actions | 1 |

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
- **Response:** `recommend_segment_isolation` (simulated)
- **Purpose:** Recommend isolating the synthetic source segment and preserving the matched event set for analyst review.

## Safety note

All responses in this report are simulations. The replay engine does not connect to firewalls, hypervisors, endpoints, or production services.
