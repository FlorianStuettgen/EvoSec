from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from soc_replay.adapters import normalize_file
from soc_replay.engine import run_scenario
from soc_replay.report import write_bundle

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "network-scan",
    "privileged-group-change",
    "failed-authentication-burst",
    "benign-privileged-change",
)
SCHEMA_FILES = (
    "event.schema.json",
    "scenario.schema.json",
    "execution-ledger.schema.json",
    "report.schema.json",
    "bundle-manifest.schema.json",
)


def _load_schemas(root: Path) -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas: dict[str, dict[str, Any]] = {}
    resources: list[tuple[str, Resource[Any]]] = []
    for filename in SCHEMA_FILES:
        path = root / "schemas" / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain an object")
        Draft202012Validator.check_schema(payload)
        schema_id = payload.get("$id")
        if not isinstance(schema_id, str):
            raise ValueError(f"{path} requires a string $id")
        schemas[filename] = payload
        resources.append((schema_id, Resource.from_contents(payload)))
    return schemas, Registry().with_resources(resources)


def _validator(schema: dict[str, Any], registry: Registry) -> Draft202012Validator:
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def _collect_errors(
    validator: Draft202012Validator,
    instance: Any,
    label: str,
    errors: list[str],
) -> None:
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path)
        suffix = f".{location}" if location else ""
        errors.append(f"{label}{suffix}: {error.message}")


def validate_repository_contracts(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        schemas, registry = _load_schemas(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"schema loading failed: {exc}"]

    event_validator = _validator(schemas["event.schema.json"], registry)
    scenario_validator = _validator(schemas["scenario.schema.json"], registry)
    report_validator = _validator(schemas["report.schema.json"], registry)
    manifest_validator = _validator(schemas["bundle-manifest.schema.json"], registry)
    ledger_validator = _validator(schemas["execution-ledger.schema.json"], registry)

    for name in SCENARIOS:
        scenario_dir = root / "scenarios" / name
        try:
            scenario_payload = json.loads((scenario_dir / "scenario.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{name}/scenario.json: {exc}")
            continue
        _collect_errors(scenario_validator, scenario_payload, f"{name}/scenario.json", errors)

        try:
            lines = (scenario_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(f"{name}/events.jsonl: {exc}")
            continue
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                event_payload = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{name}/events.jsonl:{line_number}: {exc}")
                continue
            _collect_errors(event_validator, event_payload, f"{name}/events.jsonl:{line_number}", errors)

        try:
            result = run_scenario(scenario_dir)
            with TemporaryDirectory() as temporary:
                bundle = write_bundle(result, temporary)
                report_payload = json.loads(bundle.json_path.read_text(encoding="utf-8"))
                manifest_payload = json.loads(bundle.manifest_path.read_text(encoding="utf-8"))
                _collect_errors(report_validator, report_payload, f"{name}/report.json", errors)
                _collect_errors(manifest_validator, manifest_payload, f"{name}/manifest.json", errors)
                _collect_errors(
                    ledger_validator,
                    report_payload.get("execution", {}).get("ledger"),
                    f"{name}/execution-ledger",
                    errors,
                )
        except Exception as exc:  # repository auditor must aggregate failures
            errors.append(f"{name}/generated-bundle: {type(exc).__name__}: {exc}")

    adapter_source = root / "examples" / "adapters" / "suricata-eve.jsonl"
    if adapter_source.exists():
        try:
            with TemporaryDirectory() as temporary:
                destination = Path(temporary) / "normalized.jsonl"
                normalize_file("suricata-eve", adapter_source, destination)
                for line_number, line in enumerate(destination.read_text(encoding="utf-8").splitlines(), start=1):
                    _collect_errors(
                        event_validator,
                        json.loads(line),
                        f"suricata-normalized:{line_number}",
                        errors,
                    )
        except Exception as exc:
            errors.append(f"suricata-normalized: {type(exc).__name__}: {exc}")
    return errors


def main() -> int:
    errors = validate_repository_contracts()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"contract validation: PASS ({len(SCENARIOS)} scenarios, {len(SCHEMA_FILES)} schemas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
