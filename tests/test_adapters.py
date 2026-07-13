from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.adapters import adapter_registry, normalize_file
from soc_replay.models import Event, ValidationError

ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def test_registry_exposes_suricata(self) -> None:
        descriptors = adapter_registry().descriptors()
        self.assertEqual([descriptor.name for descriptor in descriptors], ["suricata-eve"])

    def test_suricata_normalization_is_deterministic_and_valid(self) -> None:
        source = ROOT / "examples" / "adapters" / "suricata-eve.jsonl"
        with TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.jsonl"
            second = Path(temporary) / "second.jsonl"
            one = normalize_file("suricata-eve", source, first)
            two = normalize_file("suricata-eve", source, second)
            self.assertEqual(one.output_sha256, two.output_sha256)
            self.assertEqual(one.records_read, 3)
            self.assertEqual(one.records_written, 2)
            self.assertEqual(one.records_skipped, 1)
            for line in first.read_text().splitlines():
                Event.from_dict(json.loads(line))

    def test_unknown_adapter_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "unknown adapter"):
            adapter_registry().get("missing")
