from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._version import __version__
from .contracts import ENGINE_NAME, MANIFEST_SCHEMA_VERSION, PIPELINE_STAGES, REPORT_SCHEMA_VERSION
from .io import atomic_write_text
from .ledger import verify_ledger_payload
from .models import ValidationError, VerificationCheck, VerificationResult
from .report_render import render_json, render_markdown
from .result import ReplayResult
from .serialization import digest_object, pretty_json, sha256_bytes

_REPORT_JSON = "report.json"
_REPORT_MARKDOWN = "report.md"
_MANIFEST_JSON = "manifest.json"

@dataclass(frozen=True, slots=True)
class ReportBundle:
    directory: Path
    json_path: Path
    markdown_path: Path
    manifest_path: Path
    bundle_id: str


def _artifact_record(content: str) -> dict[str, Any]:
    encoded = content.encode("utf-8")
    return {"sha256": sha256_bytes(encoded), "bytes": len(encoded)}


def _manifest_core(result: ReplayResult, json_content: str, markdown_content: str) -> dict[str, Any]:
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": __version__},
        "run_id": result.loaded.run_id,
        "plan_fingerprint": result.plan.fingerprint,
        "ledger_root": result.ledger.root_hash,
        "inputs": {
            "scenario_sha256": result.loaded.scenario_sha256,
            "events_sha256": result.loaded.events_sha256,
        },
        "verification_passed": result.verification.passed,
        "artifacts": {
            _REPORT_JSON: _artifact_record(json_content),
            _REPORT_MARKDOWN: _artifact_record(markdown_content),
        },
    }


def render_manifest(result: ReplayResult, json_content: str, markdown_content: str) -> str:
    core = _manifest_core(result, json_content, markdown_content)
    return pretty_json({**core, "bundle_id": digest_object(core)})


def write_bundle(result: ReplayResult, output_dir: str | Path) -> ReportBundle:
    destination = Path(output_dir)
    json_path = destination / _REPORT_JSON
    markdown_path = destination / _REPORT_MARKDOWN
    manifest_path = destination / _MANIFEST_JSON
    json_content = render_json(result)
    markdown_content = render_markdown(result)
    manifest_content = render_manifest(result, json_content, markdown_content)
    manifest = json.loads(manifest_content)
    # Manifest-last commit protocol: its presence indicates both artifacts were fully replaced.
    atomic_write_text(json_path, json_content)
    atomic_write_text(markdown_path, markdown_content)
    atomic_write_text(manifest_path, manifest_content)
    return ReportBundle(destination, json_path, markdown_path, manifest_path, str(manifest["bundle_id"]))


def write_reports(result: ReplayResult, output_dir: str | Path) -> tuple[Path, Path]:
    bundle = write_bundle(result, output_dir)
    return bundle.json_path, bundle.markdown_path


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"{label} must contain a JSON object: {path}")
    return payload


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be an array")
    return value


def _objects(value: Any, label: str) -> list[dict[str, Any]]:
    items = _array(value, label)
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError(f"{label}[{index}] must be an object")
        normalized.append(item)
    return normalized


def verify_bundle(directory: str | Path) -> VerificationResult:
    bundle_dir = Path(directory)
    manifest = _read_object(bundle_dir / _MANIFEST_JSON, "bundle manifest")
    report = _read_object(bundle_dir / _REPORT_JSON, "JSON report")
    checks: list[VerificationCheck] = []

    def add(name: str, expected: Any, actual: Any) -> None:
        checks.append(VerificationCheck(name, expected, actual, actual == expected))

    expected_manifest_fields = {
        "manifest_schema_version",
        "bundle_id",
        "engine",
        "run_id",
        "plan_fingerprint",
        "ledger_root",
        "inputs",
        "verification_passed",
        "artifacts",
    }
    expected_report_fields = {
        "report_schema_version",
        "engine",
        "provenance",
        "execution",
        "scenario",
        "summary",
        "verification",
        "detections",
        "simulated_actions",
    }
    add("manifest_fields", sorted(expected_manifest_fields), sorted(manifest))
    add("report_fields", sorted(expected_report_fields), sorted(report))
    add("manifest_schema_version", MANIFEST_SCHEMA_VERSION, manifest.get("manifest_schema_version"))
    add("report_schema_version", REPORT_SCHEMA_VERSION, report.get("report_schema_version"))

    manifest_engine = _object(manifest.get("engine"), "bundle manifest.engine")
    report_engine = _object(report.get("engine"), "JSON report.engine")
    provenance = _object(report.get("provenance"), "JSON report.provenance")
    inputs = _object(manifest.get("inputs"), "bundle manifest.inputs")
    execution = _object(report.get("execution"), "JSON report.execution")
    plan = _object(execution.get("plan"), "JSON report.execution.plan")
    traces = _objects(execution.get("rules"), "JSON report.execution.rules")
    ledger = _object(execution.get("ledger"), "JSON report.execution.ledger")
    scenario = _object(report.get("scenario"), "JSON report.scenario")
    summary = _object(report.get("summary"), "JSON report.summary")
    verification = _object(report.get("verification"), "JSON report.verification")
    verification_checks = _objects(verification.get("checks"), "JSON report.verification.checks")
    detections = _objects(report.get("detections"), "JSON report.detections")
    actions = _objects(report.get("simulated_actions"), "JSON report.simulated_actions")

    add("engine_name", ENGINE_NAME, manifest_engine.get("name"))
    add("report_engine_name", ENGINE_NAME, report_engine.get("name"))
    add("engine_version", report_engine.get("version"), manifest_engine.get("version"))
    add("run_id", provenance.get("run_id"), manifest.get("run_id"))
    add("scenario_sha256", provenance.get("scenario_sha256"), inputs.get("scenario_sha256"))
    add("events_sha256", provenance.get("events_sha256"), inputs.get("events_sha256"))
    add("scenario_id", scenario.get("id"), plan.get("scenario_id"))

    ledger_valid, ledger_errors = verify_ledger_payload(ledger, require_complete=True)
    add("ledger_valid", True, ledger_valid)
    add("ledger_errors", [], list(ledger_errors))
    add("plan_fingerprint", plan.get("fingerprint"), manifest.get("plan_fingerprint"))
    add("ledger_root", ledger.get("root_hash"), manifest.get("ledger_root"))
    add("verification_passed", verification.get("passed"), manifest.get("verification_passed"))
    add("summary_verification_passed", verification.get("passed"), summary.get("verification_passed"))

    plan_rules = _objects(plan.get("rules"), "JSON report.execution.plan.rules")
    plan_rule_ids = [item.get("id") for item in plan_rules]
    trace_rule_ids = [item.get("rule_id") for item in traces]
    add("plan_rule_ids_unique", len(plan_rule_ids), len(set(plan_rule_ids)))
    add("plan_trace_rule_ids", plan_rule_ids, trace_rule_ids)
    add("rules_executed", len(traces), summary.get("rules_executed"))

    plan_fingerprints = {item.get("id"): item.get("fingerprint") for item in plan_rules}
    trace_fingerprints = {item.get("rule_id"): item.get("rule_fingerprint") for item in traces}
    add("trace_rule_fingerprints", plan_fingerprints, trace_fingerprints)

    for index, trace in enumerate(traces):
        candidate_count = trace.get("candidate_count")
        matched_count = trace.get("matched_count")
        detection_count = trace.get("detection_count")
        add(
            f"rule_trace[{index}].candidate_bounds",
            True,
            isinstance(candidate_count, int)
            and not isinstance(candidate_count, bool)
            and isinstance(matched_count, int)
            and not isinstance(matched_count, bool)
            and 0 <= matched_count <= candidate_count,
        )
        add(
            f"rule_trace[{index}].detection_count",
            True,
            isinstance(detection_count, int)
            and not isinstance(detection_count, bool)
            and detection_count >= 0,
        )

    add("detection_count", len(detections), summary.get("detections"))
    add("simulated_action_count", len(actions), summary.get("simulated_actions"))
    add("action_per_detection", len(detections), len(actions))
    trace_detection_counts = [item.get("detection_count") for item in traces]
    trace_detection_sum = 0
    trace_detection_valid = True
    for value in trace_detection_counts:
        if not isinstance(value, int) or isinstance(value, bool):
            trace_detection_valid = False
            break
        trace_detection_sum += value
    trace_detection_total: int | None = trace_detection_sum if trace_detection_valid else None
    add("trace_detection_count", len(detections), trace_detection_total)

    expected_actions: list[dict[str, Any]] = []
    detection_ids: list[Any] = []
    response_modes: list[Any] = []
    for index, detection in enumerate(detections):
        response = _object(detection.get("response"), f"JSON report.detections[{index}].response")
        detection_id = detection.get("detection_id")
        detection_ids.append(detection_id)
        response_modes.append(response.get("mode"))
        expected_actions.append(
            {
                "detection_id": detection_id,
                "action": response.get("action"),
                "description": response.get("description"),
                "mode": response.get("mode"),
            }
        )
    add("detection_ids_unique", len(detection_ids), len(set(detection_ids)))
    add("simulation_only_responses", ["simulated"] * len(response_modes), response_modes)
    add("simulated_actions_match_detections", expected_actions, actions)

    entries = _objects(ledger.get("entries"), "JSON report.execution.ledger.entries")
    by_stage = {entry.get("stage"): entry for entry in entries}
    add("ledger_stage_order", list(PIPELINE_STAGES), [entry.get("stage") for entry in entries])
    if ledger_valid:
        load_entry = by_stage["load"]
        compile_entry = by_stage["compile"]
        index_entry = by_stage["index"]
        evaluate_entry = by_stage["evaluate"]
        verify_entry = by_stage["verify"]
        events_processed = summary.get("events_processed")
        add("load_records_out", events_processed, load_entry.get("records_out"))
        add("compile_records_in", len(plan_rules), compile_entry.get("records_in"))
        add("compile_records_out", len(plan_rules), compile_entry.get("records_out"))
        add("index_records_in", events_processed, index_entry.get("records_in"))
        add("index_records_out", events_processed, index_entry.get("records_out"))
        add("evaluate_records_in", events_processed, evaluate_entry.get("records_in"))
        add("evaluate_records_out", len(detections), evaluate_entry.get("records_out"))
        add("verify_records_in", len(detections), verify_entry.get("records_in"))
        add("verify_records_out", len(verification_checks), verify_entry.get("records_out"))

    artifacts = _object(manifest.get("artifacts"), "bundle manifest.artifacts")
    add("artifact_names", [_REPORT_JSON, _REPORT_MARKDOWN], sorted(artifacts))
    for filename in (_REPORT_JSON, _REPORT_MARKDOWN):
        record = _object(artifacts.get(filename), f"bundle manifest.artifacts.{filename}")
        artifact_path = bundle_dir / filename
        try:
            content = artifact_path.read_bytes()
        except FileNotFoundError as exc:
            raise ValidationError(f"bundle artifact is missing: {artifact_path}") from exc
        add(f"{filename}.sha256", record.get("sha256"), sha256_bytes(content))
        add(f"{filename}.bytes", record.get("bytes"), len(content))

    core = {key: value for key, value in manifest.items() if key != "bundle_id"}
    add("bundle_id", digest_object(core), manifest.get("bundle_id"))
    frozen_checks = tuple(checks)
    return VerificationResult(all(check.passed for check in frozen_checks), frozen_checks)
