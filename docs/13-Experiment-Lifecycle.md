# 13 — Experiment Lifecycle

SOC_Replay treats each featured experiment as a small auditable data product.

## 1. Define

Record the defensive question, authorization boundary, initial state, expected result, and explicit non-goals.

## 2. Prepare

Create synthetic or sanitized events, inspectable rules, and machine-readable expectations. Confirm that no credential, live public address, sensitive incident record, or unauthorized target is present.

## 3. Validate

```bash
soc-replay validate scenarios/<name>
soc-replay explain scenarios/<name>
```

Validation establishes contract correctness and an input-derived run ID.

## 4. Replay

```bash
soc-replay run scenarios/<name> --output build/<name>
```

The replay produces ordered detections, evidence-event references, correlation metadata, and simulated analyst recommendations.

## 5. Verify

Expectation verification answers whether the experiment still produces the declared detection count, rule IDs, severity distribution, and action count. A mismatch is a regression, not a cosmetic difference.

## 6. Preserve

Publish the scenario, sanitized event file, JSON report, Markdown report, engine version, input hashes, limitations, and interpretation.

## 7. Challenge

Review false-positive conditions, omitted telemetry, alternative interpretations, threshold sensitivity, and whether the result transfers to the physical lab. Synthetic success never proves production effectiveness.

## Evidence hierarchy

1. Photograph: a component was physically present.
2. Configuration: a policy or intended state was declared.
3. Telemetry: a system produced observable behavior.
4. Replay report: a rule produced a reproducible interpretation of stored evidence.
5. Measured lab experiment: the physical platform exhibited the documented end-to-end behavior.

Higher levels do not erase the limitations of lower ones; they answer different questions.
