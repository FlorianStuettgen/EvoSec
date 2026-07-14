from __future__ import annotations

from .bundle_verify_expectations import check_expectations
from .bundle_verify_support import BundleState, CheckCollector, DerivedState
from .bundle_verify_trace import check_trace_evidence


def check_detections(state: BundleState, derived: DerivedState, checks: CheckCollector) -> None:
    rule_ids, severities, contracts = check_trace_evidence(state, derived, checks)
    check_expectations(state, rule_ids, severities, contracts, checks)
