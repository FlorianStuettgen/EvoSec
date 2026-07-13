from __future__ import annotations

import tempfile
from pathlib import Path

from soc_replay.engine import run_scenario
from soc_replay.report import write_bundle

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "network-scan",
    "privileged-group-change",
    "failed-authentication-burst",
    "benign-privileged-change",
)


def main() -> int:
    mismatches: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        for scenario_name in SCENARIOS:
            bundle = write_bundle(run_scenario(ROOT / "scenarios" / scenario_name), temp_root / scenario_name)
            generated = {
                "json": bundle.json_path,
                "md": bundle.markdown_path,
                "manifest.json": bundle.manifest_path,
            }
            for suffix, generated_path in generated.items():
                expected = ROOT / "examples" / "reports" / f"{scenario_name}.{suffix}"
                if generated_path.read_bytes() != expected.read_bytes():
                    mismatches.append(str(expected))
    if mismatches:
        print("reference report mismatch:")
        for mismatch in mismatches:
            print(f"- {mismatch}")
        return 1
    print(f"reference report bundles verified: {len(SCENARIOS)} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
