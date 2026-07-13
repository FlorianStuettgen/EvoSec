# 14 — Implementation State

This register is the controlling statement for capability maturity.

| Capability | State | Public evidence | Next proof required |
| --- | --- | --- | --- |
| Physical rack and core components | Installed / documented | Photographs and inventory | Periodic configuration baseline |
| Qubes OS compute role | Documented operating role | Architecture and stack docs | Sanitized domain map and recovery exercise |
| Proxmox service/storage role | Documented operating role | Architecture and stack docs | Sanitized workload inventory and restore evidence |
| VLAN and trust-zone model | Documented design | Topology and policy references | Sanitized switch/firewall exports plus measured path tests |
| SELKS/Suricata SOC node | Installed / documented | Photographs and monitoring documentation | Named scenario tied to source alerts and packet evidence |
| Centralized dashboards | Partially evidenced | Captures and integration narrative | Source-to-dashboard lineage for a named experiment |
| Replay engine | Implemented | Source, tests, schemas, CLI, and reference reports | Broader adapters and benchmark history |
| Expected-outcome verification | Implemented | Scenario contracts and CI | Additional negative and sensitivity scenarios |
| Input provenance | Implemented | SHA-256 hashes and deterministic run IDs | Optional signed report envelope |
| Live response integrations | Not part of replay package | Explicit safety boundary | Separate adapter design, approvals, rollback, and isolated validation |
| SaltStack/LLM-assisted orchestration | Prototype/design track | Architecture documentation | Named implementation, inputs, outputs, metrics, and failure tests |
| Autonomous containment | Not generally claimed | Non-claim and simulation-only package | Human approval model, measured response, rollback proof, and bounded scope |
| Predictive maintenance | Roadmap | Roadmap only | Data source, target variable, baseline, and validation plan |

A capability moves only when evidence changes. Marketing language, diagrams, or intended architecture do not change its state.

## Evidence-plane additions

| Capability | State | Evidence |
| --- | --- | --- |
| Suricata EVE alert/flow normalization | Implemented | Adapter source, sanitized fixtures, tests, reference output |
| Manifest-backed report bundles | Implemented | Bundle schema, tamper tests, `verify-bundle` CLI |
| Negative-control scenarios | Implemented | Approved privileged-maintenance scenario with zero detections |
| Signed attestations | Not implemented | External signing remains a documented future boundary |
