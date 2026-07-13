# Contributing

SOC_Replay accepts improvements that preserve its defensive and simulation-only boundary.

## Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Contribution standard

A change should include:

1. A clear operating problem.
2. Synthetic or sanitized evidence only.
3. Tests for new parsing, matching, aggregation, or reporting behaviour.
4. Documentation of limitations and non-claims.
5. No live-response integrations in the core package.

Scenario contributions should include `scenario.json`, `events.jsonl`, an expected outcome, and no real credentials or identifying data.


## Adapter standard

An adapter must operate on stored sanitized input, document its supported vendor record types, validate emitted records through the public event model, expose skipped-record counts, use deterministic output, and include a byte-for-byte reference fixture. Live collection connectors do not belong in the core package.

## Evidence-bundle standard

Reference scenarios must commit `report.json`, `report.md`, and `manifest.json`. Regenerate them intentionally and run `soc-replay verify-bundle` plus `python tools/check_reference_reports.py` before committing.
