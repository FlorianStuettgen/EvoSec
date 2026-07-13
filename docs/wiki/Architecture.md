# Architecture

SOC_Replay has two planes:

1. The physical platform: compute, storage, segmentation, sensors, and out-of-band recovery.
2. The evidence plane: normalized stored events, inspectable rules, deterministic detections, expectation verification, and reports.

The planes are connected through sanitized telemetry, not through hidden live-control code.
