import json
import tempfile
import unittest
from pathlib import Path

from soc_replay.engine import run_scenario
from soc_replay.report import render_markdown, write_reports

ROOT = Path(__file__).resolve().parents[1]


class ReportingTests(unittest.TestCase):
    def test_report_contains_provenance_and_verification(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        payload = result.to_dict()
        self.assertEqual(payload["report_schema_version"], "1.0")
        self.assertEqual(len(payload["provenance"]["scenario_sha256"]), 64)
        self.assertTrue(payload["verification"]["passed"])

    def test_markdown_is_deterministic(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        self.assertEqual(render_markdown(result), render_markdown(result))
        self.assertIn("Verification: PASS", render_markdown(result))

    def test_reports_are_valid_and_replace_existing_files(self) -> None:
        result = run_scenario(ROOT / "scenarios" / "network-scan")
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            (target / "report.json").write_text("stale", encoding="utf-8")
            json_path, markdown_path = write_reports(result, target)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertTrue(payload["verification"]["passed"])
            self.assertTrue(markdown_path.read_text(encoding="utf-8").startswith("# Replay report:"))


if __name__ == "__main__":
    unittest.main()
