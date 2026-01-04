# FastestVPN Setup Guide

This guide explains how to configure Route 23 with FastestVPN.

## Prerequisites

- Active FastestVPN subscription
- FastestVPN account credentials
- Note: Budget VPN with basic features

## Getting Your Credentials

1. Sign up at: https://fastestvpn.com/
2. Log in to your account
3. Find your VPN credentials in account settings

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=fastestvpn
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: fastestvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

FastestVPN has 600+ servers in 50+ countries.

## Port Forwarding

**FastestVPN does NOT support port forwarding**

## Features

### Pros
Very affordable (lifetime deals)
Unlimited connections
P2P allowed
Basic features work

### Cons
No port forwarding
Slow speeds
Small server network
Limited features
Based in Cayman Islands

## Troubleshooting

### Slow Speeds
- FastestVPN is known for slower speeds
- Try different servers
- Consider upgrading to faster VPN

## References

- [FastestVPN Website](https://fastestvpn.com/)
- [Gluetun FastestVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/fastestvpn.md)

## Recommendation

**Not ideal for Route 23** due to:
- No port forwarding
- Slow speeds
- Limited features
- Better alternatives available at similar prices
