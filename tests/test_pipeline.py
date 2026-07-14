from __future__ import annotations

import unittest
from pathlib import Path

from soc_replay.engine import run_scenario
from soc_replay.ledger import verify_ledger_payload
from soc_replay.pipeline import PipelineConfig, ReplayPipeline
from soc_replay.serialization import pretty_json

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_all_reference_scenarios_pass_with_exact_contracts_and_traces(self) -> None:
        expected = {
            "network-scan": 1,
            "privileged-group-change": 1,
            "failed-authentication-burst": 2,
            "benign-privileged-change": 0,
        }
        for name, count in expected.items():
            with self.subTest(name=name):
                result = run_scenario(ROOT / "scenarios" / name)
                self.assertTrue(result.verification.passed)
                self.assertEqual(len(result.detections), count)
                self.assertEqual(len(result.rule_executions), len(result.plan.rules))
                self.assertEqual(sum(item.detection_count for item in result.rule_executions), count)
                self.assertEqual(
                    [entry.stage for entry in result.ledger.entries],
                    ["load", "compile", "index", "evaluate", "verify"],
                )
                self.assertTrue(any(check.name == "detection_contracts" for check in result.verification.checks))

    def test_negative_control_preserves_zero_detection_trace(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "benign-privileged-change")
        trace = result.rule_executions[0]
        self.assertEqual(trace.candidate_count, 0)
        self.assertEqual(trace.matched_count, 0)
        self.assertEqual(trace.detection_count, 0)
        self.assertEqual(result.ledger.entries[3].metadata["rule_executions"][0]["detection_count"], 0)

    def test_result_and_ledger_are_byte_deterministic(self) -> None:
        path = ROOT / "scenarios" / "network-scan"
        first = run_scenario(path)
        second = run_scenario(path)
        self.assertEqual(pretty_json(first.to_dict()), pretty_json(second.to_dict()))
        self.assertEqual(first.ledger.root_hash, second.ledger.root_hash)
        passed, errors = verify_ledger_payload(first.ledger.to_dict())
        self.assertTrue(passed, errors)

    def test_ledger_detects_internal_tampering(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        payload = result.ledger.to_dict()
        payload["entries"][2]["records_out"] = 999
        passed, errors = verify_ledger_payload(payload)
        self.assertFalse(passed)
        self.assertTrue(any("hash mismatch" in error for error in errors))

    def test_max_event_limit_is_enforced(self) -> None:
        pipeline = ReplayPipeline(PipelineConfig(max_events=2))
        with self.assertRaisesRegex(ValueError, "max_events"):
            pipeline.run(ROOT / "scenarios" / "network-scan")
