from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._version import __version__
from .contracts import (
    ENGINE_NAME,
    MANIFEST_SCHEMA_VERSION,
)
from .io import atomic_write_text
from .models import VerificationResult
from .report_render import render_json, render_markdown
from .result import ReplayResult
from .serialization import digest_object, pretty_json, sha256_bytes

_REPORT_JSON = "report.json"
_REPORT_MARKDOWN = "report.md"
_MANIFEST_JSON = "manifest.json"


@dataclass(frozen=True, slots=True)
class ReportBundle:
    directory: Path
    json_path: Path
    markdown_path: Path
    manifest_path: Path
    bundle_id: str


def _artifact_record(content: str) -> dict[str, Any]:
    encoded = content.encode("utf-8")
    return {"sha256": sha256_bytes(encoded), "bytes": len(encoded)}


def _manifest_core(result: ReplayResult, json_content: str, markdown_content: str) -> dict[str, Any]:
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": __version__},
        "run_id": result.loaded.run_id,
        "plan_fingerprint": result.plan.fingerprint,
        "ledger_root": result.ledger.root_hash,
        "inputs": {
            "scenario_sha256": result.loaded.scenario_sha256,
            "events_sha256": result.loaded.events_sha256,
        },
        "verification_passed": result.verification.passed,
        "artifacts": {
            _REPORT_JSON: _artifact_record(json_content),
            _REPORT_MARKDOWN: _artifact_record(markdown_content),
        },
    }


def render_manifest(result: ReplayResult, json_content: str, markdown_content: str) -> str:
    core = _manifest_core(result, json_content, markdown_content)
    return pretty_json({**core, "bundle_id": digest_object(core)})


def write_bundle(result: ReplayResult, output_dir: str | Path) -> ReportBundle:
    destination = Path(output_dir)
    json_path = destination / _REPORT_JSON
    markdown_path = destination / _REPORT_MARKDOWN
    manifest_path = destination / _MANIFEST_JSON
    json_content = render_json(result)
    markdown_content = render_markdown(result)
    manifest_content = render_manifest(result, json_content, markdown_content)
    manifest = json.loads(manifest_content)
    # Manifest-last commit protocol: its presence indicates both artifacts were fully replaced.
    atomic_write_text(json_path, json_content)
    atomic_write_text(markdown_path, markdown_content)
    atomic_write_text(manifest_path, manifest_content)
    return ReportBundle(destination, json_path, markdown_path, manifest_path, str(manifest["bundle_id"]))


def write_reports(result: ReplayResult, output_dir: str | Path) -> tuple[Path, Path]:
    bundle = write_bundle(result, output_dir)
    return bundle.json_path, bundle.markdown_path




def verify_bundle(
    directory: str | Path,
    *,
    source_directory: str | Path | None = None,
) -> VerificationResult:
    """Verify a report bundle, optionally reproducing it from a source scenario."""
    from .bundle_verify import verify_bundle as implementation

    return implementation(directory, source_directory=source_directory)
