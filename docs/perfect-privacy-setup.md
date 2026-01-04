# Perfect Privacy Setup Guide

This guide explains how to configure Route 23 with Perfect Privacy VPN.

## Prerequisites

- Active Perfect Privacy subscription
- Account credentials
- Note: Premium privacy-focused VPN from Switzerland

## Getting Your Credentials

1. Sign up at: https://www.perfect-privacy.com/
2. Log in to your account dashboard
3. Find VPN credentials in account settings
4. Generate OpenVPN or WireGuard configuration

## Configuration

### OpenVPN Configuration

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=perfect privacy
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: perfect privacy
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "Switzerland"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

Perfect Privacy has servers in 25+ countries.

### Best Locations
- Switzerland (company HQ)
- Netherlands
- Sweden
- Iceland

## Port Forwarding

**Perfect Privacy supports port forwarding!**

Port forwarding is included with subscription and can be configured in the account dashboard.

## Features

### Pros
**Port forwarding included**
Switzerland-based (excellent privacy)
No logs policy
Unlimited bandwidth
Cascade/Multi-hop support
Own infrastructure
TrackStop (ad/tracker blocking)
**Unlimited simultaneous connections**

### Cons
**Very expensive** (~€13/month, ~$150/year)
Smaller server network
Complex for beginners
Outdated website/UX

## Unique Features

### NeuroRouting
Automatic routing optimization for best performance

### TrackStop
Built-in ad/tracker/malware blocking at DNS level

### Multi-Hop (Cascade)
Chain multiple VPN servers for extra privacy

## Troubleshooting

### Authentication Failed
- Verify credentials in account dashboard
- Ensure account is active

## References

- [Perfect Privacy Website](https://www.perfect-privacy.com/)
- [Perfect Privacy Features](https://www.perfect-privacy.com/en/features)
- [Gluetun Perfect Privacy Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/perfect-privacy.md)

## Recommendation

**Good for Route 23 if you value privacy AND torrenting:**

**Choose Perfect Privacy if:**
Port forwarding needed
Privacy is top priority
Budget is not a concern (~$13/month)
You want unlimited connections
Swiss jurisdiction important

**Choose alternatives if:**
Budget-conscious → PIA ($3/month with port forwarding)
Value-focused → ProtonVPN or Mullvad
More servers needed → PIA, NordVPN

Perfect Privacy is **excellent but expensive**. For most users, PIA or ProtonVPN offer better value with similar features.
