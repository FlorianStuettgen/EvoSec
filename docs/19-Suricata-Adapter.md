# 19 — Sanitized Suricata EVE Adapter

## Purpose

The adapter bridges stored Suricata EVE JSONL and the normalized SOC_Replay event contract without introducing a live sensor dependency into the core engine.

```bash
soc-replay normalize-suricata input/eve.jsonl output/events.jsonl
```

## Supported records

The current adapter supports:

- `alert` records, normalized as `network_alert`; and
- `flow` records, normalized as `network_connection`.

Other EVE record types are counted as skipped. The CLI reports total records read, written, and skipped so unsupported data is visible rather than silently implied to be covered.

## Mapping principles

- EVE timestamps are normalized to canonical UTC.
- Source and destination IPs and destination ports pass through the public event validator.
- Alert signatures and flow counters remain in `details`.
- Output event IDs are deterministic for the same input ordering.
- Alert actions are represented as evidence; no response is executed.
- Writes use atomic replacement.

## Example

- Sanitized input: [`examples/adapters/suricata-eve.jsonl`](../examples/adapters/suricata-eve.jsonl)
- Expected output: [`examples/adapters/suricata-normalized.jsonl`](../examples/adapters/suricata-normalized.jsonl)

CI regenerates the normalized output and compares it byte for byte with the committed reference.

## Boundary

This adapter does not connect to SELKS, read a live socket, manage capture permissions, or claim complete Suricata schema coverage. Live collection belongs in a separately reviewed ingestion boundary.
