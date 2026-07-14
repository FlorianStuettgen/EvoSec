# 26 — Performance Methodology

## Principle

Deterministic evidence and elapsed-time measurement have different trust properties. SOC_Replay keeps benchmark data outside the replay report, execution ledger, and bundle identity.

## Deterministic workload

The benchmark expands a validated scenario by cloning each immutable event a configured number of times. Every clone receives:

- a deterministic event ID suffix; and
- a deterministic timestamp offset.

The workload ID commits to source hashes, plan fingerprint, copy count, spacing, and all expanded event IDs.

## Measurements

For each rule, the benchmark records:

- event-index construction time;
- indexed evaluation time;
- full-scan evaluation time;
- candidate counts and reduction ratio;
- median measured speedup; and
- an indexed/full-scan semantic-equivalence proof.

Timing summaries contain minimum, median, and maximum nanoseconds over configured iterations after configured warmups.

## Interpretation

Benchmark results are meaningful only with their recorded environment and workload identity. Shared CI runners are appropriate for smoke execution and regression visibility, not stable latency thresholds.

A speedup below one does not imply incorrect behavior. Small workloads can cost more to index than to scan. Candidate reduction and semantic equivalence remain separately observable.

## Non-claims

The benchmark is not a production capacity model, distributed-stream benchmark, sensor-ingestion test, or service-level objective. It measures this in-memory replay implementation under the recorded interpreter and host environment.
