# VPN Unlimited (KeepSolid) Setup Guide

This guide explains how to configure Route 23 with VPN Unlimited (KeepSolid VPN Unlimited).

## Prerequisites

- Active VPN Unlimited subscription
- Account credentials
- Note: Offers lifetime subscriptions

## Getting Your Credentials

1. Sign up at: https://www.vpnunlimitedapp.com/
2. Log in to account
3. Generate manual configuration credentials
4. Find OpenVPN username and password

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=vpn unlimited
OPENVPN_USER=your_vpn_username
OPENVPN_PASSWORD=your_vpn_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: vpn unlimited
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

VPN Unlimited has 500+ servers in 80+ countries.

## Port Forwarding

**VPN Unlimited does NOT support port forwarding**

## Features

### Pros
Lifetime subscription available
10 simultaneous devices
Allows P2P
Dedicated IP option (paid)
Personal server option (paid)

### Cons
No port forwarding
Based in USA (5 Eyes)
Logs some connection data
Inconsistent speeds
Complicated addon pricing

## Troubleshooting

### Authentication Failed
- Use manual configuration credentials
- NOT your account email/password

## References

- [VPN Unlimited Website](https://www.vpnunlimitedapp.com/)
- [Gluetun VPN Unlimited Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/vpn-unlimited.md)

## Recommendation

**Not recommended for Route 23:**
- No port forwarding
- USA jurisdiction
- Logs some data
- Better alternatives available
