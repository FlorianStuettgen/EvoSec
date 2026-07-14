# Benchmark policy

SOC_Replay benchmarks are regression evidence, not universal throughput claims.

## Purpose

The benchmark suite exists to detect material performance drift in deterministic scenario loading, rule evaluation, evidence generation, indexing, and verification. It does not predict production SOC capacity, live ingestion latency, infrastructure sizing, or vendor-platform performance.

## Controlled inputs

A benchmark result is interpretable only when it records:

- repository commit;
- Python version;
- operating system and architecture;
- scenario identifier and schema version;
- scenario copy count;
- warm-up and measured iteration counts;
- indexed or full-scan execution mode;
- generated evidence size;
- wall-clock measurement method.

Public benchmark fixtures must remain synthetic and schema-valid.

## Regression thresholds

Pull-request CI runs a small benchmark as a smoke test. It proves that the benchmark path works and emits valid evidence. It is not a stable hardware baseline because hosted runner capacity varies.

A release comparison should use the same machine or a controlled runner and compare the candidate against the previous release. Investigate when the median duration or peak memory increases materially without an explained increase in work performed.

A regression must not be hidden by reducing fixture size, iteration count, verification depth, or output evidence. Any intentional benchmark-contract change belongs in the changelog.

## Correctness before speed

Performance changes must preserve:

- exact scenario-contract verification;
- indexed and full-scan equivalence;
- deterministic evidence bytes;
- source-bound bundle verification;
- schema validity;
- complete rule traces and execution ledger entries.

An optimization that weakens evidence or changes verdict semantics is a contract change, not a benchmark improvement.

## Publication

Published results should include raw JSON evidence and the complete command. Avoid single-number marketing claims. Report the tested boundary and known sources of variance.