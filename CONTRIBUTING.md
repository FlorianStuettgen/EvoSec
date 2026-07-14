# Contributing

SOC_Replay accepts changes that strengthen its defensive, deterministic, contract-complete, and simulation-only boundary.

## Local gate

```bash
python -m pip install -e ".[dev]"
ruff check src tests tools
mypy
python -m compileall -q src tests tools
coverage run -m unittest discover -s tests -v
coverage report
soc-replay doctor
python tools/validate_contracts.py
python tools/verify_deterministic_bundles.py
python tools/verify_repository.py
python -m pip wheel . --no-deps -w dist
```

## Engineering standard

A change should include:

1. A clearly stated invariant or operating problem.
2. Tests for successful, boundary, corruption, and failure behavior.
3. Deterministic output or a documented reason determinism is impossible.
4. Deep immutability for data that crosses a completed pipeline stage.
5. No hidden socket, subprocess, credential, collection, or live-response path.
6. Schema, runtime, verifier, and documentation updates when a public contract changes.
7. Fingerprint changes whenever behavior or report-visible rule meaning changes.
8. Deterministic bundle-generation checks whenever result bytes or contracts change.

## Scenario standard

Maintained scenarios use schema `1.1` and require synthetic or properly sanitized telemetry, a precise authorization boundary, inspectable rules, aggregate semantics where applicable, and exact expected detections. Exact contracts identify the rule, severity, evidence-event IDs, group values, and simulated action in order.

Schema `1.0` remains readable for compatibility, but it is not accepted as a maintained catalog standard.

## Adapter standard

Adapters must operate on stored sanitized input, declare supported record types, validate every emitted event through the public model and schema, expose skipped counts and output hashes, write atomically, and include conformance fixtures. The global registry is frozen after startup.

## Evidence language

Use precise terms:

- a hash provides integrity evidence;
- a signature may provide authorship evidence;
- a trusted timestamp may provide time evidence;
- an execution trace explains work performed but is not an external attestation;
- none of these alone proves end-to-end physical behavior.
