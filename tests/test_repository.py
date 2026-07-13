import json
import subprocess
import sys
import unittest
from pathlib import Path

from soc_replay import __version__

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def test_version_is_current(self) -> None:
        self.assertEqual(__version__, "2.1.0")

    def test_schemas_are_valid_json(self) -> None:
        for path in sorted((ROOT / "schemas").glob("*.json")):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_repository_verifier_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "verify_repository.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
