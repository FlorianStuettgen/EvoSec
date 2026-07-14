from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence, Set
from dataclasses import dataclass
from typing import Any

from .models import SUPPORTED_OPERATORS, ValidationError

OperatorFn = Callable[[Any, Any], bool]


def _exists(actual: Any, expected: Any) -> bool:
    should_exist = True if expected is None else bool(expected)
    return (actual is not None) is should_exist


def _eq(actual: Any, expected: Any) -> bool:
    return bool(actual == expected)


def _ne(actual: Any, expected: Any) -> bool:
    return bool(actual != expected)


def _in(actual: Any, expected: Any) -> bool:
    try:
        return actual in expected
    except TypeError:
        return False


def _not_in(actual: Any, expected: Any) -> bool:
    return not _in(actual, expected)


def _contains(actual: Any, expected: Any) -> bool:
    if isinstance(actual, Mapping):
        try:
            return expected in actual
        except TypeError:
            return False
    if isinstance(actual, str | Sequence | Set) and not isinstance(actual, bytes | bytearray):
        try:
            return expected in actual
        except TypeError:
            return False
    return False


def _gte(actual: Any, expected: Any) -> bool:
    try:
        return bool(actual >= expected)
    except TypeError:
        return False


def _lte(actual: Any, expected: Any) -> bool:
    try:
        return bool(actual <= expected)
    except TypeError:
        return False


@dataclass(frozen=True, slots=True)
class OperatorSpec:
    name: str
    evaluate: OperatorFn
    description: str


_SPECS = {
    "exists": OperatorSpec("exists", _exists, "Field has or lacks a non-null value."),
    "eq": OperatorSpec("eq", _eq, "Equality comparison."),
    "ne": OperatorSpec("ne", _ne, "Inequality comparison."),
    "in": OperatorSpec("in", _in, "Value is a member of the configured collection."),
    "not_in": OperatorSpec("not_in", _not_in, "Value is not a member of the configured collection."),
    "contains": OperatorSpec("contains", _contains, "String, sequence, set, or mapping contains the configured value."),
    "gte": OperatorSpec("gte", _gte, "Greater-than-or-equal comparison."),
    "lte": OperatorSpec("lte", _lte, "Less-than-or-equal comparison."),
}

if set(_SPECS) != SUPPORTED_OPERATORS:
    raise RuntimeError("operator registry and public model contract are out of sync")


def get_operator(name: str) -> OperatorSpec:
    try:
        return _SPECS[name]
    except KeyError as exc:
        raise ValidationError(f"unsupported operator {name!r}") from exc


def operator_catalog() -> tuple[OperatorSpec, ...]:
    return tuple(_SPECS[name] for name in sorted(_SPECS))
