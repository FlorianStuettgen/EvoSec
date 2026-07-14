from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .event_models import Response
from .immutability import freeze_json
from .serialization import to_primitive


@dataclass(frozen=True, slots=True)
class Detection:
    detection_id: str
    rule_id: str
    rule_name: str
    rule_description: str
    severity: str
    first_seen: datetime
    last_seen: datetime
    event_ids: tuple[str, ...]
    group: Mapping[str, Any]
    response: Response
    correlation: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "group", freeze_json(self.group))
        object.__setattr__(self, "correlation", freeze_json(self.correlation))

    def to_dict(self) -> dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_description": self.rule_description,
            "severity": self.severity,
            "first_seen": self.first_seen.isoformat().replace("+00:00", "Z"),
            "last_seen": self.last_seen.isoformat().replace("+00:00", "Z"),
            "event_ids": list(self.event_ids),
            "group": to_primitive(self.group),
            "correlation": to_primitive(self.correlation),
            "response": {
                "action": self.response.action,
                "description": self.response.description,
                "mode": self.response.mode,
            },
        }


@dataclass(frozen=True, slots=True)
class VerificationCheck:
    name: str
    expected: Any
    actual: Any
    passed: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "expected", freeze_json(self.expected))
        object.__setattr__(self, "actual", freeze_json(self.actual))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "expected": to_primitive(self.expected),
            "actual": to_primitive(self.actual),
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class VerificationResult:
    passed: bool
    checks: tuple[VerificationCheck, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "checks": [check.to_dict() for check in self.checks]}
