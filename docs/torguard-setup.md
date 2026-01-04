# TorGuard Setup Guide

This guide explains how to configure Route 23 with TorGuard VPN.

## Prerequisites

- Active TorGuard subscription
- TorGuard account credentials
- **Note:** TorGuard is specifically designed for torrenting with **port forwarding support**

## Getting Your Credentials

### 1. Get Your VPN Credentials

TorGuard uses separate VPN credentials from your account login:

1. Log in to: https://torguard.net/clientarea.php
2. Navigate to **Services** → **My Services**
3. Click on your TorGuard VPN service
4. Look for **VPN Username** and **VPN Password**
5. These are different from your account email/password

### 2. Generate Configuration (Optional)

For WireGuard or specific OpenVPN configs:

1. Go to: https://torguard.net/clientarea.php
2. Navigate to **Tools** → **Config Generator**
3. Select your protocol (OpenVPN or WireGuard)
4. Choose servers
5. Download configuration

## Configuration

### Method 1: OpenVPN (Standard)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=torguard
OPENVPN_USER=your_vpn_username
OPENVPN_PASSWORD=your_vpn_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: torguard
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    VPN_PORT_FORWARDING: on  # If you have port forwarding addon
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### Method 2: WireGuard

```bash
# In .env
VPN_SERVICE=torguard
WIREGUARD_PRIVATE_KEY=your_private_key
WIREGUARD_ADDRESSES=10.x.x.x/32
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: torguard
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"
    VPN_PORT_FORWARDING: on
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Port Forwarding

**TorGuard supports port forwarding** (requires addon purchase)

### Purchase Port Forwarding

Port forwarding is a **paid addon** with TorGuard:

1. Log in to: https://torguard.net/clientarea.php
2. Go to **Addons** → **Port Forwarding**
3. Purchase port forwarding addon (~$1-2/month)
4. You'll be assigned 5 ports

### Configure Port Forwarding

1. After purchase, go to **Services** → **Port Forward Settings**
2. Note your assigned ports
3. Configure the port in your rTorrent settings:

```bash
# In rutorrent/.rtorrent.rc
network.port_range.set = YOUR_PORT-YOUR_PORT
```

### Enable in Gluetun

```yaml
vpn:
  environment:
    VPN_PORT_FORWARDING: on
    # TorGuard port forwarding may require manual configuration
```

## Server Locations

TorGuard has 3000+ servers in 50+ countries.

### Best for Torrenting

**Americas:**
- United States - Multiple cities (LA, NYC, Chicago, Miami)
- Canada - Toronto, Montreal, Vancouver

**Europe:**
- Netherlands - Amsterdam
- Switzerland - Zurich
- Sweden - Stockholm
- Germany - Frankfurt
- United Kingdom - London

**Asia-Pacific:**
- Singapore
- Japan - Tokyo
- Australia - Sydney

### Server Selection

```bash
# By country
SERVER_COUNTRIES: "United States"

# By city (if supported)
SERVER_CITIES: "Los Angeles"

# By region
SERVER_REGIONS: "us-west"
```

## Stealth VPN (Obfuscation)

TorGuard offers **Stealth VPN** to bypass VPN blocks and DPI:

### Enable Stealth VPN

Stealth VPN uses obfuscation protocols:

1. Purchase Stealth VPN addon (if needed)
2. Use specific Stealth servers
3. Configure OpenVPN with additional options

```yaml
# May require custom OpenVPN configuration
# See TorGuard documentation for Stealth setup
```

## Verification

Test your TorGuard connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check connection details
docker exec route23-vpn wget -qO- https://ipinfo.io/json

# Verify port forwarding
docker logs route23-vpn 2>&1 | grep -i port
```

## Troubleshooting

### Authentication Failed

```bash
# Common mistakes:
# 1. Using account email/password instead of VPN credentials
# 2. VPN credentials not generated

# Get VPN credentials at:
https://torguard.net/clientarea.php → Services → My Services

# Ensure you're using VPN_USERNAME and VPN_PASSWORD
# NOT your account email/password
```

### Connection Timeout

```bash
# Try different server
SERVER_COUNTRIES: "Netherlands"

# Or specific server region
SERVER_REGIONS: "eu-west"

# Check server status: https://torguard.net/network/
```

### Port Forwarding Not Working

```bash
# Verify you purchased port forwarding addon
# Check: https://torguard.net/clientarea.php → Addons

# Ensure ports are assigned
# Go to: Services → Port Forward Settings

# Restart VPN container
docker restart route23-vpn
```

### Slow Speeds

```bash
# Use WireGuard (faster than OpenVPN)
VPN_TYPE: wireguard

# Choose closer server
SERVER_COUNTRIES: "United States"

# Try Stealth VPN servers (may be less congested)
```

## TorGuard Features

### Pros
**Designed for torrenting** (name says it all!)
**Port forwarding available** (paid addon)
**Huge server network** (3000+ servers)
**No logs policy**
**Stealth VPN** (bypass VPN blocks)
**Dedicated IP option** (addon)
**10 Gbps servers** (fast speeds)
**Unlimited bandwidth**
**P2P optimized** (torrent-friendly)

### Cons
**Port forwarding costs extra** (~$2/month)
**Expensive base price** (~$10/month)
**Based in USA** (5 Eyes jurisdiction)
**Addon model** (nickel-and-dime approach)
**Complex pricing** (base + addons)
**Past logging concerns** (resolved but noteworthy)

## Plans & Pricing

### Anonymous VPN
- Base: ~$9.99/month (discounts for longer terms)
- 8 simultaneous connections
- All servers
- Unlimited bandwidth

### Addons (Optional)
- **Port Forwarding:** ~$1-2/month (5 ports)
- **Dedicated IP:** ~$5-8/month
- **Stealth VPN:** ~$2/month
- **Streaming Bundle:** ~$5/month

**For Route 23:** Base + Port Forwarding = ~$12/month

## Performance

With WireGuard:
- **Download:** 400-800 Mbps
- **Upload:** 300-600 Mbps
- **Latency:** Low

With OpenVPN:
- **Download:** 150-400 Mbps
- **Upload:** 100-300 Mbps

TorGuard offers 10 Gbps servers for Pro users.

## Privacy & Security

- **No logs policy** (claimed)
- **Based in USA** (5 Eyes - concern)
- **Past controversies** (2017 logging incident, now resolved)
- **Strong encryption** (AES-256)
- **Perfect forward secrecy**
- **Kill switch** (Network Lock)
- **DNS leak protection**

## Advanced Configuration

### Dedicated IP (Addon)

For a static IP address:

1. Purchase dedicated IP addon
2. Choose country and IP type
3. Configure in Gluetun with specific server

### Stealth VPN

For bypassing VPN detection:

```yaml
# May require custom OpenVPN configuration
# Contact TorGuard support for Stealth server list
```

### Streaming Bundle

TorGuard offers streaming-optimized IPs (for Netflix, etc.):
- Not needed for Route 23/torrenting
- Skip this addon

## Configuration Examples

### Basic Setup (with Port Forwarding)

```yaml
# .env
VPN_SERVICE=torguard
OPENVPN_USER=your_vpn_username
OPENVPN_PASSWORD=your_vpn_password
PRIVATE_SUBNET=192.168.1.0/24

# docker-compose.yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: torguard
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Netherlands"
    VPN_PORT_FORWARDING: on
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
```

### WireGuard Setup

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: torguard
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"
    VPN_PORT_FORWARDING: on
```

## Why Choose TorGuard?

### Excellent For:
**Serious torrenters** (designed for P2P)
**Users who need port forwarding**
**High-speed requirements**
**Bypassing VPN blocks** (Stealth VPN)
**Dedicated IP needs**

### Consider Alternatives If:
**You want port forwarding included** → Use PIA (included in base price)
**Budget-conscious** → TorGuard is expensive with addons
**Privacy-focused** → Avoid USA-based VPNs (use Mullvad/IVPN)
**Simple pricing** → Too many addons

## Comparison: TorGuard vs Competitors

| Feature | TorGuard | PIA | ProtonVPN |
|---------|----------|-----|-----------|
| Port Forwarding | (addon) | (included) | (included) |
| Price | $12/month | $3/month | $10/month |
| Servers | 3000+ | 35000+ | 1900+ |
| Jurisdiction | USA 🚩 | USA 🚩 | Switzerland |
| Best For | P2P power users | Value seekers | Privacy + P2P |

## References

- [TorGuard Website](https://torguard.net/)
- [TorGuard Client Area](https://torguard.net/clientarea.php)
- [TorGuard Config Generator](https://torguard.net/knowledgebase.php?action=displayarticle&id=53)
- [TorGuard Port Forwarding Guide](https://torguard.net/knowledgebase.php?action=displayarticle&id=149)
- [Gluetun TorGuard Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/torguard.md)

## Final Recommendation

**TorGuard is purpose-built for torrenting** but the addon pricing model makes it expensive.

**Choose TorGuard if:**
- You're a serious torrenter
- You need dedicated IP or Stealth VPN
- Speed is critical
- You don't mind paying for addons

**Choose PIA instead if:**
- You want port forwarding included
- You want better value (~$3/month)
- You don't need extras

**Choose ProtonVPN if:**
- Privacy is important (non-USA)
- You want port forwarding included
- You value transparency

TorGuard is solid for torrenting, but PIA offers better value with included port forwarding.
