from __future__ import annotations

from collections import Counter
from typing import Any

from .bundle_verify_support import (
    BundleState,
    CheckCollector,
    DerivedState,
    detection_contract,
    object_value,
    required_string,
)


def check_trace_evidence(
    state: BundleState,
    derived: DerivedState,
    checks: CheckCollector,
) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    trace_by_rule = {item.get("rule_id"): item for item in state.traces}
    detection_rule_ids = [
        required_string(detection.get("rule_id"), f"JSON report.detections[{index}].rule_id")
        for index, detection in enumerate(state.detections)
    ]
    detection_severities = [
        required_string(detection.get("severity"), f"JSON report.detections[{index}].severity")
        for index, detection in enumerate(state.detections)
    ]
    detection_rule_counts = Counter(detection_rule_ids)
    for index, trace_item in enumerate(state.traces):
        candidate_count = trace_item.get("candidate_count")
        matched_count = trace_item.get("matched_count")
        detection_count = trace_item.get("detection_count")
        candidate_bounds = (
            isinstance(candidate_count, int)
            and not isinstance(candidate_count, bool)
            and isinstance(matched_count, int)
            and not isinstance(matched_count, bool)
            and 0 <= matched_count <= candidate_count
        )
        valid_detection_count = (
            isinstance(detection_count, int) and not isinstance(detection_count, bool) and detection_count >= 0
        )
        checks.add(f"rule_trace[{index}].candidate_bounds", True, candidate_bounds)
        checks.add(f"rule_trace[{index}].detection_count", True, valid_detection_count)
        checks.add(
            f"rule_trace[{index}].detections_by_rule",
            detection_rule_counts.get(derived.trace_rule_ids[index], 0),
            detection_count,
        )

    checks.add("detection_count", len(state.detections), state.summary.get("detections"))
    checks.add("simulated_action_count", len(state.actions), state.summary.get("simulated_actions"))
    checks.add("action_per_detection", len(state.detections), len(state.actions))
    trace_counts = [item.get("detection_count") for item in state.traces]
    valid_trace_counts = all(isinstance(value, int) and not isinstance(value, bool) for value in trace_counts)
    checks.add("trace_detection_count", len(state.detections), sum(trace_counts) if valid_trace_counts else None)

    expected_actions: list[dict[str, Any]] = []
    detection_ids: list[str] = []
    response_modes: list[Any] = []
    contracts: list[dict[str, Any]] = []
    detection_ids_by_rule: dict[str, list[str]] = {}
    for index, detection in enumerate(state.detections):
        response = object_value(detection.get("response"), f"JSON report.detections[{index}].response")
        correlation = object_value(detection.get("correlation"), f"JSON report.detections[{index}].correlation")
        rule_id = detection_rule_ids[index]
        detection_id = required_string(detection.get("detection_id"), f"JSON report.detections[{index}].detection_id")
        detection_ids.append(detection_id)
        response_modes.append(response.get("mode"))
        contracts.append(detection_contract(detection, index))
        detection_ids_by_rule.setdefault(rule_id, []).append(detection_id)
        expected_actions.append(
            {
                "detection_id": detection_id,
                "action": response.get("action"),
                "description": response.get("description"),
                "mode": response.get("mode"),
            }
        )
        detection_trace = trace_by_rule.get(rule_id)
        checks.add(f"detection[{index}].known_rule", True, detection_trace is not None)
        if detection_trace is not None:
            checks.add(
                f"detection[{index}].rule_fingerprint",
                detection_trace.get("rule_fingerprint"),
                correlation.get("rule_fingerprint"),
            )
            checks.add(
                f"detection[{index}].candidate_strategy",
                detection_trace.get("candidate_strategy"),
                correlation.get("candidate_strategy"),
            )
            checks.add(
                f"detection[{index}].candidate_events",
                detection_trace.get("candidate_count"),
                correlation.get("candidate_events"),
            )
            checks.add(
                f"detection[{index}].matched_events",
                detection_trace.get("matched_count"),
                correlation.get("matched_events"),
            )
    checks.add("detection_ids_unique", len(detection_ids), len(set(detection_ids)))
    checks.add("simulation_only_responses", ["simulated"] * len(response_modes), response_modes)
    checks.add("simulated_actions_match_detections", expected_actions, state.actions)
    for rule_id in derived.plan_rule_ids:
        actual_ids = detection_ids_by_rule.get(rule_id, [])
        expected_ids = [f"{rule_id}:{index:03d}" for index in range(1, len(actual_ids) + 1)]
        checks.add(f"detection_ids_sequential[{rule_id}]", expected_ids, actual_ids)
    return detection_rule_ids, detection_severities, contracts
