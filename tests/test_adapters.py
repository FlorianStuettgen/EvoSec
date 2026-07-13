import json
import tempfile
import unittest
from pathlib import Path

from soc_replay.adapters.suricata import normalize_eve_record, normalize_suricata_file
from soc_replay.models import ValidationError

ROOT = Path(__file__).resolve().parents[1]


class SuricataAdapterTests(unittest.TestCase):
    def test_example_normalization_matches_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "normalized.jsonl"
            result = normalize_suricata_file(ROOT / "examples" / "adapters" / "suricata-eve.jsonl", destination)
            self.assertEqual(result.records_read, 3)
            self.assertEqual(result.records_written, 2)
            self.assertEqual(result.records_skipped, 1)
            self.assertEqual(
                destination.read_bytes(),
                (ROOT / "examples" / "adapters" / "suricata-normalized.jsonl").read_bytes(),
            )

    def test_alert_record_is_normalized_and_validated(self) -> None:
        payload = {
            "timestamp": "2026-07-01T12:00:00Z",
            "event_type": "alert",
            "src_ip": "10.0.0.1",
            "dest_ip": "10.0.0.2",
            "dest_port": 443,
            "alert": {"signature": "Synthetic alert", "action": "blocked"},
        }
        normalized = normalize_eve_record(payload, 4)
        self.assertIsNotNone(normalized)
        assert normalized is not None
        self.assertEqual(normalized["outcome"], "blocked")
        self.assertEqual(normalized["event_id"].split("-")[-1], "000004")

    def test_unsupported_record_is_skipped(self) -> None:
        self.assertIsNone(normalize_eve_record({"event_type": "stats"}, 1))

    def test_input_with_no_supported_records_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "eve.jsonl"
            source.write_text(json.dumps({"event_type": "stats"}) + "\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                normalize_suricata_file(source, Path(temp_dir) / "normalized.jsonl")

    def test_alert_without_alert_object_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_eve_record(
                {"timestamp": "2026-07-01T12:00:00Z", "event_type": "alert"},
                1,
            )


if __name__ == "__main__":
    unittest.main()
