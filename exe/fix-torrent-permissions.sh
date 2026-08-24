#!/bin/bash
#
# Fix ownership and permissions on a synced torrents directory.
# Install anywhere on PATH (e.g. ~/bin/fix-torrent-permissions.sh) on each
# remote device and make it executable: chmod +x fix-torrent-permissions.sh
#
# Ownership defaults to the invoking user. When run under sudo, it falls back
# to the user who invoked sudo rather than root. Override either with the
# TORRENT_OWNER / TORRENT_GROUP environment variables.
#
# Usage: fix-torrent-permissions.sh <directory>

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <directory>" >&2
    exit 2
fi

TARGET_DIR="$1"

# Prefer an explicit override, then the sudo-invoking user, then whoever we are.
OWNER="${TORRENT_OWNER:-${SUDO_USER:-$(id -un)}}"
GROUP="${TORRENT_GROUP:-$(id -gn "${OWNER}" 2>/dev/null || echo "${OWNER}")}"

DIR_MODE="${TORRENT_DIR_MODE:-755}"
FILE_MODE="${TORRENT_FILE_MODE:-644}"

if ! id -u "${OWNER}" >/dev/null 2>&1; then
    echo "[ERROR] User does not exist: ${OWNER}" >&2
    exit 1
fi

if [[ ! -d "${TARGET_DIR}" ]]; then
    echo "[ERROR] Directory does not exist: ${TARGET_DIR}" >&2
    exit 1
fi

# Resolve to an absolute path so the log line is unambiguous.
TARGET_DIR="$(cd "${TARGET_DIR}" && pwd -P)"

echo "[INFO] Fixing permissions on ${TARGET_DIR} (owner ${OWNER}:${GROUP})"

if ! chown -R "${OWNER}:${GROUP}" "${TARGET_DIR}" 2>/dev/null; then
    if ! sudo -n chown -R "${OWNER}:${GROUP}" "${TARGET_DIR}" 2>/dev/null; then
        echo "[ERROR] Could not change ownership (no permission, and passwordless sudo unavailable)" >&2
        exit 1
    fi
fi

find "${TARGET_DIR}" -type d -exec chmod "${DIR_MODE}" {} +
find "${TARGET_DIR}" -type f -exec chmod "${FILE_MODE}" {} +

echo "[INFO] Permissions fixed"