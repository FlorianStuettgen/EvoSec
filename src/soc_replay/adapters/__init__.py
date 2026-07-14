from __future__ import annotations

from pathlib import Path

from .base import AdapterDescriptor, AdapterRegistry, AdapterResult, TelemetryAdapter
from .suricata import SuricataAdapter, normalize_eve_record, normalize_suricata_file

_registry = AdapterRegistry()
_registry.register(SuricataAdapter())
_registry.freeze()


def adapter_registry() -> AdapterRegistry:
    return _registry


def normalize_file(adapter: str, source: str | Path, destination: str | Path) -> AdapterResult:
    return _registry.get(adapter).normalize_file(source, destination)


__all__ = [
    "AdapterDescriptor",
    "AdapterRegistry",
    "AdapterResult",
    "TelemetryAdapter",
    "SuricataAdapter",
    "adapter_registry",
    "normalize_eve_record",
    "normalize_file",
    "normalize_suricata_file",
]
