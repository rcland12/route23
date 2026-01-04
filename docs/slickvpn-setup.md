# SlickVPN Setup Guide

This guide explains how to configure Route 23 with SlickVPN.

## Prerequisites

- Active SlickVPN subscription
- Account credentials
- Note: Small provider based in USA

## Getting Your Credentials

1. Sign up at: https://www.slickvpn.com/
2. Log in to account
3. Find manual configuration credentials
4. Get OpenVPN username and password

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=slickvpn
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: slickvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

SlickVPN has 150+ servers in 45+ countries.

## Port Forwarding

**SlickVPN does NOT support port forwarding**

## Features

### Pros
Allows P2P
No bandwidth limits
Hydra protocol (proprietary)
5 simultaneous connections

### Cons
No port forwarding
Based in USA (5 Eyes)
Small server network
Limited features
Lesser-known provider

## Troubleshooting

### Authentication Failed
- Use manual config credentials, not account login

## References

- [SlickVPN Website](https://www.slickvpn.com/)
- [Gluetun SlickVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/slickvpn.md)

## Recommendation

**Not recommended for Route 23:**
- No port forwarding
- USA-based (5 Eyes)
- Limited features
- Better alternatives widely available
