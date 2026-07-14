from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from .compiler import CompiledRule
from .indexing import CandidateSet
from .models import Detection, Event
from .serialization import canonical_json


@dataclass(frozen=True, slots=True)
class RuleExecution:
    rule_id: str
    rule_fingerprint: str
    candidate_strategy: str
    candidate_count: int
    matched_count: int
    group_count: int
    windows_considered: int
    detections: tuple[Detection, ...]

    @property
    def detection_count(self) -> int:
        return len(self.detections)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_fingerprint": self.rule_fingerprint,
            "candidate_strategy": self.candidate_strategy,
            "candidate_count": self.candidate_count,
            "matched_count": self.matched_count,
            "group_count": self.group_count,
            "windows_considered": self.windows_considered,
            "detection_count": self.detection_count,
        }


def _group_values(rule: CompiledRule, event: Event) -> tuple[Any, ...]:
    aggregate = rule.aggregate
    if aggregate is None:
        return ()
    return tuple(accessor(event) for accessor in aggregate.group_accessors)


def _group_key(values: tuple[Any, ...]) -> tuple[str, ...]:
    return tuple(canonical_json(value) for value in values)


def _window_qualifies(rule: CompiledRule, window: list[Event]) -> bool:
    aggregate = rule.aggregate
    if aggregate is None:
        return False
    source = aggregate.source
    if len(window) < source.count_gte:
        return False
    if aggregate.distinct_accessor is not None and source.distinct_gte is not None:
        distinct = {canonical_json(aggregate.distinct_accessor(event)) for event in window}
        return len(distinct) >= source.distinct_gte
    return True


def _build_detection(
    rule: CompiledRule,
    window: list[Event],
    group: dict[str, Any],
    index: int,
    candidate_set: CandidateSet,
    matched_count: int,
) -> Detection:
    aggregate = rule.aggregate
    if aggregate is None:
        raise RuntimeError("aggregate detection requires a compiled aggregate")
    source = aggregate.source
    correlation: dict[str, Any] = {
        "type": "time_window",
        "event_count": len(window),
        "threshold": source.count_gte,
        "within_seconds": source.within_seconds,
        "window_policy": source.window_policy,
        "candidate_strategy": candidate_set.strategy,
        "candidate_events": len(candidate_set.events),
        "matched_events": matched_count,
        "rule_fingerprint": rule.fingerprint,
    }
    if aggregate.distinct_accessor is not None and source.distinct_gte is not None:
        correlation.update(
            {
                "distinct_field": source.distinct_field,
                "distinct_count": len(
                    {canonical_json(aggregate.distinct_accessor(event)) for event in window}
                ),
                "distinct_threshold": source.distinct_gte,
            }
        )
    return Detection(
        detection_id=f"{rule.source.rule_id}:{index:03d}",
        rule_id=rule.source.rule_id,
        rule_name=rule.source.name,
        rule_description=rule.source.description,
        severity=rule.source.severity,
        first_seen=window[0].timestamp,
        last_seen=window[-1].timestamp,
        event_ids=tuple(event.event_id for event in window),
        group=group,
        response=rule.source.response,
        correlation=correlation,
    )


def evaluate_compiled_rule(rule: CompiledRule, candidates: CandidateSet) -> RuleExecution:
    matched = [event for event in candidates.events if rule.matches(event)]
    if rule.aggregate is None:
        single_detections = tuple(
            Detection(
                detection_id=f"{rule.source.rule_id}:{index:03d}",
                rule_id=rule.source.rule_id,
                rule_name=rule.source.name,
                rule_description=rule.source.description,
                severity=rule.source.severity,
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                event_ids=(event.event_id,),
                group={},
                response=rule.source.response,
                correlation={
                    "type": "single_event",
                    "event_count": 1,
                    "candidate_strategy": candidates.strategy,
                    "candidate_events": len(candidates.events),
                    "matched_events": len(matched),
                    "rule_fingerprint": rule.fingerprint,
                },
            )
            for index, event in enumerate(matched, start=1)
        )
        return RuleExecution(
            rule_id=rule.source.rule_id,
            rule_fingerprint=rule.fingerprint,
            candidate_strategy=candidates.strategy,
            candidate_count=len(candidates.events),
            matched_count=len(matched),
            group_count=0,
            windows_considered=len(matched),
            detections=single_detections,
        )

    aggregate = rule.aggregate
    groups: dict[tuple[str, ...], tuple[tuple[Any, ...], list[Event]]] = {}
    for event in matched:
        raw_values = _group_values(rule, event)
        key = _group_key(raw_values)
        if key not in groups:
            groups[key] = (raw_values, [])
        groups[key][1].append(event)

    detections: list[Detection] = []
    windows_considered = 0
    for key in sorted(groups):
        raw_values, events = groups[key]
        start = 0
        end = 0
        while end < len(events):
            current = events[end]
            while start <= end and current.timestamp - events[start].timestamp > timedelta(
                seconds=aggregate.source.within_seconds
            ):
                start += 1
            window = events[start : end + 1]
            windows_considered += 1
            if _window_qualifies(rule, window):
                group = {
                    field: value
                    for field, value in zip(aggregate.source.group_by, raw_values, strict=True)
                }
                detections.append(
                    _build_detection(rule, window, group, len(detections) + 1, candidates, len(matched))
                )
                if aggregate.source.window_policy == "first_per_group":
                    break
                start = end + 1
            end += 1

    return RuleExecution(
        rule_id=rule.source.rule_id,
        rule_fingerprint=rule.fingerprint,
        candidate_strategy=candidates.strategy,
        candidate_count=len(candidates.events),
        matched_count=len(matched),
        group_count=len(groups),
        windows_considered=windows_considered,
        detections=tuple(detections),
    )
