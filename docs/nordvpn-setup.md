# NordVPN Setup Guide

This guide explains how to configure Route 23 with NordVPN using WireGuard.

## Prerequisites

- Active NordVPN subscription
- Command line access (bash/terminal)

## Getting Your Credentials

### 1. Get Your NordVPN Access Token

Visit the NordVPN account dashboard:

```bash
https://my.nordaccount.com/dashboard/nordvpn/
```

1. Log in to your NordVPN account
2. Navigate to **Services** → **NordVPN**
3. Scroll down to **Access Token** section
4. Click **Generate new token**
5. Copy the generated token (you'll only see it once!)

### 2. Get Your WireGuard Private Key

Use the access token to retrieve your WireGuard private key:

```bash
curl -s -u token:YOUR_ACCESS_TOKEN \
  "https://api.nordvpn.com/v1/users/services/credentials" | jq -r '.nordlynx_private_key'
```

Replace `YOUR_ACCESS_TOKEN` with the token from step 1.

**Alternative (without jq):**

```bash
curl -s -u token:YOUR_ACCESS_TOKEN \
  "https://api.nordvpn.com/v1/users/services/credentials"
```

Then manually copy the `nordlynx_private_key` value from the JSON response.

## Configuration

Add these values to your `.env` file:

```bash
# VPN Configuration
VPN_SERVICE=nordvpn
NORDVPN_TOKEN=your_access_token_here
WIREGUARD_PRIVATE_KEY=your_wireguard_private_key_here
```

## Advanced Configuration

### Server Selection

By default, Route 23 uses US P2P-optimized servers. You can customize this:

```yaml
# In docker-compose.yaml, modify the vpn service environment:
environment:
  SERVER_COUNTRIES: "United States"  # Change country
  SERVER_CATEGORIES: "P2P"           # Keep P2P for torrenting
```

**Available Countries:**
- United States
- United Kingdom
- Canada
- Germany
- Netherlands
- Switzerland
- etc. (check NordVPN website for full list)

### Server Regions

For specific regions:

```yaml
SERVER_REGIONS: "US East"  # Options: US East, US West, Europe, etc.
```

### Specific Server

Connect to a specific server:

```yaml
SERVER_HOSTNAMES: "us5678.nordvpn.com"
```

## Verification

After starting the VPN container, verify the connection:

```bash
# Check VPN container logs
docker logs route23-vpn

# Verify IP address (should show VPN exit IP)
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check connection status
docker exec route23-vpn wget -qO- https://ipinfo.io/json
```

## Troubleshooting

### Token Authentication Failed

```bash
# Verify your token is valid
curl -s -u token:YOUR_TOKEN \
  "https://api.nordvpn.com/v1/users/services/credentials"

# If invalid, generate a new token
```

### Connection Timeout

- Ensure WireGuard private key matches your token
- Try a different server country
- Check your firewall settings

### "No servers found" Error

- Verify `SERVER_COUNTRIES` and `SERVER_CATEGORIES` are valid
- Try removing category restriction temporarily
- Check NordVPN service status

## Token Security

- Never commit your token to version control
- Tokens don't expire but can be revoked
- Generate a new token if compromised
- Only one token can be active at a time (generating a new one revokes the old one)

## References

- [NordVPN API Documentation](https://nordvpn.com/api/)
- [Gluetun NordVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/nordvpn.md)
