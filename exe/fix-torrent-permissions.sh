#!/bin/bash
#
# Fix ownership and permissions on a synced torrents directory.
# Install at /home/russ/bin/fix-torrent-permissions.sh on each remote device.
# Make sure it is executable: chmod +x /home/russ/bin/fix-torrent-permissions.sh
#
# Usage: fix-torrent-permissions.sh <directory>

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <directory>" >&2
    exit 2
fi

TARGET_DIR="$1"
OWNER="russ"
GROUP="russ"

if [[ ! -d "${TARGET_DIR}" ]]; then
    echo "[ERROR] Directory does not exist: ${TARGET_DIR}" >&2
    exit 1
fi

echo "[INFO] Fixing permissions on ${TARGET_DIR}"

# Ownership: russ:russ for everything underneath
chown -R "${OWNER}:${GROUP}" "${TARGET_DIR}" 2>/dev/null || \
    sudo -n chown -R "${OWNER}:${GROUP}" "${TARGET_DIR}"

# Directories: 755, files: 644
find "${TARGET_DIR}" -type d -exec chmod 755 {} +
find "${TARGET_DIR}" -type f -exec chmod 644 {} +

echo "[INFO] Permissions fixed"
