# EvoSec-Lab

<div align="left">
  <img src="/assets/photos/test2.jpeg" alt="Enterprise Rack Configuration" width="65%" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>
</div>

<div align="left" style="margin-top: 16px;">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat&logo=proxmox&logoColor=white" alt="Lab Status: Active"/>
  <img src="https://img.shields.io/badge/Built-Solo-1182c3?style=flat&logo=github&logoColor=white" alt="Built Solo"/>
  <img src="https://img.shields.io/badge/Documentation-Comprehensive-ff8800?style=flat&logo=markdown&logoColor=white" alt="Comprehensive Documentation"/>
  <img src="https://img.shields.io/badge/Nerd_Factor-11/10-ff0066?style=flat&logo=dependabot&logoColor=white" alt="Nerd Factor"/>
</div>

## What is this? 

This is **EvoSec-Lab**, an isolated environment for the design & testing of network topologies, security measures, and Project Controls.
I made this to showcase how complex infrastructure, automated workflows, and robust monitoring can be orchestrated to deliver secure, controlled, and reproducible outcomes.

> [!NOTE]  
> Engineered with production-level standards and documentation on authentic enterprise-grade hardware.

> [!WARNING]
> Operated in complete isolation from production environments to enable risk-free experimentation with realistic scenarios.


## At a Glance — Current as of December 2025

<div align="center" style="margin-bottom: 24px; font-style: italic; color: #555; font-size: 0.9em;">
  Expanded overview of lab components, including detailed specifications, roles, and operational status for a comprehensive snapshot.
</div>


<table style="width: 100%; max-width: 1200px; margin: 0 auto; border-collapse: separate; border-spacing: 0 12px; font-family: Arial, sans-serif;">
  <thead>
    <tr style="background-color: #f0f4f8; color: #333;">
      <th style="padding: 12px 16px; text-align: left; border-radius: 6px 0 0 6px; font-weight: 600;">Component</th>
      <th style="padding: 12px 16px; text-align: left; font-weight: 600;">Specification</th>
      <th style="padding: 12px 16px; text-align: left; font-weight: 600;">Description</th>
      <th style="padding: 12px 16px; text-align: left; border-radius: 0 6px 6px 0; font-weight: 600;">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <td style="padding: 12px 16px; border-radius: 6px 0 0 6px;">Hypervisor</td>
      <td style="padding: 12px 16px;">Proxmox VE on Dell R710 (128 GB RAM, dual Xeon)</td>
      <td style="padding: 12px 16px;">Serves as the foundational virtualization platform, enabling efficient VM and container management with high resource utilization and failover capabilities.</td>
      <td style="padding: 12px 16px; border-radius: 0 6px 6px 0;">
        <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">Operational and Stable</span>
      </td>
    </tr>
    <tr style="background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <td style="padding: 12px 16px; border-radius: 6px 0 0 6px;">Storage</td>
      <td style="padding: 12px 16px;">Dual EqualLogic FS7610 + Avid 18-bay chassis</td>
      <td style="padding: 12px 16px;">Provides scalable, high-performance NAS storage with RAID redundancy, supporting iSCSI and NFS protocols for seamless data access across the lab.</td>
      <td style="padding: 12px 16px; border-radius: 0 6px 6px 0;">
        <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">Fully Redundant</span>
      </td>
    </tr>
    <tr style="background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <td style="padding: 12px 16px; border-radius: 6px 0 0 6px;">Core Switch</td>
      <td style="padding: 12px 16px;">Dell X1052P — 52-port, full VLAN trunking</td>
      <td style="padding: 12px 16px;">Acts as the central Layer 2 switch, handling VLAN segmentation, PoE for devices, and high-throughput traffic management in the lab's network core.</td>
      <td style="padding: 12px 16px; border-radius: 0 6px 6px 0;">
        <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">L2 Master Operational</span>
      </td>
    </tr>
    <tr style="background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <td style="padding: 12px 16px; border-radius: 6px 0 0 6px;">Perimeter</td>
      <td style="padding: 12px 16px;">Cisco ASA 5510/5515-X + SonicWall SRA 4200</td>
      <td style="padding: 12px 16px;">Forms the security boundary with adaptive firewalling, VPN support, and intrusion prevention, ensuring controlled access and threat mitigation.</td>
      <td style="padding: 12px 16px; border-radius: 0 6px 6px 0;">
        <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">Hardened and Secure</span>
      </td>
    </tr>
    <tr style="background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <td style="padding: 12px 16px; border-radius: 6px 0 0 6px;">SOC Node</td>
      <td style="padding: 12px 16px;">Panasonic Toughbook → NST/SELKS + Suricata</td>
      <td style="padding: 12px 16px;">Dedicated security operations center node for real-time monitoring, ELK stack integration, and IDS/IPS via Suricata for deep packet analysis.</td>
      <td style="padding: 12px 16px; border-radius: 0 6px 6px 0;">
        <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">Live DPI Active</span>
      </td>
    </tr>
    <tr style="background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <td style="padding: 12px 16px; border-radius: 6px 0 0 6px;">Network Model</td>
      <td style="padding: 12px 16px;">Multi-zone, ASA-only L3 routing</td>
      <td style="padding: 12px 16px;">Implements a segmented, zero-trust architecture with Layer 3 routing confined to ASA devices, promoting least-privilege access and isolation.</td>
      <td style="padding: 12px 16px; border-radius: 0 6px 6px 0;">
        <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">Zero Trust Enforced</span>
      </td>
    </tr>
    <tr style="background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <td style="padding: 12px 16px; border-radius: 6px 0 0 6px;">OOB Management</td>
      <td style="padding: 12px 16px;">OpenGear CM4148 + rack KVM + HP TFT5600</td>
      <td style="padding: 12px 16px;">Out-of-band management console for remote access, serial console switching, and KVM-over-IP, ensuring accessibility during network outages.</td>
      <td style="padding: 12px 16px; border-radius: 0 6px 6px 0;">
        <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">Always Accessible</span>
      </td>
    </tr>
  </tbody>
</table>

<div align="center" style="margin-top: 32px;">
  <strong>Lab Maturity</strong><br>
  <progress value="94" max="100" style="width: 300px; height: 20px; border-radius: 4px; background-color: #e0e0e0; color: #4caf50;"></progress> <span style="font-weight: bold; margin-left: 8px;">94%</span>
</div>


<div align="center" style="margin-bottom: 24px; font-style: italic; color: #555; font-size: 0.9em;">
With full operational maturity, the lab now operates as a dynamic, self-regulating security environment. Application VMs run critical services on isolated VLANs, while honeypots and tar pits detect and slow threats. SaltStack orchestrates real-time network adjustments, moving VMs and activating traps as needed, while LLM-driven analytics process logs to anticipate attacks and adjust topology.
</div>


<div align="center">
  <h2>🚀 Digital Infrastructure Lab</h2>
  <img src="https://github.com/FlorianStuettgen/digital-infrastructure-lab/blob/main/assets/photos/diagram.svg" alt="System Diagram" width="1000"/>
  <p><i>Full system architecture showing compute, storage, and network topology</i></p>
</div>






























































































## Table of Contents

<details open>
<summary><strong>Click sections to collapse/expand</strong></summary>

- [Purpose & Philosophy](#purpose--philosophy)
- [Physical Platform Gallery](#physical-platform-gallery)
- [Logical Architecture & Zones](#logical-architecture--zones)
- [Mermaid Traffic Flow Masterpiece](#mermaid-traffic-flow)
- [Security & Observability Stack](#security--observability)
- [Repository Structure](#repository-structure)
- [Professional Impact](#professional-impact)
- [Operations Discipline](#operations-discipline)
- [100% Solo Operator](#solo-operator)
- [Sanitization & Safety](#sanitization--safety)

</details>

## Purpose & Philosophy

This lab exists to **break things safely, document everything, and level-up**.

- Model real enterprise networks at 1/1000th the cost  
- Prototype firewall policies that survive red-team scrutiny  
- Feed honeypots to the internet and reverse-engineer attacks  
- Practice change management as if auditors were watching  
- Build observability that actually works  

~~A rack of old gear~~ → **A living, breathing portfolio masterpiece**

**Key Definitions**  
**Lab** :: Controlled environment for high-signal R&D  
**Operator** :: One human, infinite coffee  
**End State** :: Reproducible from this repo in <48 hours

## Physical Platform — Rack Porn Gallery

<details open>
<summary><strong>Compute & Storage</strong> — Click to collapse</summary>
<br>
<img src="/assets/photos/Compute1.jpg" alt="R710" loading="lazy" width="100%"/>
<img src="/assets/photos/Compute2.png" alt="EqualLogic" loading="lazy" width="100%"/>
<img src="/assets/photos/Storage1.png" alt="Avid" loading="lazy" width="100%"/>
</details>

<details>
<summary><strong>Network & OOB Management</strong></summary>
<br>
<img src="/assets/photos/switch.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/patch.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/console3.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/console1.jpg" loading="lazy" width="100%"/>
</details>

<details>
<summary><strong>Security & SOC Node</strong></summary>
<br>
<img src="/assets/photos/sec1.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/sec3.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/sec2.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/monitor1.jpg" loading="lazy" width="100%"/>
<img src="/assets/photos/monitor2.jpg" loading="lazy" width="100%"/>
</details>

## Logical Architecture & Zones

| Zone       | Trust     | Color | Purpose                              |
|------------|-----------|-------|--------------------------------------|
| Management | Highest   | Blue  | Crown jewels & consoles              |
| Core       | High      | Green | Proxmox + storage                    |
| DMZ        | Medium    | Yellow| Controlled exposure                  |
| Lab        | Medium    | Orange| General workloads                    |
| Honeypots  | Low       | Red   | Attack surface bait                  |
| Guest      | Lowest    | Black | Untrusted devices                    |

### Traffic Flow — Mermaid Masterpiece

```mermaid
graph TD
    subgraph "Internet"
        EXT[Internet<br>Scans • Bots • Script Kiddies] 
    end
    subgraph "Perimeter"
        ASA[ASA Outside<br>Cisco Firepower]
        SRA[SonicWall SRA<br>VPN Gateway]
    end
    subgraph "Trusted"
        MGMT[Management Zone]
        CORE[Core Zone]
        DMZ[DMZ Zone]
        LAB[Lab Zone]
        HONEY[Honeypots]
        GUEST[Guest Zone]
    end
    subgraph "Observability"
        SOC[SOC Node<br>Suricata + SELKS]
    end

    EXT -->|Controlled| ASA
    ASA --> DMZ & CORE & LAB & GUEST
    ASA --> SRA --> MGMT
    HONEY --> ASA
    SOC -.->|SPAN + Syslog| ASA & DMZ & HONEY

    classDef danger fill:#ff5555,stroke:#c00,color:white
    classDef secure fill:#55ff55,stroke:#080,color:black
    classDef neutral fill:#5555ff,stroke:#00c,color:white
    class EXT,HONEY danger
    class MGMT,CORE secure
    class DMZ,LAB,GUEST,SRA neutral
    class SOC fill:#ffff55,stroke:#aa0,color:black

## Repository Structure

```bash
digital-infrastructure-lab/
├── docs/                  # Architecture deep-dives & runbooks
├── diagrams/              # Mermaid + exported Visio diagrams
├── infra/                 # Sanitized ASA configs + Ansible samples
├── runbooks/              # Change log, procedures, rollback plans
└── assets/
    └── photos/            # The rack beauty you’re enjoying right now
Recommended starting point → docs/00_overview.md


### Block 9 – Professional Impact (Portfolio Gold)

```markdown
## Professional Impact — This Is Portfolio Gold

| Discipline                | Real-World Skills Demonstrated                                      |
|---------------------------|---------------------------------------------------------------------|
| Network Engineering       | Zone-based firewall design, ASA object-group mastery, VLAN architecture |
| Security Engineering      | Suricata IDS tuning, honeypot deployment, attack traffic analysis   |
| SRE / Platform Engineering| Full-stack observability, reproducibility, runbook discipline       |
| DevOps & Automation       | Ansible playbooks, config-as-code, documentation-as-code            |
| Technical Leadership      | End-to-end ownership, systems thinking, risk-aware design          |

> This single repository has replaced entire “homelab” sections on résumés.  
> Recruiters and senior engineers stop scrolling when they land here.

## 100% Solo Operator

Every cable pulled, every ACL written, every diagram drawn, every line of Markdown — **one human**.

- Sourced and refurbished all enterprise hardware  
- Designed every security zone and policy from scratch  
- Stood up Proxmox, ASA, SonicWall, Suricata, SELKS  
- Authored the entire documentation suite and runbooks  
- Still adding features at 2 a.m. because it’s fun

<p align="center">
  <strong>Built with precision.<br>Documented with obsession.<br>Operated with fire.</strong>
  <br><br>
  <img src="https://img.shields.io/badge/Level-Over_9000-ff0066?style=for-the-badge&logo=dependabot" alt="Over 9000"/>
  <br><br>
  <a href="#digital-infrastructure-lab">Back to Top</a>
</p>




















