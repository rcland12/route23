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

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
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

**Why "route23"?** The name comes from the 23 different VPN providers supported through Gluetun integration - offering you flexibility to choose the VPN service that best fits your needs, whether that's port forwarding support, privacy features, or price.

**What it does:** route23 automatically manages your torrent seeding by rotating through your collection in batches. Instead of trying to seed hundreds or thousands of torrents simultaneously (which would overwhelm most hardware), route23 intelligently seeds small batches for configurable periods, then automatically cycles to the next batch. Over time, your entire collection gets seeded fairly and efficiently.

**The Stack:** route23 is built on a foundation of proven technologies - ruTorrent for torrent management, Gluetun for VPN protection (supporting all 23 providers), and Postfix for email notifications. These supporting services exist to enable the core route23 rotation functionality.

## Features

**Core route23 Features:**

- **Intelligent Batch Rotation** — Automatically cycles through your torrent library in manageable batches
- **Time-Based Scheduling** — Configurable rotation periods (default: 14 days per batch)
- **Persistent State Management** — Remembers exactly where it left off across restarts
- **Load-Aware Operations** — Monitors system load and throttles operations for low-power devices
- **Progress Tracking** — Real-time status reporting showing progress through your collection

**Supporting Infrastructure:**

- **VPN Protection** — All torrent traffic routed through your choice of 23+ VPN providers (Gluetun)
- **Web Interface** — Full ruTorrent UI for manual torrent management
- **Email Notifications** — SMTP relay for torrent completion alerts (optional)
- **Docker-Based** — Easy deployment and management with docker-compose

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Network                        │
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐    │
│  │  nginx   │───▶│   ruTorrent  │───▶│   VPN (Gluetun)  │──▶ │ Internet
│  │  :8080   │    │   Web UI     │    │   NordVPN/WG     │    │
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

### 2. Create Environment File

Create a `.env` file with all required variables:

```bash
# VPN Configuration (required)
VPN_SERVICE="nordvpn"                    # Your VPN provider
NORDVPN_TOKEN=your_token_here            # Provider-specific token/credentials
WIREGUARD_PRIVATE_KEY=your_key_here      # Get from VPN provider API
PRIVATE_SUBNET="192.168.0.0/24"          # Your local network subnet

# System Configuration (required)
TIMEZONE="America/New_York"              # Your timezone
SERVER_NAME="route23"                    # Server hostname

# ruTorrent Authentication (required)
RTORRENT_USER=your_username              # Web UI username
RTORRENT_PASS=your_password              # Web UI password

# Email Notifications (optional)
POSTFIX_EMAIL=youremail@gmail.com        # Your email address
POSTFIX_PASSWORD=your_app_password       # Email app password
```

**Get your VPN credentials:** See [VPN Configuration](#vpn-configuration) for provider-specific setup guides.

**Find your private subnet:**
```bash
ip route show | awk '/proto kernel/ && /192\.168\./ {print $1}'
```

### 3. Create ruTorrent Authentication File

```bash
# Install htpasswd if needed
sudo apt update && sudo apt install apache2-utils

# Create authentication file (must match RTORRENT_USER/RTORRENT_PASS from .env)
htpasswd -Bbn your_username your_password > ./rutorrent/passwd/rutorrent.htpasswd
```

### 4. Start Services

```bash
docker compose up -d nginx
```

Access the web UI at `http://<your-server-ip>:8080` using the credentials you created above.

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

#### 4. Update docker-compose.yaml (if needed)

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

#### 4. Update docker-compose.yaml

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

#### 3. Update docker-compose.yaml

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

#### 4. Update docker-compose.yaml

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

#### 3. Update docker-compose.yaml

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

#### 3. Update docker-compose.yaml

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
3. Alternatively, remove the postfix service from `docker-compose.yaml`

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
- All output is logged to `./logs/rotator.log`

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

Configure route23's behavior through environment variables in `docker-compose.yaml`:

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

| Variable         | Default | Description                                     |
| ---------------- | ------- | ----------------------------------------------- |
| `FORCE_ROTATION` | `false` | Force immediate rotation regardless of time     |
| `SHOW_STATUS`    | `false` | Display status information only (no changes)    |
| `LOG_LEVEL`      | `INFO`  | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |

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
  "current_index": 10,
  "batch_started": "2024-01-15T03:00:00",
  "completed_batches": 1,
  "total_torrents": 1600,
  "batch_size": 10,
  "rotation_days": 14
}
```

**State File Details:**

- `current_index` - Position in your torrent collection (next torrent to add)
- `batch_started` - Timestamp when current batch was added
- `completed_batches` - Number of batches that have been completed
- `total_torrents` - Total torrents in your collection
- `batch_size` - Configured batch size
- `rotation_days` - Configured rotation period

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
http://<server-ip>:8080
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
├── docker-compose.yaml     # Main service definitions
├── Dockerfile              # Rotator service container
├── .env                    # Environment variables (create this)
├── logo.png                # Project logo
├── src/
│   └── main.py             # Core rotation logic
├── nginx/
│   └── nginx.conf          # Reverse proxy configuration
├── exe/
│   ├── mvmovie             # Media file utility
│   ├── monitor.sh          # Performance monitoring
│   └── backup.sh           # Backup utility
├── rutorrent/
│   ├── data/
│   │   ├── rtorrent/
│   │   │   └── .rtorrent.rc  # rTorrent configuration
│   │   └── scripts/
│   │       └── notification_agent.py  # Email notifications
│   │   └── states/
│   │       └── route23_state.json  # Rotator state JSON
│   ├── passwd/
│   │   └── rutorrent.htpasswd  # Authentication (create this)
│   └── torrents/           # Place .torrent files here
├── downloads/              # Downloaded content
│   └── complete/           # Completed downloads
│   └── temp/               # Temporary downloads
│   └── route23/            # Downloads in rotation
├── docs/                   # VPN providers setup instructions
└── logs/                   # Log files (create this)
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
htpasswd -Bbn username password > ./passwd/rutorrent.htpasswd

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

---

<p align="center">
  Made for the self-hosting community
</p>
