# Release evidence

A release is a reproducible evidence boundary, not only a version-number change.

## Required release inputs

- clean commit on protected `main`;
- version and changelog update;
- supported Python matrix result;
- passing Ruff, mypy, compilation, and coverage gates;
- passing schema, scenario, adapter, and repository invariant checks;
- verified committed reference bundle;
- verified deterministic bundle regeneration;
- verified indexed and full-scan equivalence;
- reproducible wheel result;
- CodeQL result;
- controlled benchmark comparison against the previous release.

## Release artifacts

Retain or publish:

- source archive;
- wheel;
- checksums for distributed artifacts;
- reference evidence bundle;
- machine-readable benchmark output;
- test and coverage summary;
- supported schema and adapter versions;
- known limitations and defensive-use boundary.

An SBOM and artifact attestation should be added when the release publication workflow is automated. Until then, do not claim provenance stronger than the retained checksums and Git history support.

## Verification record

The release notes should identify:

- tag and commit SHA;
- Python versions tested;
- reference scenario and evidence schema identifiers;
- whether wheel bytes reproduced under the controlled build job;
- benchmark command and runner boundary;
- security-scan result;
- compatibility changes;
- unresolved limitations.

## Prohibited release claims

Do not describe a release as proof of:

- production telemetry origin;
- external chain of custody;
- trusted time;
- hardware identity;
- live response safety;
- universal throughput or detection efficacy.

Those properties require controls outside this repository.