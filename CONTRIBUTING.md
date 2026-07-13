# Contributing

SOC_Replay accepts improvements that strengthen its defensive, evidence-first, and simulation-only boundary.

## Development environment

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Run the same quality gate used by CI:

```bash
ruff check src tests tools
mypy
python -m compileall -q src tests tools
coverage run -m unittest discover -s tests -v
coverage report
python tools/verify_repository.py
python -m build
```

## Engineering standard

A code change should include:

1. A clearly stated operating problem and invariant.
2. Tests for success, failure, and boundary behavior.
3. No hidden I/O, network calls, or live-response side effects.
4. Deterministic output or a documented reason that determinism is impossible.
5. Documentation updates when the public contract changes.
6. An implementation-state update when a capability moves between planned, prototype, evidenced, and implemented.

## Scenario standard

A scenario contribution requires:

- synthetic or properly sanitized `events.jsonl`;
- a precise authorization boundary;
- inspectable rule conditions;
- machine-readable expectations;
- a simulation-only response;
- a regenerated JSON and Markdown reference report; and
- tests when it introduces new operators or correlation semantics.

Run `soc-replay verify <scenario-directory>` before submitting a scenario. Never include credentials, keys, real personal data, sensitive management addresses, or production incident records.

## Documentation and wiki

The versioned files under `docs/` are canonical. Concise GitHub Wiki copy is maintained under `docs/wiki/`; changes to either narrative must preserve the same maturity labels and non-claims.
