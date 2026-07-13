from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

from ._version import __version__
from .io import LoadedScenario, load_scenario
from .models import (
    Condition,
    Detection,
    Event,
    Rule,
    Scenario,
    VerificationCheck,
    VerificationResult,
)


def _compare(actual: Any, condition: Condition) -> bool:
    operator = condition.operator
    expected = condition.value
    if operator == "exists":
        should_exist = True if expected is None else expected
        return (actual is not None) is should_exist
    if operator == "eq":
        return bool(actual == expected)
    if operator == "ne":
        return bool(actual != expected)
    if operator == "in":
        return actual in expected
    if operator == "not_in":
        return actual not in expected
    if operator == "contains":
        if isinstance(actual, (str, list, tuple, set, dict)):
            return expected in actual
        return False
    if operator == "gte":
        try:
            return bool(actual >= expected)
        except TypeError:
            return False
    if operator == "lte":
        try:
            return bool(actual <= expected)
        except TypeError:
            return False
    return False


def _matches(event: Event, rule: Rule) -> bool:
    return all(_compare(event.value(condition.field), condition) for condition in rule.conditions)


def _group_key(event: Event, fields: tuple[str, ...]) -> tuple[Any, ...]:
    return tuple(event.value(field) for field in fields)


def _window_qualifies(rule: Rule, window: list[Event]) -> bool:
    assert rule.aggregate is not None
    aggregate = rule.aggregate
    if len(window) < aggregate.count_gte:
        return False
    if aggregate.distinct_field is not None and aggregate.distinct_gte is not None:
        distinct = {item.value(aggregate.distinct_field) for item in window}
        return len(distinct) >= aggregate.distinct_gte
    return True


def _build_detection(rule: Rule, window: list[Event], group: dict[str, Any], index: int) -> Detection:
    assert rule.aggregate is not None
    aggregate = rule.aggregate
    correlation: dict[str, Any] = {
        "type": "time_window",
        "event_count": len(window),
        "threshold": aggregate.count_gte,
        "within_seconds": aggregate.within_seconds,
        "window_policy": aggregate.window_policy,
    }
    if aggregate.distinct_field is not None and aggregate.distinct_gte is not None:
        correlation["distinct_field"] = aggregate.distinct_field
        correlation["distinct_count"] = len({item.value(aggregate.distinct_field) for item in window})
        correlation["distinct_threshold"] = aggregate.distinct_gte
    return Detection(
        detection_id=f"{rule.rule_id}:{index:03d}",
        rule_id=rule.rule_id,
        rule_name=rule.name,
        rule_description=rule.description,
        severity=rule.severity,
        first_seen=window[0].timestamp,
        last_seen=window[-1].timestamp,
        event_ids=tuple(item.event_id for item in window),
        group=group,
        response=rule.response,
        correlation=correlation,
    )


def _aggregate_detections(rule: Rule, events: list[Event]) -> list[Detection]:
    assert rule.aggregate is not None
    aggregate = rule.aggregate
    groups: dict[tuple[Any, ...], list[Event]] = defaultdict(list)
    for event in events:
        groups[_group_key(event, aggregate.group_by)].append(event)

    detections: list[Detection] = []
    for key, grouped_events in sorted(groups.items(), key=lambda item: repr(item[0])):
        start = 0
        end = 0
        while end < len(grouped_events):
            event = grouped_events[end]
            while start <= end and event.timestamp - grouped_events[start].timestamp > timedelta(
                seconds=aggregate.within_seconds
            ):
                start += 1
            window = grouped_events[start : end + 1]
            if _window_qualifies(rule, window):
                group = {field: value for field, value in zip(aggregate.group_by, key, strict=True)}
                detections.append(_build_detection(rule, window, group, len(detections) + 1))
                if aggregate.window_policy == "first_per_group":
                    break
                start = end + 1
            end += 1
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
            rule_description=rule.description,
            severity=rule.severity,
            first_seen=event.timestamp,
            last_seen=event.timestamp,
            event_ids=(event.event_id,),
            group={},
            response=rule.response,
            correlation={"type": "single_event", "event_count": 1},
        )
        for index, event in enumerate(matched, start=1)
    ]


def verify_result(scenario: Scenario, detections: tuple[Detection, ...]) -> VerificationResult:
    expected = scenario.expectations
    actual_rule_ids = sorted(detection.rule_id for detection in detections)
    actual_severity_counts = dict(sorted(Counter(detection.severity for detection in detections).items()))
    expected_severity_counts = dict(sorted(expected.severity_counts.items()))
    checks = (
        VerificationCheck(
            name="detection_count",
            expected=expected.detection_count,
            actual=len(detections),
            passed=len(detections) == expected.detection_count,
        ),
        VerificationCheck(
            name="rule_ids",
            expected=sorted(expected.rule_ids),
            actual=actual_rule_ids,
            passed=actual_rule_ids == sorted(expected.rule_ids),
        ),
        VerificationCheck(
            name="severity_counts",
            expected=expected_severity_counts,
            actual=actual_severity_counts,
            passed=actual_severity_counts == expected_severity_counts,
        ),
        VerificationCheck(
            name="simulated_action_count",
            expected=expected.simulated_action_count,
            actual=len(detections),
            passed=len(detections) == expected.simulated_action_count,
        ),
    )
    return VerificationResult(passed=all(check.passed for check in checks), checks=checks)


@dataclass(frozen=True)
class ReplayResult:
    loaded: LoadedScenario
    detections: tuple[Detection, ...]
    verification: VerificationResult

    @property
    def scenario(self) -> Scenario:
        return self.loaded.scenario

    @property
    def events(self) -> tuple[Event, ...]:
        return self.loaded.events

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
            "report_schema_version": "1.0",
            "engine": {"name": "soc-replay", "version": __version__},
            "provenance": {
                "run_id": self.loaded.run_id,
                "scenario_sha256": self.loaded.scenario_sha256,
                "events_sha256": self.loaded.events_sha256,
            },
            "scenario": {
                "schema_version": self.scenario.schema_version,
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
                "verification_passed": self.verification.passed,
            },
            "verification": self.verification.to_dict(),
            "detections": [detection.to_dict() for detection in self.detections],
            "simulated_actions": list(self.simulated_actions),
        }


def run_scenario(directory: str | Path) -> ReplayResult:
    loaded = load_scenario(directory)
    detections: list[Detection] = []
    for rule in loaded.scenario.rules:
        detections.extend(evaluate_rule(rule, loaded.events))
    detections.sort(key=lambda item: (item.first_seen, item.rule_id, item.detection_id))
    frozen_detections = tuple(detections)
    return ReplayResult(
        loaded=loaded,
        detections=frozen_detections,
        verification=verify_result(loaded.scenario, frozen_detections),
    )
