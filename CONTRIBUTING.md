# Contributing

SOC_Replay accepts changes that strengthen its defensive, deterministic, and simulation-only boundary.

## Local gate

```bash
python -m pip install -e ".[dev]"
ruff check src tests tools
mypy
python -m compileall -q src tests tools
coverage run -m unittest discover -s tests -v
coverage report
soc-replay doctor
python tools/verify_deterministic_bundles.py
python tools/verify_repository.py
python -m pip wheel . --no-deps -w dist
```

## Engineering standard

A change should include:

1. A clearly stated invariant or operating problem.
2. Tests for successful, boundary, and failure behavior.
3. Deterministic output or a documented reason determinism is impossible.
4. No hidden socket, subprocess, credential, or live-response path.
5. Schema and documentation updates when public contracts change.
6. Deterministic bundle-generation checks whenever result bytes or contracts change.

## Scenario standard

Scenarios require synthetic or properly sanitized telemetry, an authorization boundary, exact expectations, inspectable rules, and a simulation-only response. CI must generate the JSON/Markdown/manifest bundle twice, verify both copies, and compare them byte for byte.

## Adapter standard

Adapters must operate on stored sanitized input, declare supported record types, validate all emitted events through the public model, expose skipped counts and output hashes, write atomically, and include conformance fixtures.

## Evidence language

Use precise terms:

- a hash provides integrity evidence;
- a signature may provide authorship evidence;
- a trusted timestamp may provide time evidence;
- none of these alone proves end-to-end physical behavior.
