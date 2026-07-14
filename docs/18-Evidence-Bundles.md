# 18 — Evidence Bundles

## Purpose

A completed replay is delivered as:

```text
output-directory/
├── report.json
├── report.md
└── manifest.json
```

`report.json` is the machine contract. `report.md` is the analyst surface. `manifest.json` commits to the artifact bytes and repeats the execution identities required to expose contradiction.

## Report contract 2.1

The report contains:

- engine and input provenance;
- compiled execution plan;
- one trace per rule;
- strict execution ledger;
- scenario context;
- summary counts;
- verification checks;
- ordered detections; and
- ordered simulated actions.

## Completion protocol

JSON and Markdown are written atomically first. The manifest is written atomically last. A manifest therefore marks a completed local bundle rather than an in-progress artifact pair.

## Offline verification

```bash
soc-replay verify-bundle build/network-scan
```

Verification checks:

- exact top-level report and manifest field sets;
- report and manifest contract versions;
- engine, run, scenario, and provenance identity;
- plan rule IDs and fingerprints against rule traces;
- rule-trace totals against detections;
- summary totals against traces, detections, actions, and verification;
- simulated actions against detection response objects;
- unique detection IDs and simulation-only modes;
- complete typed execution-ledger structure and hash chain;
- ledger stage counts against report contents;
- artifact names, byte counts, and SHA-256 hashes; and
- bundle ID derived from the canonical manifest body.

A modified, missing, partially written, structurally invalid, or internally contradictory artifact produces a failed verdict.

## Rehashed contradiction test

The test suite modifies report content, recalculates the report artifact hash, and recalculates the manifest bundle ID. Verification still fails because the report summary, traces, detections, actions, or ledger no longer agree. This demonstrates that the verifier is not merely a checksum checker.

## Reproducibility

`tools/verify_deterministic_bundles.py` executes every maintained scenario twice in isolated directories, verifies both bundles, and compares all three artifact byte streams exactly.

## Security meaning

The ledger and manifest provide tamper evidence relative to their hashes. They are not signatures and do not establish authorship, trusted time, external custody, hardware identity, or live telemetry provenance.
