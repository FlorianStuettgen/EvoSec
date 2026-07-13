from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .engine import ReplayResult


def render_markdown(result: ReplayResult) -> str:
    verdict = "PASS" if result.verification.passed else "FAIL"
    engine_version = result.to_dict()["engine"]["version"]
    lines = [
        f"# Replay report: {result.scenario.title}",
        "",
        (f"> **Verification: {verdict}** · Run ID `{result.loaded.run_id}` · Engine `soc-replay {engine_version}`"),
        "",
        "## Decision summary",
        "",
        "| Measure | Result |",
        "| --- | ---: |",
        f"| Events processed | {len(result.events)} |",
        f"| Detections | {len(result.detections)} |",
        f"| Simulated actions | {len(result.simulated_actions)} |",
        f"| Expectations verified | {'Yes' if result.verification.passed else 'No'} |",
        "",
        "## Provenance",
        "",
        f"- **Scenario SHA-256:** `{result.loaded.scenario_sha256}`",
        f"- **Events SHA-256:** `{result.loaded.events_sha256}`",
        f"- **Deterministic run ID:** `{result.loaded.run_id}`",
        "",
        "## Verification checks",
        "",
        "| Check | Expected | Actual | Result |",
        "| --- | --- | --- | --- |",
    ]
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
                "All responses in this report are simulations. The replay engine does not connect to firewalls, "
                "hypervisors, endpoints, identity providers, or production services."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, newline="") as handle:
        handle.write(content)
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_reports(result: ReplayResult, output_dir: str | Path) -> tuple[Path, Path]:
    destination = Path(output_dir)
    json_path = destination / "report.json"
    markdown_path = destination / "report.md"
    _atomic_write(json_path, json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n")
    _atomic_write(markdown_path, render_markdown(result))
    return json_path, markdown_path
