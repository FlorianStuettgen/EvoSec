from __future__ import annotations

import json

from ._version import __version__
from .contracts import ENGINE_NAME
from .result import ReplayResult
from .serialization import pretty_json, to_primitive


def render_json(result: ReplayResult) -> str:
    return pretty_json(result.to_dict())


def render_markdown(result: ReplayResult) -> str:
    verdict = "PASS" if result.verification.passed else "FAIL"
    lines = [
        f"# Replay report: {result.scenario.title}",
        "",
        f"> **Verification: {verdict}** · Run ID `{result.loaded.run_id}` · Engine `{ENGINE_NAME} {__version__}`",
        "",
        "## Decision summary",
        "",
        "| Measure | Result |",
        "| --- | ---: |",
        f"| Events processed | {len(result.events)} |",
        f"| Rules executed | {len(result.rule_executions)} |",
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
            "## Rule execution trace",
            "",
            "| Rule | Candidates | Matched | Groups | Windows | Detections | Strategy |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for execution in result.rule_executions:
        lines.append(
            f"| `{execution.rule_id}` | {execution.candidate_count} | {execution.matched_count} | "
            f"{execution.group_count} | {execution.windows_considered} | {execution.detection_count} | "
            f"`{execution.candidate_strategy}` |"
        )
    lines.extend(
        [
            "",
            "The trace records every rule, including rules that correctly produced zero detections.",
            "",
            "## Verification checks",
            "",
            "| Check | Expected | Actual | Result |",
            "| --- | --- | --- | --- |",
        ]
    )
    for check in result.verification.checks:
        lines.append(
            f"| `{check.name}` | `{json.dumps(to_primitive(check.expected), sort_keys=True)}` | "
            f"`{json.dumps(to_primitive(check.actual), sort_keys=True)}` | "
            f"{'PASS' if check.passed else 'FAIL'} |"
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
                    f"- **Group:** `{json.dumps(to_primitive(detection.group), sort_keys=True)}`",
                    f"- **Correlation:** `{json.dumps(to_primitive(detection.correlation), sort_keys=True)}`",
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

