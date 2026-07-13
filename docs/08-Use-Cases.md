# 08 — Use cases

SOC_Replay supports controlled defensive research across the physical platform and the repository’s evidence utility.

## Physical platform use cases

### Segmentation validation

Confirm that management, core, lab, DMZ, guest and honeypot paths match the intended trust model. Record allowed and denied flows without exposing sensitive configuration publicly.

### Honeypot and tar-pit observation

Operate decoy services in isolated zones, collect defensive telemetry and study how detection rules behave. Decoys remain separated from management and critical infrastructure.

### IDS/IPS evaluation

Use the SELKS/Suricata node to examine alert quality, event context and sensor coverage for authorized lab traffic.

### Firewall-policy and change-control exercises

Review sanitized ASA/SonicWall policy baselines, model proposed changes, capture pre/post state and validate rollback through the OOB path.

### Recovery drills

Test console access, snapshot restoration and known-good configuration recovery without relying on the normal data path.

### Training and demonstration

Explain enterprise hardware, network segmentation, SOC workflows, evidence quality and controlled automation through a tangible system.

### IoT and temporary-device isolation

Place authorized test devices in restricted zones with explicit monitoring and no implicit access to management or core services.

## Evidence replay use cases

The included replay scenarios demonstrate:

- a synthetic multi-port scan correlation; and
- a synthetic privileged-group change match.

Future scenarios can cover telemetry gaps, authentication anomalies, administrative changes, service-account use, failed validation and configuration drift—using synthetic or sanitized data and simulated responses.

## Experiment definition of done

A featured experiment should publish:

1. objective and authorization boundary;
2. relevant topology and initial state;
3. triggering event or controlled input;
4. sensor and detection evidence;
5. analyst or automation decision;
6. applied or simulated response;
7. post-response validation;
8. recovery/rollback result; and
9. limitations and next test.
