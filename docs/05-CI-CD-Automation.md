# 05 — CI/CD and automation

SOC_Replay contains three different forms of automation. They must not be collapsed into one claim.

## 1. Repository CI — implemented

GitHub Actions compiles and tests the Python replay utility on Python 3.11, 3.12 and 3.13. It validates the included scenarios and generates evidence reports as workflow artifacts.

```text
push / pull request
        ↓
install package
        ↓
compile + unit tests
        ↓
validate scenarios
        ↓
generate replay reports
```

## 2. Infrastructure automation — documented/prototype

The platform architecture describes configuration management for:

- VM/container provisioning;
- package and service state;
- lab service deployment;
- configuration backup;
- snapshot/rollback coordination;
- VLAN or policy changes; and
- decoy workload activation.

SaltStack is the primary documented orchestration direction. The restored Ansible/playbook and helper-script directories contain conceptual contribution guidance rather than executable production automation.

## 3. Event-driven response — evidence required

A telemetry event may lead to a proposed containment action, but the implementation state must be explicit:

| Mode | Meaning |
| --- | --- |
| Manual | Analyst reviews evidence and changes the platform directly |
| Assisted | Software proposes a change; a human approves execution |
| Dry run | Adapter renders the intended change without applying it |
| Automated | A governed adapter applies the change and records validation/rollback evidence |

No mode should be inferred from a diagram alone.

## Safe automation contract

Any future live adapter should include:

- least-privilege credentials stored outside Git;
- target allow-lists;
- dry-run output;
- idempotent operations;
- pre-change snapshot/config backup;
- structured audit records;
- post-change health checks;
- automatic or operator-triggered rollback; and
- an OOB recovery procedure.

## Replay engine relationship

The replay engine can test whether stored telemetry would trigger a rule and simulated recommendation. It intentionally cannot execute the recommendation. This makes it useful for validating logic before any adapter is considered.
