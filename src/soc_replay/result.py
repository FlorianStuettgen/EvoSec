from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._version import __version__
from .compiler import ExecutionPlan
from .io import LoadedScenario
from .ledger import ExecutionLedger
from .models import Detection, Event, Scenario, VerificationResult


@dataclass(frozen=True, slots=True)
class ReplayResult:
    loaded: LoadedScenario
    plan: ExecutionPlan
    detections: tuple[Detection, ...]
    verification: VerificationResult
    ledger: ExecutionLedger

    @property
    def scenario(self) -> Scenario:
        return self.loaded.scenario

    @property
    def events(self) -> tuple[Event, ...]:
        return self.loaded.events

    @property
    def simulated_actions(self) -> tuple[dict[str, str], ...]:
        return tuple(
            {
                "detection_id": detection.detection_id,
                "action": detection.response.action,
                "description": detection.response.description,
                "mode": detection.response.mode,
            }
            for detection in self.detections
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_schema_version": "2.0",
            "engine": {"name": "soc-replay", "version": __version__},
            "provenance": {
                "run_id": self.loaded.run_id,
                "scenario_sha256": self.loaded.scenario_sha256,
                "events_sha256": self.loaded.events_sha256,
            },
            "execution": {
                "plan": self.plan.to_dict(),
                "ledger": self.ledger.to_dict(),
            },
            "scenario": {
                "schema_version": self.scenario.schema_version,
                "id": self.scenario.scenario_id,
                "title": self.scenario.title,
                "objective": self.scenario.objective,
                "authorization_boundary": self.scenario.authorization_boundary,
                "expected_outcome": self.scenario.expected_outcome,
            },
            "summary": {
                "events_processed": len(self.events),
                "detections": len(self.detections),
                "simulated_actions": len(self.simulated_actions),
                "verification_passed": self.verification.passed,
            },
            "verification": self.verification.to_dict(),
            "detections": [detection.to_dict() for detection in self.detections],
            "simulated_actions": list(self.simulated_actions),
        }
