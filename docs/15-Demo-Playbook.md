# 15 — Demo Playbook

This walkthrough is designed for a technical reviewer with five minutes.

## Minute 0–1: establish the thesis

Open the README and explain that SOC_Replay joins a real segmented lab with a deterministic evidence plane. Point out the evidence hierarchy: installation, policy, telemetry, replay, measured experiment.

## Minute 1–2: inspect a scenario

```bash
soc-replay explain scenarios/network-scan
```

Show the authorization boundary, rule severity, aggregate definition, expected detection count, and deterministic run ID.

## Minute 2–3: execute and verify

```bash
soc-replay run scenarios/network-scan --output build/network-scan
```

Highlight the PASS verdict, matched event IDs, distinct-port threshold, and simulation-only response.

## Minute 3–4: prove reproducibility

Run the scenario a second time and compare reports. Then run:

```bash
python tools/check_reference_reports.py
```

Explain that CI performs the same byte-level reference check across Python 3.11–3.13.

## Minute 4–5: discuss tradeoffs

- The engine favors inspectability over a large rule language.
- Runtime dependencies are intentionally zero.
- Input hashes prove identity, not authenticity.
- Physical lab integration remains separate so the replay package cannot mutate infrastructure.
- The next meaningful proof is a named physical experiment with source telemetry, timing, containment validation, and recovery evidence.
