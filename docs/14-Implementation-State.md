# 14 — Implementation State

This register is the controlling statement for capability maturity.

| Capability | State | Evidence |
| --- | --- | --- |
| Physical rack and enterprise hardware | Installed / documented | Photographs and hardware inventory |
| Segmented trust-zone architecture | Documented design | Network and firewall-policy records |
| SELKS/Suricata analysis node | Installed / documented | Platform photographs and telemetry documentation |
| Strict event and scenario contracts | Implemented | Runtime validators, JSON Schemas, contract-validation tool |
| Deeply immutable runtime state | Implemented | Recursive freeze boundary and mutation tests |
| Complete rule fingerprints | Implemented | Output-sensitive compiler tests |
| Composite candidate indexing | Implemented | Selector-intersection implementation and equivalence tests |
| Single-event and window correlation | Implemented | Positive and repeated-window controls |
| Per-rule execution traces | Implemented | Report traces including zero-detection rules |
| Exact detection contracts | Implemented | Maintained schema 1.1 scenarios and verification tests |
| Strict deterministic execution ledger | Implemented | Typed stage contract, hash chain, corruption tests |
| Verifiable report bundles | Implemented | JSON/Markdown/manifest artifacts and offline verification |
| Real schema-instance validation | Implemented | Draft 2020-12 validation of maintained inputs and generated outputs |
| Offline Suricata normalization | Implemented | Frozen registry, fixture validation, output digest |
| Live sensor collection | Not implemented | Deliberately outside the deterministic package |
| Autonomous containment | Not claimed | Response mode is validation-locked to `simulated` |
| Signed external attestation | Roadmap | Hashes do not prove authorship or trusted time |
| Complete measured physical experiment | Highest-value next proof | Experiment template exists; published measured record pending |
