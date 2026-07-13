from __future__ import annotations

import tempfile
from pathlib import Path

from soc_replay.engine import run_scenario
from soc_replay.report import write_reports

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ("network-scan", "privileged-group-change", "failed-authentication-burst")


def main() -> int:
    mismatches: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        for scenario_name in SCENARIOS:
            output = temp_root / scenario_name
            json_path, markdown_path = write_reports(run_scenario(ROOT / "scenarios" / scenario_name), output)
            expected_json = ROOT / "examples" / "reports" / f"{scenario_name}.json"
            expected_markdown = ROOT / "examples" / "reports" / f"{scenario_name}.md"
            if json_path.read_bytes() != expected_json.read_bytes():
                mismatches.append(str(expected_json))
            if markdown_path.read_bytes() != expected_markdown.read_bytes():
                mismatches.append(str(expected_markdown))
    if mismatches:
        print("reference report mismatch:")
        for mismatch in mismatches:
            print(f"- {mismatch}")
        return 1
    print(f"reference reports verified: {len(SCENARIOS)} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
