from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._version import __version__
from .io import atomic_write_text
from .ledger import verify_ledger_payload
from .models import ValidationError, VerificationCheck, VerificationResult
from .result import ReplayResult
from .serialization import digest_object, pretty_json, sha256_bytes

_REPORT_JSON = "report.json"
_REPORT_MARKDOWN = "report.md"
_MANIFEST_JSON = "manifest.json"


def render_json(result: ReplayResult) -> str:
    return pretty_json(result.to_dict())


def render_markdown(result: ReplayResult) -> str:
    verdict = "PASS" if result.verification.passed else "FAIL"
    lines = [
        f"# Replay report: {result.scenario.title}",
        "",
        f"> **Verification: {verdict}** · Run ID `{result.loaded.run_id}` · Engine `soc-replay {__version__}`",
        "",
        "## Decision summary",
        "",
        "| Measure | Result |",
        "| --- | ---: |",
        f"| Events processed | {len(result.events)} |",
        f"| Compiled rules | {len(result.plan.rules)} |",
        f"| Detections | {len(result.detections)} |",
        f"| Simulated actions | {len(result.simulated_actions)} |",
        f"| Expectations verified | {'Yes' if result.verification.passed else 'No'} |",
        "",
        "## Provenance and execution identity",
        "",
        f"- **Scenario SHA-256:** `{result.loaded.scenario_sha256}`",
        f"- **Events SHA-256:** `{result.loaded.events_sha256}`",
        f"- **Deterministic run ID:** `{result.loaded.run_id}`",
        f"- **Execution-plan fingerprint:** `{result.plan.fingerprint}`",
        f"- **Execution-ledger root:** `{result.ledger.root_hash}`",
        "",
        "## Execution ledger",
        "",
        "| # | Stage | In | Out | Entry hash |",
        "| ---: | --- | ---: | ---: | --- |",
    ]
    for entry in result.ledger.entries:
        lines.append(
            f"| {entry.sequence} | `{entry.stage}` | {entry.records_in} | "
            f"{entry.records_out} | `{entry.entry_hash[:16]}…` |"
        )
    lines.extend(
        [
            "",
            (
                "Each ledger entry commits to the prior entry, stage inputs, stage outputs, "
                "record counts, and deterministic metadata."
            ),
            "",
            "## Verification checks",
            "",
            "| Check | Expected | Actual | Result |",
            "| --- | --- | --- | --- |",
        ]
    )
    for check in result.verification.checks:
        lines.append(
            f"| `{check.name}` | `{json.dumps(check.expected, sort_keys=True)}` | "
            f"`{json.dumps(check.actual, sort_keys=True)}` | {'PASS' if check.passed else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "## Authorization boundary",
            "",
            result.scenario.authorization_boundary,
            "",
            "## Expected outcome",
            "",
            result.scenario.expected_outcome,
            "",
            "## Detections",
            "",
        ]
    )
    if not result.detections:
        lines.append("No rules produced a detection.")
    else:
        for detection in result.detections:
            lines.extend(
                [
                    f"### {detection.detection_id} — {detection.rule_name}",
                    "",
                    f"- **Severity:** {detection.severity}",
                    f"- **First seen:** {detection.first_seen.isoformat()}",
                    f"- **Last seen:** {detection.last_seen.isoformat()}",
                    f"- **Evidence events:** {', '.join(detection.event_ids)}",
                    f"- **Group:** `{json.dumps(detection.group, sort_keys=True)}`",
                    f"- **Correlation:** `{json.dumps(detection.correlation, sort_keys=True)}`",
                    f"- **Response:** `{detection.response.action}` ({detection.response.mode})",
                    f"- **Purpose:** {detection.response.description}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Safety note",
            "",
            (
                "All responses are simulations. The package does not contact infrastructure, "
                "execute commands, or change accounts."
            ),
            "",
        ]
    )
    return "\n".join(lines)


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
        "manifest_schema_version": "2.0",
        "engine": {"name": "soc-replay", "version": __version__},
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


def verify_bundle(directory: str | Path) -> VerificationResult:
    bundle_dir = Path(directory)
    manifest = _read_object(bundle_dir / _MANIFEST_JSON, "bundle manifest")
    report = _read_object(bundle_dir / _REPORT_JSON, "JSON report")
    checks: list[VerificationCheck] = []

    def add(name: str, expected: Any, actual: Any) -> None:
        checks.append(VerificationCheck(name, expected, actual, actual == expected))

    add("manifest_schema_version", "2.0", manifest.get("manifest_schema_version"))
    add("report_schema_version", "2.0", report.get("report_schema_version"))
    add("engine_name", "soc-replay", manifest.get("engine", {}).get("name"))
    add("engine_version", report.get("engine", {}).get("version"), manifest.get("engine", {}).get("version"))
    add("run_id", report.get("provenance", {}).get("run_id"), manifest.get("run_id"))
    add(
        "scenario_sha256",
        report.get("provenance", {}).get("scenario_sha256"),
        manifest.get("inputs", {}).get("scenario_sha256"),
    )
    add(
        "events_sha256",
        report.get("provenance", {}).get("events_sha256"),
        manifest.get("inputs", {}).get("events_sha256"),
    )
    execution = report.get("execution")
    if not isinstance(execution, dict):
        raise ValidationError("JSON report.execution must be an object")
    plan = execution.get("plan")
    ledger = execution.get("ledger")
    if not isinstance(plan, dict):
        raise ValidationError("JSON report.execution.plan must be an object")
    ledger_valid, ledger_errors = verify_ledger_payload(ledger)
    add("ledger_valid", True, ledger_valid)
    add("ledger_errors", [], list(ledger_errors))
    add("plan_fingerprint", plan.get("fingerprint"), manifest.get("plan_fingerprint"))
    add("ledger_root", ledger.get("root_hash") if isinstance(ledger, dict) else None, manifest.get("ledger_root"))
    add(
        "verification_passed",
        report.get("verification", {}).get("passed"),
        manifest.get("verification_passed"),
    )

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValidationError("bundle manifest.artifacts must be an object")
    add("artifact_names", [_REPORT_JSON, _REPORT_MARKDOWN], sorted(artifacts))
    for filename in (_REPORT_JSON, _REPORT_MARKDOWN):
        record = artifacts.get(filename)
        if not isinstance(record, dict):
            raise ValidationError(f"bundle manifest missing artifact record: {filename}")
        artifact_path = bundle_dir / filename
        try:
            content = artifact_path.read_bytes()
        except FileNotFoundError as exc:
            raise ValidationError(f"bundle artifact is missing: {artifact_path}") from exc
        add(f"{filename}.sha256", record.get("sha256"), sha256_bytes(content))
        add(f"{filename}.bytes", record.get("bytes"), len(content))

    core = {key: value for key, value in manifest.items() if key != "bundle_id"}
    add("bundle_id", digest_object(core), manifest.get("bundle_id"))
    return VerificationResult(all(check.passed for check in checks), tuple(checks))
