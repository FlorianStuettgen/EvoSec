from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build(destination: Path) -> Path:
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONHASHSEED": "0",
            "SOURCE_DATE_EPOCH": "946684800",
        }
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(destination),
        ],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    wheels = tuple(destination.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one wheel in {destination}, found {len(wheels)}")
    return wheels[0]


def _entry_hashes(path: Path) -> dict[str, str]:
    with ZipFile(path) as archive:
        return {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in sorted(archive.namelist())
        }


def main() -> int:
    with TemporaryDirectory() as first_dir, TemporaryDirectory() as second_dir:
        first = _build(Path(first_dir))
        second = _build(Path(second_dir))
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
            print(f"ERROR: wheel bytes are not reproducible: {first_hash} != {second_hash}")
            for name in differing:
                print(f"  differing entry: {name}")
            return 1
        print(f"reproducible wheel: PASS ({first.name}, sha256={first_hash})")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
