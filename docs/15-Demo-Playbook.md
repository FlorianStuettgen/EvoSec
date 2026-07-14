# 15 — Demo Playbook

This walkthrough is designed for a technical reviewer with five minutes.

## Minute 0–1: establish the thesis

Open the checked-in [`reference/network-scan/report.md`](../reference/network-scan/report.md) before discussing architecture. Show the PASS decision summary, exact evidence events, rule trace, execution ledger, and simulated response. Then use the README relationship diagram to explain that the physical lab provides context and stored telemetry while the Python package remains an offline evidence engine.

## Minute 1–2: inspect the wiring

```bash
soc-replay doctor
soc-replay graph --format mermaid
soc-replay explain scenarios/network-scan
```

Show the contract versions, five stages, execution invariants, frozen adapter registry, complete plan fingerprint, composite candidate selectors, authorization boundary, and exact expected detection.

## Minute 2–3: execute and verify

```bash
soc-replay verify-bundle reference/network-scan --source scenarios/network-scan
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan --source scenarios/network-scan
```

Highlight that the committed reference bundle reproduces byte for byte before generating a fresh copy. Then show the PASS verdict, exact evidence-event IDs, rule execution trace, candidate intersection, distinct-port threshold, plan fingerprint, ledger root, bundle ID, and simulation-only response.

## Minute 3–4: prove optimization correctness

```bash
python tools/verify_index_equivalence.py
```

Explain that every rule is executed twice over the same immutable events: once through the composite index and once through the unoptimized full-scan reference path. Semantic detections and execution traces must agree exactly after optimization-only metadata is removed.

## Minute 4–5: prove contracts, reproducibility, and boundaries

```bash
python tools/validate_contracts.py
python tools/verify_deterministic_bundles.py
python tools/verify_reproducible_wheel.py
```

Explain that real instances are checked against Draft 2020-12 schemas, scenario bundles are generated twice and compared byte for byte, and package construction is repeated under fixed build inputs.

Close with the boundaries:

- runtime state is deeply immutable;
- the rule language is deliberately small and inspectable;
- hashes provide internal integrity, not authorship or trusted time;
- benchmarks are environment-bound and remain outside deterministic bundle identity;
- live collection and infrastructure control remain outside the package; and
- the next meaningful proof is a measured physical experiment with containment and recovery evidence.

## Adapter, benchmark, and negative-control extension

```bash
soc-replay normalize --adapter suricata-eve \
  examples/adapters/suricata-eve.jsonl \
  build/suricata-normalized.jsonl
python tools/benchmark_scenarios.py --copies 100 --iterations 15 --warmups 3
soc-replay verify scenarios/benign-privileged-change
```

Use these commands to demonstrate the frozen offline adapter boundary, deterministic workload benchmarking with embedded equivalence proof, and a preserved zero-detection rule trace.
