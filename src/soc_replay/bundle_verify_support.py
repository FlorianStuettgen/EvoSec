from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .bundle import render_manifest
from .contracts import INDEX_FIELDS
from .models import ValidationError, VerificationCheck
from .report_render import render_json, render_markdown
from .serialization import sha256_bytes

REPORT_JSON = "report.json"
REPORT_MARKDOWN = "report.md"
MANIFEST_JSON = "manifest.json"


@dataclass(frozen=True, slots=True)
class BundleState:
    directory: Path
    manifest: dict[str, Any]
    report: dict[str, Any]
    manifest_engine: dict[str, Any]
    report_engine: dict[str, Any]
    provenance: dict[str, Any]
    inputs: dict[str, Any]
    plan: dict[str, Any]
    traces: list[dict[str, Any]]
    ledger: dict[str, Any]
    scenario: dict[str, Any]
    summary: dict[str, Any]
    verification: dict[str, Any]
    verification_checks: list[dict[str, Any]]
    detections: list[dict[str, Any]]
    actions: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class DerivedState:
    plan_rules: list[dict[str, Any]]
    plan_rule_ids: list[str]
    plan_rule_fingerprints: list[str]
    trace_rule_ids: list[str]


class CheckCollector:
    def __init__(self) -> None:
        self.items: list[VerificationCheck] = []

    def add(self, name: str, expected: Any, actual: Any) -> None:
        self.items.append(VerificationCheck(name, expected, actual, actual == expected))


def read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"{label} must contain a JSON object: {path}")
    return payload


def object_value(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be an object")
    return value


def array_value(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be an array")
    return value


def object_array(value: Any, label: str) -> list[dict[str, Any]]:
    items = array_value(value, label)
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError(f"{label}[{index}] must be an object")
        normalized.append(item)
    return normalized


def required_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def parse_bundle(directory: str | Path) -> BundleState:
    bundle_dir = Path(directory)
    manifest = read_object(bundle_dir / MANIFEST_JSON, "bundle manifest")
    report = read_object(bundle_dir / REPORT_JSON, "JSON report")
    execution = object_value(report.get("execution"), "JSON report.execution")
    verification = object_value(report.get("verification"), "JSON report.verification")
    return BundleState(
        directory=bundle_dir,
        manifest=manifest,
        report=report,
        manifest_engine=object_value(manifest.get("engine"), "bundle manifest.engine"),
        report_engine=object_value(report.get("engine"), "JSON report.engine"),
        provenance=object_value(report.get("provenance"), "JSON report.provenance"),
        inputs=object_value(manifest.get("inputs"), "bundle manifest.inputs"),
        plan=object_value(execution.get("plan"), "JSON report.execution.plan"),
        traces=object_array(execution.get("rules"), "JSON report.execution.rules"),
        ledger=object_value(execution.get("ledger"), "JSON report.execution.ledger"),
        scenario=object_value(report.get("scenario"), "JSON report.scenario"),
        summary=object_value(report.get("summary"), "JSON report.summary"),
        verification=verification,
        verification_checks=object_array(verification.get("checks"), "JSON report.verification.checks"),
        detections=object_array(report.get("detections"), "JSON report.detections"),
        actions=object_array(report.get("simulated_actions"), "JSON report.simulated_actions"),
    )


def detection_contract(detection: dict[str, Any], index: int) -> dict[str, Any]:
    response = object_value(detection.get("response"), f"JSON report.detections[{index}].response")
    return {
        "rule_id": detection.get("rule_id"),
        "severity": detection.get("severity"),
        "event_ids": detection.get("event_ids"),
        "group": detection.get("group"),
        "action": response.get("action"),
    }


def candidate_strategy(plan_rule: dict[str, Any], index: int) -> tuple[str, int]:
    selectors = object_array(
        plan_rule.get("candidate_selectors"),
        f"JSON report.execution.plan.rules[{index}].candidate_selectors",
    )
    labels: list[str] = []
    for selector_index, selector in enumerate(selectors):
        prefix = f"JSON report.execution.plan.rules[{index}].candidate_selectors[{selector_index}]"
        field = required_string(selector.get("field"), f"{prefix}.field")
        mode = required_string(selector.get("mode"), f"{prefix}.mode")
        value = required_string(selector.get("value"), f"{prefix}.value")
        if field == "tags" and mode == "contains":
            labels.append(f"tag:{value}")
        elif mode == "eq" and field in INDEX_FIELDS:
            labels.append(f"eq:{field}={value}")
        else:
            raise ValidationError(
                "candidate selector is not a supported deterministic index plan: "
                f"field={field!r}, mode={mode!r}"
            )
    if not labels:
        return "full_scan", 0
    if len(labels) == 1:
        return labels[0], len(set(labels))
    return f"intersection[{','.join(labels)}]", len(set(labels))


def append_source_checks(
    checks: CheckCollector,
    bundle_dir: Path,
    source_directory: str | Path,
) -> None:
    from .engine import run_scenario

    result = run_scenario(source_directory)
    expected_json = render_json(result)
    expected_markdown = render_markdown(result)
    expected_manifest = render_manifest(result, expected_json, expected_markdown)
    expected = {
        REPORT_JSON: expected_json.encode("utf-8"),
        REPORT_MARKDOWN: expected_markdown.encode("utf-8"),
        MANIFEST_JSON: expected_manifest.encode("utf-8"),
    }
    for filename, content in expected.items():
        artifact_path = bundle_dir / filename
        try:
            actual = artifact_path.read_bytes()
        except FileNotFoundError as exc:
            raise ValidationError(f"bundle artifact is missing: {artifact_path}") from exc
        checks.add(
            f"source_bound.{filename}.sha256",
            sha256_bytes(content),
            sha256_bytes(actual),
        )
