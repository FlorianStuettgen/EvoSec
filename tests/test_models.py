from __future__ import annotations

import unittest

from soc_replay.models import Condition, Event, Scenario, ValidationError


class ModelTests(unittest.TestCase):
    def test_event_rejects_unknown_fields(self) -> None:
        payload = {
            "event_id": "x",
            "timestamp": "2026-01-01T00:00:00Z",
            "source": "fixture",
            "category": "test",
            "action": "observe",
            "unexpected": True,
        }
        with self.assertRaisesRegex(ValidationError, "unknown fields"):
            Event.from_dict(payload)

    def test_nested_details_path(self) -> None:
        event = Event.from_dict(
            {
                "event_id": "x",
                "timestamp": "2026-01-01T00:00:00Z",
                "source": "fixture",
                "category": "test",
                "action": "observe",
                "details": {"nested": {"value": 7}},
            }
        )
        self.assertEqual(event.value("details.nested.value"), 7)
        self.assertIsNone(event.value("details.missing"))

    def test_condition_rejects_nested_non_details_path(self) -> None:
        with self.assertRaisesRegex(ValidationError, "only permits nested paths"):
            Condition.from_dict({"field": "source.name", "operator": "eq", "value": "x"})

    def test_scenario_rejects_unknown_expectation_rule(self) -> None:
        with self.assertRaisesRegex(ValidationError, "unknown rule IDs"):
            Scenario.from_dict(
                {
                    "schema_version": "1.0",
                    "id": "x",
                    "title": "x",
                    "objective": "x",
                    "authorization_boundary": "x",
                    "expected_outcome": "x",
                    "expectations": {
                        "detection_count": 1,
                        "rule_ids": ["MISSING"],
                        "severity_counts": {"low": 1},
                        "simulated_action_count": 1,
                    },
                    "rules": [
                        {
                            "id": "R1",
                            "name": "rule",
                            "severity": "low",
                            "match": [{"field": "category", "operator": "eq", "value": "x"}],
                            "response": {"action": "review", "description": "review", "mode": "simulated"},
                        }
                    ],
                }
            )
