from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.engine import run_scenario
from soc_replay.report import render_json, verify_bundle, write_bundle

ROOT = Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    def test_bundle_round_trip_and_identity(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        with TemporaryDirectory() as temporary:
            bundle = write_bundle(result, temporary)
            verification = verify_bundle(temporary)
            self.assertTrue(verification.passed)
            manifest = json.loads(bundle.manifest_path.read_text())
            self.assertEqual(manifest["bundle_id"], bundle.bundle_id)
            self.assertEqual(manifest["ledger_root"], result.ledger.root_hash)

    def test_bundle_detects_report_tampering(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        with TemporaryDirectory() as temporary:
            bundle = write_bundle(result, temporary)
            bundle.json_path.write_text(bundle.json_path.read_text() + " ", encoding="utf-8")
            verification = verify_bundle(temporary)
            self.assertFalse(verification.passed)
            self.assertTrue(
                any(check.name == "report.json.sha256" and not check.passed for check in verification.checks)
            )

    def test_report_exposes_plan_and_ledger(self) -> None:
        payload = json.loads(render_json(run_scenario(ROOT / "scenarios" / "network-scan")))
        self.assertEqual(payload["report_schema_version"], "2.0")
        self.assertEqual(
            payload["execution"]["ledger"]["root_hash"], payload["execution"]["ledger"]["entries"][-1]["entry_hash"]
        )
        self.assertEqual(len(payload["execution"]["plan"]["rules"]), 1)
