from __future__ import annotations

from collections.abc import Mapping, Set
from types import MappingProxyType
from typing import Any


def freeze_json(value: Any) -> Any:
    """Recursively freeze JSON-compatible values without changing their serialized meaning."""
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): freeze_json(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return tuple(freeze_json(item) for item in value)
    if isinstance(value, Set) and not isinstance(value, str | bytes | bytearray):
        frozen = [freeze_json(item) for item in value]
        return tuple(sorted(frozen, key=repr))
    return value
