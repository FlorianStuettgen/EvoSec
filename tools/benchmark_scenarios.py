from __future__ import annotations

import argparse
import json
import platform
import sys
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import timedelta
from functools import partial
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from soc_replay import __version__
from soc_replay.compiler import CompiledRule, compile_scenario
from soc_replay.contracts import BENCHMARK_SCHEMA_VERSION, ENGINE_NAME
from soc_replay.correlation import evaluate_compiled_rule
from soc_replay.indexing import CandidateSet, EventIndex
from soc_replay.io import atomic_write_text, load_scenario
from soc_replay.models import Event
from soc_replay.proofs import RuleEquivalenceProof, prove_rule_equivalence
from soc_replay.serialization import digest_object, pretty_json

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    copies: int = 100
    iterations: int = 15
    warmups: int = 3
    spacing_seconds: int = 86_400

    def __post_init__(self) -> None:
        if self.copies < 1:
            raise ValueError("copies must be positive")
        if self.iterations < 1:
            raise ValueError("iterations must be positive")
        if self.warmups < 0:
            raise ValueError("warmups must be non-negative")
        if self.spacing_seconds < 1:
            raise ValueError("spacing_seconds must be positive")

    def to_dict(self) -> dict[str, int]:
        return {
            "copies": self.copies,
            "iterations": self.iterations,
            "warmups": self.warmups,
            "spacing_seconds": self.spacing_seconds,
        }


@dataclass(frozen=True, slots=True)
class TimingSummary:
    minimum_ns: int
    median_ns: int
    maximum_ns: int

    @classmethod
    def from_samples(cls, samples: tuple[int, ...]) -> TimingSummary:
        if not samples:
            raise ValueError("timing samples must not be empty")
        return cls(min(samples), int(median(samples)), max(samples))

    def to_dict(self) -> dict[str, int]:
        return {
            "minimum_ns": self.minimum_ns,
            "median_ns": self.median_ns,
            "maximum_ns": self.maximum_ns,
        }


def expand_events(
    events: tuple[Event, ...],
    *,
    copies: int,
    spacing_seconds: int,
) -> tuple[Event, ...]:
    if copies < 1:
        raise ValueError("copies must be positive")
    if spacing_seconds < 1:
        raise ValueError("spacing_seconds must be positive")
    expanded: list[Event] = []
    for copy_index in range(copies):
        offset = timedelta(seconds=copy_index * spacing_seconds)
        for event in events:
            expanded.append(
                replace(
                    event,
                    event_id=f"{event.event_id}@{copy_index:05d}",
                    timestamp=event.timestamp + offset,
                )
            )
    expanded.sort(key=lambda event: (event.timestamp, event.event_id))
    return tuple(expanded)


def _measure(operation: Callable[[], object], *, iterations: int, warmups: int) -> TimingSummary:
    for _ in range(warmups):
        operation()
    samples: list[int] = []
    for _ in range(iterations):
        started = perf_counter_ns()
        operation()
        samples.append(perf_counter_ns() - started)
    return TimingSummary.from_samples(tuple(samples))


def _evaluate_indexed(rule: CompiledRule, event_index: EventIndex) -> object:
    return evaluate_compiled_rule(rule, event_index.candidates(rule))


def _evaluate_full_scan(rule: CompiledRule, events: tuple[Event, ...]) -> object:
    return evaluate_compiled_rule(rule, CandidateSet(events, "full_scan"))


def _rule_result(
    rule: CompiledRule,
    events: tuple[Event, ...],
    event_index: EventIndex,
    config: BenchmarkConfig,
    index_build: TimingSummary,
) -> dict[str, Any]:
    candidates = event_index.candidates(rule)
    proof: RuleEquivalenceProof = prove_rule_equivalence(rule, events, event_index=event_index)
    indexed = _measure(
        partial(_evaluate_indexed, rule, event_index),
        iterations=config.iterations,
        warmups=config.warmups,
    )
    full_scan = _measure(
        partial(_evaluate_full_scan, rule, events),
        iterations=config.iterations,
        warmups=config.warmups,
    )
    speedup = 0.0 if indexed.median_ns == 0 else full_scan.median_ns / indexed.median_ns
    return {
        "rule_id": rule.source.rule_id,
        "rule_fingerprint": rule.fingerprint,
        "indexed_strategy": candidates.strategy,
        "indexed_candidate_count": len(candidates.events),
        "full_scan_candidate_count": len(events),
        "candidate_reduction_ratio": proof.candidate_reduction_ratio,
        "median_speedup": speedup,
        "timings": {
            "index_build": index_build.to_dict(),
            "indexed_evaluation": indexed.to_dict(),
            "full_scan_evaluation": full_scan.to_dict(),
        },
        "semantic_proof": proof.to_dict(),
    }


def benchmark_scenario(directory: Path, config: BenchmarkConfig) -> dict[str, Any]:
    loaded = load_scenario(directory)
    plan = compile_scenario(loaded.scenario)
    events = expand_events(
        loaded.events,
        copies=config.copies,
        spacing_seconds=config.spacing_seconds,
    )
    event_index = EventIndex(events)
    index_build = _measure(
        partial(EventIndex, events),
        iterations=config.iterations,
        warmups=config.warmups,
    )
    rules = tuple(_rule_result(rule, events, event_index, config, index_build) for rule in plan.rules)
    workload_id = digest_object(
        {
            "scenario_sha256": loaded.scenario_sha256,
            "events_sha256": loaded.events_sha256,
            "plan_fingerprint": plan.fingerprint,
            "copies": config.copies,
            "spacing_seconds": config.spacing_seconds,
            "expanded_event_ids": [event.event_id for event in events],
        }
    )
    identity = {
        "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": __version__},
        "scenario_id": loaded.scenario.scenario_id,
        "run_id": loaded.run_id,
        "plan_fingerprint": plan.fingerprint,
        "workload_id": workload_id,
        "config": config.to_dict(),
        "semantic_proofs": [rule["semantic_proof"] for rule in rules],
    }
    return {
        "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": __version__},
        "benchmark_id": digest_object(identity),
        "scenario_id": loaded.scenario.scenario_id,
        "run_id": loaded.run_id,
        "plan_fingerprint": plan.fingerprint,
        "source_event_count": len(loaded.events),
        "expanded_event_count": len(events),
        "workload_id": workload_id,
        "config": config.to_dict(),
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine() or "unknown",
            "processor": platform.processor() or "unknown",
            "executable": sys.executable,
        },
        "passed": all(bool(rule["semantic_proof"]["passed"]) for rule in rules),
        "rules": list(rules),
    }


def _scenario_directories(root: Path) -> tuple[Path, ...]:
    return tuple(sorted(path.parent for path in root.glob("*/scenario.json")))


def _validate_result(result: dict[str, Any]) -> None:
    schema_path = ROOT / "schemas" / "benchmark-result.schema.json"
    proof_schema_path = ROOT / "schemas" / "index-equivalence-proof.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    proof_schema = json.loads(proof_schema_path.read_text(encoding="utf-8"))
    registry = Registry().with_resources(
        [
            (str(schema["$id"]), Resource.from_contents(schema)),
            (str(proof_schema["$id"]), Resource.from_contents(proof_schema)),
        ]
    )
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(result), key=lambda error: list(error.absolute_path))
    if errors:
        rendered = "; ".join(error.message for error in errors)
        raise ValueError(f"benchmark result failed schema validation: {rendered}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark indexed and full-scan execution on deterministic expanded workloads."
    )
    parser.add_argument("--root", default=str(ROOT / "scenarios"))
    parser.add_argument("--output", default=str(ROOT / "build" / "benchmarks"))
    parser.add_argument("--copies", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=15)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--spacing-seconds", type=int, default=86_400)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scenarios = _scenario_directories(Path(args.root))
    if not scenarios:
        print("ERROR: no scenarios found")
        return 2
    config = BenchmarkConfig(
        copies=args.copies,
        iterations=args.iterations,
        warmups=args.warmups,
        spacing_seconds=args.spacing_seconds,
    )
    output = Path(args.output)
    results = tuple(benchmark_scenario(directory, config) for directory in scenarios)
    for result in results:
        _validate_result(result)
        destination = output / f"{result['scenario_id']}.json"
        atomic_write_text(destination, pretty_json(result))
        verdict = "PASS" if result["passed"] else "FAIL"
        print(
            f"{verdict} {result['scenario_id']}: events={result['expanded_event_count']} "
            f"benchmark={result['benchmark_id']} output={destination}"
        )
        for rule in result["rules"]:
            print(
                f"  {rule['rule_id']}: candidates={rule['indexed_candidate_count']}/"
                f"{rule['full_scan_candidate_count']} median-speedup={rule['median_speedup']:.2f}x"
            )
    return 0 if all(bool(result["passed"]) for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
