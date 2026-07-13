# Experiments

The repository includes four deterministic controls:

- network scan — one high detection;
- privileged group change — one critical detection;
- failed authentication burst — two non-overlapping medium detections; and
- approved privileged maintenance — zero detections.

The zero-detection scenario is intentional. It demonstrates that the same rule contract distinguishes authorized, ticketed activity from the positive control.

Physical-lab experiments should use the measured record template under `templates/experiment-record.md` and publish limitations alongside results.
