# Universal Lab Base-Policy

This document provides a **comprehensive lab configuration** for Cisco ASA 5510, ASA 5515-X, and SonicWall 4200 firewalls. It is designed for enterprise-grade labs, integrating advanced security, monitoring, segmentation, NAT, VPNs, IPS/IDS, and best practices.

---

## 1. Hostname, Domain, and Management Access

**Objective:** Secure admin access, enforce role-based authentication, enable logging and auditing.

**ASA Example:**

```
hostname LAB-FW
domain-name lab.local
enable password <ENCRYPTED_PASSWORD> privilege 15
ssh 192.168.1.0 255.255.255.0 inside
ssh version 2
ssh timeout 120
aaa authentication ssh console LOCAL
http 192.168.1.0 255.255.255.0 inside
snmp-server enable traps snmp
snmp-server host inside 192.168.1.20 community <COMMUNITY_STRING>
logging enable
logging buffered informational
logging trap informational
logging host inside 192.168.1.10
logging host inside 192.168.1.15 transport udp port 514
```

**SonicWall Example:**

```
configure
set hostname LAB-FW
set admin-password <STRONG_PASSWORD>
set admin-management enable https ssh
set admin-management-interface X4
set snmp enable
set snmp-community <COMMUNITY_STRING>
set snmp-traps enable
set logging enable
set logging host 192.168.1.10
set syslog enable
set syslog-host 192.168.1.15 port 514
```

**Additional Best Practices:**

* Enforce MFA for management if supported
* Restrict admin access to dedicated management VLAN
* Enable login banners and audit logging

---

## 2. Interface Segmentation & VLAN Mapping

**Objective:** Isolate zones, prevent lateral movement, simplify monitoring.

| Zone       | ASA Interface | SonicWall Interface | Security Level | Purpose               | VLAN / Notes |
| ---------- | ------------- | ------------------- | -------------- | --------------------- | ------------ |
| Outside    | G0/0          | X0                  | 0              | Untrusted Internet    | VLAN 10      |
| Inside     | G0/1          | X1                  | 100            | Trusted LAN           | VLAN 20      |
| DMZ        | G0/2          | X2                  | 50             | Semi-trusted Services | VLAN 30      |
| VPN        | G0/3          | X3                  | 70             | Remote Access         | VPN subnet   |
| Management | G0/4          | X4                  | 90             | Admin only            | Isolated     |
| Lab/Dev    | G0/5          | X5                  | 60             | Testing & Dev Zone    | VLAN 40      |

**ASA CLI Example:**

```
interface GigabitEthernet0/0
 nameif outside
 security-level 0
 ip address dhcp setroute
!
interface GigabitEthernet0/1
 nameif inside
 security-level 100
 ip address 192.168.1.1 255.255.255.0
!
interface GigabitEthernet0/2
 nameif dmz
 security-level 50
 ip address 192.168.2.1 255.255.255.0
!
interface GigabitEthernet0/3
 nameif vpn
 security-level 70
 ip address 192.168.3.1 255.255.255.0
!
interface GigabitEthernet0/4
 nameif management
 security-level 90
 ip address 192.168.4.1 255.255.255.0
!
interface GigabitEthernet0/5
 nameif lab
 security-level 60
 ip address 192.168.5.1 255.255.255.0
```

**SonicWall CLI Example:**

```
interface X0 name outside ip dhcp
interface X1 name inside ip 192.168.1.1/24
interface X2 name dmz ip 192.168.2.1/24
interface X3 name vpn ip 192.168.3.1/24
interface X4 name management ip 192.168.4.1/24
interface X5 name lab ip 192.168.5.1/24
```

**Best Practices:**

* Tag VLANs on trunk ports
* Isolate lab/dev traffic from production
* Apply inter-zone firewall rules based on risk levels

---

## 3. NAT Policy (Dynamic & Static)

**ASA Example:**

```
object network obj_any
 subnet 0.0.0.0 0.0.0.0
 nat (inside,outside) dynamic interface

object network obj_dmz
 subnet 192.168.2.0 255.255.255.0
 nat (dmz,outside) dynamic interface

object network obj_vpn
 subnet 192.168.3.0 255.255.255.0
 nat (vpn,outside) dynamic interface

object network obj_lab
 subnet 192.168.5.0 255.255.255.0
 nat (lab,outside) dynamic interface

! NAT Exemption
nat (inside,vpn) 0 access-list inside_vpn_no_nat
access-list inside_vpn_no_nat extended permit ip 192.168.1.0 255.255.255.0 192.168.3.0 255.255.255.0
```

**SonicWall Example:**

```
nat-policy add from X1 to X0 src any dst any service any
nat-policy add from X2 to X0 src any dst any service any
nat-policy add from X3 to X0 src any dst any service any
nat-policy add from X5 to X0 src any dst any service any
nat-policy add from X1 to X3 src 192.168.1.0/24 dst 192.168.3.0/24 service any no-nat
```

**Best Practices:**

* Combine dynamic NAT with static for DMZ servers
* Exclude VPN/management subnets from NAT
* Audit NAT rules regularly

---

## 4. ACL / Firewall Rules (Granular)

**ASA Example:**

```
! Inside to Outside
access-list inside_access extended permit ip any any

! Inside to DMZ
access-list inside_dmz extended permit ip any 192.168.2.0 255.255.255.0

! DMZ to Outside
access-list dmz_access extended permit tcp any any eq 80
access-list dmz_access extended permit tcp any any eq 443

! VPN to Internal
access-list vpn_access extended permit ip 192.168.3.0 255.255.255.0 any

! Management access
access-list management_access extended permit ip 192.168.4.0 255.255.255.0 any

! Apply ACLs to interfaces
access-group inside_access in interface inside
access-group inside_dmz in interface inside
access-group dmz_access in interface dmz
access-group vpn_access in interface vpn
access-group management_access in interface management
```

**SonicWall Example:**

```
access-rule add name "Inside-to-DMZ" from X1 to X2 action allow service any
access-rule add name "Inside-to-Outside" from X1 to X0 action allow service any
access-rule add name "VPN-to-Internal" from X3 to X1 action allow service any
access-rule add name "VPN-to-DMZ" from X3 to X2 action allow service any
access-rule add name "Management-to-All" from X4 to any action allow service any
```

**Best Practices:**

* Use object groups for networks and services
* Apply principle of least privilege
* Document each ACL with purpose and owner

---

## 5. VPN Setup (Site-to-Site & Remote Access)

**ASA Example:**

```
crypto ikev1 enable outside
crypto ikev1 policy 10
 authentication pre-share
 encryption aes
 hash sha
 group 2
 lifetime 86400
crypto ipsec ikev1 transform-set LAB-TRANSFORM esp-aes esp-sha-hmac
crypto map VPN-MAP 10 ipsec-isakmp
 set peer <PEER_IP>
 set transform-set LAB-TRANSFORM
 match address vpn_access
interface outside
 crypto map VPN-MAP
```

**SonicWall Example:**

```
vpn add name LAB-VPN policy ikev2 remote <PEER_IP> preshared-key <KEY> local-ip 192.168.3.1 remote-subnet 192.168.1.0/24,192.168.2.0/24
```

**Best Practices:**

* Use strong encryption (AES-256, SHA2)
* Enable split tunneling for lab networks
* Regularly rotate pre-shared keys

---

## 6. IPS/IDS & Advanced Threat Protection

**ASA Example:**

```
threat-detection basic-threat
threat-detection statistics
! Enable URL filtering if licensed
```

**SonicWall Example:**

```
set security-services enable
set ips enable
set gateway-anti-virus enable
set gateway-anti-spyware enable
```

**Best Practices:**

* Enable IPS/IDS on external and DMZ interfaces
* Regularly update threat signatures
* Monitor alerts and integrate with SIEM

---

## 7. Logging, Monitoring & SNMP

**ASA Example:**

```
logging enable
logging buffered informational
logging trap informational
logging host inside 192.168.1.10
logging host inside 192.168.1.15 transport udp port 514
snmp-server enable traps snmp
snmp-server host inside 192.168.1.20 community <COMMUNITY_STRING>
```

**SonicWall Example:**

```
logging enable
logging set level informational
logging host 192.168.1.10
snmp enable
snmp-traps enable
```

**Best Practices:**

* Centralized logging to SIEM
* Configure alerts for critical events
* Maintain log retention policies

---

## 8. Security Hardening & Best Practices

* Disable unused services and interfaces
* Enforce SSH/HTTPS management only
* Enable anti-spoofing and IP verification
* Implement strong enable/admin passwords
* Configure session timeouts and login lockouts
* Apply firmware updates and patches regularly
* Use object grouping and granular ACLs
* Enable IDS/IPS, Anti-Virus, and Anti-Spyware
* Enable rate-limiting on external interfaces
* Enable logging, syslog, SNMP traps for monitoring
* Regularly backup configuration and snapshots
* Isolate management, VPN, DMZ, and production zones
* Conduct lab testing in isolated environments
* Document all policies and maintain a versioned policy repository
