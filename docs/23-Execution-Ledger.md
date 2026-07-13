# 23 — Execution Ledger

## What it is

The execution ledger is a deterministic hash chain over the five pipeline stages. It records internal execution identity without introducing timestamps, machine names, or performance measurements that would break reproducibility.

## Entry contract

Each entry contains:

```json
{
  "sequence": 3,
  "stage": "index",
  "status": "ok",
  "input_digest": "...",
  "output_digest": "...",
  "records_in": 7,
  "records_out": 7,
  "metadata": {"index_fields": ["category", "action", "outcome"]},
  "previous_hash": "...",
  "entry_hash": "..."
}
```

`entry_hash` is the SHA-256 digest of the canonical entry body excluding `entry_hash`. `previous_hash` links the entry to the prior stage. The first entry links to a 64-character zero genesis hash.

## Root identity

The final verification entry hash becomes the ledger root. The root is embedded in:

- `report.json`;
- `report.md`; and
- `manifest.json`.

Bundle verification recalculates every entry, checks the chain, confirms the root, and cross-checks it with the manifest.

## What it proves

The ledger detects internal report modification and inconsistent stage records relative to the recorded hashes.

## What it does not prove

It does not establish:

- authorship;
- trusted time;
- external custody;
- hardware identity; or
- that the source telemetry came from a live production system.

Those require a separate signing or attestation layer.
