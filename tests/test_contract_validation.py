from __future__ import annotations

import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContractValidationTests(unittest.TestCase):
    def test_repository_contracts_validate(self) -> None:
        namespace = runpy.run_path(str(ROOT / "tools" / "validate_contracts.py"))
        errors = namespace["validate_repository_contracts"](ROOT)
        self.assertEqual(errors, [])
