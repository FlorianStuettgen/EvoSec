# 20 — Measured Experiment Record

## Purpose

Synthetic replay proves deterministic rule behavior. A physical-lab claim requires a measured experiment that connects generation, enforcement, sensing, decision, containment, and recovery evidence.

Use [`templates/experiment-record.md`](../templates/experiment-record.md) as the required structure for a publishable experiment.

## Minimum evidence

A complete record should contain:

1. the decision question;
2. authorization and abort conditions;
3. initial topology and configuration references;
4. sensor and clock-health evidence;
5. controlled trigger description;
6. expected observations by layer;
7. a measured event timeline;
8. detection and decision outcomes;
9. containment and rollback results;
10. a sanitized SOC_Replay bundle; and
11. explicit limitations and residual risk.

## Evidence classes

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Photograph | Physical installation | Correct configuration or behavior |
| Configuration snapshot | Intended state | Runtime enforcement |
| Dashboard capture | Visibility at one moment | Repeatability or causation |
| Replay bundle | Deterministic rule behavior for stored inputs | Live sensor completeness |
| Measured experiment | End-to-end behavior under named conditions | Universal production performance |

## Publication rule

Do not publish a result as end-to-end platform evidence unless the record contains the initial state, exact boundary, timestamps, evidence references, rollback result, and limitations.
