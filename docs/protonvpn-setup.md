# ProtonVPN Setup Guide

This guide explains how to configure Route 23 with ProtonVPN using WireGuard.

## Prerequisites

- Active ProtonVPN subscription (Plus, Unlimited, or Visionary for P2P)
- Note: Free and Basic plans do NOT support P2P/torrenting

## Getting Your Credentials

### 1. Generate WireGuard Configuration

1. Log in to your ProtonVPN account: https://account.protonvpn.com/
2. Navigate to **Downloads** → **WireGuard configuration**
3. Select:
   - **Platform:** Linux
   - **Protocol:** WireGuard
   - **Server:** Choose a P2P-enabled server (marked with P2P icon)
   - **NAT Type:** Moderate NAT (recommended for torrenting)
4. Click **Download** or **Create**

### 2. Extract Credentials from Config File

The downloaded `.conf` file contains your credentials. Extract them:

```bash
# View the config file
cat ProtonVPN_*.conf

# Extract private key
grep "PrivateKey" ProtonVPN_*.conf | cut -d'=' -f2 | tr -d ' '

# Extract addresses
grep "Address" ProtonVPN_*.conf | cut -d'=' -f2 | tr -d ' '

# Extract public key (peer)
grep "PublicKey" ProtonVPN_*.conf | cut -d'=' -f2 | tr -d ' '
```

## Configuration

### Option 1: Using OpenVPN Credentials (Simpler)

For OpenVPN/IKEv2 credentials:

1. Go to **Account** → **OpenVPN/IKEv2 username**
2. Copy your OpenVPN credentials

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=protonvpn
OPENVPN_USER=your_openvpn_username
OPENVPN_PASSWORD=your_openvpn_password

# Optional: Specify server
# SERVER_REGIONS=US-FREE#1
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: protonvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### Option 2: Using WireGuard (Better Performance)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=protonvpn
WIREGUARD_PRIVATE_KEY=your_private_key
WIREGUARD_ADDRESSES=10.2.0.2/32
WIREGUARD_PRESHARED_KEY=your_preshared_key  # Optional but recommended
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: protonvpn
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "Netherlands"  # P2P-friendly country
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## ProtonVPN P2P-Enabled Servers

Only **Plus, Unlimited, or Visionary** plans support P2P. Recommended countries:

**Best for P2P/Torrenting:**
-  Netherlands
-  Sweden
-  Iceland
-  Switzerland
-  Singapore

**Also Available:**
- Canada
- Spain
- Denmark
- Norway
- Hong Kong

### Specifying P2P Server

```yaml
# In docker-compose.yaml
environment:
  SERVER_COUNTRIES: Netherlands
  # Or use specific server:
  # FREE_ONLY: 'on'  # For free plan (no P2P support)
```

## Port Forwarding

ProtonVPN supports **port forwarding** (with specific config):

### Enable Port Forwarding

1. Download a config with NAT-PMP support
2. Add to docker-compose.yaml:

```yaml
environment:
  VPN_PORT_FORWARDING: on
  VPN_PORT_FORWARDING_PROVIDER: protonvpn
```

### Use Forwarded Port in rTorrent

The forwarded port will be exposed. Update your rTorrent config:

```bash
# Gluetun will handle port forwarding automatically
# Check logs for assigned port:
docker logs route23-vpn | grep "port forward"
```

## Verification

Test your ProtonVPN connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP (should show ProtonVPN server IP)
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check for DNS leaks
docker exec route23-vpn wget -qO- https://www.dnsleaktest.com

# Verify P2P is working
docker logs route23-rutorrent | grep -i peer
```

## Troubleshooting

### "P2P Not Allowed" Error

- Verify you have Plus, Unlimited, or Visionary plan
- Ensure you're connecting to a P2P-enabled server
- Check server list: https://protonvpn.com/support/p2p-vpn-redirection/

### Authentication Failed

```bash
# For OpenVPN: Verify your OpenVPN/IKEv2 credentials, NOT your account password
# Generate new credentials at: https://account.protonvpn.com/account

# For WireGuard: Re-download configuration file
```

### Connection Unstable

```bash
# Try a different server region
SERVER_COUNTRIES: "Switzerland"

# Or use OpenVPN instead of WireGuard
VPN_TYPE: openvpn
```

### DNS Issues

ProtonVPN uses its own DNS. To override:

```yaml
environment:
  DOT: off  # Disable DNS over TLS
  DNS_ADDRESS: "10.8.8.1"  # ProtonVPN DNS
```

### Port Forwarding Not Working

- Verify you downloaded config with NAT-PMP support
- Check if port forwarding is enabled on your plan
- Some servers don't support port forwarding - try different server

## Security Features

ProtonVPN includes:
- **Secure Core:** Multi-hop through privacy-friendly countries
- **NetShield:** Built-in ad/malware blocker
- **Kill Switch:** Automatic with Gluetun
- **No logs policy:** Independently audited

### Enable Secure Core

For maximum privacy (slower speeds):

1. Choose Secure Core servers in config download
2. Server names start with "SC" (e.g., SC-US#1)

```yaml
# Specify Secure Core server
SERVER_HOSTNAMES: "node-us-01.protonvpn.net"
```

## Comparison: OpenVPN vs WireGuard

| Feature | OpenVPN | WireGuard |
|---------|---------|-----------|
| Speed | Slower | Faster |
| Setup | Easier | More complex |
| Battery | Higher usage | More efficient |
| Compatibility | Better | Newer |
| Recommended | General use | Performance-critical |

## References

- [ProtonVPN WireGuard Setup](https://protonvpn.com/support/wireguard-configurations/)
- [ProtonVPN P2P Support](https://protonvpn.com/support/p2p-vpn-redirection/)
- [Gluetun ProtonVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/protonvpn.md)
- [ProtonVPN Port Forwarding](https://protonvpn.com/support/port-forwarding/)
