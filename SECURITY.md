# Security policy

SOC_Replay is intentionally limited to synthetic or sanitized telemetry and simulated response recommendations.

## Supported scope

- Scenario parsing and validation
- Deterministic rule evaluation
- Evidence report generation
- Documentation and sample data

## Out of scope

- Live firewall, switch, hypervisor, identity-provider, or endpoint control
- Offensive payloads or exploit automation
- Credential collection
- Production incident response

## Reporting a vulnerability

Do not include secrets, production telemetry, credentials, or sensitive infrastructure details in a public issue. Contact the maintainer privately through the profile contact channel and include a minimal reproduction using synthetic data.


## Evidence integrity boundary

`manifest.json` detects modification of the two report artifacts relative to recorded SHA-256 hashes and byte counts. It is not a signature and does not prove authorship, trusted time, or chain of custody. Do not represent bundle verification as external attestation.

## Adapter input

Treat vendor telemetry as untrusted input. Public adapter fixtures must be synthetic or sanitized and must not contain credentials, personal data, live public addresses, sensitive management addresses, or production incident content.
