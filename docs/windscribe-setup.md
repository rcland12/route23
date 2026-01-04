# Windscribe VPN Setup Guide

This guide explains how to configure Route 23 with Windscribe VPN.

## Prerequisites

- Active Windscribe subscription (Free or Pro)
- Windscribe account
- Note: Free plan has 10GB/month limit (not recommended for heavy torrenting)

## Getting Your Credentials

### 1. Generate OpenVPN Credentials

Windscribe uses separate credentials for VPN connections:

1. Log in to your Windscribe account: https://windscribe.com/
2. Navigate to **My Account** → **OpenVPN Credentials**
3. If credentials don't exist, click **Generate Config Credentials**
4. Copy your:
   - **Username** (usually your Windscribe username)
   - **Password** (different from your account password)

### Alternative: Via Config Generator

1. Go to: https://windscribe.com/getconfig/openvpn
2. Log in if prompted
3. Your OpenVPN username will be shown at the top
4. Password is already generated (shown on page)

## Configuration

### OpenVPN Configuration (Standard)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=windscribe
OPENVPN_USER=your_openvpn_username
OPENVPN_PASSWORD=your_openvpn_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: windscribe
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### WireGuard Configuration (Pro Only)

WireGuard requires manual key generation:

1. Generate a WireGuard config at: https://windscribe.com/getconfig/wireguard
2. Extract the private key from the config file
3. Add to `.env`:

```bash
VPN_SERVICE=windscribe
WIREGUARD_PRIVATE_KEY=your_private_key
WIREGUARD_ADDRESSES=10.x.x.x/32
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: windscribe
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

Windscribe has servers in 63+ countries and 110+ cities.

### P2P-Friendly Locations

Windscribe allows P2P on specific "Windflix" and standard servers:

**Best for Torrenting:**
-  Netherlands - Amsterdam
-  Switzerland - Zurich
-  Canada - Toronto, Montreal, Vancouver
-  Romania - Bucharest
-  Spain - Madrid

**Also Good:**
- United States (most locations)
- United Kingdom
- Germany
- France
- Hong Kong

### Specify Server Location

```bash
# In .env or docker-compose.yaml
SERVER_COUNTRIES: "Netherlands"

# Or specific city
SERVER_CITIES: "Amsterdam"

# Or specific server (find at windscribe.com/status)
SERVER_HOSTNAMES: "amsterdam-001.whiskergalaxy.com"
```

### Server Regions (Windscribe Naming)

Windscribe uses creative names:

- US East → `Burger Land East`
- US West → `Burger Land West`
- US Central → `Burger Land Central`
- UK → `Blimey`
- Canada → `Maple Leaf`
- Netherlands → `The Windmill`
- Switzerland → `Toblerone`

Use standard country names with Gluetun (it handles the mapping).

## Port Forwarding

Windscribe supports **static port forwarding** on Pro plans:

### Enable Port Forwarding

1. Log in to Windscribe: https://windscribe.com/myaccount
2. Go to **My Account** → **Port Forwarding**
3. Enable port forwarding and note your assigned port
4. Use this port in your rTorrent configuration

### Configure in Route 23

Windscribe port forwarding is static (doesn't change), so configure manually:

```bash
# In rutorrent service environment or .rtorrent.rc
# Set your port (example: 54321)
network.port_range.set = 54321-54321
```

**Note:** Windscribe assigns you a specific port. This port is static and tied to your account.

## Verification

Test your Windscribe connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP (should show Windscribe exit IP)
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check location
docker exec route23-vpn wget -qO- https://ipinfo.io/json

# Test DNS
docker exec route23-vpn nslookup google.com
```

## Troubleshooting

### Authentication Failed

```bash
# Common issues:
# 1. Using account password instead of OpenVPN password
# 2. Credentials not generated yet

# Generate credentials at:
https://windscribe.com/getconfig/openvpn

# Verify credentials:
OPENVPN_USER: your_username  # NOT your email
OPENVPN_PASSWORD: your_openvpn_password  # NOT your account password
```

### Free Plan Bandwidth Exceeded

```bash
# Free plan has 10GB/month limit
# Check usage: https://windscribe.com/myaccount

# Solutions:
# 1. Upgrade to Pro (unlimited)
# 2. Use a different VPN for heavy torrenting
# 3. Reduce BATCH_SIZE in route23 config
```

### Connection Drops

```bash
# Try different server
SERVER_COUNTRIES: "Netherlands"

# Or use UDP instead of TCP
OPENVPN_PROTOCOL: udp  # (if Gluetun supports this flag)

# Check server status: https://windscribe.com/status
```

### Slow Speeds

```bash
# Use WireGuard (Pro only)
VPN_TYPE: wireguard

# Choose closer server
SERVER_CITIES: "Chicago"  # Pick nearest city

# Check server load at: https://windscribe.com/status
# Choose servers with < 50% load
```

### Server Not Found

```bash
# Windscribe uses creative server names internally
# Gluetun should handle this, but if issues occur:

# Use standard country names
SERVER_COUNTRIES: "United States"  # NOT "Burger Land"

# Or check valid server list
docker logs route23-vpn | grep -i available
```

## Advanced Configuration

### R.O.B.E.R.T (Ad/Malware Blocker)

Windscribe includes R.O.B.E.R.T, a DNS-level ad/malware blocker:

1. Configure at: https://windscribe.com/myaccount#robert
2. Enable blocking categories (ads, trackers, malware, etc.)
3. R.O.B.E.R.T automatically works with VPN connection

### Custom DNS

```yaml
# Use Windscribe DNS (includes R.O.B.E.R.T filtering)
DNS_ADDRESS: "10.255.255.1"  # Windscribe default

# Or disable and use custom DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### Split Tunneling (Not Available in Docker)

Split tunneling isn't supported in Gluetun/Docker, but you can:
- Route specific services through VPN (already done with Route 23)
- Access local network via `FIREWALL_OUTBOUND_SUBNETS`

### Double Hop (Not Available)

Windscribe offers double-hop in their desktop apps but not in OpenVPN configs.

## Windscribe Plans

### Free Plan
- 10GB/month
- 10+ server locations
- No port forwarding
- No WireGuard
- Limited for torrenting

### Pro Plan ($4.08/month if yearly)
- Unlimited data
- All 63+ countries
- Port forwarding (static)
- WireGuard support
- R.O.B.E.R.T ad blocker
- Unlimited device connections

## Performance Comparison

| Feature | Free | Pro |
|---------|------|-----|
| Bandwidth | 10GB/month | Unlimited |
| Locations | 10 countries | 63+ countries |
| Port Forwarding | | (static) |
| WireGuard | | |
| Speed | Throttled | Full speed |
| Torrenting | Limited | Recommended |

## Why Choose Windscribe?

**Free plan available** (10GB/month)
**R.O.B.E.R.T ad/malware blocker** (built-in)
**Port forwarding** (Pro, static)
**No logs policy**
**Unlimited connections** (Pro)
**Good speeds**
Free plan too limited for torrenting
Port forwarding is static (not dynamic)

## Common Use Cases

### For Light Seeding (Free Plan)
```yaml
# Small batch, careful with bandwidth
BATCH_SIZE: 3
ROTATION_DAYS: 30
# Monitor usage at: https://windscribe.com/myaccount
```

### For Heavy Seeding (Pro Plan)
```yaml
# Larger batch, use port forwarding
BATCH_SIZE: 20
ROTATION_DAYS: 14
# Configure port forwarding in Windscribe account
```

## References

- [Windscribe Account](https://windscribe.com/myaccount)
- [OpenVPN Config Generator](https://windscribe.com/getconfig/openvpn)
- [WireGuard Config Generator](https://windscribe.com/getconfig/wireguard)
- [Server Status](https://windscribe.com/status)
- [R.O.B.E.R.T Configuration](https://windscribe.com/myaccount#robert)
- [Gluetun Windscribe Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/windscribe.md)
