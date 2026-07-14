from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .immutability import freeze_json
from .model_common import (
    EVENT_KEYS,
    SEVERITY_ORDER,
    SUPPORTED_OPERATORS,
    WINDOW_POLICIES,
    ValidationError,
    _optional_string,
    _reject_unknown,
    _required_string,
    _validate_ip,
    parse_timestamp,
    validate_field_path,
)


@dataclass(frozen=True, slots=True)
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
    details: Mapping[str, Any] = field(default_factory=lambda: freeze_json({}))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        if not isinstance(data, dict):
            raise ValidationError("event must be an object")
        _reject_unknown(data, EVENT_KEYS, "event")
        event_id = _required_string(data, "event_id", "event")
        timestamp = _required_string(data, "timestamp", f"event {event_id!r}")
        port = data.get("destination_port")
        if port is not None and (not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65535):
            raise ValidationError(f"event {event_id!r} has invalid destination_port")
        tags = data.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(item, str) and item.strip() for item in tags):
            raise ValidationError(f"event {event_id!r} tags must be a list of non-empty strings")
        normalized_tags = tuple(item.strip() for item in tags)
        if len(normalized_tags) != len(set(normalized_tags)):
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
            tags=normalized_tags,
            details=freeze_json(details),
        )

    def value(self, field_name: str) -> Any:
        return self.value_path(tuple(field_name.split("."))) if field_name else None

    def value_path(self, path: tuple[str, ...]) -> Any:
        if not path:
            return None
        if path[0] == "details":
            current: Any = self.details
            remaining = path[1:]
        else:
            current = getattr(self, path[0], None)
            remaining = path[1:]
        for part in remaining:
            if not isinstance(current, Mapping):
                return None
            current = current.get(part)
        return current


@dataclass(frozen=True, slots=True)
class Condition:
    field: str
    operator: str
    value: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Condition:
        if not isinstance(data, dict):
            raise ValidationError("rule condition must be an object")
        _reject_unknown(data, {"field", "operator", "value"}, "rule condition")
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
        return cls(validate_field_path(field_name, "rule condition"), str(operator), freeze_json(value))


@dataclass(frozen=True, slots=True)
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
        _reject_unknown(
            data,
            {"group_by", "count_gte", "within_seconds", "distinct_field", "distinct_gte", "window_policy"},
            "aggregate",
        )
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
        policy = data.get("window_policy", "first_per_group")
        if policy not in WINDOW_POLICIES:
            raise ValidationError(f"unsupported aggregate.window_policy {policy!r}")
        return cls(
            tuple(validate_field_path(item, "aggregate.group_by") for item in group_by),
            count_gte,
            within_seconds,
            validate_field_path(distinct_field, "aggregate.distinct_field") if distinct_field else None,
            distinct_gte,
            str(policy),
        )


@dataclass(frozen=True, slots=True)
class Response:
    action: str
    description: str
    mode: str = "simulated"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        if not isinstance(data, dict):
            raise ValidationError("response must be an object")
        _reject_unknown(data, {"action", "description", "mode"}, "response")
        mode = data.get("mode", "simulated")
        if mode != "simulated":
            raise ValidationError("SOC_Replay only permits response.mode='simulated'")
        return cls(_required_string(data, "action", "response"), _required_string(data, "description", "response"))


@dataclass(frozen=True, slots=True)
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
        _reject_unknown(data, {"id", "name", "severity", "description", "match", "aggregate", "response"}, "rule")
        rule_id = _required_string(data, "id", "rule")
        severity = data.get("severity")
        if severity not in SEVERITY_ORDER:
            raise ValidationError(f"rule {rule_id!r} has unsupported severity {severity!r}")
        raw = data.get("match")
        if not isinstance(raw, list) or not raw:
            raise ValidationError(f"rule {rule_id!r} requires at least one match condition")
        return cls(
            rule_id,
            _required_string(data, "name", f"rule {rule_id!r}"),
            str(severity),
            str(data.get("description", "")).strip(),
            tuple(Condition.from_dict(item) for item in raw),
            Aggregate.from_dict(data.get("aggregate")),
            Response.from_dict(data.get("response", {})),
        )
