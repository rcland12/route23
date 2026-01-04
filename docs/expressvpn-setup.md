# ExpressVPN Setup Guide

This guide explains how to configure Route 23 with ExpressVPN.

## Prerequisites

- Active ExpressVPN subscription
- ExpressVPN account credentials

**Note:** ExpressVPN has limited support with Gluetun compared to other providers. Manual configuration may be required.

## Getting Your Credentials

### 1. Get Your ExpressVPN Activation Code

1. Log in to your ExpressVPN account: https://www.expressvpn.com/
2. Navigate to **Set Up Your Devices** or **My Account**
3. Click **Set Up Other Devices** → **Manual Config**
4. Select **OpenVPN** (or **Other OpenVPN**)
5. Copy your:
   - **Username** (starts with letters and numbers)
   - **Password** (long random string)

These credentials are specifically for manual OpenVPN configurations.

### 2. Download Server Config (Optional)

ExpressVPN doesn't provide direct WireGuard support for third-party configs. OpenVPN is the only option.

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=expressvpn
OPENVPN_USER=your_manual_config_username
OPENVPN_PASSWORD=your_manual_config_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: expressvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_REGIONS: "usa_-_new_york"  # See naming convention below
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Naming Convention

ExpressVPN uses specific naming in Gluetun. Use lowercase with underscores:

### Common Servers

**United States:**
- `usa_-_atlanta`
- `usa_-_chicago`
- `usa_-_dallas`
- `usa_-_denver`
- `usa_-_los_angeles`
- `usa_-_miami`
- `usa_-_new_jersey`
- `usa_-_new_york`
- `usa_-_santa_monica`
- `usa_-_san_francisco`
- `usa_-_seattle`
- `usa_-_washington_dc`

**Canada:**
- `canada_-_montreal`
- `canada_-_toronto`
- `canada_-_vancouver`

**Europe:**
- `netherlands_-_rotterdam`
- `netherlands_-_the_hague`
- `switzerland`
- `uk_-_london`
- `germany_-_frankfurt`

**Asia:**
- `singapore_-_marina_bay`
- `japan_-_tokyo`
- `hong_kong_-_1`

### Finding Server Names

```bash
# Start container and check logs for available servers
docker logs route23-vpn 2>&1 | grep -i "available servers"

# Or check Gluetun source:
# https://github.com/qdm12/gluetun/tree/master/internal/provider/expressvpn
```

## Server Selection

```yaml
# Specify region
environment:
  SERVER_REGIONS: "usa_-_los_angeles"

# Note: ExpressVPN in Gluetun may not support SERVER_COUNTRIES filtering
# Use SERVER_REGIONS instead
```

## Port Forwarding

**ExpressVPN does not support port forwarding.**

This is a significant limitation for torrenting, as you won't be able to:
- Accept incoming peer connections efficiently
- Maximize seeding ratios
- Achieve optimal upload speeds

**Alternatives with port forwarding:**
- Private Internet Access (PIA)
- ProtonVPN
- AirVPN

## Verification

Test your ExpressVPN connection:

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
# Verify you're using MANUAL CONFIG credentials
# NOT your ExpressVPN account email/password

# Get credentials at:
https://www.expressvpn.com/setup#manual

# Common mistake: Using account password instead of manual config password
```

### Server Not Found

```bash
# ExpressVPN server naming is strict
# Must use exact format: country_-_city

# Examples:
SERVER_REGIONS: "usa_-_new_york"      # Correct
SERVER_REGIONS: "US New York"         # Wrong
SERVER_REGIONS: "usa-new-york"        # Wrong
SERVER_REGIONS: "USA_-_NEW_YORK"      # Wrong (case sensitive)
```

### Connection Timeout

```bash
# Try different server region
SERVER_REGIONS: "usa_-_miami"

# Check ExpressVPN service status
# https://www.expressvpn.com/support/troubleshooting/vpn-server-status/
```

### Slow Connection

```bash
# ExpressVPN only supports OpenVPN with Gluetun (no WireGuard)
# OpenVPN is inherently slower than WireGuard

# Tips:
# 1. Choose geographically closer server
SERVER_REGIONS: "usa_-_seattle"  # Pick nearest

# 2. Try UDP protocol (may be faster)
# Check if Gluetun supports UDP flag for ExpressVPN
```

## Limitations

### No WireGuard Support

ExpressVPN uses proprietary "Lightway" protocol in their app, but it's not available for third-party tools like Gluetun.

**Result:**
- Stuck with OpenVPN (slower)
- Higher CPU usage
- Lower throughput

### No Port Forwarding

Major limitation for torrenting:
- Cannot accept incoming connections
- Lower seeding ratios
- Reduced upload performance

### Complex Server Naming

Requires exact region names with specific format.

## Why (or Why Not) Choose ExpressVPN?

### Pros
**Large server network** (3000+ servers, 94 countries)
**Fast speeds** (good for OpenVPN)
**Reliable connections**
**Good privacy policy**
**24/7 support**

### Cons (for Route 23)
**No port forwarding** (bad for seeding)
**No WireGuard** (stuck with slower OpenVPN)
**More expensive** than competitors
**Complex server naming** in Gluetun
**Limited Gluetun support**

## Recommended Alternative Setup

If you're committed to ExpressVPN:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: expressvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_REGIONS: "usa_-_los_angeles"
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    # Accept limitations:
    # - No port forwarding
    # - OpenVPN only (slower)
```

**For better torrenting performance, consider:**
- **PIA** - Has port forwarding, WireGuard, cheaper
- **ProtonVPN** - Has port forwarding, WireGuard, privacy-focused
- **Mullvad** - Fast WireGuard, privacy-focused (no port forwarding)

## Advanced Configuration

### DNS Settings

```yaml
# Use ExpressVPN DNS (default)
# ExpressVPN DNS is configured automatically

# Or use custom DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### Kill Switch

Built-in with Gluetun:

```yaml
FIREWALL: on  # Default, prevents non-VPN traffic
```

### Split Tunneling

Not directly supported, but local subnet access works:

```yaml
FIREWALL_OUTBOUND_SUBNETS: "192.168.0.0/24"  # Your LAN
```

## Configuration Example

Complete working example:

```yaml
# .env file
VPN_SERVICE=expressvpn
OPENVPN_USER=abc123defg456
OPENVPN_PASSWORD=hijklmnopqrstuvwxyz123456789
PRIVATE_SUBNET=192.168.1.0/24
TIMEZONE=America/New_York

# docker-compose.yaml
vpn:
  container_name: route23-vpn
  image: qmcgaw/gluetun:latest
  restart: unless-stopped
  environment:
    VPN_SERVICE_PROVIDER: expressvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_REGIONS: usa_-_new_york
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
  cap_add:
    - NET_ADMIN
  devices:
    - /dev/net/tun:/dev/net/tun
```

## References

- [ExpressVPN Manual Setup](https://www.expressvpn.com/setup#manual)
- [ExpressVPN Server Status](https://www.expressvpn.com/support/troubleshooting/vpn-server-status/)
- [Gluetun ExpressVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/expressvpn.md)

## Final Recommendation

**For Route 23 specifically:** ExpressVPN is not ideal due to lack of port forwarding. If you already have ExpressVPN, it will work, but expect:
- Lower seeding ratios
- Reduced peer connections
- Slower speeds (OpenVPN only)

Consider switching to PIA, ProtonVPN, or Mullvad for better torrenting performance.
