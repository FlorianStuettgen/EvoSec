from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..models import ValidationError


@dataclass(frozen=True, slots=True)
class AdapterDescriptor:
    name: str
    version: str
    source_format: str
    supported_record_types: tuple[str, ...]
    safety_boundary: str


@dataclass(frozen=True, slots=True)
class AdapterResult:
    adapter: AdapterDescriptor
    source: Path
    destination: Path
    records_read: int
    records_written: int
    records_skipped: int
    output_sha256: str


class TelemetryAdapter(Protocol):
    descriptor: AdapterDescriptor

    def normalize_file(self, source: str | Path, destination: str | Path) -> AdapterResult: ...


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, TelemetryAdapter] = {}
        self._frozen = False

    @property
    def frozen(self) -> bool:
        return self._frozen

    def register(self, adapter: TelemetryAdapter) -> None:
        if self._frozen:
            raise RuntimeError("adapter registry is frozen")
        name = adapter.descriptor.name
        if not name or name in self._adapters:
            raise ValueError(f"adapter {name!r} is already registered or invalid")
        self._adapters[name] = adapter

    def freeze(self) -> None:
        self._frozen = True

    def get(self, name: str) -> TelemetryAdapter:
        try:
            return self._adapters[name]
        except KeyError as exc:
            available = ", ".join(sorted(self._adapters)) or "none"
            raise ValidationError(f"unknown adapter {name!r}; available: {available}") from exc

    def descriptors(self) -> tuple[AdapterDescriptor, ...]:
        return tuple(self._adapters[name].descriptor for name in sorted(self._adapters))
