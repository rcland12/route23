#!/bin/bash

chown -R ${USER}:${USER} /mnt/plex/Media
find /mnt/plex/Media -type d -exec chmod 755 {} +
find /mnt/plex/Media -type f -exec chmod 644 {} +

rsync -avh --delete --itemize-changes --exclude='lost+found' /mnt/plex/ /mnt/backup/

echo "Backup complete!"
