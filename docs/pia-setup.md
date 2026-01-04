# Private Internet Access (PIA) Setup Guide

This guide explains how to configure Route 23 with Private Internet Access VPN.

## Prerequisites

- Active PIA subscription
- PIA supports both OpenVPN and WireGuard
- PIA has **native port forwarding support** (excellent for torrenting!)

## Getting Your Credentials

### 1. Get Your PIA Username and Password

1. Log in to your PIA account: https://www.privateinternetaccess.com/account
2. Your credentials are under **PPTP/L2TP/SOCKS Username** and **Password**
3. These are the same credentials used for OpenVPN and WireGuard

**Note:** These are NOT your PIA account email/password. They're separate VPN credentials shown in your account dashboard.

### 2. Find Your Credentials

On the account page:
- **Username:** Usually starts with `p` followed by numbers (e.g., `p1234567`)
- **Password:** Random alphanumeric string

## Configuration

### Method 1: OpenVPN (Most Compatible)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=private internet access
OPENVPN_USER=p1234567
OPENVPN_PASSWORD=your_password_here
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: private internet access
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_REGIONS: "US New York"  # Optional
    VPN_PORT_FORWARDING: on        # Enable port forwarding!
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### Method 2: WireGuard (Faster)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=private internet access
OPENVPN_USER=p1234567
OPENVPN_PASSWORD=your_password_here
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: private internet access
    VPN_TYPE: wireguard
    OPENVPN_USER: ${OPENVPN_USER}            # Yes, use these even for WireGuard
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_REGIONS: "US New York"
    VPN_PORT_FORWARDING: on
    VPN_PORT_FORWARDING_PROVIDER: private internet access
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

**Note:** PIA WireGuard still uses your OpenVPN username/password for authentication.

## Port Forwarding (Highly Recommended)

PIA is one of the few VPN providers with **native port forwarding** support, which significantly improves torrent seeding performance.

### Enable Port Forwarding

Already included in the configurations above:

```yaml
VPN_PORT_FORWARDING: on
VPN_PORT_FORWARDING_PROVIDER: private internet access
```

### Verify Forwarded Port

```bash
# Check Gluetun logs for assigned port
docker logs route23-vpn 2>&1 | grep -i "port forward"

# You should see something like:
# Port forwarded is 12345
```

### Use Forwarded Port in rTorrent

The forwarded port is automatically handled by Gluetun. To verify it's working:

```bash
# Check if port is open (from outside your network)
# Use a port checker like: https://canyouseeme.org/

# Or check rtorrent logs
docker logs route23-rutorrent | grep -i port
```

## Available Server Regions

PIA has servers worldwide. Popular regions for torrenting:

### United States
- `US Atlanta`
- `US California`
- `US Chicago`
- `US Denver`
- `US East`
- `US Florida`
- `US Houston`
- `US Las Vegas`
- `US New York`
- `US Seattle`
- `US Texas`
- `US Washington DC`
- `US West`

### Canada
- `CA Montreal`
- `CA Ontario`
- `CA Toronto`
- `CA Vancouver`

### Europe
- `Netherlands`
- `Switzerland`
- `Sweden`
- `Spain`
- `UK London`
- `UK Manchester`
- `UK Southampton`
- `DE Berlin`
- `DE Frankfurt`

### Asia-Pacific
- `AU Melbourne`
- `AU Perth`
- `AU Sydney`
- `Japan`
- `Singapore`
- `Hong Kong`

### Specify Region

```bash
# In .env file
SERVER_REGIONS=US East

# Or in docker-compose.yaml
environment:
  SERVER_REGIONS: "US East"
```

## Verification

Test your PIA connection:

```bash
# Check VPN connection
docker logs route23-vpn

# Verify IP address
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check full connection details
docker exec route23-vpn wget -qO- https://ipinfo.io/json

# Verify port forwarding is active
docker logs route23-vpn 2>&1 | grep "port forward"
```

## Troubleshooting

### Authentication Failed

```bash
# Common issues:
# 1. Using account email instead of VPN username
# 2. Copy-paste error in password

# Verify credentials at:
https://www.privateinternetaccess.com/account

# Try re-copying the credentials (avoid trailing spaces)
```

### Port Forwarding Not Working

```bash
# Ensure port forwarding is enabled
# Check logs:
docker logs route23-vpn 2>&1 | grep -i error

# Restart VPN container
docker restart route23-vpn

# Note: Port forwarding may take 30-60 seconds to activate
```

### Connection Drops

```bash
# Try a different region
SERVER_REGIONS: "US California"

# Or switch between OpenVPN and WireGuard
VPN_TYPE: openvpn  # or wireguard
```

### Slow Speeds

```bash
# Use WireGuard for better performance
VPN_TYPE: wireguard

# Or try a closer server region
SERVER_REGIONS: "US East"  # Choose nearest region
```

### "No servers found" Error

```bash
# Server region name might be incorrect
# Check valid regions at:
https://serverlist.piaservers.net/vpninfo/servers/v6

# Common format: "US East" not "US-East" or "us-east"
```

## Advanced Configuration

### Encryption Settings

PIA OpenVPN supports different encryption levels:

```yaml
# Strong encryption (default)
OPENVPN_CIPHER: aes-256-gcm

# Or use PIA's "next generation" network
# (automatically uses best encryption)
```

### DNS Configuration

PIA includes its own DNS servers:

```yaml
# Use PIA DNS (default)
DNS_ADDRESS: "209.222.18.222,209.222.18.218"

# Or use custom DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### Multi-Hop/Proxy

For additional privacy, you can chain PIA with a SOCKS5 proxy:

```yaml
HTTPPROXY: socks5://proxy:1080
HTTPPROXY_USER: your_proxy_user
HTTPPROXY_PASSWORD: your_proxy_pass
```

### Kill Switch

Built-in with Gluetun (no additional config needed):

```yaml
# Verify kill switch is active (default)
FIREWALL: on
```

## Performance Tuning for Torrenting

Recommended PIA settings for optimal torrenting:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: private internet access
    VPN_TYPE: wireguard              # Faster than OpenVPN
    VPN_PORT_FORWARDING: on          # Critical for seeding
    SERVER_REGIONS: "US East"        # Choose nearest region
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    FIREWALL_VPN_INPUT_PORTS: 6881   # Allow torrent port
```

## Why Choose PIA for Torrenting?

**Port forwarding support** (rare among VPNs)
**No logs policy** (court-proven)
**Fast WireGuard speeds**
**P2P allowed on all servers**
**Good value for price**
**Strong encryption**

## Comparison: OpenVPN vs WireGuard

| Feature | OpenVPN | WireGuard |
|---------|---------|-----------|
| Speed | ~100-200 Mbps | ~300-500 Mbps |
| CPU Usage | Higher | Lower |
| Setup | Standard | Same (PIA) |
| Stability | Very stable | Very stable |
| Recommended | Compatibility | Performance |

## References

- [PIA Account Dashboard](https://www.privateinternetaccess.com/account)
- [PIA Server List](https://serverlist.piaservers.net/vpninfo/servers/v6)
- [PIA Port Forwarding Guide](https://www.privateinternetaccess.com/helpdesk/kb/articles/how-do-i-enable-port-forwarding-on-my-vpn)
- [Gluetun PIA Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/private-internet-access.md)
