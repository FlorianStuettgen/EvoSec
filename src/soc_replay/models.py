from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from ipaddress import ip_address
from typing import Any

SEVERITY_ORDER = {"informational": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
SUPPORTED_OPERATORS = {"eq", "ne", "in", "not_in", "contains", "gte", "lte", "exists"}
WINDOW_POLICIES = {"first_per_group", "all_non_overlapping"}
EVENT_FIELDS = {
    "event_id",
    "timestamp",
    "source",
    "category",
    "action",
    "source_ip",
    "destination_ip",
    "destination_port",
    "host",
    "user",
    "outcome",
    "tags",
    "details",
}


class ValidationError(ValueError):
    """Raised when a scenario or event violates the replay contract."""


def _required_string(data: dict[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def _optional_string(data: dict[str, Any], key: str, context: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{context}.{key} must be null or a non-empty string")
    return value.strip()


def validate_field_path(field_name: str, context: str) -> str:
    normalized = field_name.strip()
    root = normalized.split(".", 1)[0]
    if root not in EVENT_FIELDS:
        raise ValidationError(f"{context} references unknown event field {normalized!r}")
    if root == "details" and normalized != "details" and not normalized.startswith("details."):
        raise ValidationError(f"{context} has invalid details path {normalized!r}")
    return normalized


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"timestamp must include a timezone: {value!r}")
    return parsed.astimezone(UTC)


def _validate_ip(value: str | None, field_name: str, event_id: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"event {event_id!r} {field_name} must be a string or null")
    try:
        ip_address(value)
    except ValueError as exc:
        raise ValidationError(f"event {event_id!r} has invalid {field_name}: {value!r}") from exc
    return value


@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp: datetime
    source: str
    category: str
    action: str
    source_ip: str | None = None
    destination_ip: str | None = None
    destination_port: int | None = None
    host: str | None = None
    user: str | None = None
    outcome: str | None = None
    tags: tuple[str, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        event_id = _required_string(data, "event_id", "event")
        timestamp = _required_string(data, "timestamp", f"event {event_id!r}")
        port = data.get("destination_port")
        if port is not None and (not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65535):
            raise ValidationError(f"event {event_id!r} has invalid destination_port")

        tags = data.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(item, str) and item.strip() for item in tags):
            raise ValidationError(f"event {event_id!r} tags must be a list of non-empty strings")
        if len(tags) != len(set(tags)):
            raise ValidationError(f"event {event_id!r} tags must be unique")

        details = data.get("details", {})
        if not isinstance(details, dict):
            raise ValidationError(f"event {event_id!r} details must be an object")

        return cls(
            event_id=event_id,
            timestamp=parse_timestamp(timestamp),
            source=_required_string(data, "source", f"event {event_id!r}"),
            category=_required_string(data, "category", f"event {event_id!r}"),
            action=_required_string(data, "action", f"event {event_id!r}"),
            source_ip=_validate_ip(data.get("source_ip"), "source_ip", event_id),
            destination_ip=_validate_ip(data.get("destination_ip"), "destination_ip", event_id),
            destination_port=port,
            host=_optional_string(data, "host", f"event {event_id!r}"),
            user=_optional_string(data, "user", f"event {event_id!r}"),
            outcome=_optional_string(data, "outcome", f"event {event_id!r}"),
            tags=tuple(item.strip() for item in tags),
            details=details,
        )

    def value(self, field_name: str) -> Any:
        if not field_name:
            return None
        parts = field_name.split(".")
        if parts[0] == "details":
            current: Any = self.details
            parts = parts[1:]
        else:
            current = getattr(self, parts[0], None)
            parts = parts[1:]
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current


@dataclass(frozen=True)
class Condition:
    field: str
    operator: str
    value: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Condition:
        if not isinstance(data, dict):
            raise ValidationError("rule condition must be an object")
        field_name = data.get("field")
        operator = data.get("operator")
        if not isinstance(field_name, str) or not field_name.strip():
            raise ValidationError("rule condition requires a field")
        if operator not in SUPPORTED_OPERATORS:
            raise ValidationError(f"unsupported operator {operator!r}")
        value = data.get("value")
        if operator in {"in", "not_in"} and (not isinstance(value, list) or not value):
            raise ValidationError(f"operator {operator!r} requires a non-empty list value")
        if operator == "exists" and value is not None and not isinstance(value, bool):
            raise ValidationError("operator 'exists' value must be true, false, or omitted")
        if operator in {"gte", "lte"} and value is None:
            raise ValidationError(f"operator {operator!r} requires a value")
        return cls(field=validate_field_path(field_name, "rule condition"), operator=operator, value=value)


@dataclass(frozen=True)
class Aggregate:
    group_by: tuple[str, ...]
    count_gte: int
    within_seconds: int
    distinct_field: str | None = None
    distinct_gte: int | None = None
    window_policy: str = "first_per_group"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Aggregate | None:
        if data is None:
            return None
        if not isinstance(data, dict):
            raise ValidationError("aggregate must be an object or null")
        group_by = data.get("group_by", [])
        if not isinstance(group_by, list) or not all(isinstance(item, str) and item.strip() for item in group_by):
            raise ValidationError("aggregate.group_by must be a list of non-empty strings")
        if len(group_by) != len(set(group_by)):
            raise ValidationError("aggregate.group_by fields must be unique")
        count_gte = data.get("count_gte")
        within_seconds = data.get("within_seconds")
        if not isinstance(count_gte, int) or isinstance(count_gte, bool) or count_gte < 1:
            raise ValidationError("aggregate.count_gte must be a positive integer")
        if not isinstance(within_seconds, int) or isinstance(within_seconds, bool) or within_seconds < 1:
            raise ValidationError("aggregate.within_seconds must be a positive integer")
        distinct_field = data.get("distinct_field")
        distinct_gte = data.get("distinct_gte")
        if (distinct_field is None) != (distinct_gte is None):
            raise ValidationError("aggregate.distinct_field and aggregate.distinct_gte must be supplied together")
        if distinct_field is not None and (not isinstance(distinct_field, str) or not distinct_field.strip()):
            raise ValidationError("aggregate.distinct_field must be a non-empty string")
        if distinct_gte is not None and (
            not isinstance(distinct_gte, int) or isinstance(distinct_gte, bool) or distinct_gte < 1
        ):
            raise ValidationError("aggregate.distinct_gte must be a positive integer")
        window_policy = data.get("window_policy", "first_per_group")
        if window_policy not in WINDOW_POLICIES:
            raise ValidationError(f"unsupported aggregate.window_policy {window_policy!r}")
        return cls(
            group_by=tuple(validate_field_path(item, "aggregate.group_by") for item in group_by),
            count_gte=count_gte,
            within_seconds=within_seconds,
            distinct_field=validate_field_path(distinct_field, "aggregate.distinct_field") if distinct_field else None,
            distinct_gte=distinct_gte,
            window_policy=window_policy,
        )


@dataclass(frozen=True)
class Response:
    action: str
    description: str
    mode: str = "simulated"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        if not isinstance(data, dict):
            raise ValidationError("response must be an object")
        action = _required_string(data, "action", "response")
        description = _required_string(data, "description", "response")
        mode = data.get("mode", "simulated")
        if mode != "simulated":
            raise ValidationError("SOC_Replay only permits response.mode='simulated'")
        return cls(action=action, description=description, mode=mode)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    severity: str
    description: str
    conditions: tuple[Condition, ...]
    aggregate: Aggregate | None
    response: Response

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Rule:
        if not isinstance(data, dict):
            raise ValidationError("rule must be an object")
        rule_id = _required_string(data, "id", "rule")
        severity = data.get("severity")
        if severity not in SEVERITY_ORDER:
            raise ValidationError(f"rule {rule_id!r} has unsupported severity {severity!r}")
        conditions_raw = data.get("match", [])
        if not isinstance(conditions_raw, list) or not conditions_raw:
            raise ValidationError(f"rule {rule_id!r} requires at least one match condition")
        return cls(
            rule_id=rule_id,
            name=_required_string(data, "name", f"rule {rule_id!r}"),
            severity=severity,
            description=str(data.get("description", "")).strip(),
            conditions=tuple(Condition.from_dict(item) for item in conditions_raw),
            aggregate=Aggregate.from_dict(data.get("aggregate")),
            response=Response.from_dict(data.get("response", {})),
        )


@dataclass(frozen=True)
class Expectations:
    detection_count: int
    rule_ids: tuple[str, ...]
    severity_counts: dict[str, int]
    simulated_action_count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Expectations:
        if not isinstance(data, dict):
            raise ValidationError("scenario.expectations must be an object")
        detection_count = data.get("detection_count")
        action_count = data.get("simulated_action_count")
        rule_ids = data.get("rule_ids")
        severity_counts = data.get("severity_counts", {})
        if not isinstance(detection_count, int) or isinstance(detection_count, bool) or detection_count < 0:
            raise ValidationError("expectations.detection_count must be a non-negative integer")
        if not isinstance(action_count, int) or isinstance(action_count, bool) or action_count < 0:
            raise ValidationError("expectations.simulated_action_count must be a non-negative integer")
        if not isinstance(rule_ids, list) or not all(isinstance(item, str) and item.strip() for item in rule_ids):
            raise ValidationError("expectations.rule_ids must be a list of non-empty strings")
        if not isinstance(severity_counts, dict):
            raise ValidationError("expectations.severity_counts must be an object")
        normalized_counts: dict[str, int] = {}
        for severity, count in severity_counts.items():
            if severity not in SEVERITY_ORDER:
                raise ValidationError(f"expectations contains unsupported severity {severity!r}")
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise ValidationError(f"expectations.severity_counts.{severity} must be a non-negative integer")
            normalized_counts[severity] = count
        if len(rule_ids) != detection_count:
            raise ValidationError("expectations.rule_ids length must equal expectations.detection_count")
        if sum(normalized_counts.values()) != detection_count:
            raise ValidationError("expectations.severity_counts must sum to expectations.detection_count")
        if action_count != detection_count:
            raise ValidationError("each detection produces one simulated action; expected counts must match")
        return cls(
            detection_count=detection_count,
            rule_ids=tuple(rule_ids),
            severity_counts=normalized_counts,
            simulated_action_count=action_count,
        )


@dataclass(frozen=True)
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
        schema_version = data.get("schema_version")
        if schema_version != "1.0":
            raise ValidationError("scenario.schema_version must be '1.0'")
        scenario_id = _required_string(data, "id", "scenario")
        rules_raw = data.get("rules", [])
        if not isinstance(rules_raw, list) or not rules_raw:
            raise ValidationError("scenario requires at least one rule")
        rules = tuple(Rule.from_dict(item) for item in rules_raw)
        rule_ids = [rule.rule_id for rule in rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValidationError("scenario rule IDs must be unique")
        expectations = Expectations.from_dict(data.get("expectations", {}))
        unknown_rule_ids = sorted(set(expectations.rule_ids) - set(rule_ids))
        if unknown_rule_ids:
            raise ValidationError(f"expectations reference unknown rule IDs: {', '.join(unknown_rule_ids)}")
        return cls(
            schema_version=schema_version,
            scenario_id=scenario_id,
            title=_required_string(data, "title", "scenario"),
            objective=_required_string(data, "objective", "scenario"),
            authorization_boundary=_required_string(data, "authorization_boundary", "scenario"),
            expected_outcome=_required_string(data, "expected_outcome", "scenario"),
            rules=rules,
            expectations=expectations,
        )


@dataclass(frozen=True)
class Detection:
    detection_id: str
    rule_id: str
    rule_name: str
    rule_description: str
    severity: str
    first_seen: datetime
    last_seen: datetime
    event_ids: tuple[str, ...]
    group: dict[str, Any]
    response: Response
    correlation: dict[str, Any]

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
            "group": self.group,
            "correlation": self.correlation,
            "response": {
                "action": self.response.action,
                "description": self.response.description,
                "mode": self.response.mode,
            },
        }


@dataclass(frozen=True)
class VerificationCheck:
    name: str
    expected: Any
    actual: Any
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "expected": self.expected, "actual": self.actual, "passed": self.passed}


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    checks: tuple[VerificationCheck, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "checks": [check.to_dict() for check in self.checks]}
