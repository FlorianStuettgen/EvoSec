# 13 — Experiment lifecycle

SOC_Replay experiments may be synthetic replays, physical lab exercises or paired tests that use both.

## 1. Define

- State the defensive question.
- Set the authorization and safety boundary.
- Identify affected trust zones and recovery path.
- Describe the expected result.

## 2. Establish initial state

- Record topology and relevant configuration version.
- Confirm OOB access.
- Capture snapshot or configuration backup where appropriate.
- Identify sensors and expected telemetry.

## 3. Execute bounded input

Use only authorized lab activity, synthetic events or sanitized records. Keep the input narrow enough that the result can be attributed and repeated.

## 4. Collect evidence

Preserve source timestamps, event IDs, sensor identity, topology context and any configuration change records.

## 5. Detect and decide

Document the rule, analyst interpretation or automation logic that led to the decision. Distinguish proposed, dry-run, manually applied and automated responses.

## 6. Validate

Confirm whether the intended containment or configuration result occurred and whether unrelated zones remained healthy.

## 7. Recover

Return the environment to a known state using snapshots, configuration rollback or OOB access. Record the recovery result.

## 8. Replay, when useful

Normalize sanitized evidence and run the repository utility:

```bash
soc-replay validate scenarios/<name>
soc-replay run scenarios/<name> --output build/<name>
```

Synthetic replay and physical validation are different evidence classes. A replay result cannot prove live sensor coverage or network containment by itself.

## 9. Publish

A portfolio-ready experiment record includes objective, boundary, topology, evidence, decision, response, validation, recovery, limitations and next test.
