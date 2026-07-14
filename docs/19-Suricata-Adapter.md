# 19 — Suricata Adapter

## Boundary

The adapter consumes stored synthetic or sanitized Suricata EVE JSONL. It does not connect to a sensor, request credentials, open a socket, or alter Suricata configuration.

## Registry

The built-in `suricata-eve` adapter is registered during package initialization. The shared registry is then frozen so global adapter behavior cannot change after startup.

## Supported records

- `alert`
- `flow`

Unsupported record types are counted and skipped. A file containing no supported records fails validation.

## Command

```bash
soc-replay normalize --adapter suricata-eve \
  examples/adapters/suricata-eve.jsonl \
  build/suricata-normalized.jsonl
```

## Guarantees

- every emitted record passes through the same deeply immutable event model used by scenarios;
- output order follows input order;
- event IDs are deterministic;
- timestamps are normalized to UTC;
- writes are atomic;
- read, written, and skipped counts are returned; and
- the final output SHA-256 digest is reported.

`tools/validate_contracts.py` also validates each normalized fixture record against `event.schema.json`.
