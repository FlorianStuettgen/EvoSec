from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .compiler import ExecutionPlan, compile_scenario
from .contracts import INDEX_FIELDS, PIPELINE_NAME, PIPELINE_STAGES
from .correlation import RuleExecution, evaluate_compiled_rule
from .indexing import EventIndex
from .io import LoadedScenario, load_scenario
from .ledger import LedgerBuilder
from .models import Detection
from .result import ReplayResult
from .serialization import digest_object
from .verification import verify_result


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    max_events: int = 1_000_000

    def __post_init__(self) -> None:
        if self.max_events < 1:
            raise ValueError("max_events must be positive")


@dataclass(frozen=True, slots=True)
class PipelineDescription:
    name: str
    stages: tuple[str, ...]
    invariants: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "stages": list(self.stages), "invariants": list(self.invariants)}


class ReplayPipeline:
    DESCRIPTION = PipelineDescription(
        name=PIPELINE_NAME,
        stages=PIPELINE_STAGES,
        invariants=(
            "inputs and parsed JSON values are deeply immutable after load",
            "rules are compiled before evaluation",
            "candidate indexes can reduce cost but never change rule semantics",
            "every maintained scenario declares exact detection contracts",
            "responses remain simulation-only",
            "every stage is linked in a deterministic hash ledger",
        ),
    )

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()

    def run(self, directory: str | Path) -> ReplayResult:
        loaded = load_scenario(directory, max_events=self.config.max_events)
        return self.run_loaded(loaded)

    def run_loaded(self, loaded: LoadedScenario) -> ReplayResult:
        ledger = LedgerBuilder()
        load_output = digest_object(
            {
                "run_id": loaded.run_id,
                "scenario_sha256": loaded.scenario_sha256,
                "events_sha256": loaded.events_sha256,
            }
        )
        ledger.append(
            stage="load",
            input_digest=digest_object([loaded.scenario_sha256, loaded.events_sha256]),
            output_digest=load_output,
            records_in=2,
            records_out=len(loaded.events),
            metadata={"scenario_id": loaded.scenario.scenario_id, "run_id": loaded.run_id},
        )

        plan: ExecutionPlan = compile_scenario(loaded.scenario)
        ledger.append(
            stage="compile",
            input_digest=load_output,
            output_digest=plan.fingerprint,
            records_in=len(loaded.scenario.rules),
            records_out=len(plan.rules),
            metadata={"rule_fingerprints": [rule.fingerprint for rule in plan.rules]},
        )

        event_index = EventIndex(loaded.events)
        index_digest = digest_object(
            {
                "event_ids": [event.event_id for event in loaded.events],
                "event_count": len(loaded.events),
                "index_fields": [*INDEX_FIELDS, "tags"],
            }
        )
        ledger.append(
            stage="index",
            input_digest=loaded.events_sha256,
            output_digest=index_digest,
            records_in=len(loaded.events),
            records_out=len(loaded.events),
            metadata={"index_fields": [*INDEX_FIELDS, "tags"]},
        )

        executions: list[RuleExecution] = []
        detections: list[Detection] = []
        for rule in plan.rules:
            execution = evaluate_compiled_rule(rule, event_index.candidates(rule))
            executions.append(execution)
            detections.extend(execution.detections)
        detections.sort(key=lambda item: (item.first_seen, item.rule_id, item.detection_id))
        frozen_executions = tuple(executions)
        frozen_detections = tuple(detections)
        evaluation_payload = {
            "rules": [execution.to_dict() for execution in frozen_executions],
            "detections": [detection.to_dict() for detection in frozen_detections],
        }
        evaluation_digest = digest_object(evaluation_payload)
        ledger.append(
            stage="evaluate",
            input_digest=digest_object([plan.fingerprint, index_digest]),
            output_digest=evaluation_digest,
            records_in=len(loaded.events),
            records_out=len(frozen_detections),
            metadata={"rule_executions": [execution.to_dict() for execution in frozen_executions]},
        )

        verification = verify_result(loaded.scenario, frozen_detections)
        verification_digest = digest_object(verification.to_dict())
        ledger.append(
            stage="verify",
            input_digest=evaluation_digest,
            output_digest=verification_digest,
            records_in=len(frozen_detections),
            records_out=len(verification.checks),
            metadata={"passed": verification.passed},
        )

        return ReplayResult(
            loaded,
            plan,
            frozen_executions,
            frozen_detections,
            verification,
            ledger.freeze(),
        )
