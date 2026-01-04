# IVPN Setup Guide

This guide explains how to configure Route 23 with IVPN.

## Prerequisites

- Active IVPN subscription (Standard or Pro)
- IVPN account ID
- **Note:** IVPN is extremely privacy-focused but lacks port forwarding

## Getting Your Credentials

### 1. Get Your Account ID

IVPN uses account IDs instead of usernames:

1. Sign up at: https://www.ivpn.net/
2. You'll receive an **account ID** (format: `ivpnXXXXXXXX` or `i-XXXX-XXXX-XXXX`)
3. This account ID is your only identifier - no email required

### 2. Generate WireGuard Configuration

1. Log in to IVPN account: https://www.ivpn.net/account/
2. Navigate to **WireGuard**
3. Click **Generate Keys** or **Add Device**
4. Download the WireGuard configuration file
5. Extract:
   - **Private Key**
   - **IP Address** (your WireGuard address)

### Alternative: OpenVPN Setup

1. Go to: https://www.ivpn.net/account/
2. Navigate to **OpenVPN**
3. Your credentials are simply:
   - Username: Your account ID
   - Password: Generated from account page

## Configuration

### Method 1: WireGuard (Recommended)

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=ivpn
WIREGUARD_PRIVATE_KEY=your_private_key_here
WIREGUARD_ADDRESSES=your_wireguard_ip/32
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ivpn
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "United States"  # Optional
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### Method 2: OpenVPN

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=ivpn
OPENVPN_USER=ivpnXXXXXXXX  # Your account ID
OPENVPN_PASSWORD=your_generated_password
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ivpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_COUNTRIES: "United States"
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Locations

IVPN has servers in 35+ countries.

### Best for P2P/Torrenting

**Europe (Privacy-Friendly):**
-  Switzerland - Zurich
-  Sweden - Stockholm
-  Netherlands - Amsterdam
-  Iceland - Reykjavik
-  Romania - Bucharest

**Americas:**
-  United States - Multiple cities
-  Canada - Montreal, Toronto, Vancouver

**Asia-Pacific:**
-  Singapore
-  Australia - Melbourne, Sydney

### Specify Server

```bash
# By country
SERVER_COUNTRIES: "Switzerland"

# By city
SERVER_CITIES: "Zurich"

# Specific server (find in IVPN server list)
SERVER_HOSTNAMES: "ch1.gw.ivpn.net"
```

## Port Forwarding

**IVPN does NOT support port forwarding.**

IVPN explicitly removed port forwarding for security reasons (similar to Mullvad).

**Impact on Torrenting:**
- Cannot accept incoming connections
- Lower seeding ratios
- Reduced peer availability
- Still works, but less efficiently

**Alternatives with port forwarding:**
- Private Internet Access (PIA)
- ProtonVPN
- AirVPN

## Multi-Hop (Double VPN)

**IVPN supports Multi-Hop** for extra privacy!

Multi-hop routes your traffic through two VPN servers for additional anonymity.

### Enable Multi-Hop

Multi-hop is configured server-side in IVPN. When generating configs:

1. Log in to: https://www.ivpn.net/account/
2. Select **Multi-Hop** configuration
3. Choose entry and exit servers
4. Download config with multi-hop enabled

```yaml
# In docker-compose.yaml, specify multi-hop server
SERVER_HOSTNAMES: "gb-lon.gw.ivpn.net"  # Entry server
# Exit server is configured in your WireGuard key
```

## Verification

Test your IVPN connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check connection details
docker exec route23-vpn wget -qO- https://ipinfo.io/json

# IVPN connection check
docker exec route23-vpn curl https://api.ivpn.net/v4/geo-lookup
```

## Troubleshooting

### Authentication Failed

```bash
# For WireGuard: Verify private key is correct
# Regenerate at: https://www.ivpn.net/account/

# For OpenVPN: Ensure using account ID, not email
OPENVPN_USER: ivpnXXXXXXXX  # Format: ivpn followed by characters
```

### Connection Timeout

```bash
# Try different server
SERVER_COUNTRIES: "Netherlands"

# Or specific server
SERVER_HOSTNAMES: "nl1.gw.ivpn.net"

# Check IVPN server status: https://www.ivpn.net/status/
```

### Slow Speeds

```bash
# Use WireGuard (not OpenVPN)
VPN_TYPE: wireguard

# Choose geographically closer server
SERVER_COUNTRIES: "United States"

# Avoid multi-hop if speed is priority
```

### Device Limit Exceeded

```bash
# IVPN Standard: 2 devices
# IVPN Pro: 7 devices

# Remove old devices at: https://www.ivpn.net/account/
# Under WireGuard or OpenVPN device management
```

## IVPN Features

### Pros
**Extreme privacy** (no email required, anonymous accounts)
**No logs policy** (independently audited)
**Multi-hop support** (double VPN)
**WireGuard support**
**AntiTracker** (built-in ad/tracker blocking)
**Open source apps**
**Accept Bitcoin/Monero** (anonymous payment)
**Transparent** (publishes transparency reports)
**Based in Gibraltar** (privacy-friendly)

### Cons
**No port forwarding** (bad for seeding ratios)
**Expensive** ($6-10/month)
**Limited device connections** (2 on Standard, 7 on Pro)
**Smaller server network** (~100 servers)

## Plans Comparison

| Feature | Standard | Pro |
|---------|----------|-----|
| Price | $6/month | $10/month |
| Devices | 2 | 7 |
| Multi-Hop | | |
| Port Forwarding | | |
| All Servers | | |

**For Route 23:** Standard is sufficient unless you need multi-hop or more devices.

## Privacy & Security

IVPN is one of the most privacy-focused VPNs:

- **No personal info required** (not even email)
- **Anonymous account IDs** only
- **Cash/crypto payments** accepted
- **No logs** (audited by Cure53, 2020)
- **Open source** (clients and apps)
- **Regular security audits**
- **Warrant canary** (transparency)
- **Based in Gibraltar** (outside 5/9/14 Eyes)

## AntiTracker Feature

IVPN includes AntiTracker, a DNS-level blocking feature:

### Enable AntiTracker

Configure when generating WireGuard/OpenVPN config:

1. Go to: https://www.ivpn.net/account/
2. Select **AntiTracker** option when generating config
3. Choose level:
   - **Standard:** Blocks ads and trackers
   - **Hardcore:** Blocks ads, trackers, and more

```yaml
# AntiTracker is configured in your WireGuard key/config
# No additional Gluetun configuration needed
```

## Advanced Configuration

### Custom DNS

```yaml
# Use IVPN DNS (with AntiTracker)
# Automatically configured based on your account settings

# Or use custom DNS
DNS_ADDRESS: "1.1.1.1,1.0.0.1"  # Cloudflare
```

### Multi-Hop Configuration

```yaml
# Multi-hop requires Pro plan and specific server selection
# Configure during WireGuard key generation
# Entry and exit servers are embedded in the config
```

### IPv6 Support

```yaml
# IVPN supports IPv6
WIREGUARD_ADDRESSES: "10.x.x.x/32,fd00::/128"
```

## Performance

### WireGuard Speeds
- **Download:** 300-600 Mbps
- **Upload:** 300-500 Mbps
- **Latency:** Low (+10-30ms)

### OpenVPN Speeds
- **Download:** 150-300 Mbps
- **Upload:** 100-200 Mbps
- **Latency:** Moderate (+20-50ms)

### Multi-Hop Impact
- Approximately 50% speed reduction
- Double latency
- Use only when privacy is critical

## Why Choose IVPN?

### Excellent For:
**Maximum privacy** (best in class)
**Anonymity** (no personal info)
**Trust and transparency**
**Multi-hop** (Pro plan)
**Open source commitment**

### Not Ideal For:
**Torrenting with high ratios** (no port forwarding)
**Budget-conscious users** (expensive)
**Many devices** (limited connections)
**Casual users** (overkill for basic needs)

## Configuration Example

```yaml
# .env
VPN_SERVICE=ivpn
WIREGUARD_PRIVATE_KEY=your_private_key
WIREGUARD_ADDRESSES=10.x.x.x/32
PRIVATE_SUBNET=192.168.1.0/24

# docker-compose.yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: ivpn
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_COUNTRIES: "Switzerland"
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
```

## Comparison: Privacy vs Torrenting Performance

| VPN | Privacy | Port Forwarding | Best For |
|-----|---------|----------------|----------|
| **IVPN** | | | Privacy-focused users |
| Mullvad | | | Privacy + speed |
| ProtonVPN | | | Privacy + torrenting |
| PIA | | | Torrenting performance |

## References

- [IVPN Website](https://www.ivpn.net/)
- [IVPN Account](https://www.ivpn.net/account/)
- [IVPN Server Status](https://www.ivpn.net/status/)
- [IVPN Transparency](https://www.ivpn.net/transparency/)
- [Gluetun IVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/ivpn.md)

## Final Recommendation

**IVPN is excellent for privacy** but not ideal for Route 23 due to lack of port forwarding.

**Choose IVPN if:**
- Privacy is your #1 priority
- You don't mind lower seeding ratios
- You want multi-hop (Pro plan)
- You value transparency and audits

**Choose PIA, ProtonVPN, or AirVPN if:**
- You want optimal torrenting performance (port forwarding)
- Seeding ratios matter to you
- You want better value for price
