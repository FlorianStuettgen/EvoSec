import unittest
from datetime import UTC

from soc_replay.models import Aggregate, Condition, Event, Expectations, Response, ValidationError, parse_timestamp


class ModelValidationTests(unittest.TestCase):
    def test_timestamp_is_normalized_to_utc(self) -> None:
        parsed = parse_timestamp("2026-07-01T08:00:00-04:00")
        self.assertEqual(parsed.tzinfo, UTC)
        self.assertEqual(parsed.hour, 12)

    def test_naive_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            parse_timestamp("2026-07-01T12:00:00")

    def test_invalid_ip_is_rejected(self) -> None:
        payload = {
            "event_id": "x",
            "timestamp": "2026-07-01T12:00:00Z",
            "source": "sensor",
            "category": "network",
            "action": "observe",
            "source_ip": "999.1.1.1",
        }
        with self.assertRaises(ValidationError):
            Event.from_dict(payload)

    def test_nested_detail_lookup(self) -> None:
        event = Event.from_dict(
            {
                "event_id": "x",
                "timestamp": "2026-07-01T12:00:00Z",
                "source": "sensor",
                "category": "identity",
                "action": "change",
                "details": {"actor": {"role": "admin"}},
            }
        )
        self.assertEqual(event.value("details.actor.role"), "admin")
        self.assertIsNone(event.value("details.actor.missing"))

    def test_duplicate_tags_are_rejected(self) -> None:
        payload = {
            "event_id": "x",
            "timestamp": "2026-07-01T12:00:00Z",
            "source": "sensor",
            "category": "network",
            "action": "observe",
            "tags": ["one", "one"],
        }
        with self.assertRaises(ValidationError):
            Event.from_dict(payload)

    def test_membership_operator_requires_list(self) -> None:
        with self.assertRaises(ValidationError):
            Condition.from_dict({"field": "source", "operator": "in", "value": "sensor"})

    def test_exists_operator_accepts_false(self) -> None:
        condition = Condition.from_dict({"field": "details.ticket", "operator": "exists", "value": False})
        self.assertFalse(condition.value)

    def test_distinct_fields_must_be_paired(self) -> None:
        with self.assertRaises(ValidationError):
            Aggregate.from_dict({"group_by": [], "count_gte": 2, "within_seconds": 30, "distinct_field": "user"})

    def test_non_simulated_response_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Response.from_dict({"action": "block", "description": "bad", "mode": "live"})

    def test_expectation_counts_must_reconcile(self) -> None:
        with self.assertRaises(ValidationError):
            Expectations.from_dict(
                {
                    "detection_count": 2,
                    "rule_ids": ["R-1"],
                    "severity_counts": {"high": 2},
                    "simulated_action_count": 2,
                }
            )


if __name__ == "__main__":
    unittest.main()
