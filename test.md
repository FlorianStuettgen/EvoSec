# EvoSec-Lab
<div align="center">
  <img src="/assets/photos/test2.jpeg" alt="Enterprise Rack Configuration" width="90%" style="border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.25);"/>
</div>

<div align="center" style="margin-top: 16px;">
  <img src="https://img.shields.io/badge/Status:-Active-brightgreen?style=for-the-badge&logo=proxmox&logoColor=white" alt="Lab Status"/>
  <img src="https://img.shields.io/badge/Built:-Solo-blue?style=for-the-badge&logo=github&logoColor=white" alt="Built Solo"/>
  <img src="https://img.shields.io/badge/Nerd_Factor:-11/10-pink?style=for-the-badge&logo=dependabot&logoColor=white" alt="Nerd Factor"/>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge&logo=github&logoColor=white" alt="MIT License"/>
  <img src="https://img.shields.io/badge/LinkedIn-Florian_Stuettgen-blue?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
</div>

---

> [!NOTE]  
> Engineered with enterprise-grade precision and fully documented hardware, software, and network operations.

> [!WARNING]  
> All sensitive credentials and network details are obfuscated or excluded to protect operational security.

---

<details open>
<summary><strong>Table of Contents</strong></summary>

1. [Key Highlights](#key-highlights)  
2. [Lab Overview & Platform](#lab-overview--platform)  
    - [Compute & Storage](#compute--storage)  
    - [Network & OOB Management](#network--oob-management)  
    - [Security & SOC Node](#security--soc-node)  
3. [System Architecture & Qubes OS Integration](#system-architecture--qubes-os-integration)  
4. [Logical Architecture & Zones](#logical-architecture--zones)  
5. [Professional Impact](#professional-impact)  
6. [100% Solo Operator](#100-solo-operator)  

</details>

---

## **Key Highlights**
- **Enterprise-Grade Simulation** — Hardware and network topology mirror real production environments with realistic workloads.  
- **Project Controls Workflows** — Formalized processes for planning, monitoring, and documenting IT and network operations.  
- **Security Experimentation** — Deployment of honeypots, tar pits, and network monitoring for safe adversarial testing.  
- **Automation & Orchestration** — LLM + SaltStack dynamically manage VM placement, firewall rules, and honeypot activation.  
- **Isolated Testing Environment** — Fully contained lab for experimentation, mitigating risk to any external or production systems.  
- **Thorough Documentation** — Diagrams, notes, and procedures ensure repeatability, transparency, and operational clarity.

---

## **Lab Overview & Platform**
This section integrates hardware, software, and operational details into a coherent overview, highlighting all major components in the lab environment.

<details open>
<summary><em>Expand for full component list, specifications, and operational status</em></summary>

| Component        | Specification                            | Description                                                                 | Status |
|-----------------|-----------------------------------------|----------------------------------------------------------------------------|--------|
| **Compute Node (R710)**   | Dell R710, dual Xeon, 128GB RAM | Runs **Qubes OS** as the primary experimental hypervisor for multi-domain security isolation (AppVMs for management, honeypots, and guest domains). | 🟦 Secure & Isolated |
| **Primary Storage (EqualLogic + Avid Bay)** | Dual EqualLogic FS7610 + Avid 18-bay chassis | Runs **Proxmox VE** to host storage-centric VMs, containers, and orchestration services. Provides redundant, high-performance iSCSI/NFS storage for all lab workloads. | 🟩 Operational & Stable |
| **Core Switch**  | Dell X1052P — 52-port VLAN trunking | Layer 2 central switch managing VLAN segmentation, PoE, and high-throughput traffic. | 🟩 Active |
| **Perimeter Firewall** | Cisco ASA 5510/5515-X + SonicWall SRA 4200 | Security boundary with adaptive firewalling, VPN, intrusion prevention, and multi-zone segmentation. | 🟩 Hardened & Secure |
| **SOC Node**     | Panasonic Toughbook → SELKS + Suricata | Real-time monitoring, ELK stack integration, IDS/IPS, and DPI analysis. | 🟧 Live DPI Active |
| **Out-of-Band Management** | OpenGear CM4148 + Rack KVM + HP TFT5600 | Remote access, serial console switching, KVM-over-IP for all rack devices. | 🟩 Always Accessible |
| **Patch Panels & Cabling** | Standard 24/48-port panels | Structured cabling for connectivity, redundancy, and isolation. | 🟩 Fully Installed |
| **Lab Workstation** | Desktop PC + monitors | Administrative orchestration and monitoring of the lab environment. | 🟩 Operational |
| **Honeypot Nodes** | Virtualized in Qubes OS AppVMs | Attack surface simulation for IDS/IPS validation. | 🟧 Active |

---

### Compute & Storage
- **Dell R710** runs **Qubes OS** as a VM-centric hypervisor to enforce security domains.  
- **EqualLogic FS7610 + Avid 18-bay chassis** run **Proxmox VE**, hosting storage-heavy VMs, orchestration, and containerized workloads.  
- This separation allows **compute isolation (R710/Qubes)** and **storage orchestration (EqualLogic/Avid/Proxmox)** simultaneously, maximizing security while maintaining high-performance storage and compute capabilities.  

### Network & OOB Management
- Core switch Dell X1052P handles all VLANs and traffic flows.  
- Patch panels and structured cabling maintain clean, redundant connections.  
- Out-of-band access via OpenGear CM4148 and Rack KVM allows management of all devices even during network outages.  

### Security & SOC Node
- Panasonic Toughbook running SELKS + Suricata provides continuous monitoring, intrusion detection, and ELK integration.  
- SaltStack automates VM orchestration, firewall adjustments, and dynamic honeypot activation across Proxmox and Qubes domains.  
- LLM-driven analysis interprets logs, anticipates threats, and reconfigures the network in real-time.

---

## **System Architecture & Qubes OS Integration**
<div align="center">
  <img src="/assets/animations/lab-operations.gif" alt="Lab Operations Animation" width="100%"/>
</div>

- **Proxmox VE** hosts storage-centric workloads on EqualLogic + Avid hardware.  
- **Qubes OS** runs on the R710 as the main experimental and security-focused hypervisor.  
- AppVMs in Qubes separate workloads by trust: management, lab, guest, and honeypot domains.  
- SaltStack orchestrates VMs across Proxmox and Qubes for dynamic deployment, network adjustments, and honeypot activation.  
- LLM-driven analytics read logs, predict attacks, and reconfigure both Proxmox and Qubes VMs in real time.

---

## **Logical Architecture & Zones**
<div align="center">
  <img src="/assets/photos/diagram.svg" alt="System Architecture Diagram" width="100%"/>
</div>

| Zone       | Trust     | Color  | Purpose                              |
|------------|-----------|--------|--------------------------------------|
| Management | Highest   | 🔵 Blue | Administrative consoles & critical assets |
| Core       | High      | 🟢 Green | Proxmox VMs & Qubes R710 workloads   |
| DMZ        | Medium    | 🟡 Yellow| Controlled exposure & service testing |
| Lab        | Medium    | 🟠 Orange| General experimental workloads        |
| Honeypots  | Low       | 🔴 Red   | IDS/IPS bait & attack simulation      |
| Guest      | Lowest    | ⚫ Black | Untrusted devices & code testing      |

---

## **Professional Impact**
| Discipline                | Skills & Experience Demonstrated                                    |
|---------------------------|---------------------------------------------------------------------|
| **Network Engineering**    | VLAN design, ASA object-group mastery, L2/L3 architecture, zone-based routing |
| **Security Engineering**   | Honeypot deployment, Suricata IDS tuning, zero-trust enforcement, tar pits |
| **SRE / Platform Engineering** | Observability, HA, DR planning, reproducibility, full-stack orchestration |
| **DevOps & Automation**    | SaltStack orchestration, config-as-code, Qubes OS AppVM management |
| **Technical Leadership**   | End-to-end ownership, workflow optimization, risk-aware system design |

---

## **100% Solo Operator**
Every component, configuration, and line of Markdown was completed by **one human**:

- Refurbished and integrated all enterprise hardware.  
- Built and configured Proxmox, Qubes OS, ASA, SonicWall, SELKS, and Suricata.  
- Authored all diagrams, documentation, and runbooks.  
- Continuously adding features, expanding lab operations, and integrating automation.

<p align="center">
  <strong>Built with precision.<br>Documented with obsession.<br>Operated with fire.</strong>
  <br><br>
  <img src="https://img.shields.io/badge/Level-Over_9000-ff0066?style=for-the-badge&logo=dependabot"/>
  <br><br>
  <a href="#evosec-lab">Back to Top</a>
</p>
