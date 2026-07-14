from __future__ import annotations

import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.cli import main

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_doctor_and_graph(self) -> None:
        code, output, _ = self.run_cli("doctor", "--scenarios", str(ROOT / "scenarios"))
        self.assertEqual(code, 0)
        self.assertIn("doctor: PASS", output)
        self.assertIn("scenario=1.1", output)
        code, output, _ = self.run_cli("graph", "--format", "mermaid")
        self.assertEqual(code, 0)
        self.assertIn("flowchart LR", output)
        self.assertIn("LOAD --> COMPILE", output)

    def test_run_and_verify_bundle(self) -> None:
        scenario = str(ROOT / "scenarios" / "network-scan")
        with TemporaryDirectory() as temporary:
            code, output, _ = self.run_cli(
                "run",
                scenario,
                "--output",
                temporary,
            )
            self.assertEqual(code, 0)
            self.assertIn("ledger:", output)
            code, output, _ = self.run_cli("verify-bundle", temporary)
            self.assertEqual(code, 0)
            self.assertIn("bundle verification: PASS", output)
            self.assertIn("0 failed", output)
            self.assertNotIn("engine_name", output)

            code, output, _ = self.run_cli("verify-bundle", temporary, "--source", scenario, "--verbose")
            self.assertEqual(code, 0)
            self.assertIn("source_bound.report.json.sha256", output)

            code, output, _ = self.run_cli("verify-bundle", temporary, "--source", scenario, "--json")
            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertTrue(payload["passed"])
            self.assertTrue(any(check["name"].startswith("source_bound.") for check in payload["checks"]))

    def test_generic_adapter_command(self) -> None:
        with TemporaryDirectory() as temporary:
            destination = str(Path(temporary) / "normalized.jsonl")
            code, output, _ = self.run_cli(
                "normalize",
                "--adapter",
                "suricata-eve",
                str(ROOT / "examples" / "adapters" / "suricata-eve.jsonl"),
                destination,
            )
            self.assertEqual(code, 0)
            self.assertIn("written=2", output)
