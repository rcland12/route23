# Mullvad VPN Setup Guide

This guide explains how to configure Route 23 with Mullvad VPN.

## Prerequisites

- Active Mullvad subscription
- Mullvad account number (16-digit number, no username/email)
- Mullvad supports WireGuard (recommended) and OpenVPN

## Getting Your Credentials

### 1. Account Number

When you sign up for Mullvad, you receive a **16-digit account number** (e.g., `1234567890123456`). This is your only identifier - no email or username.

Find it at: https://mullvad.net/account/

### 2. Generate WireGuard Key

#### Method 1: Via Mullvad Website (Easiest)

1. Go to https://mullvad.net/account/
2. Log in with your 16-digit account number
3. Navigate to **WireGuard configuration**
4. Click **Manage keys** or **Generate key**
5. Copy the generated private key
6. Note the public key (automatically created)

#### Method 2: Using Mullvad API

```bash
# Generate a new WireGuard key pair locally
wg genkey | tee privatekey | wg pubkey > publickey

# Read your private key
PRIVATE_KEY=$(cat privatekey)

# Read your public key
PUBLIC_KEY=$(cat publickey)

# Upload public key to Mullvad
curl -X POST https://api.mullvad.net/wg/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_ACCOUNT_NUMBER" \
  -d "{\"pubkey\":\"$PUBLIC_KEY\"}"

# Save your private key for .env
echo $PRIVATE_KEY
```

#### Method 3: Via Mullvad App (Then Extract)

1. Install Mullvad app on your computer
2. Generate WireGuard key in app
3. Go to https://mullvad.net/account/
4. View your keys under **WireGuard configuration**
5. Copy the private key

## Configuration

### WireGuard Configuration (Recommended)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=mullvad
WIREGUARD_PRIVATE_KEY=your_private_key_here
WIREGUARD_ADDRESSES=10.64.0.1/32  # Mullvad assigns this
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: mullvad
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"  # Optional
    SERVER_CITIES: "New York NY"       # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### OpenVPN Configuration (Alternative)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=mullvad
OPENVPN_USER=your_16_digit_account_number
OPENVPN_PASSWORD=m  # Mullvad uses 'm' as password for OpenVPN
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: mullvad
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "USA"
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Selection

Mullvad has servers in 45+ countries. Choose wisely for torrenting:

### Best Countries for P2P

All Mullvad servers allow P2P, but these are recommended:

**Americas:**
- `USA` - Multiple cities
- `Canada` - Montreal, Toronto, Vancouver

**Europe:**
- `Sweden` - Gothenburg, Malmö, Stockholm
- `Netherlands` - Amsterdam
- `Switzerland` - Zurich
- `Germany` - Berlin, Frankfurt

**Asia-Pacific:**
- `Singapore`
- `Australia` - Melbourne, Sydney
- `Japan` - Tokyo

### Specify Location

```bash
# By country
SERVER_COUNTRIES=USA

# By city (more specific)
SERVER_CITIES=New York NY

# By specific server
SERVER_HOSTNAMES=us-nyc-wg-001.mullvad.net
```

### Available Cities

View all servers: https://mullvad.net/servers/

**US Cities:**
- `Atlanta GA`
- `Chicago IL`
- `Dallas TX`
- `Denver CO`
- `Los Angeles CA`
- `Miami FL`
- `New York NY`
- `Phoenix AZ`
- `Seattle WA`

## Port Forwarding

**Important:** Mullvad **discontinued port forwarding** in May 2023 for security reasons.

If you need port forwarding for better seeding ratios, consider:
- Private Internet Access (PIA)
- ProtonVPN
- AirVPN

Mullvad still works great for torrenting, but without port forwarding you may see:
- Slower connection to peers
- Lower upload speeds
- Potentially lower seeding ratios

## Verification

Test your Mullvad connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP (should show Mullvad exit IP)
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check with Mullvad's own tool
docker exec route23-vpn curl https://am.i.mullvad.net/json

# Expected response:
# {"ip":"xxx.xxx.xxx.xxx","country":"USA","city":"New York","mullvad_exit_ip":true,...}
```

## Troubleshooting

### Authentication Failed

```bash
# For WireGuard: Verify your private key
# Check https://mullvad.net/account/ → WireGuard configuration

# For OpenVPN: Ensure password is 'm' (lowercase)
OPENVPN_PASSWORD=m

# Verify account number (16 digits)
```

### Key Not Found / Invalid Key

```bash
# Generate a new WireGuard key
# Go to: https://mullvad.net/account/
# Click "Manage keys" → "Generate key"
# Replace old key in .env
```

### Connection Timeout

```bash
# Try different server
SERVER_CITIES: "Los Angeles CA"

# Or different country
SERVER_COUNTRIES: "Netherlands"

# Or specific server
SERVER_HOSTNAMES: "us-nyc-wg-301.mullvad.net"
```

### Slow Speeds

```bash
# Use WireGuard (not OpenVPN)
VPN_TYPE: wireguard

# Choose geographically closer server
SERVER_CITIES: "Your nearest city"

# Check server load: https://mullvad.net/servers/
# Green = low load, Yellow = medium, Red = high
```

### DNS Leaks

Mullvad uses its own DNS:

```yaml
# Verify DNS settings (should be set by default)
DNS_ADDRESS: "10.64.0.1"

# Or use Mullvad's DNS
DNS_ADDRESS: "193.138.218.74"
```

## Advanced Configuration

### Custom DNS

```yaml
# Use Mullvad DNS (blocks ads/trackers)
DNS_ADDRESS: "100.64.0.7"  # Mullvad DNS with ad-blocking

# Or use external DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### IPv6 Support

Mullvad fully supports IPv6:

```yaml
# Enable IPv6
WIREGUARD_ADDRESSES: "10.64.0.1/32,fc00:bbbb:bbbb:bb01::1/128"
```

### Multi-Hop (Bridge Mode)

For maximum privacy, use Mullvad's bridge servers:

```yaml
# Connect through Sweden, exit from USA
SERVER_HOSTNAMES: "se-sto-wg-001.mullvad.net"
# Then configure bridge routing (advanced)
```

### Kill Switch

Built-in with Gluetun:

```yaml
# Verify firewall enabled (default)
FIREWALL: on

# Block non-VPN traffic
FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
```

## Mullvad Features

### Privacy-Focused
- **No account info required** (just account number)
- **Cash/cryptocurrency accepted**
- **No logs policy** (independently audited)
- **Open source apps**
- **Diskless infrastructure**

### Security
- **WireGuard** (modern, fast protocol)
- **AES-256 encryption** (OpenVPN)
- **Own DNS servers** (no leaks)
- **Kill switch** (automatic)

### Limitations
- **No port forwarding** (removed May 2023)
- **No dedicated IP** (not needed for most users)

## Performance: WireGuard vs OpenVPN

| Feature | WireGuard | OpenVPN |
|---------|-----------|---------|
| Speed |  Very fast | Slower |
| CPU Usage | Low | Higher |
| Encryption | ChaCha20 | AES-256 |
| Battery | Efficient | Less efficient |
| Recommended | Yes | Compatibility |

## Mullvad Account Management

```bash
# Check account expiry
curl -X GET https://api.mullvad.net/accounts/v1/YOUR_ACCOUNT_NUMBER

# Add time (30 days)
# Do this via website: https://mullvad.net/account/

# List your WireGuard keys
curl https://api.mullvad.net/accounts/v1/YOUR_ACCOUNT_NUMBER/wireguard-keys
```

## Why Choose Mullvad?

**Best privacy practices** (no personal info)
**Fast WireGuard speeds**
**All servers support P2P**
**No logs policy** (audited)
**Fixed price** (€5/month, no tiers)
**Anonymous payment** (cash/crypto)
**No port forwarding** (major limitation for seeding)

## References

- [Mullvad Account](https://mullvad.net/account/)
- [Mullvad Server List](https://mullvad.net/servers/)
- [Mullvad API Documentation](https://mullvad.net/en/help/api/)
- [Gluetun Mullvad Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/mullvad.md)
- [Mullvad Port Forwarding Announcement](https://mullvad.net/en/blog/2023/5/29/removing-the-support-for-forwarded-ports/)
