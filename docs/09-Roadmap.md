# 09 — Roadmap

The roadmap protects the project’s original platform identity while improving evidence quality.

## Restored and completed

- Physical rack and component photography restored
- Original architecture diagrams restored
- Firewall policy, playbook and script-reference library restored
- Full hardware, software and topology documentation rebuilt
- Implementation-state register added
- Deterministic replay utility retained with tests and CI
- Two synthetic reference scenarios retained

## Near-term platform work

1. Reconcile the public inventory with the current physical rack.
2. Add sanitized firmware/version and interface-role records.
3. Publish a current rack-elevation diagram.
4. Capture sanitized switch/firewall VLAN evidence.
5. Publish one measured end-to-end Suricata experiment.
6. Record OOB recovery and rollback evidence.
7. Align or retire stale wiki language in favour of file-based docs.

## Automation validation track

1. Define SaltStack states or equivalent configuration contracts.
2. Add read-only discovery before any write adapter.
3. Implement dry-run rendering and target allow-lists.
4. Record human approval and audit events.
5. Validate one bounded change in a disposable lab segment.
6. Measure detection, decision, execution and verification separately.
7. Prove rollback through OOB access.

## Evidence tooling track

- Golden-file tests for replay reports
- Optional schema validation
- Read-only import adapters for sanitized exports
- Signed report manifests
- Replay scale and timing benchmarks
- Scenario coverage summaries

## Longer-term ideas

- Additional decoy and IoT experiment templates
- Reusable environment snapshots
- Expanded telemetry enrichment
- Multi-site or hybrid-lab federation
- Predictive maintenance only after sufficient platform telemetry exists

Roadmap items must remain future tense until evidence is published.
