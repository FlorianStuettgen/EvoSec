from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import run_scenario
from .io import load_scenario
from .models import ValidationError
from .report import write_reports


def _catalog(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if not root.exists():
        return entries
    for scenario_file in sorted(root.glob("*/scenario.json")):
        try:
            scenario, _ = load_scenario(scenario_file.parent)
        except ValidationError:
            continue
        entries.append({"id": scenario.scenario_id, "title": scenario.title, "path": str(scenario_file.parent)})
    return entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="soc-replay", description="Replay synthetic SOC telemetry against inspectable defensive rules.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a scenario directory")
    validate_parser.add_argument("scenario")

    run_parser = subparsers.add_parser("run", help="run a scenario and write JSON/Markdown reports")
    run_parser.add_argument("scenario")
    run_parser.add_argument("--output", default="build/replay")

    catalog_parser = subparsers.add_parser("catalog", help="list valid scenarios")
    catalog_parser.add_argument("--root", default="scenarios")
    catalog_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            scenario, events = load_scenario(args.scenario)
            print(f"valid: {scenario.scenario_id} ({len(events)} events, {len(scenario.rules)} rules)")
            return 0
        if args.command == "run":
            result = run_scenario(args.scenario)
            json_path, markdown_path = write_reports(result, args.output)
            print(f"replayed {len(result.events)} events; detections={len(result.detections)}")
            print(f"json: {json_path}")
            print(f"markdown: {markdown_path}")
            return 0
        if args.command == "catalog":
            entries = _catalog(Path(args.root))
            if args.json:
                print(json.dumps(entries, indent=2))
            else:
                for entry in entries:
                    print(f"{entry['id']}: {entry['title']} [{entry['path']}]")
            return 0
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
