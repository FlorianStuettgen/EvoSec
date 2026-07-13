from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.engine import run_scenario
from soc_replay.report import verify_bundle, write_bundle

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "network-scan",
    "privileged-group-change",
    "failed-authentication-burst",
    "benign-privileged-change",
)


def main() -> int:
    errors: list[str] = []
    for name in SCENARIOS:
        result = run_scenario(ROOT / "scenarios" / name)
        with TemporaryDirectory() as first_dir, TemporaryDirectory() as second_dir:
            first = write_bundle(result, first_dir)
            second = write_bundle(result, second_dir)
            if not verify_bundle(first.directory).passed or not verify_bundle(second.directory).passed:
                errors.append(f"generated bundle failed verification: {name}")
                continue
            for artifact in ("report.json", "report.md", "manifest.json"):
                if (first.directory / artifact).read_bytes() != (second.directory / artifact).read_bytes():
                    errors.append(f"non-deterministic generated artifact: {name}/{artifact}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"deterministic bundle generation: PASS ({len(SCENARIOS)} scenarios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
