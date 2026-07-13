from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from .models import Event, Scenario, ValidationError
from .serialization import sha256_bytes


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return payload


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, newline="") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class LoadedScenario:
    directory: Path
    scenario: Scenario
    events: tuple[Event, ...]
    scenario_sha256: str
    events_sha256: str

    @property
    def run_id(self) -> str:
        payload = f"{self.scenario.schema_version}:{self.scenario_sha256}:{self.events_sha256}".encode()
        return sha256_bytes(payload)[:16]


def _load_events(path: Path, *, max_events: int) -> tuple[Event, ...]:
    try:
        handle = path.open("r", encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc
    events: list[Event] = []
    seen_ids: set[str] = set()
    with handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            if len(events) >= max_events:
                raise ValidationError(f"scenario exceeds max_events={max_events}")
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValidationError(f"event at {path}:{line_number} must be an object")
            event = Event.from_dict(payload)
            if event.event_id in seen_ids:
                raise ValidationError(f"duplicate event_id {event.event_id!r}")
            seen_ids.add(event.event_id)
            events.append(event)
    if not events:
        raise ValidationError("scenario contains no events")
    events.sort(key=lambda item: (item.timestamp, item.event_id))
    return tuple(events)


def load_scenario(directory: str | Path, *, max_events: int = 1_000_000) -> LoadedScenario:
    scenario_dir = Path(directory)
    scenario_path = scenario_dir / "scenario.json"
    events_path = scenario_dir / "events.jsonl"
    return LoadedScenario(
        directory=scenario_dir,
        scenario=Scenario.from_dict(_read_json(scenario_path)),
        events=_load_events(events_path, max_events=max_events),
        scenario_sha256=sha256_file(scenario_path),
        events_sha256=sha256_file(events_path),
    )
