from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Any

from .compiler import CompiledRule
from .indexing import CandidateSet
from .models import Detection, Event


def _group_key(rule: CompiledRule, event: Event) -> tuple[Any, ...]:
    aggregate = rule.aggregate
    if aggregate is None:
        return ()
    return tuple(accessor(event) for accessor in aggregate.group_accessors)


def _window_qualifies(rule: CompiledRule, window: list[Event]) -> bool:
    aggregate = rule.aggregate
    if aggregate is None:
        return False
    source = aggregate.source
    if len(window) < source.count_gte:
        return False
    if aggregate.distinct_accessor is not None and source.distinct_gte is not None:
        distinct = {aggregate.distinct_accessor(event) for event in window}
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
                "distinct_count": len({aggregate.distinct_accessor(event) for event in window}),
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


def evaluate_compiled_rule(rule: CompiledRule, candidates: CandidateSet) -> tuple[Detection, ...]:
    matched = [event for event in candidates.events if rule.matches(event)]
    if rule.aggregate is None:
        return tuple(
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

    aggregate = rule.aggregate
    groups: dict[tuple[Any, ...], list[Event]] = defaultdict(list)
    for event in matched:
        groups[_group_key(rule, event)].append(event)

    detections: list[Detection] = []
    for key, events in sorted(groups.items(), key=lambda item: repr(item[0])):
        start = 0
        end = 0
        while end < len(events):
            current = events[end]
            while start <= end and current.timestamp - events[start].timestamp > timedelta(
                seconds=aggregate.source.within_seconds
            ):
                start += 1
            window = events[start : end + 1]
            if _window_qualifies(rule, window):
                group = {field: value for field, value in zip(aggregate.source.group_by, key, strict=True)}
                detections.append(_build_detection(rule, window, group, len(detections) + 1, candidates, len(matched)))
                if aggregate.source.window_policy == "first_per_group":
                    break
                start = end + 1
            end += 1
    return tuple(detections)
