#!/bin/bash
#
# Re-run preload against every torrent in the current batch. Torrents already
# at 100% are skipped. Use after fixing connectivity to the remote media
# machine, or after restoring its data.
#
# Usage:
#   ./exe/force_preload.sh
#
# Runs in the background so it survives a dropped SSH session. Tail the log to
# follow along. `docker compose run` enables the service's own profile
# automatically, so no --profile flag is needed.

set -euo pipefail

mkdir -p ./logs
LOG_FILE="./logs/route23_preload.log"

docker compose run --rm -e REPRELOAD=true app > "${LOG_FILE}" 2>&1 &

echo "Repreload started in background. Tail with: tail -f ${LOG_FILE}"
