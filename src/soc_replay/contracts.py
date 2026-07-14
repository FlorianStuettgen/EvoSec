from __future__ import annotations

ENGINE_NAME = "soc-replay"
PIPELINE_NAME = "soc-replay-evidence-pipeline"
PIPELINE_STAGES = ("load", "compile", "index", "evaluate", "verify")
INDEX_FIELDS = ("category", "action", "outcome", "source", "host", "user")

SCENARIO_SCHEMA_VERSIONS = frozenset({"1.0", "1.1"})
CURRENT_SCENARIO_SCHEMA_VERSION = "1.1"
REPORT_SCHEMA_VERSION = "2.1"
MANIFEST_SCHEMA_VERSION = "2.1"
LEDGER_SCHEMA_VERSION = "1.0"
