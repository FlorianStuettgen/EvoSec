from pathlib import Path
import unittest

from soc_replay.engine import run_scenario
from soc_replay.io import load_scenario
from soc_replay.models import ValidationError

ROOT = Path(__file__).resolve().parents[1]


class ReplayEngineTests(unittest.TestCase):
    def test_network_scan_produces_one_detection(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        self.assertEqual(len(result.events), 7)
        self.assertEqual(len(result.detections), 1)
        detection = result.detections[0]
        self.assertEqual(detection.rule_id, "NET-SCAN-001")
        self.assertEqual(len(detection.event_ids), 5)
        self.assertEqual(detection.response.mode, "simulated")

    def test_privileged_group_change_produces_critical_detection(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "privileged-group-change")
        self.assertEqual(len(result.detections), 1)
        self.assertEqual(result.detections[0].severity, "critical")
        self.assertEqual(result.detections[0].event_ids, ("iam-002",))

    def test_live_response_mode_is_rejected(self) -> None:
        scenario, _ = load_scenario(ROOT / "scenarios" / "network-scan")
        self.assertTrue(all(rule.response.mode == "simulated" for rule in scenario.rules))

    def test_missing_scenario_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            load_scenario(ROOT / "scenarios" / "does-not-exist")


if __name__ == "__main__":
    unittest.main()
