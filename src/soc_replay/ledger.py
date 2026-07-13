from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ValidationError
from .serialization import digest_object

_GENESIS_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    sequence: int
    stage: str
    status: str
    input_digest: str
    output_digest: str
    records_in: int
    records_out: int
    metadata: dict[str, Any]
    previous_hash: str
    entry_hash: str

    def core_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "stage": self.stage,
            "status": self.status,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "records_in": self.records_in,
            "records_out": self.records_out,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core_dict(), "entry_hash": self.entry_hash}


@dataclass(frozen=True, slots=True)
class ExecutionLedger:
    entries: tuple[LedgerEntry, ...]
    root_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "genesis_hash": _GENESIS_HASH,
            "root_hash": self.root_hash,
            "entries": [entry.to_dict() for entry in self.entries],
        }


class LedgerBuilder:
    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    def append(
        self,
        *,
        stage: str,
        input_digest: str,
        output_digest: str,
        records_in: int,
        records_out: int,
        metadata: dict[str, Any] | None = None,
        status: str = "ok",
    ) -> LedgerEntry:
        if not stage.strip():
            raise ValueError("ledger stage must be non-empty")
        if status not in {"ok", "failed"}:
            raise ValueError("ledger status must be 'ok' or 'failed'")
        previous = self._entries[-1].entry_hash if self._entries else _GENESIS_HASH
        sequence = len(self._entries) + 1
        core = {
            "sequence": sequence,
            "stage": stage,
            "status": status,
            "input_digest": input_digest,
            "output_digest": output_digest,
            "records_in": records_in,
            "records_out": records_out,
            "metadata": metadata or {},
            "previous_hash": previous,
        }
        entry = LedgerEntry(
            sequence=sequence,
            stage=stage,
            status=status,
            input_digest=input_digest,
            output_digest=output_digest,
            records_in=records_in,
            records_out=records_out,
            metadata=metadata or {},
            previous_hash=previous,
            entry_hash=digest_object(core),
        )
        self._entries.append(entry)
        return entry

    def freeze(self) -> ExecutionLedger:
        root = self._entries[-1].entry_hash if self._entries else _GENESIS_HASH
        return ExecutionLedger(tuple(self._entries), root)


def verify_ledger_payload(payload: Any) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return False, ("ledger must be an object",)
    if payload.get("schema_version") != "1.0":
        errors.append("unsupported ledger schema_version")
    if payload.get("genesis_hash") != _GENESIS_HASH:
        errors.append("invalid ledger genesis_hash")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return False, tuple(errors + ["ledger entries must be a list"])
    previous = _GENESIS_HASH
    for index, raw in enumerate(entries, start=1):
        if not isinstance(raw, dict):
            errors.append(f"ledger entry {index} must be an object")
            continue
        expected_keys = {
            "sequence",
            "stage",
            "status",
            "input_digest",
            "output_digest",
            "records_in",
            "records_out",
            "metadata",
            "previous_hash",
            "entry_hash",
        }
        if set(raw) != expected_keys:
            errors.append(f"ledger entry {index} has an invalid field set")
            continue
        if raw.get("sequence") != index:
            errors.append(f"ledger entry {index} has an invalid sequence")
        if raw.get("previous_hash") != previous:
            errors.append(f"ledger entry {index} breaks the hash chain")
        core = {key: raw[key] for key in expected_keys - {"entry_hash"}}
        expected_hash = digest_object(core)
        if raw.get("entry_hash") != expected_hash:
            errors.append(f"ledger entry {index} hash mismatch")
        previous = str(raw.get("entry_hash"))
    if payload.get("root_hash") != previous:
        errors.append("ledger root_hash mismatch")
    return not errors, tuple(errors)


def require_valid_ledger(payload: Any) -> None:
    passed, errors = verify_ledger_payload(payload)
    if not passed:
        raise ValidationError("invalid execution ledger: " + "; ".join(errors))
