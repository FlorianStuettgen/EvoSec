# 27 — Reproducible Builds

## Goal

A clean source tree should produce the same wheel bytes when built twice with the same toolchain and deterministic build inputs.

## Verification process

`tools/verify_reproducible_wheel.py`:

1. copies the repository into two independent clean source directories;
2. excludes version-control state, caches, virtual environments, build output, distributions, and egg-info metadata;
3. fixes `SOURCE_DATE_EPOCH` and `PYTHONHASHSEED`;
4. builds each copy without dependency isolation using the explicitly declared setuptools and wheel development dependencies;
5. compares wheel names and complete SHA-256 hashes; and
6. preserves build logs, both wheel files, differing entry content, and ZIP metadata when verification fails.

The CI artifact uploader runs even after a failed gate and includes `build/reproducibility/`, so a failed supply-chain check remains inspectable rather than disappearing with its temporary directory.

## Why it matters

Deterministic package bytes make accidental build drift visible and allow an independently repeated build to be compared directly with a distributed artifact.

## Boundary

A reproducible build does not prove who performed the build, whether the build host was trustworthy, or when the artifact was created. Those properties require signing, trusted timestamps, or external provenance attestation.

The tool intentionally lives outside the runtime package because it invokes the Python build frontend through a subprocess. The replay engine itself retains its no-subprocess boundary.
