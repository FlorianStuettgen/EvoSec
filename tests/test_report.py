from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.engine import run_scenario
from soc_replay.report import ReportBundle, render_json, verify_bundle, write_bundle
from soc_replay.serialization import digest_object, pretty_json, sha256_bytes

ROOT = Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    @staticmethod
    def _rewrite_report_and_manifest(
        bundle: ReportBundle,
        report: dict[str, object],
        manifest: dict[str, object],
    ) -> None:
        report_content = pretty_json(report)
        bundle.json_path.write_text(report_content, encoding="utf-8")
        artifacts = manifest["artifacts"]
        assert isinstance(artifacts, dict)
        artifacts["report.json"] = {
            "sha256": sha256_bytes(report_content.encode()),
            "bytes": len(report_content.encode()),
        }
        core = {key: value for key, value in manifest.items() if key != "bundle_id"}
        manifest["bundle_id"] = digest_object(core)
        bundle.manifest_path.write_text(pretty_json(manifest), encoding="utf-8")

    def test_bundle_round_trip_and_identity(self) -> None:
        scenario = ROOT / "scenarios" / "network-scan"
        result = run_scenario(scenario)
        with TemporaryDirectory() as temporary:
            bundle = write_bundle(result, temporary)
            self.assertTrue(verify_bundle(temporary).passed)
            self.assertTrue(verify_bundle(temporary, source_directory=scenario).passed)
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

    def test_bundle_detects_rehashed_internal_inconsistency(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        with TemporaryDirectory() as temporary:
            bundle = write_bundle(result, temporary)
            report = json.loads(bundle.json_path.read_text())
            manifest = json.loads(bundle.manifest_path.read_text())
            report["summary"]["detections"] = 99
            self._rewrite_report_and_manifest(bundle, report, manifest)
            verification = verify_bundle(temporary)
            self.assertFalse(verification.passed)
            self.assertTrue(any(check.name == "detection_count" and not check.passed for check in verification.checks))

    def test_bundle_detects_rehashed_detection_semantic_tampering(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        with TemporaryDirectory() as temporary:
            bundle = write_bundle(result, temporary)
            report = json.loads(bundle.json_path.read_text())
            manifest = json.loads(bundle.manifest_path.read_text())
            report["detections"][0]["severity"] = "low"
            self._rewrite_report_and_manifest(bundle, report, manifest)
            verification = verify_bundle(temporary)
            self.assertFalse(verification.passed)
            failed = {check.name for check in verification.checks if not check.passed}
            self.assertIn("verification.severity_counts.actual", failed)
            self.assertIn("ledger.evaluate.output_digest", failed)

    def test_source_bound_verification_detects_coherent_report_rewrite(self) -> None:
        scenario = ROOT / "scenarios" / "network-scan"
        result = run_scenario(scenario)
        with TemporaryDirectory() as temporary:
            bundle = write_bundle(result, temporary)
            report = json.loads(bundle.json_path.read_text())
            manifest = json.loads(bundle.manifest_path.read_text())
            report["scenario"]["title"] = "Coherently rehashed but not source-derived"
            self._rewrite_report_and_manifest(bundle, report, manifest)
            self.assertTrue(verify_bundle(temporary).passed)
            source_verification = verify_bundle(temporary, source_directory=scenario)
            self.assertFalse(source_verification.passed)
            failed = {check.name for check in source_verification.checks if not check.passed}
            self.assertIn("source_bound.report.json.sha256", failed)
            self.assertIn("source_bound.manifest.json.sha256", failed)

    def test_report_exposes_plan_traces_and_ledger(self) -> None:
        payload = json.loads(render_json(run_scenario(ROOT / "scenarios" / "network-scan")))
        self.assertEqual(payload["report_schema_version"], "2.1")
        self.assertEqual(
            payload["execution"]["ledger"]["root_hash"],
            payload["execution"]["ledger"]["entries"][-1]["entry_hash"],
        )
        self.assertEqual(len(payload["execution"]["plan"]["rules"]), 1)
        self.assertEqual(payload["execution"]["rules"][0]["detection_count"], 1)
