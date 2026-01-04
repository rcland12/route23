# HideMyAss (HMA) VPN Setup Guide

This guide explains how to configure Route 23 with HideMyAss VPN.

## Prerequisites

- Active HMA VPN subscription
- HMA account credentials
- Note: HMA is now owned by Avast

## Getting Your Credentials

### Account Credentials

HMA uses your account credentials:

1. Sign up at: https://www.hidemyass.com/
2. Your credentials are:
   - **Username:** Your email or username
   - **Password:** Your account password

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=hidemyass
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: hidemyass
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

HMA has 1100+ servers in 210+ countries (largest coverage).

### Server Selection

```bash
SERVER_COUNTRIES: "Netherlands"
# or
SERVER_COUNTRIES: "Switzerland"
```

## Port Forwarding

**HMA does NOT support port forwarding**

## Features

### Pros
Largest country coverage (210+)
Allows P2P on some servers
10 simultaneous connections
Good speeds

### Cons
No port forwarding
Based in UK (5 Eyes)
Owned by Avast (privacy concerns)
Keeps connection logs
Not recommended for privacy

## Troubleshooting

### Authentication Failed
- Use account email/username and password
- Verify at: https://www.hidemyass.com/

### P2P Not Allowed
- Not all HMA servers support P2P
- Choose P2P-friendly locations (Netherlands, Switzerland)

## References

- [HideMyAss Website](https://www.hidemyass.com/)
- [Gluetun HMA Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/hidemyass.md)

## Recommendation

**NOT recommended for Route 23** due to:
- No port forwarding
- Logs connection data
- UK jurisdiction (5 Eyes)
- Owned by Avast (questionable privacy)
- Better alternatives: PIA, ProtonVPN, Mullvad
