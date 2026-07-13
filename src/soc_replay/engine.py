from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

from .io import load_scenario
from .models import Condition, Detection, Event, Rule, Scenario


def _compare(actual: Any, condition: Condition) -> bool:
    operator = condition.operator
    expected = condition.value
    if operator == "exists":
        return actual is not None
    if operator == "eq":
        return actual == expected
    if operator == "ne":
        return actual != expected
    if operator == "in":
        return isinstance(expected, list) and actual in expected
    if operator == "contains":
        return actual is not None and expected in actual
    if operator == "gte":
        try:
            return actual >= expected
        except TypeError:
            return False
    if operator == "lte":
        try:
            return actual <= expected
        except TypeError:
            return False
    return False


def _matches(event: Event, rule: Rule) -> bool:
    return all(_compare(event.value(condition.field), condition) for condition in rule.conditions)


def _group_key(event: Event, fields: tuple[str, ...]) -> tuple[Any, ...]:
    return tuple(event.value(field) for field in fields)


def _aggregate_detections(rule: Rule, events: list[Event]) -> list[Detection]:
    assert rule.aggregate is not None
    aggregate = rule.aggregate
    groups: dict[tuple[Any, ...], list[Event]] = defaultdict(list)
    for event in events:
        groups[_group_key(event, aggregate.group_by)].append(event)

    detections: list[Detection] = []
    for key, grouped_events in sorted(groups.items(), key=lambda item: repr(item[0])):
        start = 0
        for end, event in enumerate(grouped_events):
            while event.timestamp - grouped_events[start].timestamp > timedelta(seconds=aggregate.within_seconds):
                start += 1
            window = grouped_events[start : end + 1]
            if len(window) < aggregate.count_gte:
                continue
            if aggregate.distinct_field is not None and aggregate.distinct_gte is not None:
                distinct = {item.value(aggregate.distinct_field) for item in window}
                if len(distinct) < aggregate.distinct_gte:
                    continue
            group = {field: value for field, value in zip(aggregate.group_by, key)}
            detection_id = f"{rule.rule_id}:{len(detections) + 1:03d}"
            detections.append(
                Detection(
                    detection_id=detection_id,
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    first_seen=window[0].timestamp,
                    last_seen=window[-1].timestamp,
                    event_ids=tuple(item.event_id for item in window),
                    group=group,
                    response=rule.response,
                )
            )
            break
    return detections


def evaluate_rule(rule: Rule, events: Iterable[Event]) -> list[Detection]:
    matched = [event for event in events if _matches(event, rule)]
    if rule.aggregate is not None:
        return _aggregate_detections(rule, matched)
    return [
        Detection(
            detection_id=f"{rule.rule_id}:{index:03d}",
            rule_id=rule.rule_id,
            rule_name=rule.name,
            severity=rule.severity,
            first_seen=event.timestamp,
            last_seen=event.timestamp,
            event_ids=(event.event_id,),
            group={},
            response=rule.response,
        )
        for index, event in enumerate(matched, start=1)
    ]


@dataclass(frozen=True)
class ReplayResult:
    scenario: Scenario
    events: tuple[Event, ...]
    detections: tuple[Detection, ...]

    @property
    def simulated_actions(self) -> tuple[dict[str, str], ...]:
        return tuple(
            {
                "detection_id": detection.detection_id,
                "action": detection.response.action,
                "description": detection.response.description,
                "mode": detection.response.mode,
            }
            for detection in self.detections
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": {
                "id": self.scenario.scenario_id,
                "title": self.scenario.title,
                "objective": self.scenario.objective,
                "authorization_boundary": self.scenario.authorization_boundary,
                "expected_outcome": self.scenario.expected_outcome,
            },
            "summary": {
                "events_processed": len(self.events),
                "detections": len(self.detections),
                "simulated_actions": len(self.simulated_actions),
            },
            "detections": [detection.to_dict() for detection in self.detections],
            "simulated_actions": list(self.simulated_actions),
        }


def run_scenario(directory: str | Path) -> ReplayResult:
    scenario, events = load_scenario(directory)
    detections: list[Detection] = []
    for rule in scenario.rules:
        detections.extend(evaluate_rule(rule, events))
    detections.sort(key=lambda item: (item.first_seen, item.rule_id, item.detection_id))
    return ReplayResult(scenario=scenario, events=tuple(events), detections=tuple(detections))
