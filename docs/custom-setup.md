# Custom VPN Setup Guide

This guide explains how to configure Route 23 with a **custom VPN provider** or your own OpenVPN/WireGuard configuration files.

## When to Use Custom Configuration

Use the custom provider option when:
- Your VPN provider isn't directly supported by Gluetun
- You have your own VPN server (self-hosted)
- You want to use specific OpenVPN/WireGuard config files
- You need advanced custom configurations

## Prerequisites

- OpenVPN (.ovpn) or WireGuard (.conf) configuration file(s)
- VPN credentials (if required)
- Understanding of VPN configuration basics

## Method 1: Custom OpenVPN Configuration

### Step 1: Prepare Your Config File

Obtain your `.ovpn` configuration file from your VPN provider or generate one for your self-hosted VPN server.

### Step 2: Place Config File

```bash
# Create directory for custom configs
mkdir -p ./gluetun/openvpn

# Copy your config file
cp your-vpn-config.ovpn ./gluetun/openvpn/
```

### Step 3: Update docker-compose.yaml

```yaml
vpn:
  container_name: route23-vpn
  image: qmcgaw/gluetun:latest
  restart: unless-stopped
  networks:
    - nginx
  environment:
    VPN_SERVICE_PROVIDER: custom
    VPN_TYPE: openvpn
    OPENVPN_CUSTOM_CONFIG: /gluetun/custom.conf
    OPENVPN_USER: ${OPENVPN_USER}  # If auth required
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}  # If auth required
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
  cap_add:
    - NET_ADMIN
  devices:
    - /dev/net/tun:/dev/net/tun
  volumes:
    - ./gluetun/openvpn:/gluetun:ro  # Mount your config directory
```

### Step 4: Configure .env

```bash
# VPN Configuration
VPN_SERVICE=custom
OPENVPN_USER=your_username  # If auth required
OPENVPN_PASSWORD=your_password  # If auth required
PRIVATE_SUBNET=192.168.1.0/24
TIMEZONE=America/New_York
```

## Method 2: Custom WireGuard Configuration

### Step 1: Prepare WireGuard Config

Obtain or create your WireGuard configuration file (`.conf`).

Example WireGuard config:
```ini
[Interface]
PrivateKey = YOUR_PRIVATE_KEY_HERE
Address = 10.x.x.x/32
DNS = 1.1.1.1

[Peer]
PublicKey = SERVER_PUBLIC_KEY_HERE
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

### Step 2: Extract Configuration Details

From your WireGuard config, extract:
- **PrivateKey** (your private key)
- **Address** (your WireGuard IP)
- **PublicKey** (server's public key)
- **Endpoint** (server address and port)

### Step 3: Update .env

```bash
# VPN Configuration
VPN_SERVICE=custom
WIREGUARD_PRIVATE_KEY=your_private_key_here
WIREGUARD_ADDRESSES=10.x.x.x/32
WIREGUARD_PUBLIC_KEY=server_public_key_here
WIREGUARD_ENDPOINT_IP=vpn.example.com
WIREGUARD_ENDPOINT_PORT=51820
```

### Step 4: Update docker-compose.yaml

```yaml
vpn:
  container_name: route23-vpn
  image: qmcgaw/gluetun:latest
  restart: unless-stopped
  networks:
    - nginx
  environment:
    VPN_SERVICE_PROVIDER: custom
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    WIREGUARD_PUBLIC_KEY: ${WIREGUARD_PUBLIC_KEY}
    WIREGUARD_ENDPOINT_IP: ${WIREGUARD_ENDPOINT_IP}
    WIREGUARD_ENDPOINT_PORT: ${WIREGUARD_ENDPOINT_PORT}
    FIREWALL_OUTBOUND_SUBNETS: ${PRIVATE_SUBNET}
    TZ: ${TIMEZONE}
  cap_add:
    - NET_ADMIN
  devices:
    - /dev/net/tun:/dev/net/tun
```

## Method 3: Self-Hosted VPN Server

If you're running your own VPN server:

### OpenVPN Server

1. Generate OpenVPN config on your server
2. Download `.ovpn` client config
3. Follow Method 1 above

### WireGuard Server

1. Generate WireGuard keys on your server
2. Create peer configuration
3. Follow Method 2 above

### Example: WireGuard on Your Server

```bash
# On your VPN server:
# Generate server keys
wg genkey | tee server_private.key | wg pubkey > server_public.key

# Generate client keys
wg genkey | tee client_private.key | wg pubkey > client_public.key

# Configure server with client's public key
# Use client's private key in Route 23 config
```

## Port Forwarding with Custom VPN

Port forwarding depends on your VPN provider or server:

### Self-Hosted VPN
You have full control - configure port forwarding on your server

### Third-Party VPN
- Check if provider supports port forwarding
- May require manual configuration
- Set `VPN_PORT_FORWARDING=on` if supported

## Verification

```bash
# Check VPN connection
docker logs route23-vpn

# Verify IP changed
docker exec route23-vpn wget -qO- https://ipinfo.io/ip

# Check connection details
docker exec route23-vpn wget -qO- https://ipinfo.io/json
```

## Troubleshooting

### Connection Failed

```bash
# Check logs for specific error
docker logs route23-vpn

# Common issues:
# 1. Incorrect path to config file
# 2. Missing credentials
# 3. Firewall blocking VPN ports
# 4. Invalid config format
```

### Authentication Failed

```bash
# For OpenVPN with embedded auth:
# Ensure auth is embedded in .ovpn file OR
# Provide OPENVPN_USER and OPENVPN_PASSWORD

# For certificate-based auth:
# Ensure certs are included in .ovpn file
```

### DNS Issues

```yaml
# Add custom DNS
environment:
  DNS_ADDRESS: "1.1.1.1,1.0.0.1"
```

### Firewall Issues

```bash
# Ensure tun device is available
ls -la /dev/net/tun

# Check Gluetun firewall settings
docker logs route23-vpn | grep -i firewall
```

## Advanced Configuration

### Multiple VPN Configs

```yaml
# You can switch between multiple configs
volumes:
  - ./gluetun/config1.ovpn:/gluetun/custom.conf:ro
  # or
  - ./gluetun/config2.ovpn:/gluetun/custom.conf:ro
```

### Custom DNS

```yaml
environment:
  DNS_ADDRESS: "1.1.1.1,1.0.0.1"
  DOT: off  # Disable DNS over TLS if needed
```

### IPv6 Support

```yaml
environment:
  IPV6: on
  WIREGUARD_ADDRESSES: "10.x.x.x/32,fd00::/128"
```

### Custom Firewall Rules

```yaml
environment:
  FIREWALL_INPUT_PORTS: 8080  # Allow web UI
  FIREWALL_VPN_INPUT_PORTS: 6881  # Allow torrent port
```

## Example Configurations

### Example 1: Custom OpenVPN with Auth

```yaml
# docker-compose.yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: custom
    VPN_TYPE: openvpn
    OPENVPN_CUSTOM_CONFIG: /gluetun/custom.conf
    OPENVPN_USER: ${OPENVPN_USER}
    OPENVPN_PASSWORD: ${OPENVPN_PASSWORD}
  volumes:
    - ./my-vpn-config.ovpn:/gluetun/custom.conf:ro
```

### Example 2: Self-Hosted WireGuard

```yaml
# .env
WIREGUARD_PRIVATE_KEY=your_client_private_key
WIREGUARD_ADDRESSES=10.0.0.2/24
WIREGUARD_PUBLIC_KEY=your_server_public_key
WIREGUARD_ENDPOINT_IP=your-server.example.com
WIREGUARD_ENDPOINT_PORT=51820

# docker-compose.yaml
vpn:
  environment:
    VPN_SERVICE_PROVIDER: custom
    VPN_TYPE: wireguard
    WIREGUARD_PRIVATE_KEY: ${WIREGUARD_PRIVATE_KEY}
    WIREGUARD_ADDRESSES: ${WIREGUARD_ADDRESSES}
    WIREGUARD_PUBLIC_KEY: ${WIREGUARD_PUBLIC_KEY}
    WIREGUARD_ENDPOINT_IP: ${WIREGUARD_ENDPOINT_IP}
    WIREGUARD_ENDPOINT_PORT: ${WIREGUARD_ENDPOINT_PORT}
```

## When to Use Custom Configuration

**Use Custom Configuration For:**
Self-hosted VPN servers
Unsupported VPN providers
Corporate/enterprise VPNs
Advanced custom setups
Testing custom configs

**Use Provider-Specific Setup For:**
- Supported providers (PIA, NordVPN, etc.)
- Simpler setup process
- Better Gluetun integration
- Automatic server selection

## Security Considerations

- **Keep private keys secure** (never commit to git)
- **Verify server certificates** (for OpenVPN)
- **Use strong encryption** (AES-256)
- **Enable kill switch** (built into Gluetun)
- **Test for DNS leaks** after setup

## References

- [Gluetun Custom Provider Wiki](https://github.com/qdm12/gluetun-wiki/blob/main/setup/providers/custom.md)
- [Gluetun Environment Variables](https://github.com/qdm12/gluetun-wiki/blob/main/setup/options/)
- [OpenVPN Configuration Reference](https://openvpn.net/community-resources/reference-manual-for-openvpn-2-4/)
- [WireGuard Quick Start](https://www.wireguard.com/quickstart/)

## Final Notes

Custom configurations offer maximum flexibility but require more technical knowledge. For most users, using a supported VPN provider (PIA, ProtonVPN, Mullvad) is simpler and better integrated with Gluetun.

**Use custom configuration when you have specific requirements that supported providers can't meet.**
