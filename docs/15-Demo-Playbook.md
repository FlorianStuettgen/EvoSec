# 15 — Demo Playbook

This walkthrough is designed for a technical reviewer with five minutes.

## Minute 0–1: establish the thesis

Open the README and explain that SOC_Replay joins a real segmented lab with a contract-validated evidence engine. Point out the evidence hierarchy: installation, policy, telemetry, deterministic replay, and measured physical experiment.

## Minute 1–2: inspect the wiring

```bash
soc-replay doctor
soc-replay graph --format mermaid
soc-replay explain scenarios/network-scan
```

Show the contract versions, five stages, execution invariants, frozen adapter registry, complete plan fingerprint, composite candidate selectors, authorization boundary, and exact expected detection.

## Minute 2–3: execute and verify

```bash
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan
```

Highlight the PASS verdict, exact evidence-event IDs, rule execution trace, candidate intersection, distinct-port threshold, plan fingerprint, ledger root, bundle ID, and simulation-only response.

## Minute 3–4: prove contract validity and reproducibility

```bash
python tools/validate_contracts.py
python tools/verify_deterministic_bundles.py
```

Explain that real repository and generated instances are checked against Draft 2020-12 schemas, then every scenario is generated twice and compared byte for byte.

## Minute 4–5: discuss boundaries and trade-offs

- Runtime state is deeply immutable.
- The rule language is deliberately small and inspectable.
- Composite indexes improve cost but cannot change truth conditions.
- Every rule leaves a trace, even when it does not fire.
- Hashes provide internal integrity, not authorship or trusted time.
- Live collection and infrastructure control remain outside the package.
- The next meaningful proof is a measured physical experiment with containment and recovery evidence.

## Adapter and negative-control extension

```bash
soc-replay normalize --adapter suricata-eve \
  examples/adapters/suricata-eve.jsonl \
  build/suricata-normalized.jsonl
soc-replay verify scenarios/benign-privileged-change
```

Use these commands to demonstrate the frozen offline adapter boundary and a preserved zero-detection rule trace.
