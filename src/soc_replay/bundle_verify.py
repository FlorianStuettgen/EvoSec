from __future__ import annotations

from pathlib import Path

from .bundle_verify_identity import check_identity
from .bundle_verify_ledger import check_ledger
from .bundle_verify_support import (
    REPORT_JSON,
    REPORT_MARKDOWN,
    CheckCollector,
    append_source_checks,
    object_value,
    parse_bundle,
)
from .models import ValidationError, VerificationResult
from .serialization import digest_object, sha256_bytes


def verify_bundle(
    directory: str | Path,
    *,
    source_directory: str | Path | None = None,
) -> VerificationResult:
    state = parse_bundle(directory)
    checks = CheckCollector()
    derived = check_identity(state, checks)
    check_ledger(state, derived, checks)

    artifacts = object_value(state.manifest.get("artifacts"), "bundle manifest.artifacts")
    checks.add("artifact_names", [REPORT_JSON, REPORT_MARKDOWN], sorted(artifacts))
    for filename in (REPORT_JSON, REPORT_MARKDOWN):
        record = object_value(artifacts.get(filename), f"bundle manifest.artifacts.{filename}")
        artifact_path = state.directory / filename
        try:
            content = artifact_path.read_bytes()
        except FileNotFoundError as exc:
            raise ValidationError(f"bundle artifact is missing: {artifact_path}") from exc
        checks.add(f"{filename}.sha256", record.get("sha256"), sha256_bytes(content))
        checks.add(f"{filename}.bytes", record.get("bytes"), len(content))

    core = {key: value for key, value in state.manifest.items() if key != "bundle_id"}
    checks.add("bundle_id", digest_object(core), state.manifest.get("bundle_id"))
    if source_directory is not None:
        append_source_checks(checks, state.directory, source_directory)
    frozen_checks = tuple(checks.items)
    return VerificationResult(all(check.passed for check in frozen_checks), frozen_checks)
