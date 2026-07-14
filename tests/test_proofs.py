from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from soc_replay.indexing import CandidateSet, EventIndex
from soc_replay.io import load_scenario
from soc_replay.proofs import RuleEquivalenceProof, prove_index_equivalence

ROOT = Path(__file__).resolve().parents[1]


class ProofTests(unittest.TestCase):
    def test_all_scenarios_are_index_equivalent(self) -> None:
        scenario_dirs = sorted(path.parent for path in (ROOT / "scenarios").glob("*/scenario.json"))
        self.assertTrue(scenario_dirs)
        for scenario_dir in scenario_dirs:
            with self.subTest(scenario=scenario_dir.name):
                proof = prove_index_equivalence(scenario_dir)
                self.assertTrue(proof.passed)
                payload = proof.to_dict()
                self.assertEqual(len(proof.proof_id), 64)
                self.assertEqual(payload["proof_id"], proof.proof_id)
                self.assertEqual(payload["engine"]["version"], "3.2.0")
                self.assertEqual(payload["passed"], True)

    def test_network_scan_index_reduces_candidates(self) -> None:
        proof = prove_index_equivalence(ROOT / "scenarios" / "network-scan")
        self.assertGreater(proof.candidate_reduction, 0)
        self.assertLess(proof.indexed_candidate_count, proof.full_scan_candidate_count)

    def test_optimization_metadata_is_not_semantic_output(self) -> None:
        loaded = load_scenario(ROOT / "scenarios" / "network-scan")
        with patch.object(
            EventIndex,
            "candidates",
            return_value=CandidateSet(loaded.events, "alternate-full-scan-label"),
        ):
            proof = prove_index_equivalence(ROOT / "scenarios" / "network-scan")
        self.assertTrue(proof.passed)
        self.assertEqual(proof.indexed_candidate_count, proof.full_scan_candidate_count)

    def test_zero_candidate_denominator_is_defined(self) -> None:
        proof = RuleEquivalenceProof(
            rule_id="R",
            rule_fingerprint="0" * 64,
            indexed_strategy="full_scan",
            indexed_candidate_count=0,
            full_scan_candidate_count=0,
            semantic_digest="1" * 64,
            passed=True,
            failures=(),
        )
        self.assertEqual(proof.candidate_reduction_ratio, 0.0)
        self.assertEqual(proof.to_dict()["candidate_reduction"], 0)

    def test_proof_detects_semantic_index_corruption(self) -> None:
        with patch.object(EventIndex, "candidates", return_value=CandidateSet((), "tampered")):
            proof = prove_index_equivalence(ROOT / "scenarios" / "network-scan")
        self.assertFalse(proof.passed)
        self.assertTrue(any(rule.failures for rule in proof.rules))
