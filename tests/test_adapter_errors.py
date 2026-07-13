from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.adapters.suricata import SuricataAdapter, normalize_eve_record
from soc_replay.models import ValidationError


class AdapterErrorTests(unittest.TestCase):
    def test_record_validation_errors(self) -> None:
        self.assertIsNone(normalize_eve_record({"event_type": "stats"}, 1))
        with self.assertRaisesRegex(ValidationError, "timestamp"):
            normalize_eve_record({"event_type": "alert", "alert": {"signature": "x"}}, 1)
        with self.assertRaisesRegex(ValidationError, "dest_port"):
            normalize_eve_record(
                {"event_type": "flow", "timestamp": "2026-01-01T00:00:00Z", "dest_port": "x"},
                1,
            )
        with self.assertRaisesRegex(ValidationError, "alert must be an object"):
            normalize_eve_record({"event_type": "alert", "timestamp": "2026-01-01T00:00:00Z"}, 1)
        with self.assertRaisesRegex(ValidationError, "signature"):
            normalize_eve_record(
                {"event_type": "alert", "timestamp": "2026-01-01T00:00:00Z", "alert": {}},
                1,
            )
        with self.assertRaisesRegex(ValidationError, "flow must be an object"):
            normalize_eve_record(
                {"event_type": "flow", "timestamp": "2026-01-01T00:00:00Z", "flow": []},
                1,
            )

    def test_file_validation_errors(self) -> None:
        adapter = SuricataAdapter()
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValidationError, "missing"):
                adapter.normalize_file(root / "missing", root / "out")
            source = root / "source.jsonl"
            source.write_text("not-json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "invalid JSON"):
                adapter.normalize_file(source, root / "out")
            source.write_text("[]\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "must be an object"):
                adapter.normalize_file(source, root / "out")
            source.write_text('{"event_type":"stats"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "no supported"):
                adapter.normalize_file(source, root / "out")
