# Surfshark Setup Guide

This guide explains how to configure Route 23 with Surfshark VPN using WireGuard.

## Prerequisites

- Active Surfshark subscription
- Command line access

## Getting Your Credentials

### Method 1: Via Surfshark Manual Setup Page

1. Log in to your Surfshark account at: https://my.surfshark.com/
2. Navigate to **VPN** → **Manual setup**
3. Select the **WireGuard** tab
4. You'll see your credentials:
   - **Service credentials (username)** - Use this as your username
   - **Service credentials (password)** - Use this as your password
   - **Private key** - Your WireGuard private key
   - **Addresses** - Your WireGuard addresses

### Method 2: Generate via API

```bash
# Using your Surfshark service credentials
USERNAME="your_service_username"
PASSWORD="your_service_password"

# Get WireGuard private key
curl -s -u "$USERNAME:$PASSWORD" \
  "https://my.surfshark.com/vpn/api/v1/server/credentials"
```

## Configuration

Update your `.env` file:

```bash
# VPN Configuration
VPN_SERVICE=surfshark
WIREGUARD_PRIVATE_KEY=your_private_key_here
WIREGUARD_ADDRESSES=10.14.x.x/16

# Optional: Use specific region
# SERVER_REGIONS=us-den  # Denver, US
```

## Docker Compose Configuration

Update the `vpn` service in `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: surfshark
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Available Server Locations

Surfshark has servers in 100+ countries. Popular options for P2P:

**Americas:**
- `us-chi` - Chicago, US
- `us-den` - Denver, US
- `us-mia` - Miami, US
- `us-nyc` - New York, US
- `ca-tor` - Toronto, Canada
- `ca-van` - Vancouver, Canada

**Europe:**
- `nl-ams` - Amsterdam, Netherlands
- `ch-zur` - Zurich, Switzerland
- `de-fra` - Frankfurt, Germany
- `uk-lon` - London, UK

**Asia:**
- `sg-sng` - Singapore
- `jp-tok` - Tokyo, Japan

To use a specific region, add to `.env`:

```bash
SERVER_REGIONS=us-den
```

## Verification

Test your Surfshark connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify VPN IP
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check full connection info
docker exec route23-vpn wget -qO- https://ipinfo.io/json
```

## Troubleshooting

### Authentication Failed

- Verify you're using **service credentials**, not your Surfshark account email/password
- Service credentials are different from your login credentials
- Regenerate credentials from the manual setup page if needed

### Connection Drops

```bash
# Enable persistent keepalive
# Add to docker-compose.yaml vpn environment:
WIREGUARD_PERSISTENT_KEEPALIVE: 25
```

### No Internet Connection

- Verify `WIREGUARD_ADDRESSES` is correctly set
- Check if your subscription allows P2P on selected server
- Try a different server region

### DNS Issues

```bash
# Add custom DNS servers
# In docker-compose.yaml vpn environment:
DNS_ADDRESS: "1.1.1.1,1.0.0.1"
```

## Advanced Options

### Kill Switch

Gluetun includes a built-in kill switch. To configure:

```yaml
environment:
  FIREWALL_VPN_INPUT_PORTS: 6881  # Allow torrent port
  FIREWALL_INPUT_PORTS: 8080      # Allow ruTorrent web UI
```

### Multi-hop (Double VPN)

Surfshark supports multi-hop. To enable:

1. Get multi-hop server details from Surfshark
2. Configure in Gluetun with specific server hostname

### Port Forwarding

Note: Surfshark does not support port forwarding as of 2026. Consider using a VPN provider that supports port forwarding if this is critical for your seeding ratios.

## Security Notes

- WireGuard keys are tied to your account
- Never share your private key
- Regenerate keys if compromised
- Use service credentials, not account password

## References

- [Surfshark Manual Setup Guide](https://support.surfshark.com/hc/en-us/articles/360011051133-How-to-set-up-manual-WireGuard-connection)
- [Gluetun Surfshark Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/surfshark.md)
- [Surfshark P2P Servers](https://support.surfshark.com/hc/en-us/articles/360010927960-Which-Surfshark-servers-are-P2P-friendly)
