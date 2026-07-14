from __future__ import annotations

from .bundle_verify_detections import check_detections
from .bundle_verify_plan import check_plan
from .bundle_verify_support import BundleState, CheckCollector, DerivedState


def check_identity(state: BundleState, checks: CheckCollector) -> DerivedState:
    derived = check_plan(state, checks)
    check_detections(state, derived, checks)
    return derived
