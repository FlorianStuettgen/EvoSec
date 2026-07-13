# 07 — Security model

SOC_Replay’s security model combines segmentation, compartmentalized compute, independent recovery, monitored boundaries and controlled change.

## Core controls

### Trust-zone separation

Management, core, DMZ, lab, honeypot and guest functions have different trust levels. VLANs, firewall policy and hypervisor networking enforce those boundaries.

### Compartmentalized compute

Qubes OS separates privileged and experimental domains. Lab workloads should not inherit management access merely because they share physical hardware.

### Dedicated SOC visibility

The SELKS/Suricata node observes network evidence independently from ordinary lab workloads.

### Out-of-band recovery

OpenGear, KVM and the rack console provide access when a firewall, VLAN or hypervisor change disrupts normal connectivity.

### Change control

The restored policy library includes a change-control baseline. Network and security changes should preserve request, risk, approval, implementation, validation and rollback records.

## Public repository controls

- No credentials, keys, session material or real recovery secrets.
- No unsanitized public IPs or sensitive management addresses.
- Placeholder values remain obvious.
- Component serial numbers and private inventory remain outside the public repository.
- Replay scenarios use synthetic or deliberately sanitized events.

## Automation boundary

Automated response is not a universal platform claim. A live adapter must be bounded, auditable and recoverable. The Python replay core enforces `response.mode = "simulated"` and cannot change network or identity state.

## Firewall policy references

The policy library covers:

- hostname/domain and management access;
- interface segmentation;
- NAT;
- granular ACLs;
- VPN baselines;
- IDS/IPS integration;
- logging and SNMP;
- hardening; and
- change control.

These files are lab references. Device firmware, interface names and supported cryptography must be verified against the actual appliance before use.

## Non-claims

SOC_Replay is not a production security certification, a commercial SOC, or proof that every historical automation statement is presently operational. [Implementation State](14-Implementation-State.md) is authoritative.
