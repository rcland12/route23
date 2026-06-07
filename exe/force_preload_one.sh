#!/bin/bash
#
# Force preload of a single torrent.
#
# Usage:
#   ./exe/force_preload_one.sh <torrent-substring> [<remote-dir-override>]
#
# Examples:
#   ./exe/force_preload_one.sh "mississippi"
#   ./exe/force_preload_one.sh "mississippi" "Mississippi Burning (1988) {imdb-tt0095647}"
#
# The substring is matched case-insensitively against .torrent filenames in
# the current batch (and falls back to the full torrent dir if no match).
# If the remote-dir-override is given, it is used verbatim — the auto-matcher
# is skipped. Use this when the Plex directory name doesn't match what the
# matcher would derive from the torrent name.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <torrent-substring> [<remote-dir-override>]" >&2
    exit 2
fi

TORRENT_SUBSTR="$1"
REMOTE_DIR_OVERRIDE="${2:-}"

mkdir -p ./logs
LOG_FILE="./logs/route23_force_preload.log"

docker compose run --rm \
    --profile route23 \
    -e FORCE_PRELOAD_TORRENT="${TORRENT_SUBSTR}" \
    -e FORCE_PRELOAD_REMOTE_DIR="${REMOTE_DIR_OVERRIDE}" \
    app > "${LOG_FILE}" 2>&1 &

echo "Force preload started in background. Tail with: tail -f ${LOG_FILE}"
