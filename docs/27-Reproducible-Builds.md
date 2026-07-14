# 27 — Reproducible Builds

## Goal

A source tree should produce the same wheel bytes when built twice with the same toolchain and deterministic build inputs.

## Verification process

`tools/verify_reproducible_wheel.py`:

1. creates two isolated output directories;
2. fixes `SOURCE_DATE_EPOCH` and `PYTHONHASHSEED`;
3. builds the wheel twice without dependency isolation;
4. compares wheel names and SHA-256 hashes; and
5. reports differing archive entries when bytes diverge.

## Why it matters

Deterministic package bytes make accidental build drift visible and allow an independently repeated build to be compared directly with a distributed artifact.

## Boundary

A reproducible build does not prove who performed the build, whether the build host was trustworthy, or when the artifact was created. Those properties require signing, trusted timestamps, or external provenance attestation.

The tool intentionally lives outside the runtime package because it invokes the Python build frontend through a subprocess. The replay engine itself retains its no-subprocess boundary.
