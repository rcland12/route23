# VPN.ac (VPN Secure) Setup Guide

This guide explains how to configure Route 23 with VPN.ac (also known as VPN Secure).

## Prerequisites

- Active VPN.ac subscription
- Account credentials
- Note: Privacy-focused VPN from Romania

## Getting Your Credentials

1. Sign up at: https://vpn.ac/
2. Log in to account dashboard
3. Find manual setup credentials
4. Get OpenVPN or WireGuard configuration

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=vpn secure
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: vpn secure
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Romania"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

VPN.ac has 100+ servers in 20+ countries.

### Best Locations
- Romania (company HQ)
- Netherlands
- Switzerland
- United States

## Port Forwarding

**VPN.ac does NOT support port forwarding**

## Features

### Pros
Romania-based (good privacy)
Strong encryption (AES-256)
No logs policy
Allows P2P
SecureProxy (double VPN)
6 simultaneous connections

### Cons
No port forwarding
Small server network
More expensive
Limited features
Not beginner-friendly

## Troubleshooting

### Authentication Failed
- Use manual config credentials from dashboard

## References

- [VPN.ac Website](https://vpn.ac/)
- [Gluetun VPN Secure Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/vpn-secure.md)

## Recommendation

**Not ideal for Route 23:**
- No port forwarding
- Limited server network
- Better alternatives: ProtonVPN, Mullvad
