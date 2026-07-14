from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence, Set
from datetime import datetime
from pathlib import Path
from typing import Any


def to_primitive(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): to_primitive(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [to_primitive(item) for item in value]
    if isinstance(value, Set) and not isinstance(value, str | bytes | bytearray):
        converted = [to_primitive(item) for item in value]
        return sorted(converted, key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False))
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(to_primitive(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def pretty_json(value: Any) -> str:
    return json.dumps(to_primitive(value), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_text(content: str) -> str:
    return sha256_bytes(content.encode("utf-8"))


def digest_object(value: Any) -> str:
    return sha256_text(canonical_json(value))
