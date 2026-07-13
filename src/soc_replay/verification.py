from __future__ import annotations

from collections import Counter

from .models import Detection, Scenario, VerificationCheck, VerificationResult


def verify_result(scenario: Scenario, detections: tuple[Detection, ...]) -> VerificationResult:
    expected = scenario.expectations
    actual_rule_ids = sorted(detection.rule_id for detection in detections)
    actual_severity_counts = dict(sorted(Counter(detection.severity for detection in detections).items()))
    expected_severity_counts = dict(sorted(expected.severity_counts.items()))
    checks = (
        VerificationCheck(
            "detection_count", expected.detection_count, len(detections), len(detections) == expected.detection_count
        ),
        VerificationCheck(
            "rule_ids", sorted(expected.rule_ids), actual_rule_ids, actual_rule_ids == sorted(expected.rule_ids)
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
    )
    return VerificationResult(all(check.passed for check in checks), checks)
