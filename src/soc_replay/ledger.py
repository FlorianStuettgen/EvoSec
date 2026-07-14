from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import LEDGER_SCHEMA_VERSION, PIPELINE_STAGES
from .immutability import freeze_json
from .models import ValidationError
from .serialization import digest_object, to_primitive

_GENESIS_HASH = "0" * 64
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _valid_count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(_HEX64.fullmatch(value))


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    sequence: int
    stage: str
    status: str
    input_digest: str
    output_digest: str
    records_in: int
    records_out: int
    metadata: Mapping[str, Any]
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
            "metadata": to_primitive(self.metadata),
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
            "schema_version": LEDGER_SCHEMA_VERSION,
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
        metadata: Mapping[str, Any] | None = None,
        status: str = "ok",
    ) -> LedgerEntry:
        if len(self._entries) >= len(PIPELINE_STAGES):
            raise ValueError("execution ledger already contains every pipeline stage")
        expected_stage = PIPELINE_STAGES[len(self._entries)]
        if stage != expected_stage:
            raise ValueError(f"ledger stage must be {expected_stage!r}, not {stage!r}")
        if status not in {"ok", "failed"}:
            raise ValueError("ledger status must be 'ok' or 'failed'")
        if self._entries and self._entries[-1].status == "failed":
            raise ValueError("cannot append after a failed ledger stage")
        if not _valid_digest(input_digest) or not _valid_digest(output_digest):
            raise ValueError("ledger digests must be lowercase 64-character SHA-256 hex strings")
        if not _valid_count(records_in) or not _valid_count(records_out):
            raise ValueError("ledger record counts must be non-negative integers")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise ValueError("ledger metadata must be a mapping")

        previous = self._entries[-1].entry_hash if self._entries else _GENESIS_HASH
        sequence = len(self._entries) + 1
        frozen_metadata = freeze_json(metadata or {})
        core = {
            "sequence": sequence,
            "stage": stage,
            "status": status,
            "input_digest": input_digest,
            "output_digest": output_digest,
            "records_in": records_in,
            "records_out": records_out,
            "metadata": to_primitive(frozen_metadata),
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
            metadata=frozen_metadata,
            previous_hash=previous,
            entry_hash=digest_object(core),
        )
        self._entries.append(entry)
        return entry

    def freeze(self) -> ExecutionLedger:
        root = self._entries[-1].entry_hash if self._entries else _GENESIS_HASH
        return ExecutionLedger(tuple(self._entries), root)


def verify_ledger_payload(payload: Any, *, require_complete: bool = True) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return False, ("ledger must be an object",)
    expected_top = {"schema_version", "genesis_hash", "root_hash", "entries"}
    if set(payload) != expected_top:
        errors.append("ledger has an invalid top-level field set")
    if payload.get("schema_version") != LEDGER_SCHEMA_VERSION:
        errors.append("unsupported ledger schema_version")
    if payload.get("genesis_hash") != _GENESIS_HASH:
        errors.append("invalid ledger genesis_hash")
    if not _valid_digest(payload.get("root_hash")):
        errors.append("ledger root_hash must be a lowercase SHA-256 hex string")

    entries = payload.get("entries")
    if not isinstance(entries, list):
        return False, tuple(errors + ["ledger entries must be a list"])
    if require_complete and len(entries) != len(PIPELINE_STAGES):
        errors.append(f"ledger must contain exactly {len(PIPELINE_STAGES)} entries")
    if not require_complete and len(entries) > len(PIPELINE_STAGES):
        errors.append("ledger contains more entries than the pipeline has stages")

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
        expected_stage = PIPELINE_STAGES[index - 1] if index <= len(PIPELINE_STAGES) else None
        if raw.get("stage") != expected_stage:
            errors.append(f"ledger entry {index} has invalid stage order")
        status = raw.get("status")
        if not isinstance(status, str) or status not in {"ok", "failed"}:
            errors.append(f"ledger entry {index} has an invalid status")
        if require_complete and status != "ok":
            errors.append(f"ledger entry {index} must have status 'ok' in a complete bundle")
        if status == "failed" and index != len(entries):
            errors.append(f"ledger entry {index} is failed but is not the final entry")
        if not _valid_digest(raw.get("input_digest")):
            errors.append(f"ledger entry {index} has an invalid input_digest")
        if not _valid_digest(raw.get("output_digest")):
            errors.append(f"ledger entry {index} has an invalid output_digest")
        if not _valid_count(raw.get("records_in")):
            errors.append(f"ledger entry {index} has an invalid records_in")
        if not _valid_count(raw.get("records_out")):
            errors.append(f"ledger entry {index} has an invalid records_out")
        if not isinstance(raw.get("metadata"), dict):
            errors.append(f"ledger entry {index} metadata must be an object")
        if raw.get("previous_hash") != previous:
            errors.append(f"ledger entry {index} breaks the hash chain")
        if not _valid_digest(raw.get("entry_hash")):
            errors.append(f"ledger entry {index} has an invalid entry_hash")
            previous = str(raw.get("entry_hash"))
            continue
        core = {key: raw[key] for key in expected_keys - {"entry_hash"}}
        expected_hash = digest_object(core)
        if raw.get("entry_hash") != expected_hash:
            errors.append(f"ledger entry {index} hash mismatch")
        previous = str(raw.get("entry_hash"))

    if payload.get("root_hash") != previous:
        errors.append("ledger root_hash mismatch")
    return not errors, tuple(errors)


def require_valid_ledger(payload: Any, *, require_complete: bool = True) -> None:
    passed, errors = verify_ledger_payload(payload, require_complete=require_complete)
    if not passed:
        raise ValidationError("invalid execution ledger: " + "; ".join(errors))
