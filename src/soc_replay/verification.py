from __future__ import annotations

from collections import Counter

from .models import Detection, Scenario, VerificationCheck, VerificationResult
from .serialization import to_primitive


def _detection_contract(detection: Detection) -> dict[str, object]:
    return {
        "rule_id": detection.rule_id,
        "severity": detection.severity,
        "event_ids": list(detection.event_ids),
        "group": to_primitive(detection.group),
        "action": detection.response.action,
    }


def verify_result(scenario: Scenario, detections: tuple[Detection, ...]) -> VerificationResult:
    expected = scenario.expectations
    actual_rule_ids = [detection.rule_id for detection in detections]
    actual_severity_counts = dict(sorted(Counter(detection.severity for detection in detections).items()))
    expected_severity_counts = dict(sorted(expected.severity_counts.items()))
    checks: list[VerificationCheck] = [
        VerificationCheck(
            "detection_count", expected.detection_count, len(detections), len(detections) == expected.detection_count
        ),
        VerificationCheck(
            "rule_ids", list(expected.rule_ids), actual_rule_ids, actual_rule_ids == list(expected.rule_ids)
        ),
        VerificationCheck(
            "severity_counts",
            expected_severity_counts,
            actual_severity_counts,
            actual_severity_counts == expected_severity_counts,
        ),
        VerificationCheck(
            "simulated_action_count",
            expected.simulated_action_count,
            len(detections),
            len(detections) == expected.simulated_action_count,
        ),
    ]
    if expected.detection_contracts is not None:
        expected_contracts = [contract.to_dict() for contract in expected.detection_contracts]
        actual_contracts = [_detection_contract(detection) for detection in detections]
        checks.append(
            VerificationCheck(
                "detection_contracts",
                expected_contracts,
                actual_contracts,
                actual_contracts == expected_contracts,
            )
        )
    frozen_checks = tuple(checks)
    return VerificationResult(all(check.passed for check in frozen_checks), frozen_checks)
