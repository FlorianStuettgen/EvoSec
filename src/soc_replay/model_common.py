from __future__ import annotations

from datetime import UTC, datetime
from ipaddress import ip_address
from typing import Any

SEVERITY_ORDER = {"informational": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
SUPPORTED_OPERATORS = {"eq", "ne", "in", "not_in", "contains", "gte", "lte", "exists"}
WINDOW_POLICIES = {"first_per_group", "all_non_overlapping"}
EVENT_FIELDS = {
    "event_id", "timestamp", "source", "category", "action", "source_ip",
    "destination_ip", "destination_port", "host", "user", "outcome", "tags", "details",
}
EVENT_KEYS = EVENT_FIELDS
SCENARIO_KEYS = {
    "schema_version", "id", "title", "objective", "authorization_boundary",
    "expected_outcome", "expectations", "rules",
}

class ValidationError(ValueError):
    """Raised when an input violates a public SOC_Replay contract."""


def _reject_unknown(data: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValidationError(f"{context} contains unknown fields: {', '.join(unknown)}")


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
    if not normalized:
        raise ValidationError(f"{context} requires a field path")
    parts = normalized.split(".")
    root = parts[0]
    if root not in EVENT_FIELDS:
        raise ValidationError(f"{context} references unknown event field {normalized!r}")
    if any(not part for part in parts):
        raise ValidationError(f"{context} has invalid field path {normalized!r}")
    if len(parts) > 1 and root != "details":
        raise ValidationError(f"{context} only permits nested paths below details: {normalized!r}")
    return normalized


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"timestamp must include a timezone: {value!r}")
    return parsed.astimezone(UTC)


def _validate_ip(value: Any, field_name: str, event_id: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"event {event_id!r} {field_name} must be a string or null")
    try:
        return str(ip_address(value))
    except ValueError as exc:
        raise ValidationError(f"event {event_id!r} has invalid {field_name}: {value!r}") from exc

