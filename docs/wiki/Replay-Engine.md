# Replay Engine

SOC_Replay evaluates stored normalized events with a small declarative rule language. It supports field conditions, nested `details.*` paths, grouping, thresholds, distinct-value requirements, and explicit window policies.

Each scenario declares exact expectations. The engine emits deterministic JSON and Markdown reports plus a manifest containing artifact hashes and byte counts.

```bash
soc-replay run scenarios/network-scan --output build/network-scan
soc-replay verify-bundle build/network-scan
```

Responses are data with `mode: simulated`; the package has no device-control connector.
