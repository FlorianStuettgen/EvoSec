from __future__ import annotations

from collections import Counter
from typing import Any

from .bundle_verify_support import BundleState, CheckCollector, required_string


def check_expectations(
    state: BundleState,
    detection_rule_ids: list[str],
    detection_severities: list[str],
    detection_contracts: list[dict[str, Any]],
    checks: CheckCollector,
) -> None:
    actuals: dict[str, Any] = {
        "detection_count": len(state.detections),
        "rule_ids": detection_rule_ids,
        "severity_counts": dict(sorted(Counter(detection_severities).items())),
        "simulated_action_count": len(state.detections),
        "detection_contracts": detection_contracts,
    }
    names = [
        required_string(check.get("name"), f"JSON report.verification.checks[{index}].name")
        for index, check in enumerate(state.verification_checks)
    ]
    required_names = {"detection_count", "rule_ids", "severity_counts", "simulated_action_count"}
    if state.scenario.get("schema_version") == "1.1":
        required_names.add("detection_contracts")
    allowed_names = required_names | {"detection_contracts"}
    checks.add("verification_fields", ["checks", "passed"], sorted(state.verification))
    checks.add("verification_check_names_unique", len(names), len(set(names)))
    checks.add("verification_required_checks", [], sorted(required_names - set(names)))
    checks.add("verification_unknown_checks", [], sorted(set(names) - allowed_names))
    recomputed_passes: list[bool] = []
    for index, check in enumerate(state.verification_checks):
        checks.add(
            f"verification.check[{index}].fields",
            ["actual", "expected", "name", "passed"],
            sorted(check),
        )
        name = names[index]
        if name not in actuals:
            recomputed_passes.append(False)
            continue
        actual = actuals[name]
        checks.add(f"verification.{name}.actual", actual, check.get("actual"))
        recomputed_passed = check.get("expected") == actual
        recomputed_passes.append(recomputed_passed)
        checks.add(f"verification.{name}.passed", recomputed_passed, check.get("passed"))
    names_valid = (
        len(names) == len(set(names))
        and required_names.issubset(set(names))
        and set(names).issubset(allowed_names)
    )
    checks.add(
        "verification_passed_recomputed",
        names_valid and all(recomputed_passes),
        state.verification.get("passed"),
    )
