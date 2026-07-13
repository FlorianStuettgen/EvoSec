# 18 — Evidence Bundles

## Purpose

A completed replay is delivered as a three-file bundle:

```text
output-directory/
├── report.json
├── report.md
└── manifest.json
```

`report.json` is the machine contract. `report.md` is the analyst surface. `manifest.json` commits to both artifact byte streams and cross-checks the run ID, input hashes, execution-plan fingerprint, execution-ledger root, engine version, and verification result.

## Completion protocol

The JSON and Markdown reports are written atomically first. The manifest is written atomically last. The manifest is therefore the local completion marker for the bundle, not merely another report.

## Offline verification

```bash
soc-replay verify-bundle build/network-scan
```

Verification checks:

- report and manifest schema versions;
- engine and run identity;
- scenario and event provenance hashes;
- plan fingerprint;
- the complete execution-ledger hash chain and root;
- expectation-verification consistency;
- exact artifact names, byte counts, and SHA-256 hashes; and
- the bundle ID derived from the canonical manifest body.

A modified, missing, partially written, or internally inconsistent artifact produces a failed verdict and a non-zero CLI exit code.

## Reproducibility test

The repository does not trust stale committed report snapshots. `tools/verify_deterministic_bundles.py` runs every scenario twice in isolated directories, verifies both bundles, and compares `report.json`, `report.md`, and `manifest.json` byte for byte.

This proves deterministic generation from the current source, scenarios, schemas, and engine version.

## Security meaning

The ledger and manifest provide tamper evidence relative to their hashes. They are not digital signatures and do not establish authorship, trusted time, external custody, or that source telemetry originated from a live system.

## Machine contracts

- [`schemas/report.schema.json`](../schemas/report.schema.json)
- [`schemas/bundle-manifest.schema.json`](../schemas/bundle-manifest.schema.json)
- [`schemas/execution-ledger.schema.json`](../schemas/execution-ledger.schema.json)
