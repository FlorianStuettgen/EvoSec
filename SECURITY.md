# Security policy

SOC_Replay is a public record of a private lab. Reports should focus on repository-code vulnerabilities or accidental disclosure risks.

Do not open a public issue containing:

- credentials, keys or session material;
- public or management addresses tied to the live lab;
- device serial numbers;
- private configuration exports;
- sensitive incident data; or
- recovery procedures that expose secrets.

The firewall-policy library is sanitized reference material. Placeholder values must remain placeholders, and every example requires environment-specific validation.

The replay package processes local JSON/JSONL and writes local reports. It contains no live-response or remote-command path.
