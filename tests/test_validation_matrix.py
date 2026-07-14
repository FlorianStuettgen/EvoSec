from __future__ import annotations

import unittest

from soc_replay.models import (
    Aggregate,
    Condition,
    Event,
    Expectations,
    ExpectedDetection,
    Response,
    Rule,
    Scenario,
    ValidationError,
)

BASE_EVENT = {
    "event_id": "evt",
    "timestamp": "2026-01-01T00:00:00Z",
    "source": "fixture",
    "category": "test",
    "action": "observe",
}


class ValidationMatrixTests(unittest.TestCase):
    def test_event_validation_failures(self) -> None:
        cases = [
            ({**BASE_EVENT, "timestamp": "not-a-time"}, "invalid ISO"),
            ({**BASE_EVENT, "timestamp": "2026-01-01T00:00:00"}, "timezone"),
            ({**BASE_EVENT, "destination_port": True}, "destination_port"),
            ({**BASE_EVENT, "destination_port": 70000}, "destination_port"),
            ({**BASE_EVENT, "tags": "x"}, "tags"),
            ({**BASE_EVENT, "tags": ["x", "x"]}, "unique"),
            ({**BASE_EVENT, "details": []}, "details"),
            ({**BASE_EVENT, "source_ip": 1}, "source_ip"),
            ({**BASE_EVENT, "source_ip": "not-an-ip"}, "invalid source_ip"),
            ({**BASE_EVENT, "host": ""}, "host"),
        ]
        for payload, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValidationError, message):
                Event.from_dict(payload)

    def test_condition_validation_failures(self) -> None:
        cases = [
            ([], "object"),
            ({"field": "", "operator": "eq"}, "requires a field"),
            ({"field": "category", "operator": "bad"}, "unsupported operator"),
            ({"field": "category", "operator": "in", "value": []}, "non-empty list"),
            ({"field": "category", "operator": "exists", "value": "yes"}, "true, false"),
            ({"field": "category", "operator": "gte"}, "requires a value"),
            ({"field": "missing", "operator": "eq", "value": 1}, "unknown event field"),
            ({"field": "details..x", "operator": "eq", "value": 1}, "invalid field path"),
            ({"field": "category", "operator": "eq", "value": 1, "extra": 2}, "unknown fields"),
        ]
        for payload, message in cases:
            with self.subTest(payload=payload), self.assertRaisesRegex(ValidationError, message):
                Condition.from_dict(payload)  # type: ignore[arg-type]

    def test_aggregate_validation_failures(self) -> None:
        cases = [
            ([], "object or null"),
            ({"group_by": "x", "count_gte": 1, "within_seconds": 1}, "group_by"),
            ({"group_by": ["host", "host"], "count_gte": 1, "within_seconds": 1}, "unique"),
            ({"group_by": [], "count_gte": 0, "within_seconds": 1}, "count_gte"),
            ({"group_by": [], "count_gte": 1, "within_seconds": 0}, "within_seconds"),
            ({"group_by": [], "count_gte": 1, "within_seconds": 1, "distinct_field": "host"}, "supplied together"),
            (
                {"group_by": [], "count_gte": 1, "within_seconds": 1, "distinct_field": "", "distinct_gte": 1},
                "distinct_field",
            ),
            (
                {"group_by": [], "count_gte": 1, "within_seconds": 1, "distinct_field": "host", "distinct_gte": 0},
                "distinct_gte",
            ),
            ({"group_by": [], "count_gte": 1, "within_seconds": 1, "window_policy": "bad"}, "unsupported"),
            ({"group_by": [], "count_gte": 1, "within_seconds": 1, "extra": 2}, "unknown fields"),
        ]
        for payload, message in cases:
            with self.subTest(payload=payload), self.assertRaisesRegex(ValidationError, message):
                Aggregate.from_dict(payload)  # type: ignore[arg-type]

    def test_response_rule_expectation_failures(self) -> None:
        with self.assertRaisesRegex(ValidationError, "object"):
            Response.from_dict([])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValidationError, "only permits"):
            Response.from_dict({"action": "x", "description": "x", "mode": "live"})
        with self.assertRaisesRegex(ValidationError, "unknown fields"):
            Response.from_dict({"action": "x", "description": "x", "extra": 1})
        with self.assertRaisesRegex(ValidationError, "object"):
            Rule.from_dict([])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValidationError, "unsupported severity"):
            Rule.from_dict({"id": "R", "name": "r", "severity": "bad", "match": []})
        with self.assertRaisesRegex(ValidationError, "at least one"):
            Rule.from_dict({"id": "R", "name": "r", "severity": "low", "match": []})
        with self.assertRaisesRegex(ValidationError, "non-negative"):
            Expectations.from_dict(
                {"detection_count": -1, "rule_ids": [], "severity_counts": {}, "simulated_action_count": 0}
            )
        with self.assertRaisesRegex(ValidationError, "must equal"):
            Expectations.from_dict(
                {"detection_count": 1, "rule_ids": [], "severity_counts": {"low": 1}, "simulated_action_count": 1}
            )
        with self.assertRaisesRegex(ValidationError, "must sum"):
            Expectations.from_dict(
                {"detection_count": 1, "rule_ids": ["R"], "severity_counts": {}, "simulated_action_count": 1}
            )
        with self.assertRaisesRegex(ValidationError, "expected counts"):
            Expectations.from_dict(
                {"detection_count": 1, "rule_ids": ["R"], "severity_counts": {"low": 1}, "simulated_action_count": 0}
            )

    def test_exact_detection_validation_failures(self) -> None:
        with self.assertRaisesRegex(ValidationError, "object"):
            ExpectedDetection.from_dict([])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValidationError, "unsupported severity"):
            ExpectedDetection.from_dict(
                {"rule_id": "R", "severity": "bad", "event_ids": ["e"], "group": {}, "action": "a"}
            )
        with self.assertRaisesRegex(ValidationError, "non-empty"):
            ExpectedDetection.from_dict(
                {"rule_id": "R", "severity": "low", "event_ids": [], "group": {}, "action": "a"}
            )
        with self.assertRaisesRegex(ValidationError, "rule order"):
            Expectations.from_dict(
                {
                    "detection_count": 1,
                    "rule_ids": ["R1"],
                    "severity_counts": {"low": 1},
                    "simulated_action_count": 1,
                    "detections": [
                        {"rule_id": "R2", "severity": "low", "event_ids": ["e"], "group": {}, "action": "a"}
                    ],
                }
            )

    def test_scenario_validation_failures(self) -> None:
        with self.assertRaisesRegex(ValidationError, "object"):
            Scenario.from_dict([])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValidationError, "one of"):
            Scenario.from_dict({"schema_version": "9"})
        with self.assertRaisesRegex(ValidationError, "requires at least one rule"):
            Scenario.from_dict(
                {
                    "schema_version": "1.0",
                    "id": "x",
                    "title": "x",
                    "objective": "x",
                    "authorization_boundary": "x",
                    "expected_outcome": "x",
                    "expectations": {
                        "detection_count": 0,
                        "rule_ids": [],
                        "severity_counts": {},
                        "simulated_action_count": 0,
                    },
                    "rules": [],
                }
            )
