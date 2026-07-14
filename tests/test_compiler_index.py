from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from soc_replay.compiler import compile_scenario
from soc_replay.indexing import EventIndex
from soc_replay.io import load_scenario
from soc_replay.models import Scenario

ROOT = Path(__file__).resolve().parents[1]


class CompilerIndexTests(unittest.TestCase):
    def test_plan_is_deterministic_and_output_sensitive(self) -> None:
        payload = json.loads((ROOT / "scenarios" / "network-scan" / "scenario.json").read_text())
        first = compile_scenario(Scenario.from_dict(payload))
        second = compile_scenario(Scenario.from_dict(copy.deepcopy(payload)))
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertEqual(first.rules[0].fingerprint, second.rules[0].fingerprint)

        payload["rules"][0]["response"]["description"] += " changed"
        changed = compile_scenario(Scenario.from_dict(payload))
        self.assertNotEqual(first.fingerprint, changed.fingerprint)
        self.assertNotEqual(first.rules[0].fingerprint, changed.rules[0].fingerprint)

    def test_composite_selectors_reduce_candidates_without_changing_semantics(self) -> None:
        loaded = load_scenario(ROOT / "scenarios" / "privileged-group-change")
        rule = compile_scenario(loaded.scenario).rules[0]
        candidates = EventIndex(loaded.events).candidates(rule)
        self.assertEqual(
            candidates.strategy,
            "intersection[eq:category=identity_change,eq:action=add_to_privileged_group,"
            "eq:outcome=success,tag:unauthorized]",
        )
        self.assertEqual([event.event_id for event in candidates.events], ["iam-002"])
        self.assertTrue(rule.matches(candidates.events[0]))
        self.assertEqual(len(rule.candidate_selectors), 4)

    def test_empty_selector_intersection_is_explicit(self) -> None:
        loaded = load_scenario(ROOT / "scenarios" / "benign-privileged-change")
        rule = compile_scenario(loaded.scenario).rules[0]
        candidates = EventIndex(loaded.events).candidates(rule)
        self.assertEqual(candidates.events, ())
        self.assertIn("intersection[", candidates.strategy)
