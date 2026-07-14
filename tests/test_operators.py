from __future__ import annotations

import unittest
from types import MappingProxyType

from soc_replay.models import ValidationError
from soc_replay.operators import get_operator, operator_catalog


class OperatorTests(unittest.TestCase):
    def test_all_operator_semantics(self) -> None:
        cases = [
            ("exists", "x", None, True),
            ("exists", None, False, True),
            ("exists", "x", False, False),
            ("eq", 2, 2, True),
            ("ne", 2, 3, True),
            ("in", "a", ("a", "b"), True),
            ("in", [], {"a": 1}, False),
            ("not_in", "z", ("a",), True),
            ("contains", "abcdef", "bcd", True),
            ("contains", (1, 2), 2, True),
            ("contains", MappingProxyType({"key": 1}), "key", True),
            ("contains", 7, 7, False),
            ("contains", {"a": 1}, [], False),
            ("gte", 5, 4, True),
            ("gte", "x", 4, False),
            ("lte", 4, 5, True),
            ("lte", "x", 4, False),
        ]
        for name, actual, expected, result in cases:
            with self.subTest(name=name, actual=actual, expected=expected):
                self.assertEqual(get_operator(name).evaluate(actual, expected), result)

    def test_operator_catalog_and_unknown_operator(self) -> None:
        self.assertEqual(len(operator_catalog()), 8)
        with self.assertRaisesRegex(ValidationError, "unsupported operator"):
            get_operator("missing")
