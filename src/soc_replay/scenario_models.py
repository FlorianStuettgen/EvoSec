from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import SCENARIO_SCHEMA_VERSIONS
from .event_models import Rule
from .immutability import freeze_json
from .model_common import SCENARIO_KEYS, SEVERITY_ORDER, ValidationError, _reject_unknown, _required_string
from .serialization import to_primitive


@dataclass(frozen=True, slots=True)
class ExpectedDetection:
    rule_id: str
    severity: str
    event_ids: tuple[str, ...]
    group: Mapping[str, Any]
    action: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExpectedDetection:
        if not isinstance(data, dict):
            raise ValidationError("expected detection must be an object")
        _reject_unknown(data, {"rule_id", "severity", "event_ids", "group", "action"}, "expected detection")
        rule_id = _required_string(data, "rule_id", "expected detection")
        severity = data.get("severity")
        if severity not in SEVERITY_ORDER:
            raise ValidationError(f"expected detection has unsupported severity {severity!r}")
        event_ids = data.get("event_ids")
        if not isinstance(event_ids, list) or not event_ids or not all(
            isinstance(item, str) and item.strip() for item in event_ids
        ):
            raise ValidationError("expected detection.event_ids must be a non-empty list of strings")
        normalized_event_ids = tuple(item.strip() for item in event_ids)
        if len(normalized_event_ids) != len(set(normalized_event_ids)):
            raise ValidationError("expected detection.event_ids must be unique")
        group = data.get("group")
        if not isinstance(group, dict):
            raise ValidationError("expected detection.group must be an object")
        return cls(
            rule_id=rule_id,
            severity=str(severity),
            event_ids=normalized_event_ids,
            group=freeze_json(group),
            action=_required_string(data, "action", "expected detection"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "event_ids": list(self.event_ids),
            "group": to_primitive(self.group),
            "action": self.action,
        }


@dataclass(frozen=True, slots=True)
class Expectations:
    detection_count: int
    rule_ids: tuple[str, ...]
    severity_counts: Mapping[str, int]
    simulated_action_count: int
    detection_contracts: tuple[ExpectedDetection, ...] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Expectations:
        if not isinstance(data, dict):
            raise ValidationError("scenario.expectations must be an object")
        _reject_unknown(
            data,
            {"detection_count", "rule_ids", "severity_counts", "simulated_action_count", "detections"},
            "expectations",
        )
        detection_count = data.get("detection_count")
        action_count = data.get("simulated_action_count")
        rule_ids = data.get("rule_ids")
        counts = data.get("severity_counts", {})
        if not isinstance(detection_count, int) or isinstance(detection_count, bool) or detection_count < 0:
            raise ValidationError("expectations.detection_count must be a non-negative integer")
        if not isinstance(action_count, int) or isinstance(action_count, bool) or action_count < 0:
            raise ValidationError("expectations.simulated_action_count must be a non-negative integer")
        if not isinstance(rule_ids, list) or not all(isinstance(item, str) and item.strip() for item in rule_ids):
            raise ValidationError("expectations.rule_ids must be a list of non-empty strings")
        if not isinstance(counts, dict):
            raise ValidationError("expectations.severity_counts must be an object")
        normalized_counts: dict[str, int] = {}
        for severity, count in counts.items():
            if severity not in SEVERITY_ORDER:
                raise ValidationError(f"expectations contains unsupported severity {severity!r}")
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise ValidationError(f"expectations.severity_counts.{severity} must be a non-negative integer")
            normalized_counts[str(severity)] = count
        normalized_rule_ids = tuple(item.strip() for item in rule_ids)
        if len(normalized_rule_ids) != detection_count:
            raise ValidationError("expectations.rule_ids length must equal expectations.detection_count")
        if sum(normalized_counts.values()) != detection_count:
            raise ValidationError("expectations.severity_counts must sum to expectations.detection_count")
        if action_count != detection_count:
            raise ValidationError("each detection produces one simulated action; expected counts must match")

        contracts: tuple[ExpectedDetection, ...] | None = None
        if "detections" in data:
            raw_contracts = data.get("detections")
            if not isinstance(raw_contracts, list):
                raise ValidationError("expectations.detections must be a list")
            contracts = tuple(ExpectedDetection.from_dict(item) for item in raw_contracts)
            if len(contracts) != detection_count:
                raise ValidationError("expectations.detections length must equal expectations.detection_count")
            if tuple(contract.rule_id for contract in contracts) != normalized_rule_ids:
                raise ValidationError("expectations.detections rule order must equal expectations.rule_ids")
            contract_counts = dict(sorted(Counter(contract.severity for contract in contracts).items()))
            if contract_counts != dict(sorted(normalized_counts.items())):
                raise ValidationError("expectations.detections severities must equal expectations.severity_counts")

        return cls(
            detection_count,
            normalized_rule_ids,
            freeze_json(normalized_counts),
            action_count,
            contracts,
        )


@dataclass(frozen=True, slots=True)
class Scenario:
    schema_version: str
    scenario_id: str
    title: str
    objective: str
    authorization_boundary: str
    expected_outcome: str
    rules: tuple[Rule, ...]
    expectations: Expectations

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Scenario:
        if not isinstance(data, dict):
            raise ValidationError("scenario must be an object")
        _reject_unknown(data, SCENARIO_KEYS, "scenario")
        schema_version = data.get("schema_version")
        if schema_version not in SCENARIO_SCHEMA_VERSIONS:
            supported = ", ".join(sorted(SCENARIO_SCHEMA_VERSIONS))
            raise ValidationError(f"scenario.schema_version must be one of: {supported}")
        scenario_id = _required_string(data, "id", "scenario")
        raw_rules = data.get("rules")
        if not isinstance(raw_rules, list) or not raw_rules:
            raise ValidationError("scenario requires at least one rule")
        rules = tuple(Rule.from_dict(item) for item in raw_rules)
        rule_ids = [rule.rule_id for rule in rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValidationError("scenario rule IDs must be unique")
        expectations = Expectations.from_dict(data.get("expectations", {}))
        if schema_version == "1.1" and expectations.detection_contracts is None:
            raise ValidationError("scenario schema 1.1 requires expectations.detections")
        unknown = sorted(set(expectations.rule_ids) - set(rule_ids))
        if unknown:
            raise ValidationError(f"expectations reference unknown rule IDs: {', '.join(unknown)}")
        return cls(
            str(schema_version),
            scenario_id,
            _required_string(data, "title", "scenario"),
            _required_string(data, "objective", "scenario"),
            _required_string(data, "authorization_boundary", "scenario"),
            _required_string(data, "expected_outcome", "scenario"),
            rules,
            expectations,
        )
