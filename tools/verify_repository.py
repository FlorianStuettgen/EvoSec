from __future__ import annotations

import ast
import json
import tomllib
from pathlib import Path

from soc_replay import __version__
from soc_replay.adapters import adapter_registry
from soc_replay.contracts import (
    CURRENT_SCENARIO_SCHEMA_VERSION,
    INDEX_FIELDS,
    PIPELINE_STAGES,
)
from soc_replay.engine import run_scenario
from soc_replay.ledger import verify_ledger_payload
from soc_replay.operators import operator_catalog
from soc_replay.pipeline import ReplayPipeline

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "network-scan",
    "privileged-group-change",
    "failed-authentication-burst",
    "benign-privileged-change",
)
REQUIRED_DOCS = (
    "docs/11-Replay-Engine.md",
    "docs/14-Implementation-State.md",
    "docs/16-Engineering-Review.md",
    "docs/17-Architecture-Decisions.md",
    "docs/18-Evidence-Bundles.md",
    "docs/22-Execution-Core.md",
    "docs/23-Execution-Ledger.md",
    "docs/24-Contract-Validation.md",
)
REQUIRED_SCHEMAS = (
    "schemas/event.schema.json",
    "schemas/scenario.schema.json",
    "schemas/report.schema.json",
    "schemas/bundle-manifest.schema.json",
    "schemas/execution-ledger.schema.json",
)
REQUIRED_TOOLS = (
    "tools/validate_contracts.py",
    "tools/verify_deterministic_bundles.py",
)


def _version_from_pyproject() -> str:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def _check_import_safety() -> list[str]:
    forbidden = {"socket", "subprocess", "paramiko", "requests", "urllib.request"}
    errors: list[str] = []
    for path in sorted((ROOT / "src" / "soc_replay").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""}
            else:
                continue
            blocked = sorted(name for name in names if name in forbidden)
            if blocked:
                errors.append(f"forbidden live-I/O import in {path.relative_to(ROOT)}: {', '.join(blocked)}")
    return errors


def main() -> int:
    errors: list[str] = []
    if _version_from_pyproject() != __version__:
        errors.append("pyproject and package versions differ")
    if ReplayPipeline.DESCRIPTION.stages != PIPELINE_STAGES:
        errors.append("pipeline stage contract changed unexpectedly")
    if len(operator_catalog()) != 8:
        errors.append("operator registry is incomplete")
    registry = adapter_registry()
    if not registry.descriptors():
        errors.append("adapter registry is empty")
    if not registry.frozen:
        errors.append("global adapter registry must be frozen")
    for relative in REQUIRED_DOCS + REQUIRED_SCHEMAS + REQUIRED_TOOLS:
        if not (ROOT / relative).exists():
            errors.append(f"missing required repository file: {relative}")
    for schema in REQUIRED_SCHEMAS:
        try:
            payload = json.loads((ROOT / schema).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid schema {schema}: {exc}")
            continue
        if payload.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"schema is not draft 2020-12: {schema}")

    for name in SCENARIOS:
        result = run_scenario(ROOT / "scenarios" / name)
        if result.scenario.schema_version != CURRENT_SCENARIO_SCHEMA_VERSION:
            errors.append(f"maintained scenario is not current schema version: {name}")
        if result.scenario.expectations.detection_contracts is None:
            errors.append(f"maintained scenario lacks exact detection contracts: {name}")
        if not result.verification.passed:
            errors.append(f"scenario verification failed: {name}")
        if len(result.rule_executions) != len(result.plan.rules):
            errors.append(f"rule trace count does not match plan: {name}")
        if sum(execution.detection_count for execution in result.rule_executions) != len(result.detections):
            errors.append(f"rule traces do not account for every detection: {name}")
        ledger_valid, ledger_errors = verify_ledger_payload(result.ledger.to_dict(), require_complete=True)
        if not ledger_valid:
            errors.extend(f"{name}: {error}" for error in ledger_errors)
        if len(result.ledger.entries) != len(PIPELINE_STAGES):
            errors.append(f"unexpected ledger length: {name}")
        index_fields = result.ledger.entries[2].metadata.get("index_fields")
        if list(index_fields) != [*INDEX_FIELDS, "tags"]:
            errors.append(f"index-field contract drift: {name}")

    errors.extend(_check_import_safety())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "repository verification: PASS "
        f"({len(SCENARIOS)} exact scenarios, {len(operator_catalog())} operators, "
        f"{len(registry.descriptors())} frozen adapters)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
