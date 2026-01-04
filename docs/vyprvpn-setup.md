# VyprVPN Setup Guide

This guide explains how to configure Route 23 with VyprVPN.

## Prerequisites

- Active VyprVPN subscription
- VyprVPN account credentials
- **Note:** VyprVPN owns all its servers (no third-party hosting)

## Getting Your Credentials

### Simple Setup

VyprVPN uses your account credentials directly:

1. Sign up at: https://www.vyprvpn.com/
2. Your credentials are:
   - **Username:** Your email address OR username
   - **Password:** Your account password

**That's it!** No separate VPN credentials needed.

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=vyprvpn
OPENVPN_USER=your_email_or_username
OPENVPN_PASSWORD=your_account_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: vyprvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### WireGuard Configuration

**Note:** VyprVPN uses their proprietary "Chameleon" protocol in their apps. Standard WireGuard may not be fully supported through Gluetun.

If WireGuard is available:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: vyprvpn
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"
```

## Server Locations

VyprVPN has 700+ servers in 70+ countries. **All owned infrastructure** (no third-party).

### Best Locations for P2P

**Americas:**
- United States - Multiple cities
- Canada - Toronto
- Mexico - Mexico City

**Europe:**
- Netherlands - Amsterdam
- Switzerland - Zurich
- Spain - Madrid
- Sweden - Stockholm
- United Kingdom - London

**Asia-Pacific:**
- Singapore
- Japan - Tokyo
- Australia - Sydney
- Hong Kong

### Server Selection

```bash
# By country
SERVER_COUNTRIES: "Netherlands"

# Or by city (if supported)
SERVER_CITIES: "Amsterdam"
```

## Port Forwarding

**VyprVPN does NOT support port forwarding.**

**Impact:**
- Cannot accept incoming peer connections
- Lower seeding ratios
- Reduced upload performance

**Alternatives with port forwarding:**
- Private Internet Access (PIA)
- ProtonVPN
- AirVPN
- TorGuard

## Chameleon Protocol

VyprVPN's unique feature is the **Chameleon protocol** - OpenVPN with obfuscation to bypass DPI (Deep Packet Inspection) and VPN blocking.

### Using Chameleon

Chameleon is available in VyprVPN's official apps but may not be directly supported in Gluetun. If you need Chameleon:

1. Use VyprVPN's official app instead
2. Or contact VyprVPN for OpenVPN configs with Chameleon
3. Standard OpenVPN works for most use cases

## Verification

Test your VyprVPN connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check connection details
docker exec route23-vpn wget -qO- https://ipinfo.io/json
```

## Troubleshooting

### Authentication Failed

```bash
# VyprVPN uses account credentials directly
# Common issues:
# 1. Typo in email/password
# 2. Account suspended/expired

# Verify at: https://www.vyprvpn.com/login
# No separate VPN credentials needed
```

### Connection Timeout

```bash
# Try different server location
SERVER_COUNTRIES: "Switzerland"

# Or
SERVER_COUNTRIES: "Netherlands"

# Check VyprVPN server status
```

### Slow Speeds

```bash
# Choose geographically closer server
SERVER_COUNTRIES: "United States"

# VyprVPN OpenVPN may be slower than WireGuard-based competitors
# This is inherent to the protocol
```

### "No servers found" Error

```bash
# Verify server country name format
# Use full country names:
SERVER_COUNTRIES: "United States"  # Not "USA" or "US"
SERVER_COUNTRIES: "United Kingdom"  # Not "UK"
```

## VyprVPN Features

### Pros
**Own all servers** (no third-party hosting - unique!)
**Chameleon protocol** (bypass VPN blocks/censorship)
**No logs policy** (independently audited)
**Good speeds** (owned infrastructure)
**30 simultaneous connections**
**NAT firewall** included
**Cloud storage** (VyprVPN Cloud addon)
**Switzerland-based** (good jurisdiction)

### Cons
**No port forwarding** (bad for seeding ratios)
**More expensive** (~$5-10/month)
**Past logging concerns** (resolved in 2018)
**Chameleon not in Gluetun** (proprietary)
**No cryptocurrency payment**

## Privacy & Security

### No Logs Policy
- **Independently audited** (2018 by Leviathan Security)
- **Past:** Had logs before 2018
- **Current:** Zero-logs policy

### Jurisdiction
- **Based in Switzerland** (good privacy laws)
- **Not in 5/9/14 Eyes**

### Encryption
- **OpenVPN:** AES-256 encryption
- **Chameleon:** AES-256 + obfuscation
- **Perfect forward secrecy**
- **Kill switch** (VyprVPN app only)

### Owned Infrastructure
VyprVPN's biggest advantage: **They own ALL their servers**
- No third-party data centers
- Full control over hardware
- Better security posture
- Potentially better speeds

## Performance

With OpenVPN:
- **Download:** 150-400 Mbps
- **Upload:** 100-300 Mbps
- **Latency:** Moderate

**Note:** VyprVPN may be slower than WireGuard-based VPNs (Mullvad, NordVPN, PIA).

## Plans

### VyprVPN Plan
- **Price:** ~$5/month (annual) or $10/month (monthly)
- **30 connections**
- **700+ servers, 70+ countries**
- **Unlimited bandwidth**
- **Chameleon protocol**
- **NAT firewall**
- **Cloud storage** (1TB addon)

## Advanced Configuration

### Custom DNS

```yaml
# Use VyprVPN DNS (default)
# Automatically configured

# Or custom DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### Kill Switch

Kill switch is built into Gluetun:

```yaml
FIREWALL: on  # Default, blocks non-VPN traffic
```

### NAT Firewall

VyprVPN includes NAT firewall by default (server-side feature).

## Configuration Examples

### Basic Setup

```yaml
# .env
VPN_SERVICE=vyprvpn
OPENVPN_USER=your_email@example.com
OPENVPN_PASSWORD=your_password
PRIVATE_SUBNET=192.168.1.0/24

# docker-compose.yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: vyprvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Switzerland"
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
```

### For Best Privacy

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: vyprvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Switzerland"  # VyprVPN HQ
```

## Why Choose VyprVPN?

### Excellent For:
**Users in censored countries** (Chameleon protocol)
**Privacy-conscious** (owned infrastructure)
**Bypassing VPN blocks**
**Many devices** (30 connections)

### Not Ideal For:
**Torrenting with high ratios** (no port forwarding)
**Budget users** (more expensive)
**Maximum speeds** (OpenVPN limitations)
**Cryptocurrency users** (no crypto payment)

## Comparison: VyprVPN vs Competitors

| Feature | VyprVPN | PIA | Mullvad | ProtonVPN |
|---------|---------|-----|---------|-----------|
| Port Forwarding | | | | |
| Owned Servers | | | | Partial |
| Obfuscation | Chameleon | | | Stealth |
| Connections | 30 | 10 | 5 | 10 |
| Jurisdiction |  Switzerland |  USA |  Sweden |  Switzerland |
| Price | $$ | $ | $ | $$ |

## Use Cases

### Good For Route 23 If:
- You're in a censored country (need Chameleon)
- Privacy is important (owned infrastructure)
- You have many devices to connect
- You don't care about maximum seeding ratios

### Not Recommended If:
- Port forwarding is critical
- You want best value for torrenting
- You need fastest speeds
- Budget is a concern

## References

- [VyprVPN Website](https://www.vyprvpn.com/)
- [VyprVPN Login](https://www.vyprvpn.com/login)
- [VyprVPN Audit Report](https://www.vyprvpn.com/blog/vyprvpn-announces-audit-results)
- [Gluetun VyprVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/vyprvpn.md)

## Final Recommendation

**VyprVPN is solid but not optimal for Route 23.**

**Choose VyprVPN if:**
- You need Chameleon to bypass VPN blocking
- Owned infrastructure matters to you
- You want Swiss jurisdiction
- You have 30+ devices

**Choose alternatives if:**
- **Port forwarding needed** → PIA, ProtonVPN, AirVPN
- **Best torrenting performance** → PIA (cheapest + port forwarding)
- **Maximum privacy** → Mullvad or IVPN
- **Best value** → PIA or Mullvad

VyprVPN is a good general-purpose VPN, but for dedicated torrenting with Route 23, PIA or ProtonVPN are better choices.
