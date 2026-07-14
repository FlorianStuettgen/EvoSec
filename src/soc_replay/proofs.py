from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._version import __version__
from .compiler import CompiledRule, compile_scenario
from .contracts import ENGINE_NAME, PROOF_SCHEMA_VERSION
from .correlation import RuleExecution, evaluate_compiled_rule
from .indexing import CandidateSet, EventIndex
from .io import LoadedScenario, load_scenario
from .models import Detection, Event
from .serialization import digest_object

_OPTIMIZATION_ONLY_CORRELATION_FIELDS = frozenset({"candidate_strategy", "candidate_events"})


def _semantic_detection(detection: Detection) -> dict[str, Any]:
    """Return the behaviorally meaningful detection view.

    Candidate strategy and candidate count describe optimization choices. They are
    intentionally excluded so indexed and full-scan execution can be compared on
    detection semantics rather than implementation mechanics.
    """

    payload = detection.to_dict()
    correlation = dict(payload.get("correlation", {}))
    for field in _OPTIMIZATION_ONLY_CORRELATION_FIELDS:
        correlation.pop(field, None)
    payload["correlation"] = correlation
    return payload


def _semantic_trace(execution: RuleExecution) -> dict[str, int]:
    return {
        "matched_count": execution.matched_count,
        "group_count": execution.group_count,
        "windows_considered": execution.windows_considered,
        "detection_count": execution.detection_count,
    }


@dataclass(frozen=True, slots=True)
class RuleEquivalenceProof:
    rule_id: str
    rule_fingerprint: str
    indexed_strategy: str
    indexed_candidate_count: int
    full_scan_candidate_count: int
    semantic_digest: str
    passed: bool
    failures: tuple[str, ...]

    @property
    def candidate_reduction(self) -> int:
        return self.full_scan_candidate_count - self.indexed_candidate_count

    @property
    def candidate_reduction_ratio(self) -> float:
        if self.full_scan_candidate_count == 0:
            return 0.0
        return self.candidate_reduction / self.full_scan_candidate_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_fingerprint": self.rule_fingerprint,
            "indexed_strategy": self.indexed_strategy,
            "indexed_candidate_count": self.indexed_candidate_count,
            "full_scan_candidate_count": self.full_scan_candidate_count,
            "candidate_reduction": self.candidate_reduction,
            "candidate_reduction_ratio": self.candidate_reduction_ratio,
            "semantic_digest": self.semantic_digest,
            "passed": self.passed,
            "failures": list(self.failures),
        }


@dataclass(frozen=True, slots=True)
class IndexEquivalenceProof:
    scenario_id: str
    run_id: str
    plan_fingerprint: str
    event_count: int
    rules: tuple[RuleEquivalenceProof, ...]

    @property
    def passed(self) -> bool:
        return all(rule.passed for rule in self.rules)

    @property
    def proof_id(self) -> str:
        return digest_object(self._identity_payload())

    @property
    def indexed_candidate_count(self) -> int:
        return sum(rule.indexed_candidate_count for rule in self.rules)

    @property
    def full_scan_candidate_count(self) -> int:
        return sum(rule.full_scan_candidate_count for rule in self.rules)

    @property
    def candidate_reduction(self) -> int:
        return self.full_scan_candidate_count - self.indexed_candidate_count

    def _identity_payload(self) -> dict[str, Any]:
        return {
            "proof_schema_version": PROOF_SCHEMA_VERSION,
            "engine": {"name": ENGINE_NAME, "version": __version__},
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "plan_fingerprint": self.plan_fingerprint,
            "event_count": self.event_count,
            "rules": [rule.to_dict() for rule in self.rules],
            "passed": self.passed,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._identity_payload(),
            "proof_id": self.proof_id,
            "indexed_candidate_count": self.indexed_candidate_count,
            "full_scan_candidate_count": self.full_scan_candidate_count,
            "candidate_reduction": self.candidate_reduction,
        }


def prove_rule_equivalence(
    rule: CompiledRule,
    events: tuple[Event, ...],
    *,
    event_index: EventIndex | None = None,
) -> RuleEquivalenceProof:
    index = event_index or EventIndex(events)
    indexed_candidates = index.candidates(rule)
    indexed_execution = evaluate_compiled_rule(rule, indexed_candidates)
    full_scan_execution = evaluate_compiled_rule(rule, CandidateSet(events, "full_scan"))

    indexed_detections = [_semantic_detection(detection) for detection in indexed_execution.detections]
    full_scan_detections = [_semantic_detection(detection) for detection in full_scan_execution.detections]
    indexed_trace = _semantic_trace(indexed_execution)
    full_scan_trace = _semantic_trace(full_scan_execution)

    failures: list[str] = []
    if indexed_detections != full_scan_detections:
        failures.append("semantic detection output differs")
    if indexed_trace != full_scan_trace:
        failures.append("semantic execution trace differs")

    semantic_digest = digest_object(
        {
            "rule_fingerprint": rule.fingerprint,
            "trace": indexed_trace,
            "detections": indexed_detections,
        }
    )
    return RuleEquivalenceProof(
        rule_id=rule.source.rule_id,
        rule_fingerprint=rule.fingerprint,
        indexed_strategy=indexed_candidates.strategy,
        indexed_candidate_count=len(indexed_candidates.events),
        full_scan_candidate_count=len(events),
        semantic_digest=semantic_digest,
        passed=not failures,
        failures=tuple(failures),
    )


def prove_loaded_scenario(loaded: LoadedScenario) -> IndexEquivalenceProof:
    plan = compile_scenario(loaded.scenario)
    event_index = EventIndex(loaded.events)
    rules = tuple(
        prove_rule_equivalence(rule, loaded.events, event_index=event_index)
        for rule in plan.rules
    )
    return IndexEquivalenceProof(
        scenario_id=loaded.scenario.scenario_id,
        run_id=loaded.run_id,
        plan_fingerprint=plan.fingerprint,
        event_count=len(loaded.events),
        rules=rules,
    )


def prove_index_equivalence(directory: str | Path) -> IndexEquivalenceProof:
    return prove_loaded_scenario(load_scenario(directory))
