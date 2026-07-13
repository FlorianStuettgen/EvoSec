# 18 — Evidence Bundles

## Purpose

A replay result is delivered as a three-file bundle:

```text
output-directory/
├── report.json
├── report.md
└── manifest.json
```

`report.json` is the machine contract. `report.md` is the human review surface. `manifest.json` records the SHA-256 digest and byte count of both artifacts and repeats the engine, input-provenance, run-ID, and verification fields required to detect internal inconsistency.

## Write ordering

The two reports are written atomically first. The manifest is written last. A present manifest therefore represents a completed local bundle rather than an in-progress report pair.

## Verification

```bash
soc-replay verify-bundle build/network-scan
```

Verification checks:

- manifest schema version;
- engine name and version consistency;
- run ID consistency;
- scenario and event hash consistency;
- scenario-verification verdict consistency;
- exact artifact names;
- artifact byte counts; and
- artifact SHA-256 hashes.

A modified or missing report causes a failed bundle verdict and a non-zero CLI exit code.

## Security meaning

The manifest is tamper-evident, not a digital signature. Anyone able to replace every bundle file can create a new internally consistent manifest. Authorship, trusted timestamps, and legal chain of custody require an external signing or attestation system.

## Machine contract

The manifest schema is [`schemas/bundle-manifest.schema.json`](../schemas/bundle-manifest.schema.json). Committed examples live beside each reference report under [`examples/reports/`](../examples/reports/).
