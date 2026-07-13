from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .adapters import normalize_suricata_file
from .engine import ReplayResult, run_scenario
from .io import load_scenario
from .models import ValidationError
from .report import verify_bundle, write_bundle


def _catalog(root: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    if not root.exists():
        return entries
    for scenario_file in sorted(root.glob("*/scenario.json")):
        try:
            loaded = load_scenario(scenario_file.parent)
        except ValidationError as exc:
            entries.append({"path": str(scenario_file.parent), "valid": False, "error": str(exc)})
            continue
        entries.append(
            {
                "id": loaded.scenario.scenario_id,
                "title": loaded.scenario.title,
                "path": str(scenario_file.parent),
                "events": len(loaded.events),
                "rules": len(loaded.scenario.rules),
                "run_id": loaded.run_id,
                "valid": True,
            }
        )
    return entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="soc-replay",
        description="Replay synthetic SOC telemetry against inspectable defensive rules and verify expected outcomes.",
    )
    parser.add_argument("--version", action="version", version=f"soc-replay {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a scenario directory and its input provenance")
    validate_parser.add_argument("scenario")

    run_parser = subparsers.add_parser("run", help="run a scenario, verify expectations, and write reports")
    run_parser.add_argument("scenario")
    run_parser.add_argument("--output", default="build/replay")
    run_parser.add_argument("--allow-mismatch", action="store_true", help="return success even when expectations fail")

    verify_parser = subparsers.add_parser("verify", help="run a scenario and verify its machine-readable expectations")
    verify_parser.add_argument("scenario")

    explain_parser = subparsers.add_parser("explain", help="print the scenario, rules, and expected result")
    explain_parser.add_argument("scenario")
    explain_parser.add_argument("--json", action="store_true")

    bundle_parser = subparsers.add_parser(
        "verify-bundle", help="verify report artifact hashes and manifest consistency"
    )
    bundle_parser.add_argument("bundle")

    adapter_parser = subparsers.add_parser(
        "normalize-suricata", help="normalize sanitized Suricata EVE JSONL into the SOC_Replay event contract"
    )
    adapter_parser.add_argument("source")
    adapter_parser.add_argument("destination")

    catalog_parser = subparsers.add_parser("catalog", help="list scenarios, including invalid entries")
    catalog_parser.add_argument("--root", default="scenarios")
    catalog_parser.add_argument("--json", action="store_true")
    return parser


def _print_verification(result: ReplayResult) -> None:
    verification = result.verification
    print(f"verification: {'PASS' if verification.passed else 'FAIL'}")
    for check in verification.checks:
        print(
            f"  {'PASS' if check.passed else 'FAIL'} {check.name}: expected={check.expected!r} actual={check.actual!r}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            loaded = load_scenario(args.scenario)
            print(
                f"valid: {loaded.scenario.scenario_id} "
                f"({len(loaded.events)} events, {len(loaded.scenario.rules)} rules, run_id={loaded.run_id})"
            )
            return 0
        if args.command == "run":
            result = run_scenario(args.scenario)
            bundle = write_bundle(result, args.output)
            print(f"replayed {len(result.events)} events; detections={len(result.detections)}")
            _print_verification(result)
            print(f"json: {bundle.json_path}")
            print(f"markdown: {bundle.markdown_path}")
            print(f"manifest: {bundle.manifest_path}")
            return 0 if result.verification.passed or args.allow_mismatch else 3
        if args.command == "verify":
            result = run_scenario(args.scenario)
            _print_verification(result)
            return 0 if result.verification.passed else 3
        if args.command == "explain":
            loaded = load_scenario(args.scenario)
            payload = {
                "id": loaded.scenario.scenario_id,
                "title": loaded.scenario.title,
                "objective": loaded.scenario.objective,
                "authorization_boundary": loaded.scenario.authorization_boundary,
                "rules": [
                    {
                        "id": rule.rule_id,
                        "name": rule.name,
                        "severity": rule.severity,
                        "aggregate": None if rule.aggregate is None else rule.aggregate.__dict__,
                    }
                    for rule in loaded.scenario.rules
                ],
                "expectations": loaded.scenario.expectations.__dict__,
                "run_id": loaded.run_id,
            }
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True, default=list))
            else:
                print(f"{payload['id']}: {payload['title']}")
                print(f"objective: {payload['objective']}")
                print(f"boundary: {payload['authorization_boundary']}")
                print(f"run_id: {payload['run_id']}")
                for rule in loaded.scenario.rules:
                    print(f"rule {rule.rule_id}: {rule.name} [{rule.severity}]")
                print(f"expected detections: {loaded.scenario.expectations.detection_count}")
            return 0
        if args.command == "verify-bundle":
            verification = verify_bundle(args.bundle)
            print(f"bundle verification: {'PASS' if verification.passed else 'FAIL'}")
            for check in verification.checks:
                print(
                    f"  {'PASS' if check.passed else 'FAIL'} {check.name}: "
                    f"expected={check.expected!r} actual={check.actual!r}"
                )
            return 0 if verification.passed else 4
        if args.command == "normalize-suricata":
            adapter_result = normalize_suricata_file(args.source, args.destination)
            print(
                f"normalized Suricata EVE: read={adapter_result.records_read} written={adapter_result.records_written} "
                f"skipped={adapter_result.records_skipped} output={adapter_result.destination}"
            )
            return 0
        if args.command == "catalog":
            entries = _catalog(Path(args.root))
            if args.json:
                print(json.dumps(entries, indent=2, sort_keys=True))
            else:
                for entry in entries:
                    if entry["valid"]:
                        print(
                            f"{entry['id']}: {entry['title']} "
                            f"[{entry['events']} events, {entry['rules']} rules, run_id={entry['run_id']}]"
                        )
                    else:
                        print(f"INVALID: {entry['path']} — {entry['error']}")
            return 0 if all(entry["valid"] for entry in entries) else 2
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
