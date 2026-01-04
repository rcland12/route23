# PureVPN Setup Guide

This guide explains how to configure Route 23 with PureVPN.

## Prerequisites

- Active PureVPN subscription
- PureVPN account credentials
- Note: PureVPN supports port forwarding (addon required)

## Getting Your Credentials

### Get VPN Username and Password

PureVPN uses separate VPN credentials:

1. Log in to: https://my.purevpn.com/
2. Navigate to **VPN Login Details** or **Services**
3. Find your:
   - **VPN Username** (starts with "pv" or similar)
   - **VPN Password** (different from account password)
4. These are your OpenVPN/manual configuration credentials

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=purevpn
OPENVPN_USER=your_vpn_username
OPENVPN_PASSWORD=your_vpn_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: purevpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### WireGuard Configuration

If WireGuard is available:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: purevpn
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"
```

## Server Locations

PureVPN has 6500+ servers in 78+ countries.

### Best for P2P/Torrenting

**Americas:**
- United States - Multiple cities
- Canada - Toronto, Montreal
- Mexico

**Europe:**
- Netherlands - Amsterdam
- Switzerland - Zurich
- Sweden - Stockholm
- Romania - Bucharest

**Asia-Pacific:**
- Singapore
- Hong Kong
- Japan - Tokyo

### Server Selection

```bash
SERVER_COUNTRIES: "Netherlands"
# or
SERVER_CITIES: "Amsterdam"
```

## Port Forwarding

**PureVPN supports port forwarding as a paid addon**

### Purchase Port Forwarding

1. Log in to: https://my.purevpn.com/
2. Navigate to **Addons** or **Port Forwarding**
3. Purchase the port forwarding addon
4. Configure forwarded ports in your account
5. Use assigned ports in rTorrent config

**Cost:** Additional ~$1-3/month

## Verification

```bash
docker logs route23-vpn
docker exec route23-vpn wget -qO- https://ipinfo.io/ip
```

## PureVPN Features

### Pros
Large server network (6500+ servers)
Port forwarding available (addon)
Dedicated IP option
Split tunneling
10 simultaneous connections
Affordable pricing

### Cons
Port forwarding costs extra
Based in Hong Kong (jurisdiction concerns)
Past logging controversy (resolved)
Inconsistent speeds

## Troubleshooting

### Authentication Failed
- Use VPN credentials, not account email/password
- Find credentials at: https://my.purevpn.com/

### Slow Speeds
- Choose closer server
- Try WireGuard if available

## References

- [PureVPN Account](https://my.purevpn.com/)
- [PureVPN Server List](https://www.purevpn.com/servers)
- [Gluetun PureVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/purevpn.md)

## Recommendation

PureVPN works for Route 23 but isn't ideal due to:
- Extra cost for port forwarding
- Past privacy concerns
- Better alternatives available (PIA, ProtonVPN)
