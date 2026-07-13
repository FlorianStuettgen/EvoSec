import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from soc_replay.cli import main

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def _call(self, args: list[str]) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_validate(self) -> None:
        code, output, _ = self._call(["validate", str(ROOT / "scenarios" / "network-scan")])
        self.assertEqual(code, 0)
        self.assertIn("run_id=", output)

    def test_verify(self) -> None:
        code, output, _ = self._call(["verify", str(ROOT / "scenarios" / "privileged-group-change")])
        self.assertEqual(code, 0)
        self.assertIn("verification: PASS", output)

    def test_run_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            code, output, _ = self._call(["run", str(ROOT / "scenarios" / "network-scan"), "--output", temp_dir])
            self.assertEqual(code, 0)
            self.assertTrue((Path(temp_dir) / "report.json").exists())
            self.assertTrue((Path(temp_dir) / "report.md").exists())
            self.assertTrue((Path(temp_dir) / "manifest.json").exists())
            self.assertIn("verification: PASS", output)

    def test_catalog_lists_invalid_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid = Path(temp_dir) / "invalid"
            invalid.mkdir()
            (invalid / "scenario.json").write_text("{}", encoding="utf-8")
            code, output, _ = self._call(["catalog", "--root", temp_dir])
            self.assertEqual(code, 2)
            self.assertIn("INVALID", output)

    def test_explain_json(self) -> None:
        code, output, _ = self._call(["explain", str(ROOT / "scenarios" / "network-scan"), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"expectations"', output)
        self.assertIn('"run_id"', output)

    def test_verify_bundle_and_suricata_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_dir = Path(temp_dir) / "bundle"
            code, _, _ = self._call(["run", str(ROOT / "scenarios" / "network-scan"), "--output", str(bundle_dir)])
            self.assertEqual(code, 0)
            code, output, _ = self._call(["verify-bundle", str(bundle_dir)])
            self.assertEqual(code, 0)
            self.assertIn("bundle verification: PASS", output)

            normalized = Path(temp_dir) / "normalized.jsonl"
            code, output, _ = self._call([
                "normalize-suricata",
                str(ROOT / "examples" / "adapters" / "suricata-eve.jsonl"),
                str(normalized),
            ])
            self.assertEqual(code, 0)
            self.assertIn("written=2", output)
            self.assertTrue(normalized.exists())


if __name__ == "__main__":
    unittest.main()
