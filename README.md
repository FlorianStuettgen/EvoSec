
<img width="452" height="170" alt="M" src="https://github.com/user-attachments/assets/c35d9192-3736-40ba-9d59-d2660507c0c2" />
 
---

##  Welcome to EvoSec

</div>

EvoSec is a cybersecurity research lab built for experimentation and operational analysis. This exciting new platform brings together honeypots, intrusion detection, automation, and monitoring into a unified environment, enabling practical testing and innovation. 

Visit the wiki for a detailed overview of EvoSec’s architecture, components, and experiments:
[EvoSec-Lab Wiki](https://github.com/FlorianStuettgen/EvoSec/wiki).

---

<div align="center">

##  Key Features: 

| Feature | Description |
|:------:|:-----------|
| **Enterprise-Grade** | High-performance servers, storage, and networking for advanced research. |
| **Zones** | VLANs create isolated spaces for honeypots, tar pits, DMZs, and management networks. |
| **AI-Driven** | Models orchestrate network, security for rapid responses. |
| **Automated** | Pipelines streamline VM provisioning, software deployment, and configuration management at scale. |
| **Full Observability** | Monitoring and dashboards for intrusion detection and logs provide actionable insights. |
| **Zero-Trust Security** | Compartmentalized VMs, automated threat response, and SOC integration enforce strict operational security. |

</div>

---

## Quick Navigation

<div align="left">

<details open>
  <summary><strong>EvoSec-Lab Wiki Table of Contents</strong></summary>

- [01 – Architecture](https://github.com/FlorianStuettgen/EvoSec/wiki/01-%E2%80%90-Architecture)
- [02 – Hardware](https://github.com/FlorianStuettgen/EvoSec/wiki/02-%E2%80%90-Hardware)
- [03 – Software Stack](https://github.com/FlorianStuettgen/EvoSec/wiki/03-%E2%80%90-Software-Stack)
- [04 – Network Topology](https://github.com/FlorianStuettgen/EvoSec/wiki/04-%E2%80%90-Network-Topology)
- [05 – CI/CD & Automation](https://github.com/FlorianStuettgen/EvoSec/wiki/05-%E2%80%90-CI-CD-&-Automation)
- [06 – Monitoring & Telemetry](https://github.com/FlorianStuettgen/EvoSec/wiki/06-%E2%80%90-Monitoring-&-Telemetry)
- [07 – Security Model](https://github.com/FlorianStuettgen/EvoSec/wiki/07-%E2%80%90-Security-Model)
- [08 – Use Cases](https://github.com/FlorianStuettgen/EvoSec/wiki/08-%E2%80%90-Use-Cases)
- [09 – Roadmap](https://github.com/FlorianStuettgen/EvoSec/wiki/09-%E2%80%90-Roadmap)
- [10 – Appendix](https://github.com/FlorianStuettgen/EvoSec/wiki/10-%E2%80%90-Appendix)

</details>
</div>

---

## EvoSec Capabilities

EvoSec provides a comprehensive environment for cybersecurity research experimentation and demonstration, from multi-VM experiments and containerized services to hypervisor snapshots for flexible and reproducible lab testing: 

```mermaid
graph LR
    A["EvoSec-Lab Environment"] --> B["Multi-VM Experiments"]
    A --> C["Containerized Services"]
    A --> D["Hypervisor Snapshots"]

    B --> E["Flexible Testing"]
    C --> E
    D --> E

    E --> F["Reproducible Results"]
```
The platform integrates honeypots, tar pits, and IDS/IPS systems to enable controlled analysis of attacker behavior and threat research, while dynamic network orchestration allows subsecond-scale VLAN reconfigurations and automated containment, simulating complex operational scenarios. 

AI-driven automation, Infrastructure-as-Code provisioning, and pipelines ensure seamless, scalable operations, while real-time dashboards, logging, and alerts provide complete observability and actionable insights. Designed with reproducibility and demonstration in mind, EvoSec-Lab serves as a professional and educational showcase of enterprise lab practices and research-grade workflows.

---

## Security First
```mermaid
graph TD
    Core[Zero-Trust Core] --> VLAN[Segmented VLANs]
    Core --> AI[AI Threat Detection]
    Core --> SOC[SOC Monitoring]
    Core --> Isolation[Traffic Isolation]

    VLAN --> Outcome[Secure & Resilient Lab]
    AI --> Outcome
    SOC --> Outcome
    Isolation --> Outcome
```
EvoSec is built around a multi-layered zero-trust security model, combining segmented VLANs, AI-driven threat detection, and SOC-integrated monitoring. Suspicious activity is automatically contained, and dynamic traffic isolation ensures the environment remains secure and resilient. This approach enables advanced experimentation without compromising operational safety.

---

## AI-Driven Automation, Observability & Telemetry

EvoSec is a smart lab orchestration platform that leverages AI, machine learning, and DevOps to automate, optimize, and secure research environments. It continuously monitors system status and network traffic, providing real-time optimization, intelligent threat detection, and automated responses.
Core capabilities include dynamic network configuration, adaptive honeypot-based deception, and event-driven anomaly detection, enabling researchers to study threats while maintaining integrity. 

QubesOS is utilized for secure, compartmentalized experimentation and SaltStack for advanced configuration management and automated provisioning.
Supporting automated deployment, updates, scaling, adaptive experiments, and predictive maintenance, the system enhances control and efficiency while AI automation ensures secure, responsive, and adaptable lab infrastructure.

The system delivers granular observability across infrastructure, apps, and network by collecting metrics such as CPU, memory, storage I/O, and network traffic deep packet inspection for detailed analysis and interpretation: 

<div align="center">

<img width="725" height="543" alt="NSTscreen013" src="https://github.com/user-attachments/assets/cf118ed6-64b2-4ed3-bbdd-02fedad4afd5" />

</div>

The ELK stack provides central logging for real-time event tracking and anomaly detection, while Grafana dashboards visualize system and security status.
SOC integration enables continuous monitoring, advanced threat detection, and prompt response to abnormal activities. 

By bringing together data from multiple sources, EvoSec turns raw information into actionable insights, improving operational efficiency and maintaining strong security:

![Untitled](https://github.com/user-attachments/assets/11ca33e1-3acc-4314-af37-2aa7e385bd2c)


---

<div align="center">

## Why EvoSec?

EvoSec combines enterprise-grade infrastructure, AI-driven automation, 
and security, making it ideal for professional research and education.

![test2](https://github.com/user-attachments/assets/7388aa89-6603-4772-b960-438a4a78339b)

As of December 2025, EvoSec is now fully operational!

Stay tuned or visit us for more details on EvoSec’s architecture, components, and ongoing experiments:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Florian_Stuettgen-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/florian-stuettgen/)
[![EvoSec Wiki](https://img.shields.io/badge/EvoSec-Wiki-0A66C2?style=for-the-badge&logo=github)](https://github.com/FlorianStuettgen/EvoSec/wiki)

</div>


