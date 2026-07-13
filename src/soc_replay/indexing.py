from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .compiler import CandidateHint, CompiledRule
from .models import Event


@dataclass(frozen=True, slots=True)
class CandidateSet:
    events: tuple[Event, ...]
    strategy: str


class EventIndex:
    """Immutable deterministic indexes for common equality selectors and tags."""

    _FIELDS = ("category", "action", "outcome", "source", "host", "user")

    def __init__(self, events: tuple[Event, ...]) -> None:
        self._events = events
        by_field: dict[str, dict[Any, list[Event]]] = {field: defaultdict(list) for field in self._FIELDS}
        by_tag: dict[str, list[Event]] = defaultdict(list)
        for event in events:
            for field in self._FIELDS:
                value = getattr(event, field)
                if value is not None:
                    by_field[field][value].append(event)
            for tag in event.tags:
                by_tag[tag].append(event)
        self._by_field = {
            field: {value: tuple(items) for value, items in values.items()} for field, values in by_field.items()
        }
        self._by_tag = {tag: tuple(items) for tag, items in by_tag.items()}

    @property
    def events(self) -> tuple[Event, ...]:
        return self._events

    def candidates(self, rule: CompiledRule) -> CandidateSet:
        hint: CandidateHint | None = rule.candidate_hint
        if hint is None:
            return CandidateSet(self._events, "full_scan")
        if hint.field == "tags":
            return CandidateSet(self._by_tag.get(hint.value, ()), f"tag:{hint.value}")
        return CandidateSet(
            self._by_field.get(hint.field, {}).get(hint.value, ()),
            f"eq:{hint.field}={hint.value}",
        )
