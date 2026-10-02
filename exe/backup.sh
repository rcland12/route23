#!/bin/bash

# rsync --delete from an empty or unmounted source would wipe the backup.
if [ -z "$(ls -A /mnt/plex/Media 2>/dev/null)" ]; then
    echo "/mnt/plex/Media is missing or empty, refusing to sync" >&2
    exit 1
fi

chown -R "${USER}:${USER}" /mnt/plex/Media
find /mnt/plex/Media -type d -exec chmod 755 {} +
find /mnt/plex/Media -type f -exec chmod 644 {} +

rsync -avh --delete --itemize-changes --exclude='lost+found' /mnt/plex/ /mnt/backup/

echo "Backup complete!"
