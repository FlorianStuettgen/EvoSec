from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.cli import main

ROOT = Path(__file__).resolve().parents[1]


class CliExtendedTests(unittest.TestCase):
    def call(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_validate_verify_explain_catalog_and_adapters(self) -> None:
        scenario = str(ROOT / "scenarios" / "network-scan")
        for args, fragment in [
            (("validate", scenario), "exact_contracts=True"),
            (("verify", scenario), "detection_contracts"),
            (("explain", scenario), "selectors="),
            (("explain", scenario, "--json"), '"rule_executions"'),
            (("catalog", "--root", str(ROOT / "scenarios")), "schema=1.1"),
            (("catalog", "--root", str(ROOT / "scenarios"), "--json"), '"exact_detection_contracts": true'),
            (("adapters",), "suricata-eve"),
            (("adapters", "--json"), '"supported_record_types"'),
            (("graph", "--format", "json"), '"invariants"'),
            (("graph",), "load -> compile"),
            (("doctor", "--scenarios", str(ROOT / "scenarios"), "--json"), '"passed": true'),
        ]:
            with self.subTest(args=args):
                code, stdout, _ = self.call(*args)
                self.assertEqual(code, 0)
                self.assertIn(fragment, stdout)

    def test_alias_adapter_and_error_paths(self) -> None:
        with TemporaryDirectory() as temporary:
            destination = str(Path(temporary) / "out.jsonl")
            code, output, _ = self.call(
                "normalize-suricata",
                str(ROOT / "examples" / "adapters" / "suricata-eve.jsonl"),
                destination,
            )
            self.assertEqual(code, 0)
            self.assertIn("written=2", output)
        code, _, stderr = self.call("validate", str(ROOT / "missing"))
        self.assertEqual(code, 2)
        self.assertIn("error:", stderr)
        code, _, _ = self.call("catalog", "--root", str(ROOT / "missing"))
        self.assertEqual(code, 2)
