from __future__ import annotations

import unittest
from pathlib import Path

from soc_replay.compiler import compile_scenario
from soc_replay.indexing import EventIndex
from soc_replay.io import load_scenario

ROOT = Path(__file__).resolve().parents[1]


class CompilerIndexTests(unittest.TestCase):
    def test_plan_is_deterministic(self) -> None:
        scenario = load_scenario(ROOT / "scenarios" / "network-scan").scenario
        first = compile_scenario(scenario)
        second = compile_scenario(scenario)
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertEqual(first.rules[0].fingerprint, second.rules[0].fingerprint)

    def test_category_hint_reduces_candidates_without_changing_semantics(self) -> None:
        loaded = load_scenario(ROOT / "scenarios" / "privileged-group-change")
        rule = compile_scenario(loaded.scenario).rules[0]
        candidates = EventIndex(loaded.events).candidates(rule)
        self.assertEqual(candidates.strategy, "eq:category=identity_change")
        self.assertEqual([event.event_id for event in candidates.events], ["iam-002"])
        self.assertTrue(rule.matches(candidates.events[0]))

    def test_tag_hint_is_available_when_no_equality_hint_exists(self) -> None:
        loaded = load_scenario(ROOT / "scenarios" / "network-scan")
        rule = compile_scenario(loaded.scenario).rules[0]
        self.assertEqual(rule.candidate_hint.field, "category")
