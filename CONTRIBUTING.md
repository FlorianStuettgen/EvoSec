# Contributing

SOC_Replay accepts improvements that strengthen its defensive, evidence-first, and simulation-only boundary.

## Development environment

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Run the complete local quality gate before publishing a change:

```bash
ruff check src tests tools
mypy
python -m compileall -q src tests tools
coverage run -m unittest discover -s tests -v
coverage report
python tools/verify_repository.py
python -m pip wheel . --no-deps -w dist
```

## Engineering standard

A code change should include:

1. A clearly stated operating problem and invariant.
2. Tests for success, failure, and boundary behavior.
3. No hidden network calls, command execution, or live-response side effects.
4. Deterministic output, or a documented reason determinism is impossible.
5. Documentation updates when a public contract or non-claim changes.
6. An implementation-state update when a capability moves between planned, prototype, evidenced, and implemented.

## Scenario standard

A scenario contribution requires:

- synthetic or properly sanitized `events.jsonl`;
- a precise authorization boundary;
- inspectable rule conditions;
- machine-readable expectations;
- a simulation-only response;
- regenerated JSON, Markdown, and manifest reference artifacts; and
- tests when it introduces new operators or correlation semantics.

Run `soc-replay verify <scenario-directory>` before publishing a scenario. Include negative controls where they materially test false-positive behavior.

## Adapter standard

An adapter must:

- operate only on stored synthetic or sanitized input;
- document its supported vendor record types and skipped-record behavior;
- validate every emitted record through the public event model;
- expose deterministic output and supported/skipped counts;
- write output atomically;
- include byte-for-byte input and output fixtures; and
- remain separate from live collection, credentials, and sensor permissions.

## Evidence-bundle standard

Reference scenarios must commit `report.json`, `report.md`, and `manifest.json`. Regenerate them intentionally and run:

```bash
soc-replay verify-bundle <bundle-directory>
python tools/check_reference_reports.py
```

The manifest is tamper-evident, not a digital signature. Do not describe it as proof of authorship, trusted time, or external chain of custody.

## Documentation and wiki

The versioned files under `docs/` are canonical. Concise GitHub Wiki copy is maintained under `docs/wiki/`; changes to either narrative must preserve the same maturity labels, evidence classes, safety boundaries, and non-claims.

Never publish credentials, keys, real personal data, sensitive management addresses, or production incident records.