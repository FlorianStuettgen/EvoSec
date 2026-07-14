from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .compiler import CandidateSelector, CompiledRule
from .contracts import INDEX_FIELDS
from .models import Event


@dataclass(frozen=True, slots=True)
class CandidateSet:
    events: tuple[Event, ...]
    strategy: str


class EventIndex:
    """Immutable deterministic indexes for common equality selectors and tags."""

    def __init__(self, events: tuple[Event, ...]) -> None:
        self._events = events
        self._positions = MappingProxyType({event.event_id: index for index, event in enumerate(events)})
        by_field: dict[str, dict[Any, list[Event]]] = {field: defaultdict(list) for field in INDEX_FIELDS}
        by_tag: dict[str, list[Event]] = defaultdict(list)
        for event in events:
            for field in INDEX_FIELDS:
                value = getattr(event, field)
                if value is not None:
                    by_field[field][value].append(event)
            for tag in event.tags:
                by_tag[tag].append(event)
        frozen_fields: dict[str, Mapping[Any, tuple[Event, ...]]] = {
            field: MappingProxyType({value: tuple(items) for value, items in values.items()})
            for field, values in by_field.items()
        }
        frozen_tags: dict[str, tuple[Event, ...]] = {tag: tuple(items) for tag, items in by_tag.items()}
        self._by_field: Mapping[str, Mapping[Any, tuple[Event, ...]]] = MappingProxyType(frozen_fields)
        self._by_tag: Mapping[str, tuple[Event, ...]] = MappingProxyType(frozen_tags)

    @property
    def events(self) -> tuple[Event, ...]:
        return self._events

    def _selector_events(self, selector: CandidateSelector) -> tuple[Event, ...]:
        if selector.field == "tags":
            return self._by_tag.get(selector.value, ())
        return self._by_field.get(selector.field, {}).get(selector.value, ())

    @staticmethod
    def _selector_label(selector: CandidateSelector) -> str:
        if selector.field == "tags":
            return f"tag:{selector.value}"
        return f"eq:{selector.field}={selector.value}"

    def candidates(self, rule: CompiledRule) -> CandidateSet:
        selectors = rule.candidate_selectors
        if not selectors:
            return CandidateSet(self._events, "full_scan")

        pools = [(selector, self._selector_events(selector)) for selector in selectors]
        labels = [self._selector_label(selector) for selector, _ in pools]
        strategy = labels[0] if len(labels) == 1 else f"intersection[{','.join(labels)}]"
        if any(not events for _, events in pools):
            return CandidateSet((), strategy)

        candidate_ids = set(event.event_id for event in pools[0][1])
        for _, events in pools[1:]:
            candidate_ids.intersection_update(event.event_id for event in events)
            if not candidate_ids:
                return CandidateSet((), strategy)

        smallest_pool = min((events for _, events in pools), key=len)
        selected = [event for event in smallest_pool if event.event_id in candidate_ids]
        selected.sort(key=lambda event: self._positions[event.event_id])
        return CandidateSet(tuple(selected), strategy)
