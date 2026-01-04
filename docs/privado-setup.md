# Privado VPN Setup Guide

This guide explains how to configure Route 23 with Privado VPN.

## Prerequisites

- Active Privado VPN subscription (Free or Premium)
- Privado account
- Note: Free plan available with limitations

## Getting Your Credentials

1. Sign up at: https://privadovpn.com/
2. Log in to account dashboard
3. Navigate to manual setup section
4. Get OpenVPN or WireGuard credentials

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=privado
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: privado
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Switzerland"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

Privado has servers in 45+ countries.

**Free Plan:** 13 server locations
**Premium:** All 45+ locations

## Port Forwarding

**Privado does NOT support port forwarding**

## Plans

### Free Plan
- 10GB/month data
- 13 server locations
- 1 device
- Standard speed

### Premium Plan
- Unlimited data
- 45+ locations
- 10 devices
- Unlimited speed

## Features

### Pros
Free plan available (10GB/month)
Zero logs policy
Switzerland-based
Allows P2P
Affordable premium ($2-3/month)

### Cons
No port forwarding
Free plan very limited (10GB)
Smaller server network
Lesser-known provider

## Troubleshooting

### Free Plan Data Limit
- 10GB/month is insufficient for torrenting
- Upgrade to Premium for unlimited

## References

- [Privado VPN Website](https://privadovpn.com/)
- [Gluetun Privado Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/privado.md)

## Recommendation

**Not ideal for Route 23:**
- No port forwarding
- Free plan too limited
- Better alternatives: PIA, ProtonVPN, Mullvad
