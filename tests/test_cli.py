from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from soc_replay.cli import main

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_validate(self) -> None:
        code = main(["validate", str(ROOT / "scenarios" / "network-scan")])
        self.assertEqual(code, 0)

    def test_run_writes_reports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            code = main(["run", str(ROOT / "scenarios" / "network-scan"), "--output", temp_dir])
            self.assertEqual(code, 0)
            self.assertTrue((Path(temp_dir) / "report.json").exists())
            self.assertTrue((Path(temp_dir) / "report.md").exists())

    def test_catalog(self) -> None:
        code = main(["catalog", "--root", str(ROOT / "scenarios")])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
