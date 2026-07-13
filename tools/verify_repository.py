from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from soc_replay import __version__
from soc_replay.engine import run_scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ("network-scan", "privileged-group-change", "failed-authentication-burst")
SCHEMAS = ("event.schema.json", "scenario.schema.json", "report.schema.json")


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]
    if project_version != __version__:
        fail(f"version mismatch: pyproject={project_version} package={__version__}")

    for schema_name in SCHEMAS:
        payload = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
        if payload.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"unexpected schema declaration in {schema_name}")

    for scenario_name in SCENARIOS:
        result = run_scenario(ROOT / "scenarios" / scenario_name)
        if not result.verification.passed:
            fail(f"scenario verification failed: {scenario_name}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for relative in re.findall(r"\]\(([^)]+)\)", readme):
        if relative.startswith(("http://", "https://", "#")):
            continue
        candidate = (ROOT / relative.split("#", 1)[0]).resolve()
        if not candidate.exists():
            fail(f"README link target does not exist: {relative}")

    completed = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_reference_reports.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        fail(completed.stdout + completed.stderr)

    print(
        f"repository verified: version={__version__} schemas={len(SCHEMAS)} "
        f"scenarios={len(SCENARIOS)} reference_reports=3"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"repository verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
