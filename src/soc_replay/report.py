from __future__ import annotations

import json
from pathlib import Path

from .engine import ReplayResult


def render_markdown(result: ReplayResult) -> str:
    lines = [
        f"# Replay report: {result.scenario.title}",
        "",
        "## Decision summary",
        "",
        "| Measure | Result |",
        "| --- | ---: |",
        f"| Events processed | {len(result.events)} |",
        f"| Detections | {len(result.detections)} |",
        f"| Simulated actions | {len(result.simulated_actions)} |",
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
                    f"- **Response:** `{detection.response.action}` ({detection.response.mode})",
                    f"- **Purpose:** {detection.response.description}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Safety note",
            "",
            "All responses in this report are simulations. The replay engine does not connect to firewalls, hypervisors, endpoints, or production services.",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(result: ReplayResult, output_dir: str | Path) -> tuple[Path, Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "report.json"
    markdown_path = destination / "report.md"
    json_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    return json_path, markdown_path
