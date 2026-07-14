# Reference evidence

This directory contains a checked-in evidence bundle for the maintained [`network-scan`](../scenarios/network-scan) scenario.

Start with the human-readable [`report.md`](network-scan/report.md), then inspect [`report.json`](network-scan/report.json) and [`manifest.json`](network-scan/manifest.json).

Reproduce and verify it from the repository root:

```bash
python -m pip install -e .
soc-replay verify-bundle reference/network-scan --source scenarios/network-scan
```

Expected result:

```text
bundle verification: PASS (... checks, 0 failed)
```

The bundle is committed as a review surface, not as an external attestation. Its hashes establish internal integrity, and source-bound verification establishes exact reproduction from the supplied scenario under the installed engine. Neither proves authorship, trusted time, external custody, or production telemetry origin.
