# Digital Fortress Lab

**Digital Fortress Lab** is a self-hosted security and infrastructure lab built on enterprise hardware and operated like a small production network. It combines:

- Proxmox virtualization
- Dell server and storage platforms
- Cisco ASA and SonicWall security appliances
- VLAN-based segmentation on a managed switch
- Centralized logging and IDS/IPS with NST/SELKS and Suricata

The lab is isolated from production networks and is used to design, test, and operate realistic network and security topologies.

---

## 🧭 Purpose

The lab is intended to:

- Model a compact enterprise-style network end to end  
- Provide a controlled environment for firewall policy, VPN, and segmentation work  
- Capture logs and packet data for analysis and IDS/IPS tuning  
- Practice routine operations such as backup, restore, and change management  

This repository documents the physical layout, logical design, security model, and operational approach.

---

## 🧱 Physical Platform

The environment is built into a rack with structured cabling, patch panels, and out-of-band access.

### Core Hardware

- **Compute**
  - Dell PowerEdge R710 – primary Proxmox host (dual Xeon, 128 GB RAM)
  - Dell EqualLogic FS7610 (2 nodes) – additional compute and storage services

- **Storage**
  - Avid 18-bay chassis with mixed SAS/SATA disks
  - EqualLogic-backed storage presented to Proxmox and other services

- **Network & Management**
  - Dell X1052P 52-port managed switch – core switching and VLAN hub
  - Dual shielded Cat6 patch panels (front + rear) – cable termination and cross-connect
  - OpenGear CM4148 console manager – centralized serial access for network and security devices
  - Rackmount KVM and HP TFT5600 rack console – local VGA/keyboard access

- **Security & Remote Access**
  - Cisco ASA 5510 / 5515-X – perimeter firewalls and zone routing
  - SonicWall SRA 4200 – SSL VPN and remote access gateway

- **Monitoring Node**
  - Panasonic Toughbook CF-30 – runs NST/SELKS and Suricata as a small SOC node

All devices are cabled through the patch panels into the core switch. Management access is available over a dedicated management VLAN, via serial on the console manager, or locally through the KVM.

---

## 🌐 Logical Architecture

The network is segmented into distinct zones. Each zone maps to one or more VLANs and to specific firewall policies.

### Zones (Sanitized)

| Zone        | Role                                              |
|------------|---------------------------------------------------|
| Management | Switch, firewalls, console, iDRAC, SOC node       |
| Core       | Proxmox host(s), storage, shared infrastructure   |
| DMZ        | Externally reachable lab services                 |
| Lab        | General-purpose workloads and test VMs            |
| Honeypots  | Intentionally exposed services for observation    |
| Guest      | Untrusted devices and temporary clients           |

The Dell X1052P switch provides Layer 2 separation for each VLAN.  
Inter-VLAN routing and filtering are performed on the ASA, not on the switch.

### Traffic Flows (Conceptual)

- **Internet ↔ ASA ↔ DMZ**  
  Public-facing lab services and controlled exposure tests.

- **Internet ↔ ASA/SRA ↔ Management**  
  Remote administration over VPN.

- **Lab / Guest ↔ ASA ↔ Internet**  
  Outbound access under restricted policies and logging.

- **Honeypots ↔ ASA ↔ Internet**  
  Inbound scans and attacks are allowed in a controlled way; outbound traffic is tightly limited.

- **Management ↔ Other Zones**  
  Administrative access to infrastructure from specific management hosts and protocols only.

Exact IP addressing and VLAN IDs are described in sanitized form in `docs/02-network-architecture.md`.

---

## 🔒 Security & Monitoring

Security and observability are part of the base design.

### Perimeter & Segmentation

- Cisco ASA appliances:
  - Define interface roles (outside, management, core, DMZ, lab, honeypots, guest)
  - Apply NAT for public exposure and outbound access
  - Enforce ACLs describing which zones can communicate and on which ports

- SonicWall SRA 4200:
  - Terminates remote VPN sessions
  - Restricts VPN users to selected management and lab subnets

Administrative interfaces for core infrastructure devices are reachable only from the management zone.

### Logging, DPI, and SOC Node

The Toughbook CF-30 (NST/SELKS) acts as a SOC node:

- Receives:
  - Syslog from firewalls and selected hosts
  - Logs from core services
  - Mirrored traffic from chosen switch ports and/or ASA interfaces

- Runs:
  - Suricata for deep packet inspection, alerting, and traffic analysis

Monitoring design focuses on a small number of well-chosen mirror points (for example DMZ ↔ Internet and honeypots ↔ Internet) rather than attempting to capture all traffic.

Additional details are documented in `docs/03-security-architecture.md`.

---

## 📁 Repository Layout

The repository reflects the structure of the lab and its documentation.

```text
digital-fortress-lab/
├── README.md
├── docs/
│   ├── 00_overview.md
│   ├── 01_hardware-inventory.md
│   ├── 02-network-architecture.md
│   ├── 03-security-architecture.md
│   ├── 04-services-and-vms.md
│   ├── 05-operations-and-maintenance.md
│   └── 06-future-roadmap.md
├── diagrams/
│   └── logical-network-diagram.png
├── infra/
│   ├── example-firewall-policies/
│   │   └── asa-lab-base-policy.txt
│   ├── sample-ansible-playbooks/
│   └── scripts/
├── runbooks/
│   └── change-log.md
└── assets/
    └── photos/
```

### Directory Overview

- **`docs/`** – Narrative documentation:
  - Overview, hardware inventory, network and security architecture, services, operations, and roadmap.
- **`diagrams/`** – Visual diagrams:
  - Logical network diagram; rack and service diagrams can be added over time.
- **`infra/`** – Technical examples:
  - Sanitized ASA base policy and placeholders for automation and scripts.
- **`runbooks/`** – Operational notes:
  - Change history and, in future, backup/restore and incident response steps.
- **`assets/`** – Visual assets:
  - Redacted photos and related imagery, if needed.

---

## ⚙️ Operations

The lab is operated with the expectation that it may need to be rebuilt or modified over time:

- Device configurations and Proxmox VM backups are taken regularly (stored outside this repository).
- Topology and policy changes are reflected in `docs/` and summarized in `runbooks/change-log.md`.
- New services or exposure scenarios are introduced with corresponding documentation so the logical design stays aligned with the actual implementation.

---

## 🧼 Sanitization & Scope

All content in this repository is intentionally sanitized:

- IP ranges, hostnames, and object names are examples, not live values.
- No keys, credentials, or VPN profiles are committed.
- Hardware identifiers such as serial numbers and MAC addresses are omitted.

The lab is isolated from production or customer systems. Honeypot and exposure testing is confined to this environment and configured to avoid unintended impact on external networks.

---
