from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SEVERITY_ORDER = {"informational": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
SUPPORTED_OPERATORS = {"eq", "ne", "in", "contains", "gte", "lte", "exists"}


class ValidationError(ValueError):
    """Raised when a scenario or event violates the replay contract."""


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        required = ("event_id", "timestamp", "source", "category", "action")
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ValidationError(f"event missing required fields: {', '.join(missing)}")
        port = data.get("destination_port")
        if port is not None and (not isinstance(port, int) or not 0 <= port <= 65535):
            raise ValidationError(f"event {data['event_id']!r} has invalid destination_port")
        tags = data.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(item, str) for item in tags):
            raise ValidationError(f"event {data['event_id']!r} tags must be a list of strings")
        details = data.get("details", {})
        if not isinstance(details, dict):
            raise ValidationError(f"event {data['event_id']!r} details must be an object")
        return cls(
            event_id=str(data["event_id"]),
            timestamp=parse_timestamp(str(data["timestamp"])),
            source=str(data["source"]),
            category=str(data["category"]),
            action=str(data["action"]),
            source_ip=data.get("source_ip"),
            destination_ip=data.get("destination_ip"),
            destination_port=port,
            host=data.get("host"),
            user=data.get("user"),
            outcome=data.get("outcome"),
            tags=tuple(tags),
            details=details,
        )

    def value(self, field_name: str) -> Any:
        if field_name.startswith("details."):
            return self.details.get(field_name.split(".", 1)[1])
        return getattr(self, field_name, None)


@dataclass(frozen=True)
class Condition:
    field: str
    operator: str
    value: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Condition":
        field_name = data.get("field")
        operator = data.get("operator")
        if not isinstance(field_name, str) or not field_name:
            raise ValidationError("rule condition requires a field")
        if operator not in SUPPORTED_OPERATORS:
            raise ValidationError(f"unsupported operator {operator!r}")
        return cls(field=field_name, operator=operator, value=data.get("value"))


@dataclass(frozen=True)
class Aggregate:
    group_by: tuple[str, ...]
    count_gte: int
    within_seconds: int
    distinct_field: str | None = None
    distinct_gte: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Aggregate | None":
        if data is None:
            return None
        group_by = data.get("group_by", [])
        if not isinstance(group_by, list) or not all(isinstance(item, str) for item in group_by):
            raise ValidationError("aggregate.group_by must be a list of strings")
        count_gte = data.get("count_gte")
        within_seconds = data.get("within_seconds")
        if not isinstance(count_gte, int) or count_gte < 1:
            raise ValidationError("aggregate.count_gte must be a positive integer")
        if not isinstance(within_seconds, int) or within_seconds < 1:
            raise ValidationError("aggregate.within_seconds must be a positive integer")
        distinct_field = data.get("distinct_field")
        distinct_gte = data.get("distinct_gte")
        if distinct_field is not None and not isinstance(distinct_field, str):
            raise ValidationError("aggregate.distinct_field must be a string")
        if distinct_gte is not None and (not isinstance(distinct_gte, int) or distinct_gte < 1):
            raise ValidationError("aggregate.distinct_gte must be a positive integer")
        return cls(tuple(group_by), count_gte, within_seconds, distinct_field, distinct_gte)


@dataclass(frozen=True)
class Response:
    action: str
    description: str
    mode: str = "simulated"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Response":
        action = data.get("action")
        description = data.get("description")
        mode = data.get("mode", "simulated")
        if not isinstance(action, str) or not action:
            raise ValidationError("response.action is required")
        if not isinstance(description, str) or not description:
            raise ValidationError("response.description is required")
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
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        rule_id = data.get("id")
        name = data.get("name")
        severity = data.get("severity")
        description = data.get("description", "")
        if not isinstance(rule_id, str) or not rule_id:
            raise ValidationError("rule.id is required")
        if not isinstance(name, str) or not name:
            raise ValidationError(f"rule {rule_id!r} requires a name")
        if severity not in SEVERITY_ORDER:
            raise ValidationError(f"rule {rule_id!r} has unsupported severity {severity!r}")
        conditions_raw = data.get("match", [])
        if not isinstance(conditions_raw, list) or not conditions_raw:
            raise ValidationError(f"rule {rule_id!r} requires at least one match condition")
        return cls(
            rule_id=rule_id,
            name=name,
            severity=severity,
            description=str(description),
            conditions=tuple(Condition.from_dict(item) for item in conditions_raw),
            aggregate=Aggregate.from_dict(data.get("aggregate")),
            response=Response.from_dict(data.get("response", {})),
        )


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    title: str
    objective: str
    authorization_boundary: str
    expected_outcome: str
    rules: tuple[Rule, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scenario":
        required = ("id", "title", "objective", "authorization_boundary", "expected_outcome")
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ValidationError(f"scenario missing required fields: {', '.join(missing)}")
        rules_raw = data.get("rules", [])
        if not isinstance(rules_raw, list) or not rules_raw:
            raise ValidationError("scenario requires at least one rule")
        rules = tuple(Rule.from_dict(item) for item in rules_raw)
        rule_ids = [rule.rule_id for rule in rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValidationError("scenario rule IDs must be unique")
        return cls(
            scenario_id=str(data["id"]),
            title=str(data["title"]),
            objective=str(data["objective"]),
            authorization_boundary=str(data["authorization_boundary"]),
            expected_outcome=str(data["expected_outcome"]),
            rules=rules,
        )


@dataclass(frozen=True)
class Detection:
    detection_id: str
    rule_id: str
    rule_name: str
    severity: str
    first_seen: datetime
    last_seen: datetime
    event_ids: tuple[str, ...]
    group: dict[str, Any]
    response: Response

    def to_dict(self) -> dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "first_seen": self.first_seen.isoformat().replace("+00:00", "Z"),
            "last_seen": self.last_seen.isoformat().replace("+00:00", "Z"),
            "event_ids": list(self.event_ids),
            "group": self.group,
            "response": {
                "action": self.response.action,
                "description": self.response.description,
                "mode": self.response.mode,
            },
        }
