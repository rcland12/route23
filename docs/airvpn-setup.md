# AirVPN Setup Guide

This guide explains how to configure Route 23 with AirVPN.

## Prerequisites

- Active AirVPN subscription
- AirVPN account credentials
- **Note:** AirVPN is excellent for torrenting with **port forwarding support**

## Getting Your Credentials

### 1. Generate OpenVPN Configuration

AirVPN uses configuration file-based authentication:

1. Log in to your AirVPN account: https://airvpn.org/
2. Navigate to **Client Area** → **Config Generator**
3. Select:
   - **Protocols:** OpenVPN or WireGuard
   - **Servers:** Choose P2P-friendly servers
   - **Port:** Default or custom
   - **Advanced:** Enable port forwarding if desired
4. Click **Generate** to download the config file

### 2. Extract Credentials from Config

#### For OpenVPN:

```bash
# View the downloaded config
cat AirVPN_*.ovpn

# Extract the username (usually inside the config or in a separate file)
# AirVPN uses certificate-based authentication, so you may need:
# - Client certificate (cert)
# - Private key (key)
# - CA certificate (ca)
```

#### For WireGuard:

```bash
# Extract from WireGuard config
grep "PrivateKey" AirVPN_*.conf | cut -d'=' -f2 | tr -d ' '
grep "Address" AirVPN_*.conf | cut -d'=' -f2 | tr -d ' '
```

## Configuration

### Method 1: OpenVPN with Certificate

AirVPN typically uses certificate-based authentication. You'll need to extract the certificates from your config file:

Add to `.env`:

```bash
# VPN Configuration
VPN_SERVICE=airvpn
OPENVPN_USER=your_username  # From AirVPN config
OPENVPN_PASSWORD=your_password  # From AirVPN config
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: airvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_REGIONS: "America"  # or "Europe", "Asia"
    VPN_PORT_FORWARDING: on  # Enable port forwarding!
    VPN_PORT_FORWARDING_PROVIDER: airvpn
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

### Method 2: WireGuard

```bash
# In .env
VPN_SERVICE=airvpn
WIREGUARD_PRIVATE_KEY=your_private_key
WIREGUARD_ADDRESSES=10.x.x.x/32
```

Update `docker-compose.yaml`:

```yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: airvpn
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    SERVER_REGIONS: "America"
    VPN_PORT_FORWARDING: on
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
```

## Server Regions

AirVPN has servers in three main regions:

**Americas:**
- United States (multiple locations)
- Canada

**Europe:**
- Netherlands (Amsterdam)
- Germany (Frankfurt)
- Switzerland (Zurich)
- Sweden (Stockholm)
- United Kingdom
- Italy, France, Spain

**Asia:**
- Singapore
- Japan
- Hong Kong

## Port Forwarding (MAJOR FEATURE!)

**AirVPN fully supports port forwarding** - This is huge for torrenting!

### Enable Port Forwarding

Port forwarding is managed through AirVPN's control panel:

1. Log in to: https://airvpn.org/
2. Navigate to **Client Area** → **Forwarded Ports**
3. Click **Add Port** to create a forwarded port
4. Note your assigned port number
5. Configure this port in your rTorrent settings

### Configure in Gluetun

```yaml
vpn:
  environment:
    VPN_PORT_FORWARDING: on
    VPN_PORT_FORWARDING_PROVIDER: airvpn
```

### Check Forwarded Port

```bash
# View forwarded port in logs
docker logs route23-vpn 2>&1 | grep -i "port forward"

# Or check AirVPN control panel
```

## Verification

Test your AirVPN connection:

```bash
# Check VPN logs
docker logs route23-vpn

# Verify IP
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check connection details
docker exec route23-vpn wget -qO- https://ipinfo.io/json

# Verify port forwarding
docker logs route23-vpn 2>&1 | grep -i port
```

## Troubleshooting

### Authentication Failed

```bash
# AirVPN uses certificate-based auth
# Ensure you've properly extracted credentials from config file

# Check AirVPN Client Area for valid credentials
# Regenerate config if needed
```

### Connection Timeout

```bash
# Try different server region
SERVER_REGIONS: "Europe"

# Or specific country
SERVER_COUNTRIES: "Netherlands"
```

### Port Forwarding Not Working

```bash
# Verify port forwarding is enabled in AirVPN control panel
# Check: https://airvpn.org/ → Client Area → Forwarded Ports

# Ensure it's enabled in Gluetun
VPN_PORT_FORWARDING: on
VPN_PORT_FORWARDING_PROVIDER: airvpn

# Restart VPN container
docker restart route23-vpn
```

## AirVPN Features

### Pros
**Port forwarding support** (excellent for torrenting!)
**No logs policy** (strong privacy)
**WireGuard support**
**P2P encouraged** on all servers
**Network Lock** (kill switch)
**OpenVPN over SSH/SSL/Stunnel**
**Based in Italy** (decent jurisdiction)
**Unlimited bandwidth**
**5 simultaneous connections**

### Cons
**Smaller server network** (~250 servers vs 1000s)
**Complex setup** (certificate-based auth)
**More technical** (not beginner-friendly)
**Higher price point**

## Why Choose AirVPN for Torrenting?

### Excellent For:
**Port forwarding** (critical for seeding ratios)
**Privacy-conscious** users
**Torrenters** (P2P explicitly supported)
**Technical users** who want control

### Considerations:
- Smaller server selection
- Slightly more complex setup
- Higher price than competitors
- Less user-friendly than mainstream VPNs

## Performance

With WireGuard:
- **Download:** 300-600 Mbps
- **Upload:** 300-500 Mbps
- **Latency:** Low

With OpenVPN:
- **Download:** 150-300 Mbps
- **Upload:** 100-200 Mbps

## Privacy & Security

- **No logs policy** (transparent, audited)
- **Based in Italy** (EU, but privacy-friendly)
- **Accepts Bitcoin** (anonymous payment)
- **Perfect forward secrecy**
- **Strong encryption** (AES-256)
- **Open source client** (Eddie)

## Advanced Configuration

### Custom DNS

```yaml
DNS_ADDRESS: "10.128.0.1"  # AirVPN DNS
# Or use custom:
DNS_ADDRESS: "1.1.1.1,1.0.0.1"
```

### Multi-Hop (OpenVPN over SSH)

AirVPN supports tunneling OpenVPN over SSH for extra obfuscation:

```yaml
# Requires additional configuration
# See AirVPN documentation for SSH tunnel setup
```

## Configuration Example

```yaml
# .env
VPN_SERVICE=airvpn
OPENVPN_USER=your_username
OPENVPN_PASSWORD=your_password
PRIVATE_SUBNET=192.168.1.0/24

# docker-compose.yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: airvpn
    VPN_TYPE: openvpn
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
    SERVER_REGIONS: "Europe"
    VPN_PORT_FORWARDING: on
    VPN_PORT_FORWARDING_PROVIDER: airvpn
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
```

## Comparison: AirVPN vs Others for Torrenting

| Feature | AirVPN | PIA | ProtonVPN | Mullvad |
|---------|--------|-----|-----------|---------|
| Port Forwarding | | | | |
| WireGuard | | | | |
| Price | $$ | $ | $$ | $ |
| Servers | ~250 | 35000+ | 1900+ | 900+ |
| Privacy | | | | |
| Ease of Use | | | | |

## References

- [AirVPN Website](https://airvpn.org/)
- [AirVPN Config Generator](https://airvpn.org/generator/)
- [AirVPN Port Forwarding Guide](https://airvpn.org/forums/topic/9852-how-to-forward-ports/)
- [Gluetun AirVPN Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/airvpn.md)

## Final Recommendation

**AirVPN is an EXCELLENT choice for Route 23** if you:
- Need port forwarding (improves seeding ratios significantly)
- Value privacy and transparency
- Don't mind slightly more complex setup
- Want full control over your VPN configuration

For maximum torrenting performance, AirVPN is one of the top 3 choices alongside PIA and ProtonVPN.
