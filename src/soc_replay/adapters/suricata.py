from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..io import atomic_write_text, sha256_file
from ..models import Event, ValidationError
from .base import AdapterDescriptor, AdapterResult

_SUPPORTED_EVENT_TYPES = {"alert", "flow"}


def _required_string(payload: dict[str, Any], key: str, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def _optional_int(payload: dict[str, Any], key: str, context: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(f"{context}.{key} must be an integer or null")
    return value


def _stable_event_id(payload: dict[str, Any], line_number: int) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()[:12]
    flow_id = payload.get("flow_id")
    prefix = str(flow_id) if isinstance(flow_id, (int, str)) else digest
    return f"suricata-{prefix}-{line_number:06d}"


def normalize_eve_record(payload: dict[str, Any], line_number: int) -> dict[str, Any] | None:
    event_type = payload.get("event_type")
    if event_type not in _SUPPORTED_EVENT_TYPES:
        return None
    timestamp = _required_string(payload, "timestamp", f"Suricata line {line_number}")
    destination_port = _optional_int(payload, "dest_port", f"Suricata line {line_number}")
    details: dict[str, Any] = {
        "event_type": event_type,
        "flow_id": payload.get("flow_id"),
        "proto": payload.get("proto"),
        "app_proto": payload.get("app_proto"),
        "in_iface": payload.get("in_iface"),
    }
    if event_type == "alert":
        alert = payload.get("alert")
        if not isinstance(alert, dict):
            raise ValidationError(f"Suricata line {line_number}.alert must be an object")
        signature = _required_string(alert, "signature", f"Suricata line {line_number}.alert")
        alert_action = str(alert.get("action", "allowed")).strip().lower()
        details.update(
            {
                "signature": signature,
                "signature_id": alert.get("signature_id"),
                "category": alert.get("category"),
                "severity": alert.get("severity"),
                "alert_action": alert_action,
            }
        )
        normalized: dict[str, Any] = {
            "event_id": _stable_event_id(payload, line_number),
            "timestamp": timestamp,
            "source": "suricata",
            "category": "network_alert",
            "action": "alert",
            "source_ip": payload.get("src_ip"),
            "destination_ip": payload.get("dest_ip"),
            "destination_port": destination_port,
            "outcome": "blocked" if alert_action in {"blocked", "block"} else "observed",
            "tags": ["suricata", "alert"],
            "details": details,
        }
    else:
        flow = payload.get("flow")
        if flow is not None and not isinstance(flow, dict):
            raise ValidationError(f"Suricata line {line_number}.flow must be an object")
        flow_details = flow if isinstance(flow, dict) else {}
        details.update(
            {
                "state": flow_details.get("state"),
                "reason": flow_details.get("reason"),
                "pkts_toserver": flow_details.get("pkts_toserver"),
                "pkts_toclient": flow_details.get("pkts_toclient"),
                "bytes_toserver": flow_details.get("bytes_toserver"),
                "bytes_toclient": flow_details.get("bytes_toclient"),
            }
        )
        normalized = {
            "event_id": _stable_event_id(payload, line_number),
            "timestamp": timestamp,
            "source": "suricata",
            "category": "network_connection",
            "action": "flow",
            "source_ip": payload.get("src_ip"),
            "destination_ip": payload.get("dest_ip"),
            "destination_port": destination_port,
            "outcome": "observed",
            "tags": ["suricata", "flow"],
            "details": details,
        }
    event = Event.from_dict(normalized)
    normalized["timestamp"] = event.timestamp.isoformat().replace("+00:00", "Z")
    return normalized


class SuricataAdapter:
    descriptor = AdapterDescriptor(
        name="suricata-eve",
        version="1.0",
        source_format="Suricata EVE JSONL",
        supported_record_types=("alert", "flow"),
        safety_boundary="Stored synthetic or sanitized files only; no sensor connection or credentials.",
    )

    def normalize_file(self, source: str | Path, destination: str | Path) -> AdapterResult:
        source_path = Path(source)
        destination_path = Path(destination)
        try:
            lines = source_path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError as exc:
            raise ValidationError(f"missing Suricata EVE input: {source_path}") from exc
        normalized_records: list[dict[str, Any]] = []
        records_read = 0
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            records_read += 1
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"invalid JSON at {source_path}:{line_number}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValidationError(f"Suricata record at {source_path}:{line_number} must be an object")
            normalized = normalize_eve_record(payload, line_number)
            if normalized is not None:
                normalized_records.append(normalized)
        if not normalized_records:
            raise ValidationError("Suricata input contains no supported alert or flow records")
        content = "".join(
            json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in normalized_records
        )
        atomic_write_text(destination_path, content)
        return AdapterResult(
            self.descriptor,
            source_path,
            destination_path,
            records_read,
            len(normalized_records),
            records_read - len(normalized_records),
            sha256_file(destination_path),
        )


def normalize_suricata_file(source: str | Path, destination: str | Path) -> AdapterResult:
    return SuricataAdapter().normalize_file(source, destination)
