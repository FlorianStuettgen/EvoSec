import tempfile
import unittest
from pathlib import Path

from soc_replay.engine import _compare, run_scenario
from soc_replay.io import load_scenario
from soc_replay.models import Condition, ValidationError

ROOT = Path(__file__).resolve().parents[1]


class ReplayEngineTests(unittest.TestCase):
    def test_network_scan_produces_verified_detection(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        self.assertEqual(len(result.events), 7)
        self.assertEqual(len(result.detections), 1)
        self.assertTrue(result.verification.passed)
        detection = result.detections[0]
        self.assertEqual(detection.rule_id, "NET-SCAN-001")
        self.assertEqual(len(detection.event_ids), 5)
        self.assertEqual(detection.correlation["distinct_count"], 5)
        self.assertEqual(detection.response.mode, "simulated")

    def test_privileged_group_change_uses_nested_exists_condition(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "privileged-group-change")
        self.assertTrue(result.verification.passed)
        self.assertEqual(result.detections[0].severity, "critical")
        self.assertEqual(result.detections[0].event_ids, ("iam-002",))

    def test_all_non_overlapping_policy_emits_two_detections(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "failed-authentication-burst")
        self.assertTrue(result.verification.passed)
        self.assertEqual(
            [item.event_ids for item in result.detections],
            [("auth-001", "auth-002", "auth-003"), ("auth-004", "auth-005", "auth-006")],
        )

    def test_negative_control_produces_no_detection(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "benign-privileged-change")
        self.assertTrue(result.verification.passed)
        self.assertEqual(result.detections, ())
        self.assertEqual(result.simulated_actions, ())

    def test_run_id_is_deterministic(self) -> None:
        first = run_scenario(ROOT / "scenarios" / "network-scan")
        second = run_scenario(ROOT / "scenarios" / "network-scan")
        self.assertEqual(first.loaded.run_id, second.loaded.run_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_contains_is_safe_for_non_iterable_actual(self) -> None:
        condition = Condition(field="destination_port", operator="contains", value=4)
        self.assertFalse(_compare(443, condition))

    def test_not_in_operator(self) -> None:
        condition = Condition(field="source", operator="not_in", value=["trusted"])
        self.assertTrue(_compare("sensor", condition))

    def test_missing_scenario_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            load_scenario(ROOT / "scenarios" / "does-not-exist")

    def test_expectation_mismatch_fails_verification(self) -> None:
        source = ROOT / "scenarios" / "network-scan"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            scenario_text = (
                (source / "scenario.json")
                .read_text(encoding="utf-8")
                .replace('"detection_count": 1', '"detection_count": 0')
                .replace('"rule_ids": ["NET-SCAN-001"]', '"rule_ids": []')
                .replace('"severity_counts": {"high": 1}', '"severity_counts": {}')
                .replace('"simulated_action_count": 1', '"simulated_action_count": 0')
            )
            (target / "scenario.json").write_text(scenario_text, encoding="utf-8")
            (target / "events.jsonl").write_text(
                (source / "events.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
            )
            result = run_scenario(target)
            self.assertFalse(result.verification.passed)


if __name__ == "__main__":
    unittest.main()
