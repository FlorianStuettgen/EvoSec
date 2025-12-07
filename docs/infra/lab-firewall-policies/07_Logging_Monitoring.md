# 07 Logging, Monitoring & SNMP

## Objective

Establish comprehensive logging, monitoring, and SNMP configuration for ASA and SonicWall firewalls. Ensure visibility into network events, performance, and security incidents.

---

## 1. ASA Logging Configuration

```bash
logging enable
logging buffered informational
logging trap informational
logging host inside 192.168.1.10
logging host inside 192.168.1.15 transport udp port 514
snmp-server enable traps snmp
snmp-server host inside 192.168.1.20 community <COMMUNITY_STRING>
```

**Best Practices:**

* Centralize logs to SIEM or syslog servers.
* Include device hostname, interface, and timestamp in logs.
* Enable logging for critical security events (failures, threats, configuration changes).
* Retain logs based on compliance and operational requirements.
* Configure SNMP read-only for monitoring, avoid write access on production.
* Monitor SNMP traps for threshold alerts and anomalous activity.
* Enable logging on all zones for critical traffic visibility.

---

## 2. SonicWall Logging & SNMP Configuration

```bash
logging enable
logging set level informational
logging host 192.168.1.10
snmp enable
snmp-traps enable
```

**Best Practices:**

* Centralize logs to a syslog server or SIEM.
* Configure SNMP traps for interface, firewall, VPN, and security events.
* Use different log levels for informational, warnings, and critical events.
* Maintain historical logs for auditing and troubleshooting.
* Enable alerts for high-severity events like intrusion detection or VPN failures.

---

## 3. Monitoring Recommendations

* Deploy a Network Monitoring System (NMS) to track device status, performance, and traffic patterns.
* Use dashboards for real-time network health monitoring.
* Implement alerting thresholds for CPU, memory, interface utilization, and traffic anomalies.
* Monitor inter-zone traffic to detect misconfigurations or unauthorized access.
* Integrate logs with SIEM for correlation and incident response.
* Schedule periodic reviews of log data and alerts.

---

## 4. Advanced Monitoring

* Enable NetFlow or equivalent telemetry to capture flow data for deeper analysis.
* Implement automated alerting and remediation for critical events.
* Correlate firewall logs with IPS/IDS, VPN, and endpoint events for comprehensive threat detection.
* Maintain an audit trail for all configuration changes and administrative actions.
* Regularly test monitoring and alerting systems for accuracy and responsiveness.

---

## References

* Cisco ASA 5510/5515-X Logging & SNMP Guides
* SonicWall NSa Series Logging and Monitoring Guide
* NIST SP 800-137 – Information Security Continuous Monitoring (ISCM)
* CIS Firewall Benchmarks – Logging & Monitoring
