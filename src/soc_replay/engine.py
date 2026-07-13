from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .compiler import compile_rule
from .correlation import evaluate_compiled_rule
from .indexing import EventIndex
from .models import Detection, Event, Rule, Scenario, VerificationResult
from .pipeline import PipelineConfig, ReplayPipeline
from .result import ReplayResult
from .verification import verify_result


def evaluate_rule(rule: Rule, events: Iterable[Event]) -> list[Detection]:
    frozen = tuple(sorted(events, key=lambda event: (event.timestamp, event.event_id)))
    compiled = compile_rule(rule)
    return list(evaluate_compiled_rule(compiled, EventIndex(frozen).candidates(compiled)))


def run_scenario(directory: str | Path, *, max_events: int = 1_000_000) -> ReplayResult:
    return ReplayPipeline(PipelineConfig(max_events=max_events)).run(directory)


__all__ = ["ReplayResult", "evaluate_rule", "run_scenario", "verify_result", "VerificationResult", "Scenario"]
