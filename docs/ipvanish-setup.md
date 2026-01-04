# IPVanish VPN Setup Guide

This guide explains how to configure Route 23 with IPVanish VPN.

## Prerequisites

- Active IPVanish subscription
- IPVanish account credentials
- Note: IPVanish allows unlimited P2P/torrenting on all servers

## Getting Your Credentials

### Simple Setup

IPVanish uses your account credentials directly for VPN connections:

1. Your **email address** = OpenVPN username
2. Your **account password** = OpenVPN password

**That's it!** No need to generate separate VPN credentials.

### Alternative: SOCKS5 Proxy

IPVanish also offers SOCKS5 proxy (faster, but less secure):
- Not recommended for Route 23 (use full VPN instead)

## Configuration

### OpenVPN Configuration (Standard)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=ipvanish
OPENVPN_USER=your_email@example.com
OPENVPN_PASSWORD=your_account_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ipvanish
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    SERVER_CITIES: "New York"          # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### WireGuard Configuration

**Note:** IPVanish WireGuard support through Gluetun may be limited. OpenVPN is recommended.

If WireGuard is available:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ipvanish
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    # ... additional WireGuard config
```

## Server Selection

IPVanish has 2000+ servers in 75+ locations worldwide. All servers support P2P.

### Popular Server Locations

**United States (Best Coverage):**
- Atlanta
- Boston
- Chicago
- Dallas
- Denver
- Las Vegas
- Los Angeles
- Miami
- New York
- Phoenix
- San Jose
- Seattle
- Washington DC

**Canada:**
- Montreal
- Toronto
- Vancouver

**Europe:**
- Amsterdam, Netherlands
- Frankfurt, Germany
- London, United Kingdom
- Paris, France
- Stockholm, Sweden
- Zurich, Switzerland

**Asia-Pacific:**
- Singapore
- Tokyo, Japan
- Sydney, Australia
- Hong Kong

### Specify Server Location

```bash
# By country
SERVER_COUNTRIES: "United States"

# By city (more specific)
SERVER_CITIES: "Chicago"

# By region/city
SERVER_REGIONS: "Chicago"
```

## Port Forwarding

**IPVanish does NOT support port forwarding.**

This limitation affects torrenting:
- Cannot accept incoming peer connections
- Lower seeding ratios
- Reduced upload speeds

**Alternatives with port forwarding:**
- Private Internet Access (PIA)
- ProtonVPN
- AirVPN

## Verification

Test your IPVanish connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP (should show IPVanish server IP)
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check connection details
docker exec route23-vpn wget -qO- https://ipinfo.io/json

# Verify location
docker logs route23-vpn 2>&1 | grep -i "connected"
```

## Troubleshooting

### Authentication Failed

```bash
# Common issues:
# 1. Typo in email/password
# 2. Account suspended/expired

# Verify credentials:
# Email: your_email@example.com (must be exact)
# Password: your IPVanish account password

# Check account status at: https://www.ipvanish.com/account/
```

### Connection Timeout

```bash
# Try different server location
SERVER_CITIES: "Los Angeles"

# Or different country
SERVER_COUNTRIES: "Netherlands"

# Check IPVanish status: https://support.ipvanish.com/hc/en-us/articles/360001336313
```

### "Server not found" Error

```bash
# IPVanish server naming can be specific
# Try using country only first:
SERVER_COUNTRIES: "United States"

# Then add city if needed:
SERVER_CITIES: "New York"

# Check valid servers in Gluetun logs:
docker logs route23-vpn 2>&1 | grep -i "available servers"
```

### Slow Speeds

```bash
# Choose geographically closer server
SERVER_CITIES: "Seattle"  # Pick nearest city

# IPVanish OpenVPN may be slower than competitors
# This is inherent to IPVanish's network

# Try enabling fast connect (if supported)
# Or choose less congested servers
```

### Frequent Disconnections

```bash
# Enable persistent connection settings
# Add to docker-compose.yaml if supported:

environment:
  OPENVPN_PROTOCOL: udp  # UDP may be more stable
  # or try TCP:
  OPENVPN_PROTOCOL: tcp
```

## Advanced Configuration

### Optimized Settings for Torrenting

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ipvanish
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Netherlands"  # Good for P2P
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    FIREWALL_VPN_INPUT_PORTS: 6881   # Allow torrent port
    TZ: ${TIMEZONE}
```

### DNS Configuration

```yaml
# Use IPVanish DNS (default)
# Automatically configured

# Or use custom DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### Kill Switch

Built-in with Gluetun:

```yaml
FIREWALL: on  # Default, blocks non-VPN traffic
```

### Protocol Selection

```yaml
# Try UDP for better performance
OPENVPN_PROTOCOL: udp

# Or TCP for more reliability
OPENVPN_PROTOCOL: tcp
```

## IPVanish Features

### Pros
**All servers support P2P** (no restrictions)
**Unlimited connections** (use on unlimited devices)
**Good server coverage** (75+ locations)
**No logs policy** (audited)
**24/7 support**
**Simple setup** (use account credentials)
**Owned infrastructure** (no third-party servers)

### Cons
**No port forwarding** (limits seeding efficiency)
**Based in USA** (5 Eyes jurisdiction)
**Slower than competitors** (in some tests)
**No WireGuard** (OpenVPN only with most setups)
**Mixed privacy reputation** (past cooperation with authorities)

## Performance Considerations

### Expected Speeds

With OpenVPN:
- **Download:** 100-300 Mbps (depending on server/location)
- **Upload:** 50-150 Mbps
- **Latency:** +20-50ms

### Server Load

IPVanish displays server load on their website:
- https://www.ipvanish.com/server-locations/

Choose servers with < 50% load for best performance.

## Privacy & Security

### Logging Policy
- **No logs** of activity, connection timestamps, or traffic
- Independently audited (2022)

### Jurisdiction
- **Based in USA** (5 Eyes country)
- Past controversy: Cooperated with authorities in 2016 (before "no logs" policy)
- Current policy: No logs to hand over

### Encryption
- **OpenVPN:** AES-256 encryption
- **Protocols:** OpenVPN (UDP/TCP), IKEv2, WireGuard (in app only)

## Configuration Examples

### Basic Setup (USA)

```yaml
# .env
VPN_SERVICE=ipvanish
OPENVPN_USER=your_email@example.com
OPENVPN_PASSWORD=your_password
PRIVATE_SUBNET=192.168.1.0/24

# docker-compose.yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ipvanish
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"
```

### Privacy-Focused (Europe)

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ipvanish
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Switzerland"  # Privacy-friendly
```

### Best Performance

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ipvanish
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_CITIES: "New York"  # Pick nearest major city
    OPENVPN_PROTOCOL: udp      # Faster than TCP
```

## Why Choose IPVanish?

### Good For
**Unlimited connections** (great if you have many devices)
**Simple setup** (just use account credentials)
**All servers support P2P** (no restrictions)
**Good for casual torrenting**

### Not Ideal For
**Maximum seeding ratios** (no port forwarding)
**Privacy purists** (USA jurisdiction)
**Speed-focused users** (slower than some competitors)
**Advanced features** (limited compared to competitors)

## Comparison with Other VPNs

| Feature | IPVanish | PIA | Mullvad | NordVPN |
|---------|----------|-----|---------|---------|
| Port Forwarding | | | | |
| WireGuard | Limited | | | |
| Unlimited Devices | | (10) | (5) | (6) |
| Price | $$ | $ | $ | $$ |
| Torrenting | Good | Excellent | Good | Good |

## Recommendations

### Use IPVanish If:
- You need **unlimited simultaneous connections**
- You want **simple setup** (no extra credential generation)
- You're okay with **no port forwarding**
- You don't mind **USA jurisdiction**

### Consider Alternatives If:
- You need **port forwarding** → Use PIA or ProtonVPN
- You want **fastest speeds** → Use Mullvad or NordVPN
- You want **maximum privacy** → Use Mullvad
- You're **privacy-focused** → Avoid 5 Eyes countries

## References

- [IPVanish Account](https://www.ipvanish.com/account/)
- [IPVanish Server List](https://www.ipvanish.com/servers/)
- [IPVanish Server Status](https://support.ipvanish.com/hc/en-us/articles/360001336313)
- [Gluetun IPVanish Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/ipvanish.md)
- [IPVanish Privacy Policy](https://www.ipvanish.com/privacy-policy/)
