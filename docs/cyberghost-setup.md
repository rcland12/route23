# CyberGhost VPN Setup Guide

This guide explains how to configure Route 23 with CyberGhost VPN.

## Prerequisites

- Active CyberGhost subscription
- CyberGhost account credentials
- Note: CyberGhost has specific servers optimized for torrenting

## Getting Your Credentials

### 1. Get Your VPN Credentials

CyberGhost uses separate VPN credentials (different from your account login):

1. Log in to your CyberGhost account: https://my.cyberghostvpn.com/
2. Navigate to **My Devices** or **Configure New Device**
3. Select **Configure New Device** → **Other**
4. Choose **OpenVPN** or **WireGuard**
5. Copy your:
   - **Username** (usually starts with your account ID)
   - **Password** (random string, different from account password)
   - **Device token** (for some configurations)

### 2. Server Selection

CyberGhost has dedicated **torrenting servers** (P2P optimized). Always use these for Route 23.

## Configuration

### Method 1: OpenVPN (Most Compatible)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=cyberghost
OPENVPN_USER=your_vpn_username
OPENVPN_PASSWORD=your_vpn_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: cyberghost
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"
    SERVER_CATEGORIES: P2P  # Important: Use P2P servers!
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### Method 2: WireGuard (Faster)

```bash
# VPN Configuration
VPN_SERVICE=cyberghost
WIREGUARD_PRIVATE_KEY=your_wireguard_private_key
WIREGUARD_ADDRESSES=your_wireguard_address
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: cyberghost
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"
    SERVER_CATEGORIES: P2P
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## P2P-Optimized Servers

**IMPORTANT:** Always use `SERVER_CATEGORIES: P2P` to ensure you connect to torrent-friendly servers.

### Best P2P Server Locations

CyberGhost has dedicated P2P servers in:

**Americas:**
- United States (multiple locations)
- Canada

**Europe:**
-  Germany (best for Europe)
-  Netherlands
-  Romania (CyberGhost HQ, excellent speeds)
-  Spain
-  Switzerland
-  Sweden
- Poland
- Czech Republic

**Asia-Pacific:**
- Singapore
- Hong Kong
- Australia

### Server Configuration Examples

```yaml
# Recommended: Romania (CyberGhost's home country, best speeds)
SERVER_COUNTRIES: "Romania"
SERVER_CATEGORIES: P2P

# Or USA
SERVER_COUNTRIES: "United States"
SERVER_CATEGORIES: P2P

# Or Germany
SERVER_COUNTRIES: "Germany"
SERVER_CATEGORIES: P2P
```

## Port Forwarding

**CyberGhost does not support port forwarding.**

This limitation affects:
- Incoming peer connections
- Seeding ratios
- Upload speeds

If port forwarding is critical, consider:
- Private Internet Access (PIA)
- ProtonVPN
- AirVPN

## Verification

Test your CyberGhost connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP (should show CyberGhost server IP)
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Verify you're on a P2P server
docker exec route23-vpn wget -qO- https://ipinfo.io/json

# Check connection details in logs
docker logs route23-vpn 2>&1 | grep -i "connected"
```

## Troubleshooting

### Authentication Failed

```bash
# Common mistakes:
# 1. Using account email/password instead of VPN credentials
# 2. Not generating device credentials

# Solution:
# Go to: https://my.cyberghostvpn.com/
# Configure New Device → OpenVPN
# Copy the VPN credentials (NOT your account password)
```

### "P2P Not Allowed" Error

```bash
# You're connected to a non-P2P server
# Add this to docker-compose.yaml:

environment:
  SERVER_CATEGORIES: P2P  # This is REQUIRED for torrenting
```

### Connection Timeout

```bash
# Try different P2P server location
SERVER_COUNTRIES: "Romania"  # CyberGhost HQ, usually fastest

# Or
SERVER_COUNTRIES: "Netherlands"  # Also good for P2P
```

### Slow Speeds

```bash
# Use WireGuard if available
VPN_TYPE: wireguard

# Choose geographically closer server
SERVER_COUNTRIES: "United States"  # If in North America

# Use CyberGhost's fastest servers (Romania)
SERVER_COUNTRIES: "Romania"
```

### Device Limit Reached

```bash
# CyberGhost limits simultaneous connections (7 devices)
# If you see "device limit" error:

# 1. Log in to: https://my.cyberghostvpn.com/
# 2. Go to "My Devices"
# 3. Remove unused devices
# 4. Or disconnect other active connections
```

## Advanced Configuration

### Optimized P2P Setup

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: cyberghost
    VPN_TYPE: wireguard  # Faster than OpenVPN
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "Romania"  # Fastest CyberGhost servers
    SERVER_CATEGORIES: P2P       # Required for torrenting
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    FIREWALL_VPN_INPUT_PORTS: 6881  # Allow torrent port
    TZ: ${TIMEZONE}
```

### DNS Configuration

```yaml
# Use CyberGhost DNS (default, includes malware blocking)
# Automatically configured

# Or use custom DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### Kill Switch

Built-in with Gluetun:

```yaml
FIREWALL: on  # Default, blocks non-VPN traffic
```

### Ad Blocking

CyberGhost includes built-in ad/tracker blocking (enabled by default in their DNS).

## CyberGhost Features

### Pros
**Dedicated P2P servers** (optimized for torrenting)
**NoSpy servers** (located in Romania, extra privacy)
**7 simultaneous connections**
**Good speeds** (especially Romania servers)
**45-day money-back guarantee**
**Built-in malware blocking**
**WireGuard support**

### Cons
**No port forwarding** (limits seeding efficiency)
**Based in Romania** (EU jurisdiction, 14 Eyes adjacent)
**Aggressive marketing**
**Device limit** can be restrictive

## Server Categories Explained

CyberGhost organizes servers by purpose:

| Category | Purpose | Use for Route 23? |
|----------|---------|------------------|
| **P2P** | Torrenting | **YES - Always use this** |
| Streaming | Netflix, etc. | No |
| NoSpy | Extra privacy | Optional |
| Gaming | Low latency | No |

**Always specify:** `SERVER_CATEGORIES: P2P`

## Performance Comparison

### OpenVPN vs WireGuard

| Feature | OpenVPN | WireGuard |
|---------|---------|-----------|
| Speed | 100-200 Mbps | 300-500 Mbps |
| CPU Usage | Higher | Lower |
| Battery Impact | Higher | Lower |
| Compatibility | Better | Good |
| Recommended | Compatibility | Performance |

### Server Location Impact

| Location | Pros | Cons |
|----------|------|------|
| **Romania** |  Fastest, CyberGhost HQ | Farther from US |
| **Germany** | Fast, good EU location | Moderate |
| **Netherlands** | Good speeds, P2P-friendly | Moderate |
| **USA** | Close if in US | May be slower |

## Configuration Examples

### For Maximum Speed

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: cyberghost
    VPN_TYPE: wireguard
    SERVER_COUNTRIES: "Romania"  # Fastest
    SERVER_CATEGORIES: P2P
```

### For Privacy + Speed

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: cyberghost
    VPN_TYPE: wireguard
    SERVER_COUNTRIES: "Romania"
    SERVER_CATEGORIES: "P2P,NoSpy"  # Extra privacy
```

### For US Users

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: cyberghost
    VPN_TYPE: wireguard
    SERVER_COUNTRIES: "United States"
    SERVER_CATEGORIES: P2P
```

## Why Choose CyberGhost for Torrenting?

### Good For
**Dedicated P2P servers** (properly optimized)
**Good speeds** (especially Romania)
**Easy setup**
**Unlimited bandwidth**
**P2P allowed and encouraged**

### Not Ideal For
**Maximum seeding ratios** (no port forwarding)
**Advanced users** (less configurable)
**Many devices** (7 connection limit)

## Recommended Setup

For Route 23 with CyberGhost:

```bash
# .env
VPN_SERVICE=cyberghost
OPENVPN_USER=your_vpn_username
OPENVPN_PASSWORD=your_vpn_password
PRIVATE_SUBNET=192.168.1.0/24
TIMEZONE=America/New_York

# docker-compose.yaml key settings:
SERVER_COUNTRIES: "Romania"     # or your preferred location
SERVER_CATEGORIES: P2P          # REQUIRED
VPN_TYPE: openvpn              # or wireguard if you have the key
```

## References

- [CyberGhost Account](https://my.cyberghostvpn.com/)
- [CyberGhost Server List](https://www.cyberghostvpn.com/en_US/servers)
- [CyberGhost P2P Servers](https://support.cyberghostvpn.com/hc/en-us/articles/360010245159-Which-servers-allow-Torrenting-)
- [Gluetun CyberGhost Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/cyberghost.md)
