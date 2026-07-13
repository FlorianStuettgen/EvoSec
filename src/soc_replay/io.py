from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Event, Scenario, ValidationError


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return data


def load_scenario(directory: str | Path) -> tuple[Scenario, list[Event]]:
    scenario_dir = Path(directory)
    scenario = Scenario.from_dict(_read_json(scenario_dir / "scenario.json"))
    events_path = scenario_dir / "events.jsonl"
    try:
        lines = events_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {events_path}") from exc

    events: list[Event] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"invalid JSON at {events_path}:{line_number}: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValidationError(f"event at {events_path}:{line_number} must be an object")
        event = Event.from_dict(payload)
        if event.event_id in seen_ids:
            raise ValidationError(f"duplicate event_id {event.event_id!r}")
        seen_ids.add(event.event_id)
        events.append(event)

    if not events:
        raise ValidationError("scenario contains no events")
    events.sort(key=lambda item: (item.timestamp, item.event_id))
    return scenario, events
