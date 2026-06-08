<div align="center">
  <table>
    <tr>
      <td><img src="logo.png" alt="route23 Logo" width="120" height="120"></td>
      <td><h1 style="font-size: 64px; margin: 0; padding-left: 20px;">route23</h1></td>
    </tr>
  </table>
</div>

<p align="center">
  <strong>Automated torrent seeding with VPN protection and intelligent rotation</strong>
</p>

<p align="center">
  <a href="https://github.com/rcland12/route23/actions/workflows/docker-publish.yml">
    <img src="https://github.com/rcland12/route23/actions/workflows/docker-publish.yml/badge.svg" alt="Build and Security Scan">
  </a>
  <a href="https://hub.docker.com/r/rcland12/route23">
    <img src="https://img.shields.io/docker/pulls/rcland12/route23?logo=docker" alt="Docker Pulls">
  </a>
  <a href="https://hub.docker.com/r/rcland12/route23">
    <img src="https://img.shields.io/docker/v/rcland12/route23?logo=docker&label=version" alt="Docker Version">
  </a>
  <a href="https://github.com/rcland12/route23/pkgs/container/route23">
    <img src="https://img.shields.io/badge/ghcr-image-blue?logo=github" alt="GHCR">
  </a>
  <a href="https://securityscorecards.dev/viewer/?uri=github.com/rcland12/route23">
    <img src="https://api.securityscorecards.dev/projects/github.com/rcland12/route23/badge" alt="OpenSSF Scorecard">
  </a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [VPN Configuration](#vpn-configuration)
  - [Supported VPN Providers](#supported-vpn-providers)
  - [Recommendations](#recommendations)
  - [Understanding Port Forwarding](#understanding-port-forwarding)
  - [Setup Instructions](#setup-instructions)
- [Installation](#installation)
- [Email Notifications (Optional)](#email-notifications-optional)
  - [Gmail Setup](#gmail-setup)
  - [Outlook/Hotmail/Live Setup](#outlookhotmaillive-setup)
  - [Yahoo Mail Setup](#yahoo-mail-setup)
  - [ProtonMail Setup](#protonmail-setup)
  - [iCloud Mail Setup](#icloud-mail-setup)
  - [Custom SMTP Server Setup](#custom-smtp-server-setup)
  - [Testing Email Notifications](#testing-email-notifications)
  - [Troubleshooting Email Issues](#troubleshooting-email-issues)
- [route23 - The Rotator](#route23---the-rotator)
  - [How It Works](#how-it-works)
  - [Running route23](#running-route23)
  - [Checking Status](#checking-status)
  - [Force Rotation](#force-rotation)
  - [Preload from Remote (Optional)](#preload-from-remote-optional)
  - [Recovery: Repreload and Force Preload](#recovery-repreload-and-force-preload)
  - [Automating with Cron](#automating-with-cron)
  - [Configuration Options](#configuration-options)
  - [Understanding Rotation Timeline](#understanding-rotation-timeline)
  - [State Management](#state-management)
- [Additional Features](#additional-features)
  - [ruTorrent Web Interface](#rutorrent-web-interface)
  - [Move Completed Downloads](#move-completed-downloads)
- [File Structure](#file-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

route23 is a self-hosted, Docker-based automated torrent rotation system designed for low-power devices like Raspberry Pi.

**Why "route23"?** The name comes from the 23 different VPN providers supported through Gluetun integration - offering you flexibility to choose the VPN service that best fits your needs, whether that's port forwarding support, privacy features, or price. It's also a major US Highway that runs from Michigan to Florida that I frequently drive on.

**What it does:** route23 automatically manages your torrent seeding by rotating through your collection in batches. Instead of trying to seed hundreds or thousands of torrents simultaneously (which would overwhelm most hardware), route23 intelligently seeds small batches for configurable periods, then automatically cycles to the next batch. Over time, your entire collection gets seeded fairly and efficiently.

**The Stack:** route23 is built on a foundation of proven technologies - ruTorrent for torrent management, Gluetun for VPN protection (supporting all 23 providers), and Postfix for email notifications. These supporting services exist to enable the core route23 rotation functionality.

## Features

**Core route23 Features:**

- **Intelligent Batch Rotation** — Automatically cycles through your torrent library in manageable batches
- **Time-Based Scheduling** — Configurable rotation periods (default: 14 days per batch)
- **Persistent State Management** — Remembers exactly where it left off across restarts
- **Load-Aware Operations** — Monitors system load and throttles operations for low-power devices
- **Progress Tracking** — Real-time status reporting showing progress through your collection
- **Remote Preload (Optional)** — Pre-seed new torrents from a local Plex/media server over SSH so seeding starts within minutes instead of waiting for the swarm
- **Hash-Check Verification** — After preload, route23 waits for the recheck and stops any torrent that ended up with 0% valid data, so broken preloads are visible instead of silently seeding nothing
- **Recovery Modes** — Repreload the full current batch or force-preload a single torrent without rotating

**Supporting Infrastructure:**

- **VPN Protection** — All torrent traffic routed through your choice of 23+ VPN providers (Gluetun)
- **Web Interface** — Full ruTorrent UI for manual torrent management
- **Email Notifications** — Optional digest email after each rotation/preload summarizing what was preloaded and what was missed
- **Docker-Based** — Easy deployment and management with docker compose

## Quick Start

Get up and running with route23 in 5 steps:

**1. Prerequisites**

- Docker and Docker Compose installed
- A VPN subscription with one of the 23 supported providers
- Your local network subnet (usually `192.168.1.0/24` or `192.168.0.0/24`)

**2. Clone and Configure**

```bash
git clone https://github.com/rcland12/route23.git
cd route23
cp .env.example .env  # Create your configuration file
```

**3. Get Your Credentials**

Before editing `.env`, gather these credentials:

| What You Need                | Where to Get It                                              | Notes                                                              |
| ---------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------ |
| VPN credentials              | Your VPN provider dashboard                                  | See [VPN Configuration](#vpn-configuration) for detailed guides    |
| Local network subnet         | Run: `ip route \| awk '$1 ~ /^192\.168\./ {print $1; exit}'` | Usually `192.168.1.0/24` or `192.168.0.0/24`                       |
| Email credentials (optional) | Your email provider                                          | See [Email Notifications](#email-notifications-optional) for setup |

**4. Edit Configuration**

Open `.env` and fill in your values (see [Installation](#installation) for detailed explanations).

**5. Start Services**

```bash
# Install htpasswd tool if needed
sudo apt update && sudo apt install apache2-utils

# Create web UI credentials (choose your own username/password)
htpasswd -Bbn your_username your_password > ./rutorrent/passwd/rutorrent.htpasswd

# Create a TLS certificate for the web UI (self-signed example)
sudo mkdir -p /etc/nginx/certs
sudo openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
  -keyout /etc/nginx/certs/key.pem \
  -out /etc/nginx/certs/cert.pem \
  -subj "/CN=$(hostname)"

# Start the supporting services (everything except the rotator)
docker compose up -d

# Access web UI at https://<your-server-ip>
```

That's it! Your route23 instance is running. Add `.torrent` files to `./rutorrent/torrents/` and run your first rotation with `docker compose run --rm app`.

> **Note:** The `app` (rotator) service is assigned to the `route23` Compose profile, so `docker compose up` brings up only the supporting services (nginx, ruTorrent, VPN, postfix). The rotator is meant to run on demand — `docker compose run --rm app` starts it (and automatically enables its profile), and that's what the cron job and `exe/` scripts use.

For detailed configuration options and advanced features, continue reading below.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Network                        │
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐    │
│  │  nginx   │───▶│   ruTorrent  │───▶│   VPN (Gluetun)  │──▶ │ Internet
│  │ :80/:443 │    │   Web UI     │    │   NordVPN/WG     │    │
│  └──────────┘    └──────────────┘    └──────────────────┘    │
│        │                                      │              │
│        │         ┌──────────────┐             │              │
│        │         │   Rotator    │─────────────┘              │
│        │         │   Service    │                            │
│        │         └──────────────┘                            │
│        │                                                     │
│        │         ┌──────────────┐                            │
│        └────────▶│   Postfix    │───▶ Gmail SMTP             │
│                  │   Relay      │                            │
│                  └──────────────┘                            │
└──────────────────────────────────────────────────────────────┘
```

**The route23 Rotator Service** is the core component that orchestrates everything. It connects to ruTorrent via API to add/remove torrents in batches, while the VPN ensures all torrent traffic is protected. The web UI (nginx + ruTorrent) and email notifications (Postfix) are optional supporting features.

## Prerequisites

- Docker & Docker Compose
- Supported VPN subscription (see [VPN Configuration](#vpn-configuration) below)
- Email account for notifications - optional (see [Email Notifications](#email-notifications-optional))

## VPN Configuration

route23 supports multiple VPN providers through Gluetun. Choose your provider and follow the setup guide:

### Supported VPN Providers

route23 supports all 23 VPN providers available through Gluetun. Click any provider name for detailed setup instructions.

| Provider                                         | Port Forwarding | WireGuard | Price  | Servers | Recommendation             |
| ------------------------------------------------ | --------------- | --------- | ------ | ------- | -------------------------- |
| [Private Internet Access](docs/pia-setup.md)     | Yes (included)  | Yes       | $      | 35000+  | Recommended for torrenting |
| [ProtonVPN](docs/protonvpn-setup.md)             | Yes (included)  | Yes       | $$     | 1900+   | Recommended for torrenting |
| [AirVPN](docs/airvpn-setup.md)                   | Yes (included)  | Yes       | $$     | 250+    | Recommended for torrenting |
| [Perfect Privacy](docs/perfect-privacy-setup.md) | Yes (included)  | Yes       | $$$    | 25+     | Recommended for torrenting |
| [TorGuard](docs/torguard-setup.md)               | Yes (addon)     | Yes       | $$-$$$ | 3000+   | Recommended for torrenting |
| [Mullvad](docs/mullvad-setup.md)                 | No              | Yes       | $      | 900+    | Good (privacy-focused)     |
| [IVPN](docs/ivpn-setup.md)                       | No              | Yes       | $$     | 100+    | Good (privacy-focused)     |
| [NordVPN](docs/nordvpn-setup.md)                 | No              | Yes       | $$     | 5500+   | Good (general use)         |
| [Surfshark](docs/surfshark-setup.md)             | No              | Yes       | $      | 3200+   | Good (unlimited devices)   |
| [Windscribe](docs/windscribe-setup.md)           | Static only     | Pro only  | $-$$   | 600+    | Good (budget option)       |
| [CyberGhost](docs/cyberghost-setup.md)           | No              | Yes       | $$     | 9000+   | Good (P2P servers)         |
| [VyprVPN](docs/vyprvpn-setup.md)                 | No              | No        | $$     | 700+    | Limited                    |
| [ExpressVPN](docs/expressvpn-setup.md)           | No              | No        | $$$    | 3000+   | Not recommended            |
| [IPVanish](docs/ipvanish-setup.md)               | No              | Limited   | $$     | 2000+   | Not recommended            |
| [PureVPN](docs/purevpn-setup.md)                 | Addon only      | Limited   | $      | 6500+   | Not recommended            |
| [PrivateVPN](docs/privatevpn-setup.md)           | No              | No        | $      | 200+    | Not recommended            |
| [HideMyAss](docs/hidemyass-setup.md)             | No              | No        | $$     | 1100+   | Not recommended            |
| [FastestVPN](docs/fastestvpn-setup.md)           | No              | No        | $      | 600+    | Not recommended            |
| [Privado](docs/privado-setup.md)                 | No              | Yes       | $-$$   | 45+     | Not recommended            |
| [VPN Unlimited](docs/vpn-unlimited-setup.md)     | No              | No        | $$     | 500+    | Not recommended            |
| [VPN Secure](docs/vpn-secure-setup.md)           | No              | Yes       | $$     | 100+    | Not recommended            |
| [SlickVPN](docs/slickvpn-setup.md)               | No              | No        | $      | 150+    | Not recommended            |
| [Custom Configuration](docs/custom-setup.md)     | Depends         | Depends   | -      | -       | For advanced users         |

### Recommendations

**Best for Torrenting (Port Forwarding Required):**

- Private Internet Access (PIA) - Best overall value with included port forwarding
- ProtonVPN - Strong privacy with port forwarding support
- AirVPN - Excellent for technical users and privacy-conscious torrenters

**Best for Privacy (Without Port Forwarding):**

- Mullvad - Anonymous accounts, independently audited
- IVPN - No personal information required, multi-hop support
- ProtonVPN - Swiss-based with strong privacy protections

**Best Value:**

- PIA - Approximately $3/month with port forwarding included
- Mullvad - Fixed pricing at 5 EUR/month
- Windscribe - Free tier available or affordable Pro plan

**Not Recommended:**

- Providers without port forwarding support are less optimal for torrenting
- ExpressVPN, IPVanish, HideMyAss, and FastestVPN have limitations for this use case

### Understanding Port Forwarding

**Why Port Forwarding Matters:** Port forwarding significantly improves seeding ratios and peer connections. Without it, you can still seed but with reduced efficiency:

- **With Port Forwarding:** Accept incoming connections, better peer discovery, higher upload speeds, improved ratios
- **Without Port Forwarding:** Outgoing connections only, slower seeding, lower ratios

**Providers with Port Forwarding:** PIA, ProtonVPN, AirVPN, Perfect Privacy, TorGuard (addon)

### Setup Instructions

Click any VPN provider above to access detailed setup guides including:

- How to get your API keys, tokens, or credentials
- Step-by-step configuration for route23
- Server recommendations optimized for P2P
- Port forwarding setup (where applicable)
- Troubleshooting common issues
- Performance tips

## Installation

### 1. Clone and Enter Directory

```bash
git clone https://github.com/rcland12/route23.git
cd route23
```

### 2. Gather Required Information

Before creating your `.env` file, you'll need to collect the following information:

#### VPN Credentials (Required)

Your VPN provider will give you credentials needed for Gluetun. Each provider is different:

- **NordVPN**: Access token from account dashboard
- **Private Internet Access**: Username and password
- **ProtonVPN**: OpenVPN/WireGuard credentials
- **Other providers**: See [VPN Configuration](#vpn-configuration) for detailed guides

Click your VPN provider in the [Supported VPN Providers](#supported-vpn-providers) table for specific instructions on obtaining these credentials.

#### Local Network Subnet (Required)

Your local network subnet allows route23 to communicate with your host machine. Find yours with:

```bash
ip route show | awk '/proto kernel/ && /192\.168\./ {print $1}'
```

Common values are `192.168.1.0/24`, `192.168.0.0/24`, or `10.0.0.0/24`. If the command returns nothing, try:

```bash
ip -4 addr show | grep inet | grep -v 127.0.0.1 | awk '{print $2}'
```

#### Web UI Credentials (Required)

Choose a username and password for accessing the ruTorrent web interface. These are credentials you create yourself - pick something secure. You'll need these in step 3.

#### Email Credentials (Optional)

If you want email notifications for torrent completion, you'll need:

- Your email address
- An app-specific password from your email provider

See [Email Notifications](#email-notifications-optional) for provider-specific instructions on generating app passwords for Gmail, Outlook, Yahoo, iCloud, and others.

### 3. Create Environment File

Create a `.env` file in the route23 directory with your configuration:

```bash
# ============================================
# VPN Configuration (Required)
# ============================================
# Get these credentials from your VPN provider dashboard
# See VPN Configuration section for provider-specific guides

VPN_SERVICE="nordvpn"                    # Your VPN provider name
NORDVPN_TOKEN=your_token_here            # Replace with your VPN token/username
WIREGUARD_PRIVATE_KEY=your_key_here      # Replace with your WireGuard private key

# ============================================
# Network Configuration (Required)
# ============================================
# Find your subnet with: ip route show | awk '/proto kernel/ && /192\.168\./ {print $1}'
# Common values: 192.168.1.0/24, 192.168.0.0/24, 10.0.0.0/24

PRIVATE_SUBNET="192.168.0.0/24"          # Replace with YOUR local network subnet

# ============================================
# System Configuration (Required)
# ============================================

TIMEZONE="America/New_York"              # Your timezone (e.g., America/Chicago, Europe/London)
SERVER_NAME="route23"                    # Hostname for your server (can be anything)

# ============================================
# ruTorrent Web UI Credentials (Required)
# ============================================
# CREATE YOUR OWN username and password here
# You'll use these in Step 4 with htpasswd command
# You'll also use these to login to the web UI

RTORRENT_USER=your_username              # Choose your own username
RTORRENT_PASS=your_password              # Choose your own password

# ============================================
# Email Notifications (Optional)
# ============================================
# Leave blank or comment out if you don't want email notifications
# See Email Notifications section for provider setup guides

POSTFIX_EMAIL=youremail@gmail.com        # Your email address
POSTFIX_PASSWORD=your_app_password       # App password from email provider (not your regular password)
POSTFIX_HOSTNAME=mail.website.com        # Optional: Your domain name
POSTFIX_ALLOWED_SENDER_DOMAINS="servername localhost website.com"  # Add your domain if using POSTFIX_HOSTNAME
```

### 4. Create ruTorrent Authentication File

Create the authentication file using the SAME username and password you specified in `.env` above:

```bash
# Install htpasswd if needed
sudo apt update && sudo apt install apache2-utils

# Create authentication file
# Replace your_username and your_password with the values from RTORRENT_USER and RTORRENT_PASS in .env
htpasswd -Bbn your_username your_password > ./rutorrent/passwd/rutorrent.htpasswd
```

**Important:** The username and password here MUST match `RTORRENT_USER` and `RTORRENT_PASS` from your `.env` file.

### 5. Create TLS Certificate

nginx serves the web UI over HTTPS, redirecting all plain HTTP traffic on port 80 to port 443. It expects a certificate and key at `/etc/nginx/certs/cert.pem` and `/etc/nginx/certs/key.pem` on the host (mounted read-only into the container).

For a quick self-signed certificate:

```bash
sudo mkdir -p /etc/nginx/certs
sudo openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
  -keyout /etc/nginx/certs/key.pem \
  -out /etc/nginx/certs/cert.pem \
  -subj "/CN=$(hostname)"
```

If you have a real certificate (e.g. from Let's Encrypt or an internal CA), drop the PEM files in the same location instead. The `server_name` in `nginx/nginx.conf` defaults to `rustypi3.home.arpa` — change it to match your hostname.

### 6. Start Services

```bash
docker compose up -d
```

The `app` (rotator) service is in the `route23` Compose profile, so `docker compose up` starts only the supporting services — nginx, ruTorrent, VPN, and postfix. The rotator runs on demand (see [Running route23](#running-route23)).

Wait for containers to start (30-60 seconds), then access the web UI at `https://<your-server-ip>` using the credentials you created in steps 3 and 4. With a self-signed certificate your browser will warn about the connection — accept it to continue.

### 7. Verify Setup

Check that all containers are running:

```bash
docker compose ps
```

You should see:

- `route23-nginx` (running)
- `route23-rutorrent` (running)
- `route23-vpn` (running)
- `route23-postfix` (running, if configured)

Test VPN connection:

```bash
docker compose exec vpn curl -s https://am.i.mullvad.net/connected
```

Should return: "You are connected to Mullvad" or similar message indicating VPN is active.

## Email Notifications (Optional)

route23 can send email notifications when torrents are added or completed. This section covers setup for major email providers.

### Supported Email Providers

route23 uses Postfix as an SMTP relay and supports any email provider that allows SMTP authentication:

- Gmail
- Outlook/Hotmail/Live
- Yahoo Mail
- ProtonMail
- iCloud Mail
- Custom SMTP servers

### Gmail Setup

Gmail requires an App Password for third-party applications.

#### 1. Enable 2-Factor Authentication

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security**
3. Enable **2-Step Verification** if not already enabled

#### 2. Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** as the app
3. Select **Other (Custom name)** as the device
4. Enter "route23" or "Postfix"
5. Click **Generate**
6. Copy the 16-character app password (remove spaces)

#### 3. Configure .env File

```bash
POSTFIX_EMAIL=your-email@gmail.com
POSTFIX_PASSWORD=your_app_password_here
```

#### 4. Update compose.yml (if needed)

The default configuration already supports Gmail:

```yaml
postfix:
  environment:
    RELAYHOST: "[smtp.gmail.com]:587"
    RELAYHOST_USERNAME: ${POSTFIX_EMAIL}
    RELAYHOST_PASSWORD: ${POSTFIX_PASSWORD}
```

### Outlook/Hotmail/Live Setup

Microsoft accounts work with their unified SMTP service.

#### 1. Enable SMTP Authentication

1. Sign in to your Microsoft account: https://account.microsoft.com/
2. Go to **Security** → **Advanced security options**
3. Ensure SMTP authentication is enabled (usually enabled by default)

#### 2. Use Your Account Password

Outlook does not require app passwords for SMTP (unless you have 2FA enabled).

#### 3. Configure .env File

```bash
POSTFIX_EMAIL=your-email@outlook.com  # or @hotmail.com, @live.com
POSTFIX_PASSWORD=your_account_password
```

#### 4. Update compose.yml

```yaml
postfix:
  environment:
    RELAYHOST: "[smtp-mail.outlook.com]:587"
    RELAYHOST_USERNAME: ${POSTFIX_EMAIL}
    RELAYHOST_PASSWORD: ${POSTFIX_PASSWORD}
```

### Yahoo Mail Setup

Yahoo requires an App Password for third-party applications.

#### 1. Generate App Password

1. Go to: https://login.yahoo.com/account/security
2. Click **Generate app password**
3. Select **Other App**
4. Enter "route23" as the app name
5. Click **Generate**
6. Copy the app password

#### 2. Configure .env File

```bash
POSTFIX_EMAIL=your-email@yahoo.com
POSTFIX_PASSWORD=your_app_password_here
```

#### 3. Update compose.yml

```yaml
postfix:
  environment:
    RELAYHOST: "[smtp.mail.yahoo.com]:587"
    RELAYHOST_USERNAME: ${POSTFIX_EMAIL}
    RELAYHOST_PASSWORD: ${POSTFIX_PASSWORD}
```

### ProtonMail Setup

ProtonMail requires the ProtonMail Bridge application for SMTP access.

#### 1. Install ProtonMail Bridge

1. Download ProtonMail Bridge: https://proton.me/mail/bridge
2. Install and log in with your ProtonMail account
3. Bridge will provide SMTP credentials

#### 2. Get Bridge Credentials

1. Open ProtonMail Bridge
2. Click on your account
3. Click **Mailbox configuration**
4. Note the SMTP server, port, username, and password

#### 3. Configure .env File

```bash
POSTFIX_EMAIL=your-bridge-username@protonmail.com
POSTFIX_PASSWORD=your_bridge_password
```

#### 4. Update compose.yml

```yaml
postfix:
  environment:
    RELAYHOST: "[127.0.0.1]:1025" # Default Bridge SMTP port
    RELAYHOST_USERNAME: ${POSTFIX_EMAIL}
    RELAYHOST_PASSWORD: ${POSTFIX_PASSWORD}
```

Note: ProtonMail Bridge must be running on the host machine for this to work.

### iCloud Mail Setup

iCloud requires an App-Specific Password.

#### 1. Generate App-Specific Password

1. Go to: https://appleid.apple.com/
2. Sign in with your Apple ID
3. Navigate to **Security** → **App-Specific Passwords**
4. Click **Generate an app-specific password**
5. Enter "route23" as the label
6. Copy the generated password

#### 2. Configure .env File

```bash
POSTFIX_EMAIL=your-email@icloud.com
POSTFIX_PASSWORD=your_app_specific_password
```

#### 3. Update compose.yml

```yaml
postfix:
  environment:
    RELAYHOST: "[smtp.mail.me.com]:587"
    RELAYHOST_USERNAME: ${POSTFIX_EMAIL}
    RELAYHOST_PASSWORD: ${POSTFIX_PASSWORD}
```

### Custom SMTP Server Setup

If you have your own SMTP server or use a different provider:

#### 1. Get SMTP Details

From your email provider, obtain:

- SMTP server address (e.g., `smtp.example.com`)
- SMTP port (usually 587 for TLS or 465 for SSL)
- Username (usually your email address)
- Password

#### 2. Configure .env File

```bash
POSTFIX_EMAIL=your-email@example.com
POSTFIX_PASSWORD=your_smtp_password
```

#### 3. Update compose.yml

```yaml
postfix:
  environment:
    RELAYHOST: "[smtp.example.com]:587" # Replace with your SMTP server and port
    RELAYHOST_USERNAME: ${POSTFIX_EMAIL}
    RELAYHOST_PASSWORD: ${POSTFIX_PASSWORD}
```

### Testing Email Notifications

After configuration, test email notifications:

#### 1. Restart Postfix Container

```bash
docker restart route23-postfix
```

#### 2. Check Postfix Logs

```bash
docker logs route23-postfix
```

Look for successful connection messages.

#### 3. Add a Test Torrent

Add a small torrent through ruTorrent. You should receive an email notification when:

- The torrent is added to ruTorrent
- The torrent completes downloading

### Troubleshooting Email Issues

#### Authentication Failed

```bash
# Check Postfix logs
docker logs route23-postfix | grep -i error

# Common issues:
# 1. Incorrect email/password
# 2. App password not generated (Gmail, Yahoo, iCloud)
# 3. 2FA not enabled (Gmail)
# 4. SMTP server/port incorrect
```

#### Emails Not Sending

```bash
# Verify Postfix is running
docker ps | grep postfix

# Check connectivity to SMTP server
docker exec route23-postfix nc -zv smtp.gmail.com 587

# Test email sending manually
docker exec route23-postfix sendmail your-email@example.com
Subject: Test
Test email
.
```

#### Gmail: "Less Secure App" Error

Gmail no longer supports "less secure apps". You must:

1. Enable 2-Factor Authentication
2. Generate an App Password (see Gmail setup above)

#### Outlook: Authentication Issues

If using 2FA with Outlook:

1. Generate an App Password at: https://account.microsoft.com/security
2. Use the App Password instead of your account password

### Disabling Email Notifications

To disable email notifications:

1. Remove or comment out the `POSTFIX_EMAIL` and `POSTFIX_PASSWORD` variables in `.env`
2. The postfix service will still run but notifications won't be sent
3. Alternatively, remove the postfix service from `compose.yml`

## route23 - The Rotator

The core of this project is the route23 rotator service (the `app` container), which intelligently manages your torrent seeding by automatically rotating through your collection. Everything else (VPN, ruTorrent, email notifications) exists to support this automated rotation functionality.

### How It Works

route23 operates on a simple but effective principle:

1. **Batch-Based Seeding** - Groups your torrents into manageable batches (default: 10 torrents)
2. **Time-Based Rotation** - Seeds each batch for a configurable period (default: 14 days)
3. **Automatic Cycling** - When the rotation period expires, removes the old batch and adds the next batch
4. **Persistent State** - Remembers its position in your collection across restarts
5. **Load Monitoring** - Monitors system load and throttles operations on low-power devices

The rotator works through your entire torrent collection sequentially, ensuring every torrent gets seeded fairly while keeping resource usage manageable for devices like Raspberry Pi.

### Running route23

Place your `.torrent` files in the `./rutorrent/torrents/` directory, then run the rotator:

```bash
# Run rotation check (only rotates if period has expired)
docker compose run --rm app
```

The rotator will:

- Check if the current rotation period has expired
- If yes, remove old torrents and add the next batch
- If no, display when the next rotation is due
- Monitor system load and pause if necessary

**Initial Run:**
On the first run, route23 will:

1. Load all `.torrent` files from `./rutorrent/torrents/`
2. Add the first batch (BATCH_SIZE torrents) to ruTorrent
3. Record the start time and batch information
4. Display status information

### Checking Status

View the current rotation status without making changes:

```bash
docker compose run --rm -e SHOW_STATUS=true app
```

This displays:

- Total number of torrents in your collection
- Current batch being seeded
- Batch start time
- Time until next rotation
- Number of completed batches
- Progress through your collection

Example output:

```
Status Report
=============
Total torrents: 1600
Batch size: 10
Current batch: 1-10
Batch started: 2024-01-15 03:00:00
Next rotation due: 2024-01-29 03:00:00 (13 days remaining)
Completed batches: 0
Progress: 0.6% (10/1600)
```

### Force Rotation

Force an immediate rotation regardless of the time period:

```bash
# Force rotation (keeps downloaded data)
docker compose run --rm -e FORCE_ROTATION=true app

# Force rotation and delete downloaded data (saves disk space)
docker compose run --rm -e FORCE_ROTATION=true -e DELETE_DATA=true app
```

**When to Force Rotation:**

- Testing the rotation system
- Manually skipping to the next batch
- Cleaning up disk space with DELETE_DATA=true
- After changing BATCH_SIZE configuration

### Preload from Remote (Optional)

If you already have the movie files on another machine (e.g., a Plex server on your LAN), route23 can pre-seed the new batch directly from there instead of waiting for the torrent swarm. Newly added torrents can start seeding within minutes.

**How it works:**

1. After route23 adds a torrent to ruTorrent, it SSHes to the remote machine
2. Looks for a directory matching the torrent's title and year (Plex naming convention)
3. Matches video files by byte length and `scp`s them into the per-torrent download directory
4. Triggers a hash check in rTorrent, waits for it to finish, and inspects the result
5. If the check finishes at 0% (e.g., the remote file has a different encode than the torrent), the torrent is stopped so it's obvious in the UI — not silently seeding nothing

**Requirements:**

- The remote machine must have SSH enabled and reachable from the route23 host
- The Plex movie library must follow the standard Plex naming convention: `Movie Title (YEAR) {imdb-ttXXXXXXX}/Movie Title (YEAR) {imdb-ttXXXXXXX}.mkv`
  - The included `./exe/verify.sh` script can audit your library for conformance
- An SSH private key on the route23 host that authenticates to the remote machine

**Setup:**

```bash
# 1. Generate an SSH key (or reuse an existing one)
ssh-keygen -t rsa -f ~/.ssh/id_rsa

# 2. Copy the public key to your media server
ssh-copy-id -i ~/.ssh/id_rsa.pub user@192.168.1.120

# 3. Add to .env
PRELOAD_HOST=192.168.1.120
PRELOAD_USER=russ
PRELOAD_SSH_KEY=/keys/id_rsa
PRELOAD_REMOTE_DIR=/mnt/plex/Media/Movies

# 4. In compose.yml, ensure PRELOAD_ENABLED: true (it is by default)
```

The private key is mounted into the container via the `compose.yml` volumes section (default: `${HOME}/.ssh/id_rsa:/keys/id_rsa:ro`). See [Preload Settings](#preload-settings-optional) for the full env-var reference.

### Recovery: Repreload and Force Preload

When preload fails for one or more torrents (the remote machine was offline, the auto-matcher missed, or the staged bytes didn't match the torrent's pieces), use these recovery modes instead of re-running the full rotation.

#### Repreload the Whole Current Batch

```bash
docker compose run --rm -e REPRELOAD=true app

# Or the wrapper that backgrounds it and writes to ./logs:
./exe/force_preload.sh
```

Re-attempts preload for every torrent in the saved current batch. Torrents already at 100% are skipped. Use this right after fixing connectivity to the remote machine or after restoring its data.

#### Force Preload a Single Torrent

When only one torrent failed and you don't want to touch the others, target it specifically:

```bash
# Auto-match: route23 picks the Plex directory based on the torrent name
./exe/force_preload_one.sh "mississippi"

# Override: skip auto-match and use an exact remote directory
./exe/force_preload_one.sh "mississippi" "Mississippi Burning (1988) {imdb-tt0095647}"
```

The substring matches case-insensitively against `.torrent` filenames in the current batch (and falls back to the full torrent directory if there's no match there). The optional second argument bypasses the auto-matcher entirely — use it when the Plex directory name differs from what the matcher derives from the torrent name (alternate titles, special characters, etc.).

After SCP, route23 triggers a hash check, waits for it to complete, and either restarts the torrent (if data is valid) or leaves it stopped with an `ERROR` log line (if the staged bytes didn't match the torrent's pieces — usually a different encode of the same movie). Logs land in `./logs/route23_force_preload.log`.

The equivalent without the wrapper:

```bash
docker compose run --rm \
    -e FORCE_PRELOAD_TORRENT="mississippi" \
    -e FORCE_PRELOAD_REMOTE_DIR="Mississippi Burning (1988) {imdb-tt0095647}" \
    app
```

### Automating with Cron

Set up a daily cron job to check for rotation automatically:

```bash
# Edit your crontab
crontab -e

# Add this line to check daily at 3am
0 3 * * * cd /path/to/route23 && docker compose run --rm app >> ./logs/route23.log 2>&1
```

**How Automation Works:**

- Cron runs the rotator daily (or at your chosen interval)
- The rotator checks if the rotation period has expired
- If expired, it performs the rotation automatically
- If not expired, it exits without changes
- All output is logged to `./logs/route23.log`

**Alternative Schedules:**

```bash
# Check every 12 hours
0 */12 * * * cd /path/to/route23 && docker compose run --rm app >> ./logs/route23.log 2>&1

# Check weekly (Sundays at 3am)
0 3 * * 0 cd /path/to/route23 && docker compose run --rm app >> ./logs/route23.log 2>&1

# Check twice daily (3am and 3pm)
0 3,15 * * * cd /path/to/route23 && docker compose run --rm app >> ./logs/route23.log 2>&1
```

### Configuration Options

Configure route23's behavior through environment variables in `compose.yml`:

#### Core Settings

| Variable        | Default | Description                              |
| --------------- | ------- | ---------------------------------------- |
| `BATCH_SIZE`    | `10`    | Number of torrents per rotation batch    |
| `ROTATION_DAYS` | `14`    | Days before rotating to next batch       |
| `DELETE_DATA`   | `false` | Delete downloaded data when rotating out |

#### Performance Settings (for Raspberry Pi)

| Variable        | Default | Description                                       |
| --------------- | ------- | ------------------------------------------------- |
| `ADD_DELAY`     | `30`    | Seconds to wait between adding each torrent       |
| `REMOVE_DELAY`  | `5`     | Seconds to wait between removing each torrent     |
| `MAX_LOAD`      | `4.0`   | Pause operations if system load exceeds this      |
| `LOAD_WAIT`     | `30`    | Seconds to wait when load is high before retrying |
| `STARTUP_DELAY` | `10`    | Seconds to wait before starting operations        |

#### Advanced Settings

| Variable                    | Default         | Description                                                                           |
| --------------------------- | --------------- | ------------------------------------------------------------------------------------- |
| `FORCE_ROTATION`            | `false`         | Force immediate rotation regardless of time                                           |
| `SHOW_STATUS`               | `false`         | Display status information only (no changes)                                          |
| `REPRELOAD`                 | `false`         | Re-run preload against every torrent in the current batch (see [Recovery](#recovery-repreload-and-force-preload)) |
| `FORCE_PRELOAD_TORRENT`     | (empty)         | Substring identifying a single torrent to force-preload                               |
| `FORCE_PRELOAD_REMOTE_DIR`  | (empty)         | Optional exact remote directory to skip the auto-matcher                              |
| `SORT_ORDER`                | `alphabetical`  | Order to cycle through torrents: `alphabetical`, `reverse`, `random`, `date_added`    |
| `LOG_LEVEL`                 | `INFO`          | Logging verbosity (DEBUG, INFO, WARNING, ERROR)                                       |

#### Preload Settings (Optional)

Enable and configure remote preload. See [Preload from Remote](#preload-from-remote-optional) for the conceptual overview.

| Variable             | Default         | Description                                                                  |
| -------------------- | --------------- | ---------------------------------------------------------------------------- |
| `PRELOAD_ENABLED`    | `false`         | Master switch — must be `true` for preload to run                            |
| `PRELOAD_HOST`       | (empty)         | Hostname or IP of the remote media server                                    |
| `PRELOAD_USER`       | (empty)         | SSH username on the remote                                                   |
| `PRELOAD_SSH_KEY`    | `/keys/id_rsa`  | Path to the SSH private key inside the container                             |
| `PRELOAD_REMOTE_DIR` | (empty)         | Remote directory to search (e.g., `/mnt/plex/Media/Movies`)                  |

#### Notification Settings (Optional)

After a rotation, repreload, or force-preload run, route23 can send a digest email summarizing what was preloaded and what was missed.

| Variable      | Default              | Description                                                          |
| ------------- | -------------------- | -------------------------------------------------------------------- |
| `SMTP_SERVER` | `route23-postfix`    | SMTP relay (defaults to the included postfix container)              |
| `SMTP_PORT`   | `25`                 | SMTP port                                                            |
| `FROM_EMAIL`  | `torrents@website.com` | Sender address                                                     |
| `NOTIFY_EMAIL`| (empty)              | Recipient for the digest. Leave blank to disable.                    |
| `SERVER_NAME` | `route23`            | Server label shown in the email header                               |

**Example Configuration for Heavy Load:**

```yaml
environment:
  BATCH_SIZE: 5 # Smaller batches
  ADD_DELAY: 60 # Wait longer between operations
  MAX_LOAD: 2.0 # Lower load threshold
  LOAD_WAIT: 60 # Wait longer when load is high
```

**Example Configuration for Powerful Server:**

```yaml
environment:
  BATCH_SIZE: 50 # Larger batches
  ROTATION_DAYS: 7 # Faster rotation
  ADD_DELAY: 5 # Shorter delays
  MAX_LOAD: 8.0 # Higher load tolerance
```

### Understanding Rotation Timeline

Calculate how long it takes to seed your entire collection:

**Formula:** `Total Time = (Total Torrents / BATCH_SIZE) × ROTATION_DAYS`

**Examples:**

| Collection Size | Batch Size | Rotation Days | Total Time  | Notes              |
| --------------- | ---------- | ------------- | ----------- | ------------------ |
| 1600 torrents   | 10         | 14            | ~6.1 years  | Default settings   |
| 1600 torrents   | 20         | 14            | ~3.1 years  | Larger batches     |
| 1600 torrents   | 20         | 7             | ~1.5 years  | Faster rotation    |
| 1600 torrents   | 50         | 7             | ~7.5 months | Aggressive seeding |
| 500 torrents    | 10         | 14            | ~1.9 years  | Smaller collection |
| 500 torrents    | 25         | 7             | ~4.8 months | Faster cycling     |

**Considerations:**

- **Longer rotation periods** = Better seeding ratios per torrent
- **Shorter rotation periods** = More of your collection gets seeded sooner
- **Larger batches** = Faster through collection, but higher resource usage
- **Smaller batches** = Better for low-power devices like Raspberry Pi

### State Management

route23 maintains persistent state in `./rutorrent/data/states/route23_state.json`:

```json
{
  "current_index": 80,
  "batch_started": "2026-05-12T03:42:31",
  "current_batch": [
    "/torrents/Dune (1984) [2160p] [BluRay] [x265] [10bit] [5.1] [YTS.MX].torrent",
    "/torrents/Treasure Buddies (2012) [720p] [BluRay] [YTS.MX].torrent"
  ],
  "completed_batches": 8,
  "sort_seed": 1234567890,
  "seeded_this_cycle": [
    "/torrents/Dune (1984) [2160p] [BluRay] [x265] [10bit] [5.1] [YTS.MX].torrent"
  ],
  "torrent_history": {
    "07d43e26a3c4...": {
      "times_seeded": 1,
      "path": "/torrents/Dune (1984) [2160p] [BluRay] [x265] [10bit] [5.1] [YTS.MX].torrent",
      "last_seeded": "2026-05-12T03:42:31"
    }
  }
}
```

**State File Details:**

- `current_index` — Number of torrents seeded so far in the current cycle
- `batch_started` — Timestamp when the current batch was added
- `current_batch` — Torrent files in the currently-seeding batch (consumed by repreload and force-preload)
- `completed_batches` — Number of batches completed across the lifetime of the install
- `sort_seed` — Random seed used to shuffle the collection when `SORT_ORDER=random` (kept stable within a cycle for reproducibility)
- `seeded_this_cycle` — Torrents that have already been seeded in the current pass through the collection (resets when the full library is exhausted)
- `torrent_history` — Per-torrent history keyed by file hash: how many times seeded and when last seeded

**Managing State:**

```bash
# View current state
cat ./rutorrent/data/states/route23_state.json

# Reset state (starts from beginning)
rm ./rutorrent/data/states/route23_state.json

# Backup state before major changes
cp ./rutorrent/data/states/route23_state.json ./rutorrent/data/states/route23_state.json.backup
```

## Additional Features

While route23 is the core automation, these additional features enhance the overall experience.

### ruTorrent Web Interface

Access the ruTorrent web interface for manual torrent management:

```
https://<server-ip>
```

**Features:**

- Manually add/remove torrents
- Monitor download/upload speeds
- View peer connections
- Check torrent details
- Pause/resume torrents

**Credentials:**
Use the username and password you configured with `htpasswd` during installation.

**Downloaded Files:**
Completed downloads are saved to `./rutorrent/downloads/complete/`

### Move Completed Downloads

The included `mvmovie` utility safely moves completed downloads to your media server:

```bash
# Install
mkdir -p ~/.local/bin/
cp ./exe/mvmovie ~/.local/bin/
chmod u+x ~/.local/bin/mvmovie

# Add to PATH (add to ~/.bashrc)
export PATH=~/.local/bin:$PATH

# Usage
mvmovie <movie-file> <destination>
```

The utility includes:

- Safe file moving with verification
- Automatic backup synchronization
- Plex library integration
- Error handling and rollback

## File Structure

```
route23/
├── compose.yml                # Main service definitions
├── Dockerfile                 # Rotator service container
├── .env                       # Environment variables (create this)
├── .env.example               # Template for .env
├── pyproject.toml             # Python project metadata
├── VERSION                    # Version stamp
├── logo.png                   # Project logo
├── src/
│   └── main.py                # Core rotation logic (rotator, preload, recovery modes)
├── nginx/
│   └── nginx.conf             # Reverse proxy configuration
├── exe/
│   ├── backup.sh              # Backup utility
│   ├── fix-torrent-permissions.sh  # Normalize ownership on the preload source
│   ├── force_preload.sh       # Repreload the whole current batch
│   ├── force_preload_one.sh   # Force preload a single torrent
│   ├── force_rotation.sh      # Trigger an immediate rotation
│   ├── monitor.sh             # Performance monitoring
│   ├── mvmovie                # Media file move utility
│   └── verify.sh              # Plex naming verification
├── rutorrent/
│   ├── data/
│   │   ├── rtorrent/
│   │   │   └── .rtorrent.rc   # rTorrent configuration
│   │   ├── scripts/
│   │   │   └── notification_agent.py  # Email notifications
│   │   └── states/
│   │       └── route23_state.json  # Rotator state JSON
│   ├── passwd/
│   │   └── rutorrent.htpasswd # Authentication (create this)
│   ├── torrents/              # Place .torrent files here
│   └── downloads/             # Downloaded content
│       └── route23/           # Downloads in rotation
├── docs/                      # VPN provider setup instructions
└── logs/                      # Log files (create this)
```

## Troubleshooting

### VPN Not Connecting

```bash
# Check VPN container logs
docker logs route23-vpn

# Verify WireGuard key is set
docker compose exec vpn env | grep WIREGUARD
```

### ruTorrent Authentication Errors

```bash
# Regenerate htpasswd file
htpasswd -Bbn username password > ./rutorrent/passwd/rutorrent.htpasswd

# Restart services
docker compose restart rutorrent nginx
```

### High System Load on Raspberry Pi

Reduce batch size and increase delays:

```yaml
environment:
  BATCH_SIZE: 5
  ADD_DELAY: 60
  MAX_LOAD: 2.0
```

### Check Rotator Status

```bash
docker compose run --rm -e SHOW_STATUS=true app
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
