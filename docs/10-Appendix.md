# 10 — Appendix

## Status vocabulary

| Label | Meaning |
| --- | --- |
| Installed | Physical component is present in the documented build |
| Documented operating role | The repository records the role; current configuration evidence may still be needed |
| Implemented | Code or configuration exists in the repository and can be verified |
| Partially evidenced | Some screenshots/configuration or behaviour exist, but the full claim is not proven |
| Prototype | Narrow implementation or experiment; not a general platform capability |
| Design track | Intended architecture without sufficient implementation evidence |
| Roadmap | Future work only |

## Trust-zone glossary

- **Management:** privileged administration and recovery.
- **Core:** switching, storage and critical services.
- **DMZ:** boundary-facing services with restricted access.
- **Lab:** controlled application and experiment workloads.
- **Honeypot:** decoy and observation systems.
- **Guest:** temporary, non-critical and isolated access.

## Technical glossary

- **VLAN:** logical Layer-2 segmentation.
- **Honeypot:** decoy system used to observe unauthorized or suspicious activity.
- **Tar pit:** service that intentionally delays interactions for observation.
- **IDS/IPS:** intrusion detection/prevention capability.
- **OOB:** out-of-band management path independent of normal workload networking.
- **Qubes OS:** compartmentalized operating system used for security domains.
- **Proxmox VE:** virtualization platform used for storage-centric services and workloads.
- **SELKS:** security-monitoring distribution incorporating Suricata and analyst tooling.
- **Replay:** deterministic evaluation of stored events against inspectable rules.

## Restored diagram index

- [`assets/diagrams/diagram.svg`](../assets/diagrams/diagram.svg) — original full-system diagram
- [`assets/diagrams/Simulation.svg`](../assets/diagrams/Simulation.svg) — original simulation view
- [`assets/diagrams/Modular Trust Zones.svg`](../assets/diagrams/Modular%20Trust%20Zones.svg) — original trust-zone view
- [`assets/diagrams/Dynamic Orchestration 2.svg`](../assets/diagrams/Dynamic%20Orchestration%202.svg) — original orchestration view
- [`assets/diagrams/wiki-home-capability.svg`](../assets/diagrams/wiki-home-capability.svg) — original capability graphic

## Restored photo index

- Rack overview: [`test2.jpeg`](../assets/photos/test2.jpeg)
- Dell R710: [`R710.jpg`](../assets/photos/R710.jpg)
- EqualLogic: [`EqualLogic.png`](../assets/photos/EqualLogic.png)
- Avid bay: [`Avid Bay.png`](../assets/photos/Avid%20Bay.png)
- Dell X1052P: [`Dell X1052P.jpg`](../assets/photos/Dell%20X1052P.jpg)
- Cisco ASA 5510: [`Cisco ASA 5510.jpg`](../assets/photos/Cisco%20ASA%205510.jpg)
- Cisco ASA 5515-X: [`Cisco ASA 5515-x.jpg`](../assets/photos/Cisco%20ASA%205515-x.jpg)
- SonicWall SRA 4200: [`SonicWall SRA 4200.jpg`](../assets/photos/SonicWall%20SRA%204200.jpg)
- OpenGear CM4148: [`OpenGear CM4148.jpg`](../assets/photos/OpenGear%20CM4148.jpg)
- Console views: [`console1.jpg`](../assets/photos/console1.jpg), [`console2.jpg`](../assets/photos/console2.jpg)
- Monitoring views: [`monitor1.jpg`](../assets/photos/monitor1.jpg), [`monitor2.jpg`](../assets/photos/monitor2.jpg)
- Patch/cabling: [`patch.jpg`](../assets/photos/patch.jpg)
- Build images: [`build1.png`](../assets/photos/build1.png), [`build2.png`](../assets/photos/build2.png), [`build3.png`](../assets/photos/build3.png)

## Firewall policy index

The restored policy set under `infra/lab-firewall-policies/` includes the universal baseline plus focused pages for management, segmentation, NAT, ACLs, VPN, IDS/IPS, logging, hardening and change control.

## Historical note

The GitHub wiki preserves earlier project language and revisions. The maintained Markdown files in this repository now provide the source of truth, particularly [Implementation State](14-Implementation-State.md).
