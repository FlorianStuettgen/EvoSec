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
> Engineered with **production-level standards**, fully documented, and executed on authentic enterprise-grade hardware.

> [!WARNING]  
> All sensitive information, credentials, or production network data are **obfuscated or excluded**. This lab is fully sanitized.

---

## **Table of Contents**
1. [Key Highlights](#key-highlights)  
2. [At a Glance (Dec 2025)](#at-a-glance-december-2025)  
3. [Physical Platform](#physical-platform)  
    - [Compute & Storage](#compute--storage)  
    - [Network & OOB Management](#network--oob-management)  
    - [Security & SOC Node](#security--soc-node)  
4. [System Architecture & Qubes OS Integration](#system-architecture--qubes-os-integration)  
5. [Logical Architecture & Zones](#logical-architecture--zones)  
6. [Professional Impact](#professional-impact)  
7. [100% Solo Operator](#100-solo-operator)  

---

## **Key Highlights**
- **Enterprise-Grade Simulation**  
  Realistic network environments with racks, switches, firewalls, and segmented topologies mirroring production infrastructure.

- **Project Controls Workflows**  
  Structured processes for planning, monitoring, and managing complex IT, networking, and change-controlled operations.

- **Security Experimentation**  
  Controlled deployment of honeypots, tar pits, and monitoring systems for safe adversarial research.

- **Automation & Orchestration**  
  LLM-assisted SaltStack workflows dynamically manage VM topology, deploy states, and ensure operational consistency.

- **Isolated Testing Environment**  
  Fully contained lab environment for risk-free experimentation without touching live systems.

- **Thorough Documentation**  
  Diagrams, notes, and reproducible procedures ensure clarity, repeatability, and transparency.

---

## **At a Glance (December 2025)**
<details open>
<summary><em>Component summary, specifications, and operational status</em></summary>

| Component       | Specification                            | Description                                                                 | Status |
|-----------------|-----------------------------------------|----------------------------------------------------------------------------|--------|
| **Hypervisor**      | Proxmox VE on Dell R710 — 128 GB RAM | Core virtualization platform supporting clustered VM deployments. | 🟩 **Operational** |
| **Compute Node (Qubes OS)** | Qubes OS VMs on R710, isolated per domain | Each VM represents isolated workloads: management, lab, honeypot, guest. Provides an additional layer of security beyond Proxmox. | 🟦 **Secure & Isolated** |
| **Storage**         | EqualLogic FS7610 + Avid 18-bay NAS  | Redundant, high-performance iSCSI/NFS storage backbone. | 🟦 **Fully Redundant** |
| **Core Switch**     | Dell X1052P — 52-port VLAN trunking  | Central L2 switching plane for all segments and management networks. | 🟩 **Active** |
| **Perimeter**       | Cisco ASA 5510/5515-X + SonicWall SRA | Boundary firewalls and VPN endpoints enforcing strict zone policies. | 🟩 **Hardened** |
| **SOC Node**        | Panasonic Toughbook running SELKS     | Dedicated IDS/IPS telemetry node with Suricata and ELK stack. | 🟧 **Live DPI** |
| **Network Model**   | Multi-zone, ASA-only L3 routing       | Zero-trust segmentation with strict L3 enforcement. | 🟩 **Zero Trust** |
| **OOB Management**  | OpenGear CM4148 + Rack KVM + HP TFT5600 | Out-of-band remote access for emergency maintenance. | 🟩 **Always Accessible** |

</details>

---

## **Physical Platform**
The EvoSec-Lab is divided into three primary domains: **Compute & Storage**, **Network & OOB Management**, and **Security & SOC Node**.  
Each domain mirrors enterprise operations while remaining fully isolated for experimentation.

### Compute & Storage
<details>
<summary>Click to expand</summary>

<img src="/assets/photos/Compute1.jpg" alt="R710" loading="lazy" width="100%"/>
<img src="/assets/photos/Compute2.png" alt="EqualLogic" loading="lazy" width="100%"/>
<img src="/assets/photos/Storage1.png" alt="Avid" loading="lazy" width="100%"/>

**Compute:**  
- Dell R710 servers with dual Xeon CPUs and 128GB RAM.  
- Hosts **Proxmox VE** and **Qubes OS VMs**, isolating critical services and providing security-by-design domains.  
- Each Qubes VM represents a secure environment: management, lab workloads, honeypots, and guest access.  
- High-availability design ensures fault-tolerant workloads.

**Storage:**  
- Dual EqualLogic FS7610 arrays with 18-bay Avid chassis.  
- Redundant, high-speed NAS storage for all VMs, logs, and datasets.  
- Supports iSCSI and NFS for seamless integration with Proxmox and Qubes OS environments.

</details>

### Network & OOB Management
<details>
<summary>Click to expand</summary>

<img src="/assets/photos/switch.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/patch.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/console3.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/console1.jpg" loading="lazy" width="100%"/>

**Network Core:**  
- Dell X1052P switches provide VLAN segmentation and high-throughput L2 switching.  
- Supports lab, DMZ, management, honeypot, and guest networks.  
- PoE for edge devices, IP cameras, and VoIP.

**OOB Management:**  
- OpenGear CM4148 combined with Rack KVM and HP TFT5600 ensures remote console access.  
- Guarantees full recovery and administration even during network failures.

</details>

### Security & SOC Node
<details>
<summary>Click to expand</summary>

<img src="/assets/photos/sec1.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/sec3.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/sec2.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/monitor1.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/monitor2.jpg" loading="lazy" width="100%"/>

**SOC Node:**  
- Panasonic Toughbook running SELKS/NST with Suricata for IDS/IPS.  
- ELK stack ingests logs from Proxmox, Qubes OS, honeypots, and network devices.  
- Provides real-time visibility and dynamic defensive responses.

**Honeypots & Tar Pits:**  
- Strategically deployed in lab and DMZ zones to attract and slow attackers.  
- SaltStack automation triggers adaptive network changes in response to threat events.  
- LLM analytics monitor, predict, and orchestrate VM network changes dynamically.

</details>

---

## **System Architecture & Qubes OS Integration**
<div align="center">
  <img src="/assets/animations/lab-operations.gif" alt="Lab Operations Animation" width="100%"/>
  <p><i>Animated representation of compute, storage, and network orchestration. Qubes OS VMs are isolated domains managing workloads securely, while SaltStack automates dynamic VM movements and network changes in response to threat signals.</i></p>
</div>

**How it works:**  
- Proxmox VE manages the hypervisor layer and VM lifecycles.  
- Qubes OS VMs provide **secure isolation**, each representing a specific trust domain.  
- SaltStack automation dynamically deploys configurations, moves VMs, and triggers honeypot traps.  
- IDS alerts from Suricata feed into LLM-based analytics, which orchestrates proactive network adjustments.  
- Honeypots and tar pits provide real-world adversarial testing without impacting critical workloads.

---

## **Logical Architecture & Zones**
The lab enforces a **zero-trust, segmented model**, with zones categorized by trust, purpose, and visual identifiers:

| Zone       | Trust     | Color  | Purpose                              |
|------------|-----------|--------|--------------------------------------|
| Management | Highest   | 🔵 Blue | Crown jewels & consoles              |
| Core       | High      | 🟢 Green | Proxmox + Qubes OS workloads         |
| DMZ        | Medium    | 🟡 Yellow| Controlled exposure                  |
| Lab        | Medium    | 🟠 Orange| General workloads                    |
| Honeypots  | Low       | 🔴 Red   | Attack surface bait                  |
| Guest      | Lowest    | ⚫ Black | Untrusted devices                     |

---

## **Professional Impact**
| Discipline                | Real-World Skills Demonstrated                                      |
|---------------------------|---------------------------------------------------------------------|
| Network Engineering       | Zone-based firewall design, ASA object-group mastery, VLAN planning |
| Security Engineering      | Suricata tuning, honeypot deployment, attack traffic analysis       |
| SRE / Platform Engineering| Observability, reproducibility, runbook discipline                 |
| DevOps & Automation       | SaltStack playbooks, Qubes OS integration, config-as-code           |
| Technical Leadership      | End-to-end ownership, systems thinking, risk-aware architecture     |

---

## **100% Solo Operator**
Every cable pulled, ACL written, diagram drawn, and line of Markdown — **one human**.

- Sourced & refurbished all enterprise hardware  
- Designed every security zone & policy from scratch  
- Stood up Proxmox, Qubes OS, ASA, SonicWall, Suricata, SELKS  
- Authored full documentation & runbooks  
- Continually iterating features at 2 a.m. for fun  

<p align="center">
  <strong>Built with precision.<br>Documented with obsession.<br>Operated with fire.</strong>
  <br><br>
  <img src="https://img.shields.io/badge/Level-Over_9000-ff0066?style=for-the-badge&logo=dependabot"/>
  <br><br>
  <a href="#evosec-lab">Back to Top</a>
</p>
