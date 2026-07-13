from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from soc_replay.io import load_scenario, sha256_file
from soc_replay.ledger import LedgerBuilder, require_valid_ledger, verify_ledger_payload
from soc_replay.models import ValidationError

ROOT = Path(__file__).resolve().parents[1]


class IoLedgerErrorTests(unittest.TestCase):
    def test_missing_and_invalid_scenario_files(self) -> None:
        with self.assertRaisesRegex(ValidationError, "missing required file"):
            load_scenario(ROOT / "scenarios" / "missing")
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "scenario.json").write_text("[]", encoding="utf-8")
            (directory / "events.jsonl").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "JSON object"):
                load_scenario(directory)
            (directory / "scenario.json").write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "invalid JSON"):
                load_scenario(directory)

    def test_invalid_event_streams(self) -> None:
        source = ROOT / "scenarios" / "network-scan" / "scenario.json"
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "scenario.json").write_bytes(source.read_bytes())
            (directory / "events.jsonl").write_text("not-json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "invalid JSON"):
                load_scenario(directory)
            (directory / "events.jsonl").write_text("[]\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "must be an object"):
                load_scenario(directory)
            event = {
                "event_id": "dup",
                "timestamp": "2026-01-01T00:00:00Z",
                "source": "x",
                "category": "x",
                "action": "x",
            }
            line = json.dumps(event)
            (directory / "events.jsonl").write_text(f"{line}\n{line}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "duplicate"):
                load_scenario(directory)
            (directory / "events.jsonl").write_text("\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "no events"):
                load_scenario(directory)

    def test_sha256_missing_file(self) -> None:
        with self.assertRaisesRegex(ValidationError, "missing required file"):
            sha256_file(ROOT / "missing")

    def test_ledger_builder_and_corruption_matrix(self) -> None:
        builder = LedgerBuilder()
        with self.assertRaisesRegex(ValueError, "stage"):
            builder.append(stage="", input_digest="a", output_digest="b", records_in=0, records_out=0)
        with self.assertRaisesRegex(ValueError, "status"):
            builder.append(stage="x", status="bad", input_digest="a", output_digest="b", records_in=0, records_out=0)
        builder.append(stage="x", input_digest="a", output_digest="b", records_in=1, records_out=1)
        payload = builder.freeze().to_dict()
        self.assertTrue(verify_ledger_payload(payload)[0])
        cases = [
            (None, "object"),
            ({**payload, "schema_version": "9"}, "schema_version"),
            ({**payload, "genesis_hash": "bad"}, "genesis"),
            ({**payload, "entries": {}}, "entries"),
            ({**payload, "root_hash": "bad"}, "root_hash"),
        ]
        for candidate, message in cases:
            with self.subTest(message=message):
                passed, errors = verify_ledger_payload(candidate)
                self.assertFalse(passed)
                self.assertTrue(any(message in error for error in errors))
        broken = builder.freeze().to_dict()
        broken["entries"][0].pop("stage")
        self.assertFalse(verify_ledger_payload(broken)[0])
        with self.assertRaisesRegex(ValidationError, "invalid execution ledger"):
            require_valid_ledger(broken)
