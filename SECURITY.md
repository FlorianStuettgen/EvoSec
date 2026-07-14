# Security policy

SOC_Replay is intentionally limited to stored synthetic or sanitized telemetry and simulated response recommendations. The runtime package has no live sensor, credential, command-execution, or infrastructure-control authority.

## Supported scope

- Scenario and event parsing
- Deterministic rule evaluation
- Evidence report and manifest generation
- Standalone and source-bound bundle verification
- Offline normalization of stored telemetry fixtures
- Documentation, schemas, and sample data

## Out of scope

- Live firewall, switch, hypervisor, identity-provider, or endpoint control
- Traffic generation, offensive payloads, or exploit automation
- Credential collection or secret handling
- Production incident response
- Claims of authorship, trusted time, or chain of custody from unsigned bundles

## Reporting a vulnerability

Do not include secrets, production telemetry, credentials, personal data, or sensitive infrastructure details in a public issue. Contact the maintainer privately through the profile contact channel and include the smallest possible reproduction using synthetic data.

A useful report includes:

1. the affected version or commit;
2. the command or API path used;
3. synthetic input required to reproduce the issue;
4. the observed and expected result; and
5. whether the issue crosses the simulation-only boundary.

## Evidence verification modes

`manifest.json` records hashes and byte counts for `report.json` and `report.md` and commits to execution identities.

- **Standalone verification** recomputes internal identities and checks agreement among the report, plan, rule traces, detections, simulated actions, execution ledger, manifest, hashes, and byte counts.
- **Source-bound verification** additionally reruns a supplied scenario directory and requires all three generated bundle artifacts to reproduce exactly under the installed engine.

Neither mode is a signature, trusted timestamp, external custody record, hardware identity proof, or proof that telemetry originated from a live production system. A party able to rewrite both a bundle and its alleged source can create a new consistent evidence set.

## Malformed evidence handling

Bundle and ledger inputs are untrusted. JSON-valid but structurally invalid values must produce a controlled failed verdict or `ValidationError`; they must not cause raw runtime exceptions. Regression tests cover malformed scalar types, rehashed contradictions, and source-bound mismatches.

## Adapter input

Treat vendor telemetry as untrusted input. Public fixtures must be synthetic or sanitized and must not contain credentials, personal data, live public addresses, sensitive management addresses, production incident content, or private inventory identifiers.
