# 14 — Implementation State

This register is the controlling statement for capability maturity.

| Capability | State | Evidence |
| --- | --- | --- |
| Physical rack and enterprise hardware | Installed / documented | Photographs and hardware inventory |
| Segmented trust-zone architecture | Documented design | Network and firewall-policy records |
| SELKS/Suricata analysis node | Installed / documented | Platform photographs and telemetry documentation |
| Strict event and scenario contracts | Implemented | Runtime validators, JSON Schemas, tests |
| Compiled rule execution plans | Implemented | `compiler.py`, plan fingerprints, tests |
| Immutable candidate indexing | Implemented | `indexing.py`, equivalence and strategy tests |
| Single-event and window correlation | Implemented | `correlation.py`, positive and repeated-window controls |
| Exact expectation verification | Implemented | `verification.py`, scenario regression contracts |
| Deterministic execution ledger | Implemented | `ledger.py`, corruption tests, ledger schema |
| Verifiable report bundles | Implemented | JSON/Markdown/manifest artifacts and offline verification |
| Offline Suricata normalization | Implemented | Adapter registry, fixture comparison, output digest |
| Live sensor collection | Not implemented | Deliberately outside the deterministic package |
| Autonomous containment | Not claimed | Response mode is validation-locked to `simulated` |
| Signed external attestation | Roadmap | Hashes do not prove authorship or trusted time |
| Complete measured physical experiment | Highest-value next proof | Experiment template exists; published measured record pending |
