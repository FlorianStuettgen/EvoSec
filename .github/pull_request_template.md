## What changed

Describe the scenario, contract, engine, evidence, adapter, or documentation impact.

## Defensive-use boundary

- [ ] No live response authority, credential handling, traffic generation, exploit automation, or production telemetry is added
- [ ] Fixtures are synthetic or explicitly sanitized
- [ ] Simulated actions remain recommendations or evidence records only

## Contract and evidence integrity

- [ ] Schema compatibility is preserved or explicitly versioned
- [ ] Deterministic ordering and canonical bytes are preserved
- [ ] Reference evidence is regenerated and verified
- [ ] Standalone and source-bound verification still agree
- [ ] Indexed and full-scan execution remain equivalent

## Validation

- [ ] Ruff
- [ ] mypy strict mode
- [ ] branch-aware coverage above the enforced floor
- [ ] scenario and schema verification
- [ ] deterministic bundle generation
- [ ] reproducible wheel verification
- [ ] benchmark smoke test
- [ ] CodeQL
