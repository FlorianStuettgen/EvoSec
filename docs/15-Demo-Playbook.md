# 15 — Demo Playbook

This walkthrough is designed for a technical reviewer with five minutes.

## Minute 0–1: establish the thesis

Open the README and explain that SOC_Replay joins a real segmented lab with a compiled, deterministic evidence engine. Point out the evidence hierarchy: installation, policy, telemetry, replay, and measured experiment.

## Minute 1–2: inspect the wiring

```bash
soc-replay doctor
soc-replay graph --format mermaid
soc-replay explain scenarios/network-scan
```

Show the five pipeline stages, execution invariants, adapter registry, compiled plan fingerprint, authorization boundary, rule severity, and exact expectations.

## Minute 2–3: execute and verify

```bash
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan
```

Highlight the PASS verdict, matched event IDs, candidate strategy, distinct-port threshold, plan fingerprint, ledger root, bundle ID, and simulation-only response.

## Minute 3–4: prove reproducibility

```bash
python tools/verify_deterministic_bundles.py
```

Explain that every scenario is generated twice in isolated directories. Both bundles are independently verified, then their JSON, Markdown, and manifest bytes are compared exactly. CI repeats the gate across Python 3.11–3.13.

## Minute 4–5: discuss boundaries and trade-offs

- Rules are compiled into a deliberately small inspectable language.
- Candidate indexes reduce work but cannot alter rule truth conditions.
- The execution ledger is deterministic and excludes wall-clock timing.
- Runtime dependencies are intentionally zero.
- Hashes prove internal integrity, not authorship or trusted time.
- Live collection and infrastructure control remain outside the package.
- The next meaningful proof is a measured physical experiment with source telemetry, containment validation, rollback, and recovery evidence.

## Adapter and negative-control extension

```bash
soc-replay normalize --adapter suricata-eve \
  examples/adapters/suricata-eve.jsonl \
  build/suricata-normalized.jsonl
soc-replay verify scenarios/benign-privileged-change
```

Use these commands to demonstrate a real offline telemetry-normalization boundary and an expected zero-detection control.
