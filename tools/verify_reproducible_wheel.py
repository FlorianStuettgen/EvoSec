from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_DIRECTORY = ROOT / "build" / "reproducibility"
_SOURCE_IGNORE = shutil.ignore_patterns(
    ".git",
    ".venv",
    ".coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.egg-info",
    "build",
    "dist",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_source(destination: Path) -> Path:
    source = destination / "source"
    shutil.copytree(ROOT, source, ignore=_SOURCE_IGNORE)
    return source


def _build(source: Path, destination: Path) -> Path:
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONHASHSEED": "0",
            "SOURCE_DATE_EPOCH": "946684800",
        }
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(destination),
        ],
        cwd=source,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        print("ERROR: wheel build failed")
        if completed.stdout:
            print("--- build stdout ---")
            print(completed.stdout.rstrip())
        if completed.stderr:
            print("--- build stderr ---")
            print(completed.stderr.rstrip())
        raise RuntimeError(f"wheel build exited with status {completed.returncode}")
    wheels = tuple(destination.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one wheel in {destination}, found {len(wheels)}")
    return wheels[0]


def _entry_hashes(path: Path) -> dict[str, str]:
    with ZipFile(path) as archive:
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in sorted(archive.namelist())}


def _entry_metadata(path: Path) -> dict[str, dict[str, object]]:
    with ZipFile(path) as archive:
        return {
            info.filename: {
                "crc": info.CRC,
                "compressed_size": info.compress_size,
                "file_size": info.file_size,
                "date_time": list(info.date_time),
                "compression": info.compress_type,
                "external_attr": info.external_attr,
                "create_system": info.create_system,
            }
            for info in sorted(archive.infolist(), key=lambda item: item.filename)
        }


def _preserve_failure(first: Path, second: Path, differing: list[str]) -> Path:
    DIAGNOSTIC_DIRECTORY.mkdir(parents=True, exist_ok=True)
    first_copy = DIAGNOSTIC_DIRECTORY / "first.whl"
    second_copy = DIAGNOSTIC_DIRECTORY / "second.whl"
    shutil.copy2(first, first_copy)
    shutil.copy2(second, second_copy)
    payload = {
        "first": {
            "filename": first.name,
            "sha256": _sha256(first),
            "entries": _entry_metadata(first),
        },
        "second": {
            "filename": second.name,
            "sha256": _sha256(second),
            "entries": _entry_metadata(second),
        },
        "differing_entries": differing,
    }
    diagnostics = DIAGNOSTIC_DIRECTORY / "diagnostics.json"
    diagnostics.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return diagnostics


def main() -> int:
    DIAGNOSTIC_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for path in DIAGNOSTIC_DIRECTORY.iterdir():
        if path.is_file():
            path.unlink()
    with TemporaryDirectory() as first_dir, TemporaryDirectory() as second_dir:
        first_root = Path(first_dir)
        second_root = Path(second_dir)
        first_source = _copy_source(first_root)
        second_source = _copy_source(second_root)
        try:
            first = _build(first_source, first_root / "dist")
            second = _build(second_source, second_root / "dist")
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            return 1
        if first.name != second.name:
            print(f"ERROR: wheel names differ: {first.name!r} != {second.name!r}")
            return 1
        first_hash = _sha256(first)
        second_hash = _sha256(second)
        if first_hash != second_hash:
            first_entries = _entry_hashes(first)
            second_entries = _entry_hashes(second)
            differing = sorted(
                name
                for name in set(first_entries) | set(second_entries)
                if first_entries.get(name) != second_entries.get(name)
            )
            diagnostics = _preserve_failure(first, second, differing)
            print(f"ERROR: wheel bytes are not reproducible: {first_hash} != {second_hash}")
            if differing:
                for name in differing:
                    print(f"  differing entry content: {name}")
            else:
                print("  entry contents match; ZIP container metadata or ordering differs")
            print(f"  diagnostics: {diagnostics}")
            return 1
        print(f"reproducible wheel: PASS ({first.name}, sha256={first_hash})")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
