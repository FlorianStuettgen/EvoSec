"""Offline adapters that normalize sanitized vendor telemetry into SOC_Replay events."""

from .suricata import AdapterResult, normalize_suricata_file

__all__ = ["AdapterResult", "normalize_suricata_file"]
