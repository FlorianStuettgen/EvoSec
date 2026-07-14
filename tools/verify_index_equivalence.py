from __future__ import annotations

import argparse
import json
from pathlib import Path

from soc_replay.proofs import prove_index_equivalence

ROOT = Path(__file__).resolve().parents[1]


def _scenario_directories(root: Path) -> tuple[Path, ...]:
    return tuple(sorted(path.parent for path in root.glob("*/scenario.json")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prove that indexed execution is semantically equivalent to full-scan execution."
    )
    parser.add_argument("--root", default=str(ROOT / "scenarios"))
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scenarios = _scenario_directories(Path(args.root))
    if not scenarios:
        print("ERROR: no scenarios found")
        return 2

    proofs = tuple(prove_index_equivalence(directory) for directory in scenarios)
    if args.json:
        print(json.dumps([proof.to_dict() for proof in proofs], indent=2, sort_keys=True))
    else:
        for proof in proofs:
            verdict = "PASS" if proof.passed else "FAIL"
            print(
                f"{verdict} {proof.scenario_id}: events={proof.event_count} "
                f"candidates={proof.indexed_candidate_count}/{proof.full_scan_candidate_count} "
                f"reduction={proof.candidate_reduction} proof={proof.proof_id}"
            )
            for rule in proof.rules:
                if not rule.passed:
                    print(f"  {rule.rule_id}: {'; '.join(rule.failures)}")
    return 0 if all(proof.passed for proof in proofs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
