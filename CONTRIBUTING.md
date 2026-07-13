# Contributing

SOC_Replay accepts improvements to both the physical-platform record and the evidence replay utility.

## Platform documentation changes

- Preserve the distinction between installed hardware, documented roles, prototypes and roadmap items.
- Link claims to photographs, sanitized configuration, measured telemetry or experiment records.
- Never publish credentials, keys, serial numbers, recovery secrets or sensitive management addresses.
- Update `docs/14-Implementation-State.md` when capability maturity changes.

## Replay utility changes

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Code changes should include tests and preserve the simulation-only response boundary.

## Scenario contributions

A scenario requires a clear defensive objective, authorization boundary, synthetic or sanitized events, expected outcome, inspectable rule, generated report and limitations.

## Infrastructure references

Firewall, playbook and script examples must use placeholders and must be reviewed against the actual device/firmware before application.
