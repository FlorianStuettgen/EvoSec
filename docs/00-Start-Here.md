# Start here

SOC_Replay has two connected surfaces:

```text
Segmented physical lab
  └─ produces and contextualizes stored, sanitized telemetry
       └─ SOC_Replay evidence engine
            ├─ validates exact scenario contracts
            ├─ replays detections deterministically
            ├─ compares indexed and full-scan execution
            └─ publishes verifiable evidence bundles
```

The physical platform is the research context. The Python package is an offline, simulation-only evidence engine and has no live infrastructure authority.

## Five-minute path

1. Open the checked-in [reference report](../reference/network-scan/report.md).
2. Review the [implementation state](14-Implementation-State.md).
3. Read the [engineering review](16-Engineering-Review.md).
4. Run the [demo playbook](15-Demo-Playbook.md).
5. Check the [threat model](21-Threat-Model.md) before interpreting integrity claims.

## Evidence vocabulary

- **Exact verification** means output matches the scenario's declared detection contract.
- **Standalone bundle verification** means the bundle is internally consistent.
- **Source-bound reproduction** means the supplied scenario regenerates the committed artifacts byte for byte under the installed engine.
- **Differential correctness** means indexed execution matches the full-scan reference for tested inputs.
- **Reproducible build** means clean source copies produce identical wheels under the defined toolchain.

None of these alone establishes authorship, trusted time, independent custody, or production telemetry origin.

## Documentation numbering

The numeric filenames preserve the original platform documentation series. Retired or consolidated chapters were intentionally not renumbered, so gaps such as `05` and `08–10` do not indicate missing current documentation. Use the goal-based map in [docs/README.md](README.md) rather than reading by number.
