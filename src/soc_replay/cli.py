from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import adapter_registry, normalize_file, normalize_suricata_file
from .engine import ReplayResult, run_scenario
from .io import load_scenario
from .models import ValidationError
from .operators import operator_catalog
from .pipeline import ReplayPipeline
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


def _print_verification(result: ReplayResult) -> None:
    print(f"verification: {'PASS' if result.verification.passed else 'FAIL'}")
    for check in result.verification.checks:
        print(
            f"  {'PASS' if check.passed else 'FAIL'} {check.name}: expected={check.expected!r} actual={check.actual!r}"
        )


def _pipeline_mermaid() -> str:
    stages = ReplayPipeline.DESCRIPTION.stages
    edges = "\n".join(
        f"    {stages[index].upper()} --> {stages[index + 1].upper()}" for index in range(len(stages) - 1)
    )
    nodes = "\n".join(f"    {stage.upper()}[{stage}]" for stage in stages)
    return f"flowchart LR\n{nodes}\n{edges}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="soc-replay",
        description="Deterministic evidence pipeline for synthetic and sanitized defensive telemetry.",
    )
    parser.add_argument("--version", action="version", version=f"soc-replay {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a scenario directory and input provenance")
    validate_parser.add_argument("scenario")

    run_parser = subparsers.add_parser("run", help="execute the evidence pipeline and write a report bundle")
    run_parser.add_argument("scenario")
    run_parser.add_argument("--output", default="build/replay")
    run_parser.add_argument("--allow-mismatch", action="store_true")
    run_parser.add_argument("--max-events", type=int, default=1_000_000)

    verify_parser = subparsers.add_parser("verify", help="execute a scenario and verify declared expectations")
    verify_parser.add_argument("scenario")

    explain_parser = subparsers.add_parser("explain", help="print scenario, compiled plan, and expectations")
    explain_parser.add_argument("scenario")
    explain_parser.add_argument("--json", action="store_true")

    bundle_parser = subparsers.add_parser("verify-bundle", help="verify artifacts, manifest, and execution ledger")
    bundle_parser.add_argument("bundle")

    normalize_parser = subparsers.add_parser("normalize", help="normalize a stored telemetry file through an adapter")
    normalize_parser.add_argument("--adapter", required=True)
    normalize_parser.add_argument("source")
    normalize_parser.add_argument("destination")

    legacy_adapter_parser = subparsers.add_parser(
        "normalize-suricata", help="compatibility alias for --adapter suricata-eve"
    )
    legacy_adapter_parser.add_argument("source")
    legacy_adapter_parser.add_argument("destination")

    adapters_parser = subparsers.add_parser("adapters", help="list registered offline telemetry adapters")
    adapters_parser.add_argument("--json", action="store_true")

    graph_parser = subparsers.add_parser("graph", help="render the internal execution pipeline")
    graph_parser.add_argument("--format", choices=("text", "json", "mermaid"), default="text")

    doctor_parser = subparsers.add_parser("doctor", help="audit package wiring and scenario catalog")
    doctor_parser.add_argument("--scenarios", default="scenarios")
    doctor_parser.add_argument("--json", action="store_true")

    catalog_parser = subparsers.add_parser("catalog", help="list scenarios, including invalid entries")
    catalog_parser.add_argument("--root", default="scenarios")
    catalog_parser.add_argument("--json", action="store_true")
    return parser


def _doctor(root: Path) -> dict[str, Any]:
    catalog = _catalog(root)
    checks = {
        "version": __version__,
        "pipeline_stages": list(ReplayPipeline.DESCRIPTION.stages),
        "pipeline_invariants": list(ReplayPipeline.DESCRIPTION.invariants),
        "operators": [operator.name for operator in operator_catalog()],
        "adapters": [descriptor.name for descriptor in adapter_registry().descriptors()],
        "scenario_count": len(catalog),
        "invalid_scenarios": [entry for entry in catalog if not entry["valid"]],
    }
    checks["passed"] = bool(catalog) and not checks["invalid_scenarios"]
    return checks


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
            result = run_scenario(args.scenario, max_events=args.max_events)
            bundle = write_bundle(result, args.output)
            print(f"replayed {len(result.events)} events; detections={len(result.detections)}")
            _print_verification(result)
            print(f"plan: {result.plan.fingerprint}")
            print(f"ledger: {result.ledger.root_hash}")
            print(f"bundle: {bundle.bundle_id}")
            print(f"manifest: {bundle.manifest_path}")
            return 0 if result.verification.passed or args.allow_mismatch else 3
        if args.command == "verify":
            result = run_scenario(args.scenario)
            _print_verification(result)
            return 0 if result.verification.passed else 3
        if args.command == "explain":
            result = run_scenario(args.scenario)
            payload = {
                "scenario": {
                    "id": result.scenario.scenario_id,
                    "title": result.scenario.title,
                    "objective": result.scenario.objective,
                    "authorization_boundary": result.scenario.authorization_boundary,
                },
                "plan": result.plan.to_dict(),
                "expectations": {
                    "detection_count": result.scenario.expectations.detection_count,
                    "rule_ids": list(result.scenario.expectations.rule_ids),
                    "severity_counts": result.scenario.expectations.severity_counts,
                    "simulated_action_count": result.scenario.expectations.simulated_action_count,
                },
                "run_id": result.loaded.run_id,
                "ledger_root": result.ledger.root_hash,
            }
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"{result.scenario.scenario_id}: {result.scenario.title}")
                print(f"objective: {result.scenario.objective}")
                print(f"boundary: {result.scenario.authorization_boundary}")
                print(f"run_id: {result.loaded.run_id}")
                print(f"plan: {result.plan.fingerprint}")
                for rule in result.plan.rules:
                    hint = (
                        "full_scan"
                        if rule.candidate_hint is None
                        else f"{rule.candidate_hint.mode}:{rule.candidate_hint.field}"
                    )
                    print(f"rule {rule.source.rule_id}: {rule.source.name} [{rule.source.severity}] candidate={hint}")
                print(f"expected detections: {result.scenario.expectations.detection_count}")
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
        if args.command == "normalize":
            adapter_result = normalize_file(args.adapter, args.source, args.destination)
            print(
                f"normalized {adapter_result.adapter.name}: read={adapter_result.records_read} "
                f"written={adapter_result.records_written} skipped={adapter_result.records_skipped} "
                f"sha256={adapter_result.output_sha256} output={adapter_result.destination}"
            )
            return 0
        if args.command == "normalize-suricata":
            adapter_result = normalize_suricata_file(args.source, args.destination)
            print(
                f"normalized {adapter_result.adapter.name}: read={adapter_result.records_read} "
                f"written={adapter_result.records_written} skipped={adapter_result.records_skipped} "
                f"sha256={adapter_result.output_sha256} output={adapter_result.destination}"
            )
            return 0
        if args.command == "adapters":
            descriptors = [
                {
                    "name": item.name,
                    "version": item.version,
                    "source_format": item.source_format,
                    "supported_record_types": list(item.supported_record_types),
                    "safety_boundary": item.safety_boundary,
                }
                for item in adapter_registry().descriptors()
            ]
            if args.json:
                print(json.dumps(descriptors, indent=2, sort_keys=True))
            else:
                for item in descriptors:
                    print(f"{item['name']} {item['version']}: {item['source_format']}")
            return 0
        if args.command == "graph":
            description = ReplayPipeline.DESCRIPTION
            if args.format == "json":
                print(json.dumps(description.to_dict(), indent=2, sort_keys=True))
            elif args.format == "mermaid":
                print(_pipeline_mermaid())
            else:
                print(" -> ".join(description.stages))
                for invariant in description.invariants:
                    print(f"  invariant: {invariant}")
            return 0
        if args.command == "doctor":
            payload = _doctor(Path(args.scenarios))
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"doctor: {'PASS' if payload['passed'] else 'FAIL'}")
                print(f"version: {payload['version']}")
                print(f"stages: {' -> '.join(payload['pipeline_stages'])}")
                print(f"operators: {', '.join(payload['operators'])}")
                print(f"adapters: {', '.join(payload['adapters'])}")
                print(f"scenarios: {payload['scenario_count']}")
            return 0 if payload["passed"] else 5
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
            return 0 if entries and all(entry["valid"] for entry in entries) else 2
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
