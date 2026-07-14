# Contributing

SOC_Replay accepts changes that strengthen its defensive, deterministic, proof-oriented, contract-complete, and simulation-only boundary.

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
python tools/verify_index_equivalence.py
python tools/verify_deterministic_bundles.py
python tools/verify_repository.py
python tools/verify_reproducible_wheel.py
python tools/benchmark_scenarios.py --copies 4 --iterations 2 --warmups 1
```

## Engineering standard

A change should include:

1. A clearly stated invariant or operating problem.
2. Tests for successful, boundary, corruption, and failure behavior.
3. Deterministic output or a documented reason determinism is impossible.
4. Deep immutability for data crossing a completed pipeline stage.
5. No hidden socket, subprocess, credential, collection, or live-response path in the runtime package.
6. Schema, runtime, verifier, and documentation updates when a public contract changes.
7. Fingerprint changes whenever behavior or report-visible rule meaning changes.
8. Differential comparison with the full-scan reference path when candidate selection changes.
9. Deterministic bundle-generation checks whenever result bytes or contracts change.
10. A reproducible-build check when package construction changes.

## Scenario standard

Maintained scenarios use schema `1.1` and require synthetic or properly sanitized telemetry, a precise authorization boundary, inspectable rules, aggregate semantics where applicable, and exact expected detections.

Schema `1.0` remains readable for compatibility, but it is not accepted as a maintained catalog standard.

## Indexing standard

Candidate selectors are performance hints, not detection semantics. Any change to compiler selector extraction, event indexes, or candidate intersections must pass `tools/verify_index_equivalence.py` and include a test that would fail under semantic drift.

## Benchmark standard

Benchmark workloads must be deterministic and identified by a workload hash. Timing results must remain outside replay ledgers and report-bundle identities. Do not add shared-runner latency thresholds without a controlled and documented environment.

## Adapter standard

Adapters must operate on stored sanitized input, declare supported record types, validate every emitted event through the public model and schema, expose skipped counts and output hashes, write atomically, and include conformance fixtures. The global registry is frozen after startup.

## Evidence language

Use precise terms:

- a hash provides integrity evidence;
- a differential proof provides equivalence evidence relative to its reference implementation and tested inputs;
- a reproducible build provides source-to-artifact repeatability under a defined toolchain;
- a benchmark provides environment-bound performance measurements;
- a signature may provide authorship evidence;
- a trusted timestamp may provide time evidence;
- none of these alone proves end-to-end physical behavior.
