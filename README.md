# Digital Fortress Lab

**Digital Fortress Lab** is a self-hosted security lab built on enterprise hardware and operated as a small production-style environment.  
It combines Proxmox virtualization, Dell storage, Cisco ASA and SonicWall firewalls, VLAN segmentation, deep packet inspection, and a Suricata/SELKS SOC node into a single, coherent platform for network and security engineering work.

---

## 1. Purpose and Scope

The lab is designed to behave like a compact enterprise network rather than a casual homelab. It provides a controlled environment to:

- Run virtualized workloads on realistic hardware
- Design and refine network segmentation and firewall policies
- Collect and inspect traffic with IDS/IPS and centralized logging
- Practice backup, recovery, and change management procedures

This repository holds the **documentation, diagrams, and sanitized configuration examples** that describe how the environment is assembled and operated. It does *not* contain live secrets or full device configurations.

---

## 2. Physical Platform

The lab is built into a rack with structured cabling and out-of-band access, so that every device can be serviced without rearranging hardware.

### 2.1 Core Hardware

- **Compute**
  - Dell PowerEdge R710 – primary Proxmox node (dual Xeon, 128 GB RAM)
  - Dell EqualLogic FS7610 (2 nodes) – additional compute/storage services

- **Storage**
  - Avid 18-bay storage chassis populated with mixed SAS/SATA drives, including higher-capacity disks installed by the user
  - EqualLogic FS7610 storage presented to Proxmox and other services

- **Network & Management**
  - Dell X1052P 52-port managed switch – core switching fabric
  - Two 24-port shielded Cat6 patch panels (front and rear) – cable termination and cross-connect
  - OpenGear CM4148 console manager – out-of-band serial access to firewalls, switch, and other devices
  - Rackmount KVM (StarTech) and HP TFT5600 rack console – direct VGA/USB access for local administration

- **Security & Remote Access**
  - Cisco ASA 5510 / 5515-X – primary perimeter firewalls
  - SonicWall SRA 4200 – SSL VPN and remote access gateway

- **Monitoring Node**
  - Panasonic Toughbook CF-30 running NST/SELKS – log sink and Suricata-based SOC dashboard

### 2.2 Rack Philosophy

The rack is wired so that:

- Every device passes through the patch panels into the core switch
- All management ports are reachable via the console manager or KVM
- Power and data cabling are separated for easier maintenance and troubleshooting

---

## 3. Logical Architecture

At a high level, the lab is split into distinct network zones, each mapped to its own VLAN and enforced by firewall policy.

### 3.1 Network Zones (Sanitized Overview)

The exact addressing is intentionally sanitized, but the structure is:

- **Management** – switch, firewalls, console manager, iDRACs, and SOC node
- **Core Services** – Proxmox nodes, storage, and shared infrastructure services
- **DMZ** – externally reachable services for testing exposure and reverse proxying
- **Lab / Workload** – general-purpose VMs, test hosts, and temporary experiments
- **Honeypots** – deliberately exposed services monitored by Suricata/SELKS
- **Guest** – isolated segment for untrusted devices and wireless clients

Inter-VLAN routing is controlled at the firewall layer, not on the core switch. The switch primarily provides Layer-2 segmentation and uplinks to the firewalls and monitoring taps.

### 3.2 Traffic Flow (Conceptual)

Typical flows include:

- **Internet ↔ ASA/SonicWall ↔ DMZ services**  
  Used to test public-facing services and remote access.

- **Lab / Guest ↔ ASA ↔ Internet**  
  Outbound access is restricted and logged, with selected traffic mirrored to Suricata.

- **Honeypots ↔ ASA ↔ Internet**  
  Tight outbound controls, with full visibility into inbound scan/attack traffic.

- **Management ↔ All zones (controlled)**  
  Administrative access is limited to specific management endpoints and protocols.

---

## 4. Security and Monitoring Design

Security controls are layered so that perimeter policy, segmentation, and DPI reinforce one another without unnecessary duplication.

### 4.1 Perimeter and Segmentation

- Cisco ASA provides perimeter firewalling, NAT, and site-to-site/VPN functions.
- SonicWall SRA 4200 terminates remote user VPN sessions.
- VLANs on the core switch implement basic separation of zones; ASA policies define which flows are permitted between them.
- Administrative interfaces are only reachable from the Management zone.

In the initial build, ASA hardware arrived with cleared credentials. Licensing state was recovered from device memory, then the firewalls were re-initialized and integrated into the environment with new policy sets and standardized management access through the console manager.

### 4.2 Deep Packet Inspection and Logging

- The Toughbook CF-30 runs NST/SELKS with Suricata to provide IDS/IPS and traffic analysis.
- Select traffic is mirrored from the switch and from key firewall interfaces into Suricata.
- The design aims to **inspect important flows once**, rather than sending identical copies through multiple tools.

Log sources include:

- Firewalls (connection logs, VPN events, system messages)
- Proxmox and core services
- Honeypot and DMZ hosts
- Network devices where useful (e.g., STP, link state changes)

These are forwarded or ingested into the SOC node for correlation and investigation.

---

## 5. Operations and Procedures

While this repository does not expose live scripts or secrets, it reflects the operational structure used to keep the lab maintainable.

Typical procedures include:

- **Configuration capture and backup**  
  Regular exports of sanitized device configurations and Proxmox backups (with secrets stored offline).

- **Change logging**  
  Noting topology changes, new VLANs, firewall rule adjustments, and service deployments, so the logical design stays aligned with the physical reality.

- **Recovery drills**  
  Testing restoration of virtual machines, recreating firewall rules from documentation, and confirming that central logging and Suricata restart cleanly after maintenance.

Runbooks in the `runbooks/` folder document these processes in more detail, in a form that can be followed by someone other than the original builder.

---

## 6. Repository Layout

As the documentation matures, the repository is organized along these lines:

- **`docs/`** – Markdown documentation
  - Overall overview and design narrative
  - Hardware inventory and rack layout notes
  - Network and security architecture, including VLAN/zone descriptions
  - Service and VM mapping, backup strategy, and roadmap

- **`diagrams/`** – Visual materials
  - Rack front and rear views
  - Logical network diagrams (zones, routing, DPI paths)
  - Any supplemental flowcharts for backup or incident response

- **`infra/`** – Sanitized technical examples
  - Sample firewall policies (ASA and SonicWall) with placeholder addresses
  - Conceptual Ansible or scripting examples for backups and routine tasks
  - Any utility scripts used to interact with the environment

- **`runbooks/`** – Operational procedures
  - Backup and restore workflows
  - Incident response steps for common scenarios
  - Change log capturing major adjustments to the environment

- **`assets/photos/`** – Redacted photos
  - Rack and equipment photos with identifying details avoided or obscured

The intent is that a visitor can move from high-level architecture down to specific examples without needing access to the physical rack.

---

## 7. Sanitization and Ethics

All IP addresses, hostnames, keys, credentials, and VPN details in this repository are **sanitized examples only**. Real secrets and identifying data are stored offline and are never committed to Git.

The lab is strictly for personal education and experimentation. It is isolated from production or customer systems. Any traffic analysis, IDS/IPS tuning, or honeypot activity is carried out within legal and ethical boundaries, and the environment is designed to avoid impacting networks outside the lab.

---
