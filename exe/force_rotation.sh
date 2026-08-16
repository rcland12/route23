#!/bin/bash
#
# Force an immediate rotation, regardless of how much of the rotation period
# is left. Removes every torrent currently loaded in rtorrent (deleting their
# data when DELETE_DATA is true) and adds the next batch.
#
# Usage:
#   ./exe/force_rotation.sh
#
# Runs in the background so it survives a dropped SSH session. Tail the log to
# follow along. `docker compose run` enables the service's own profile
# automatically, so no --profile flag is needed.

set -euo pipefail

mkdir -p ./logs
LOG_FILE="./logs/route23_rotation.log"

docker compose run --rm -e FORCE_ROTATION=true app > "${LOG_FILE}" 2>&1 &

echo "Force rotation started in background. Tail with: tail -f ${LOG_FILE}"
