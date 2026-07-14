from __future__ import annotations

from .bundle_verify_support import (
    BundleState,
    CheckCollector,
    DerivedState,
    array_value,
    candidate_strategy,
    object_array,
    required_string,
)
from .contracts import ENGINE_NAME, MANIFEST_SCHEMA_VERSION, REPORT_SCHEMA_VERSION
from .serialization import digest_object, sha256_bytes


def check_plan(state: BundleState, checks: CheckCollector) -> DerivedState:
    expected_manifest_fields = {
        "manifest_schema_version",
        "bundle_id",
        "engine",
        "run_id",
        "plan_fingerprint",
        "ledger_root",
        "inputs",
        "verification_passed",
        "artifacts",
    }
    expected_report_fields = {
        "report_schema_version",
        "engine",
        "provenance",
        "execution",
        "scenario",
        "summary",
        "verification",
        "detections",
        "simulated_actions",
    }
    checks.add("manifest_fields", sorted(expected_manifest_fields), sorted(state.manifest))
    checks.add("report_fields", sorted(expected_report_fields), sorted(state.report))
    checks.add("manifest_schema_version", MANIFEST_SCHEMA_VERSION, state.manifest.get("manifest_schema_version"))
    checks.add("report_schema_version", REPORT_SCHEMA_VERSION, state.report.get("report_schema_version"))
    checks.add("engine_name", ENGINE_NAME, state.manifest_engine.get("name"))
    checks.add("report_engine_name", ENGINE_NAME, state.report_engine.get("name"))
    checks.add("engine_version", state.report_engine.get("version"), state.manifest_engine.get("version"))
    checks.add("run_id", state.provenance.get("run_id"), state.manifest.get("run_id"))
    checks.add("scenario_sha256", state.provenance.get("scenario_sha256"), state.inputs.get("scenario_sha256"))
    checks.add("events_sha256", state.provenance.get("events_sha256"), state.inputs.get("events_sha256"))
    checks.add("scenario_id", state.scenario.get("id"), state.plan.get("scenario_id"))

    expected_run_id = sha256_bytes(
        f"{state.scenario.get('schema_version')}:{state.inputs.get('scenario_sha256')}:"
        f"{state.inputs.get('events_sha256')}".encode()
    )[:16]
    checks.add("run_id_recomputed", expected_run_id, state.provenance.get("run_id"))

    plan_rules = object_array(state.plan.get("rules"), "JSON report.execution.plan.rules")
    plan_rule_ids = [
        required_string(item.get("id"), f"JSON report.execution.plan.rules[{index}].id")
        for index, item in enumerate(plan_rules)
    ]
    plan_rule_fingerprints = [
        required_string(item.get("fingerprint"), f"JSON report.execution.plan.rules[{index}].fingerprint")
        for index, item in enumerate(plan_rules)
    ]
    expected_plan_fingerprint = digest_object(
        {
            "scenario_schema_version": state.scenario.get("schema_version"),
            "scenario_id": state.scenario.get("id"),
            "rules": plan_rule_fingerprints,
        }
    )
    checks.add("plan_fingerprint_recomputed", expected_plan_fingerprint, state.plan.get("fingerprint"))
    checks.add("plan_rule_ids_unique", len(plan_rule_ids), len(set(plan_rule_ids)))

    trace_rule_ids = [
        required_string(item.get("rule_id"), f"JSON report.execution.rules[{index}].rule_id")
        for index, item in enumerate(state.traces)
    ]
    checks.add("trace_rule_ids_unique", len(trace_rule_ids), len(set(trace_rule_ids)))
    checks.add("plan_trace_rule_ids", plan_rule_ids, trace_rule_ids)
    checks.add("rules_executed", len(state.traces), state.summary.get("rules_executed"))
    checks.add(
        "trace_rule_fingerprints",
        {item.get("id"): item.get("fingerprint") for item in plan_rules},
        {item.get("rule_id"): item.get("rule_fingerprint") for item in state.traces},
    )

    trace_by_rule = {item.get("rule_id"): item for item in state.traces}
    for index, (rule_id, plan_rule) in enumerate(zip(plan_rule_ids, plan_rules, strict=True)):
        expected_strategy, unique_selector_count = candidate_strategy(plan_rule, index)
        selectors = array_value(
            plan_rule.get("candidate_selectors"),
            f"JSON report.execution.plan.rules[{index}].candidate_selectors",
        )
        checks.add(f"plan_rule[{index}].candidate_selectors_unique", len(selectors), unique_selector_count)
        trace = trace_by_rule.get(rule_id)
        checks.add(f"plan_rule[{index}].trace_present", True, trace is not None)
        if trace is not None:
            checks.add(f"plan_rule[{index}].candidate_strategy", expected_strategy, trace.get("candidate_strategy"))

    return DerivedState(plan_rules, plan_rule_ids, plan_rule_fingerprints, trace_rule_ids)
