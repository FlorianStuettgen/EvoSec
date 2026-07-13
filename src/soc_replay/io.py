from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
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


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, newline="") as handle:
        handle.write(content)
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(64 * 1024), b""):
                digest.update(chunk)
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc
    return digest.hexdigest()


@dataclass(frozen=True)
class LoadedScenario:
    directory: Path
    scenario: Scenario
    events: tuple[Event, ...]
    scenario_sha256: str
    events_sha256: str

    @property
    def run_id(self) -> str:
        payload = f"{self.scenario.schema_version}:{self.scenario_sha256}:{self.events_sha256}".encode()
        return hashlib.sha256(payload).hexdigest()[:16]


def load_scenario(directory: str | Path) -> LoadedScenario:
    scenario_dir = Path(directory)
    scenario_path = scenario_dir / "scenario.json"
    events_path = scenario_dir / "events.jsonl"
    scenario = Scenario.from_dict(_read_json(scenario_path))
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
    return LoadedScenario(
        directory=scenario_dir,
        scenario=scenario,
        events=tuple(events),
        scenario_sha256=sha256_file(scenario_path),
        events_sha256=sha256_file(events_path),
    )
