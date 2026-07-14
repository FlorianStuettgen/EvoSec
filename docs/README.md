# SOC_Replay documentation

The version-controlled documentation is the canonical technical record. Wiki material is a convenience surface and must not contradict implementation state, contract versions, security boundaries, or measured evidence.

## Start by goal

| Goal | Recommended path |
| --- | --- |
| Evaluate the project in five minutes | [Implementation State](14-Implementation-State.md) → [Engineering Review](16-Engineering-Review.md) → [Threat Model](21-Threat-Model.md) |
| Run the maintained demonstration | [Demo Playbook](15-Demo-Playbook.md) → [Scenario Format](12-Scenario-Format.md) → [Experiment Lifecycle](13-Experiment-Lifecycle.md) |
| Understand evidence integrity | [Evidence Bundles](18-Evidence-Bundles.md) → [Execution Ledger](23-Execution-Ledger.md) → [Contract Validation](24-Contract-Validation.md) |
| Review correctness and performance | [Differential Correctness](25-Differential-Correctness.md) → [Performance Methodology](26-Performance-Methodology.md) → [Reproducible Builds](27-Reproducible-Builds.md) |
| Understand the physical lab | [Architecture](01-Architecture.md) → [Hardware](02-Hardware.md) → [Network Topology](04-Network-Topology.md) → [Monitoring and Telemetry](06-Monitoring-Telemetry.md) |
| Extend the engine | [Replay Engine](11-Replay-Engine.md) → [Execution Core](22-Execution-Core.md) → [Architecture Decisions](17-Architecture-Decisions.md) → [Contributing](../CONTRIBUTING.md) |

## System and platform

- [01 — Architecture](01-Architecture.md)
- [02 — Hardware](02-Hardware.md)
- [03 — Software Stack](03-Software-Stack.md)
- [04 — Network Topology](04-Network-Topology.md)
- [06 — Monitoring and Telemetry](06-Monitoring-Telemetry.md)
- [07 — Security Model](07-Security-Model.md)

## Evidence engine

- [11 — Replay Engine](11-Replay-Engine.md)
- [12 — Scenario Format](12-Scenario-Format.md)
- [13 — Experiment Lifecycle](13-Experiment-Lifecycle.md)
- [18 — Evidence Bundles](18-Evidence-Bundles.md)
- [19 — Suricata Adapter](19-Suricata-Adapter.md)
- [22 — Execution Core](22-Execution-Core.md)
- [23 — Execution Ledger](23-Execution-Ledger.md)
- [24 — Contract Validation](24-Contract-Validation.md)
- [25 — Differential Correctness](25-Differential-Correctness.md)
- [26 — Performance Methodology](26-Performance-Methodology.md)
- [27 — Reproducible Builds](27-Reproducible-Builds.md)

## Governance and review

- [14 — Implementation State](14-Implementation-State.md)
- [15 — Demo Playbook](15-Demo-Playbook.md)
- [16 — Engineering Review](16-Engineering-Review.md)
- [17 — Architecture Decisions](17-Architecture-Decisions.md)
- [20 — Measured Experiment Record](20-Experiment-Record.md)
- [21 — Threat Model](21-Threat-Model.md)

## Documentation rules

1. [Implementation State](14-Implementation-State.md) controls capability maturity.
2. Deterministic replay evidence does not prove live physical behavior.
3. Standalone bundle verification proves internal consistency; source-bound verification proves reproduction from the supplied scenario under the installed engine.
4. Hashes are not signatures, and timestamps are not trusted merely because they appear in a report.
5. Historical wiki language must be corrected here before it is treated as a current project claim.
