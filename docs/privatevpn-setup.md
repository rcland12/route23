# PrivateVPN Setup Guide

This guide explains how to configure Route 23 with PrivateVPN.

## Prerequisites

- Active PrivateVPN subscription
- PrivateVPN account credentials
- Note: Small provider focused on privacy and streaming

## Getting Your Credentials

### Simple Credentials

PrivateVPN uses your account credentials:

1. Sign up at: https://privatevpn.com/
2. Your credentials are:
   - **Username:** Your account username/email
   - **Password:** Your account password

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=privatevpn
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: privatevpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Sweden"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

PrivateVPN has 200+ servers in 63+ countries.

### Best Locations
- Sweden (company HQ)
- Switzerland
- Netherlands
- United States

## Port Forwarding

**PrivateVPN does NOT support port forwarding**

## Features

### Pros
Sweden-based (good privacy)
No logs policy
Allows P2P
Unlimited bandwidth
10 connections

### Cons
No port forwarding
Small server network
Slower speeds
Limited Gluetun support

## Troubleshooting

### Authentication Failed
- Use account username/email and password
- Verify at: https://privatevpn.com/

## References

- [PrivateVPN Website](https://privatevpn.com/)
- [Gluetun PrivateVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/privatevpn.md)

## Recommendation

Not ideal for Route 23 due to:
- No port forwarding
- Limited server network
- Better alternatives available (PIA, ProtonVPN, Mullvad)
