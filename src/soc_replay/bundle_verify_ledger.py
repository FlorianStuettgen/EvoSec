from __future__ import annotations

from .bundle_verify_support import BundleState, CheckCollector, DerivedState, object_array
from .contracts import INDEX_FIELDS, PIPELINE_STAGES
from .ledger import verify_ledger_payload
from .serialization import digest_object


def check_ledger(state: BundleState, derived: DerivedState, checks: CheckCollector) -> None:
    ledger_valid, ledger_errors = verify_ledger_payload(state.ledger, require_complete=True)
    checks.add("ledger_valid", True, ledger_valid)
    checks.add("ledger_errors", [], list(ledger_errors))
    checks.add("plan_fingerprint", state.plan.get("fingerprint"), state.manifest.get("plan_fingerprint"))
    checks.add("ledger_root", state.ledger.get("root_hash"), state.manifest.get("ledger_root"))
    checks.add("verification_passed", state.verification.get("passed"), state.manifest.get("verification_passed"))
    checks.add(
        "summary_verification_passed",
        state.verification.get("passed"),
        state.summary.get("verification_passed"),
    )

    entries = object_array(state.ledger.get("entries"), "JSON report.execution.ledger.entries")
    by_stage = {entry.get("stage"): entry for entry in entries}
    checks.add("ledger_stage_order", list(PIPELINE_STAGES), [entry.get("stage") for entry in entries])
    if not ledger_valid:
        return

    load_entry = by_stage["load"]
    compile_entry = by_stage["compile"]
    index_entry = by_stage["index"]
    evaluate_entry = by_stage["evaluate"]
    verify_entry = by_stage["verify"]
    events_processed = state.summary.get("events_processed")
    load_output_digest = digest_object(
        {
            "run_id": state.provenance.get("run_id"),
            "scenario_sha256": state.provenance.get("scenario_sha256"),
            "events_sha256": state.provenance.get("events_sha256"),
        }
    )
    evaluation_output_digest = digest_object({"rules": state.traces, "detections": state.detections})
    verification_output_digest = digest_object(state.verification)
    checks.add(
        "ledger.load.input_digest",
        digest_object([state.inputs.get("scenario_sha256"), state.inputs.get("events_sha256")]),
        load_entry.get("input_digest"),
    )
    checks.add("ledger.load.output_digest", load_output_digest, load_entry.get("output_digest"))
    checks.add(
        "ledger.load.metadata",
        {"scenario_id": state.scenario.get("id"), "run_id": state.provenance.get("run_id")},
        load_entry.get("metadata"),
    )
    checks.add("ledger.compile.input_digest", load_output_digest, compile_entry.get("input_digest"))
    checks.add("ledger.compile.output_digest", state.plan.get("fingerprint"), compile_entry.get("output_digest"))
    checks.add(
        "ledger.compile.metadata",
        {"rule_fingerprints": derived.plan_rule_fingerprints},
        compile_entry.get("metadata"),
    )
    checks.add("ledger.index.input_digest", state.inputs.get("events_sha256"), index_entry.get("input_digest"))
    checks.add("ledger.index.metadata", {"index_fields": [*INDEX_FIELDS, "tags"]}, index_entry.get("metadata"))
    checks.add(
        "ledger.evaluate.input_digest",
        digest_object([state.plan.get("fingerprint"), index_entry.get("output_digest")]),
        evaluate_entry.get("input_digest"),
    )
    checks.add("ledger.evaluate.output_digest", evaluation_output_digest, evaluate_entry.get("output_digest"))
    checks.add("ledger.evaluate.metadata", {"rule_executions": state.traces}, evaluate_entry.get("metadata"))
    checks.add("ledger.verify.input_digest", evaluation_output_digest, verify_entry.get("input_digest"))
    checks.add("ledger.verify.output_digest", verification_output_digest, verify_entry.get("output_digest"))
    checks.add("ledger.verify.metadata", {"passed": state.verification.get("passed")}, verify_entry.get("metadata"))
    checks.add("load_records_in", 2, load_entry.get("records_in"))
    checks.add("load_records_out", events_processed, load_entry.get("records_out"))
    checks.add("compile_records_in", len(derived.plan_rules), compile_entry.get("records_in"))
    checks.add("compile_records_out", len(derived.plan_rules), compile_entry.get("records_out")
    checks.add("index_records_in", events_processed, index_entry.get("records_in"))
    checks.add("index_records_out", events_processed, index_entry.get("records_out"))
    checks.add("evaluate_records_in", events_processed, evaluate_entry.get("records_in"))
    checks.add("evaluate_records_out", len(state.detections), evaluate_entry.get("records_out"))
    checks.add("verify_records_in", len(state.detections), verify_entry.get("records_in"))
    checks.add("verify_records_out", len(state.verification_checks), verify_entry.get("records_out"))
