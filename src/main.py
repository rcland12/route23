#!/usr/bin/env python3
"""
Torrent Rotator - Cycles through a folder of .torrent files,
seeding batches of N torrents for a configured period before rotating.

Optimized for low-power devices like Raspberry Pi with load monitoring
and configurable delays between operations.

Environment Variables:
    TORRENT_DIR         - Directory containing .torrent files (default: /torrents)
    STATE_FILE          - Path to state JSON file (default: /states/route23_state.json)
    RTORRENT_URL        - rtorrent XMLRPC endpoint (default: http://localhost:8080/RPC2)
    RTORRENT_USER       - rtorrent username for authentication (optional)
    RTORRENT_PASS       - rtorrent password for authentication (optional)
    BATCH_SIZE          - Number of torrents per batch (default: 20)
    ROTATION_DAYS       - Days between rotations (default: 14)
    DOWNLOAD_DIR        - Download directory for torrent data (default: /downloads/route23)

    Performance Settings:
    ADD_DELAY           - Seconds to wait between adding torrents (default: 30)
    REMOVE_DELAY        - Seconds to wait between removing torrents (default: 5)
    MAX_LOAD            - Max system load before waiting (default: 4.0)
    LOAD_WAIT           - Seconds to wait when load is high (default: 30)
    STARTUP_DELAY       - Seconds to wait after removals before adding (default: 10)

    Action Flags:
    FORCE_ROTATION      - Set to "true" to force rotation (default: false)
    DELETE_DATA         - Set to "true" to delete data on rotation (default: false)
    SHOW_STATUS         - Set to "true" to only show status (default: false)
    LOG_LEVEL           - Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
"""

import hashlib
import json
import logging
import os
import time
import xmlrpc.client
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, urlunparse


def get_env(key: str, default: str = "") -> str:
    """Get environment variable with default."""
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.environ.get(key, "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    if value in ("false", "0", "no", "off"):
        return False
    return default


def get_env_int(key: str, default: int) -> int:
    """Get integer environment variable."""
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def get_env_float(key: str, default: float) -> float:
    """Get float environment variable."""
    try:
        return float(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def build_rtorrent_url() -> str:
    """Build rtorrent URL with optional authentication."""
    base_url = get_env("RTORRENT_URL", "http://localhost:8080/RPC2")
    user = get_env("RTORRENT_USER")
    password = get_env("RTORRENT_PASS")

    if user and password:
        parsed = urlparse(base_url)
        netloc = f"{user}:{password}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        authenticated_url = urlunparse(
            (
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
        return authenticated_url

    return base_url


CONFIG = {
    "torrent_dir": get_env("TORRENT_DIR", "/torrents"),
    "state_file": get_env("STATE_FILE", "/states/route23_state.json"),
    "rtorrent_url": build_rtorrent_url(),
    "batch_size": get_env_int("BATCH_SIZE", 20),
    "rotation_days": get_env_int("ROTATION_DAYS", 14),
    "download_dir": get_env("DOWNLOAD_DIR", "/downloads/route23"),
    "add_delay": get_env_float("ADD_DELAY", 30.0),
    "remove_delay": get_env_float("REMOVE_DELAY", 5.0),
    "max_load": get_env_float("MAX_LOAD", 4.0),
    "load_wait": get_env_float("LOAD_WAIT", 30.0),
    "startup_delay": get_env_float("STARTUP_DELAY", 10.0),
}


FORCE_ROTATION = get_env_bool("FORCE_ROTATION", False)
DELETE_DATA = get_env_bool("DELETE_DATA", False)
SHOW_STATUS = get_env_bool("SHOW_STATUS", False)


log_level = get_env("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TorrentRotator:
    def __init__(self, config: dict):
        self.config = config
        self.state = self.load_state()
        self.rtorrent = xmlrpc.client.ServerProxy(config["rtorrent_url"])

    def get_system_load(self) -> float:
        """Get current system load average (1 minute)."""
        try:
            with open("/proc/loadavg", "r") as f:
                return float(f.read().split()[0])
        except Exception:
            return 0.0

    def wait_for_low_load(self):
        """Wait until system load drops below threshold."""
        max_load = self.config["max_load"]
        load_wait = self.config["load_wait"]

        current_load = self.get_system_load()
        while current_load > max_load:
            logger.info(
                f"System load {current_load:.2f} exceeds {max_load:.2f}, waiting {load_wait}s..."
            )
            time.sleep(load_wait)
            current_load = self.get_system_load()

        return current_load

    def throttled_sleep(self, seconds: float, reason: str = ""):
        """Sleep with logging for transparency."""
        if seconds > 0:
            if reason:
                logger.debug(f"Waiting {seconds}s ({reason})")
            time.sleep(seconds)

    def load_state(self) -> dict:
        """Load state from file or create initial state."""
        state_path = Path(self.config["state_file"])
        if state_path.exists():
            with open(state_path, "r") as f:
                return json.load(f)
        return {
            "current_index": 0,
            "batch_started": None,
            "current_batch": [],
            "completed_batches": 0,
            "torrent_history": {},
        }

    def save_state(self):
        """Persist state to file."""
        state_path = Path(self.config["state_file"])
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w") as f:
            json.dump(self.state, f, indent=2, default=str)
        logger.info(f"State saved to {state_path}")

    def get_torrent_files(self) -> list:
        """Get sorted list of all .torrent files."""
        torrent_dir = Path(self.config["torrent_dir"])
        if not torrent_dir.exists():
            logger.error(f"Torrent directory not found: {torrent_dir}")
            return []

        torrents = sorted(torrent_dir.glob("*.torrent"))
        logger.info(f"Found {len(torrents)} torrent files")
        return [str(t) for t in torrents]

    def get_torrent_hash(self, torrent_path: str) -> str:
        """Get info hash from a .torrent file (simplified - uses file hash)."""
        with open(torrent_path, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest().upper()

    def get_active_torrents(self) -> list:
        """Get list of currently active torrent hashes in rtorrent."""
        try:
            return self.rtorrent.download_list()
        except Exception as e:
            logger.error(f"Failed to get active torrents: {e}")
            return []

    def add_torrent(self, torrent_path: str) -> bool:
        """Add a torrent to rtorrent."""
        try:
            with open(torrent_path, "rb") as f:
                torrent_data = f.read()

            self.rtorrent.load.raw_start(
                "",
                xmlrpc.client.Binary(torrent_data),
                f"d.directory.set={self.config['download_dir']}",
            )
            logger.info(f"Added torrent: {Path(torrent_path).name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add torrent {torrent_path}: {e}")
            return False

    def remove_torrent(
        self, info_hash: str, delete_data: bool = False
    ) -> bool:
        """Remove a torrent from rtorrent."""
        try:
            if delete_data:
                self.rtorrent.d.stop(info_hash)
                self.rtorrent.d.close(info_hash)
                self.rtorrent.d.erase(info_hash)
            else:
                self.rtorrent.d.stop(info_hash)
                self.rtorrent.d.close(info_hash)
                self.rtorrent.d.erase(info_hash)
            logger.info(f"Removed torrent: {info_hash}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove torrent {info_hash}: {e}")
            return False

    def remove_all_active(self, delete_data: bool = False):
        """Remove all currently active torrents with delays."""
        active = self.get_active_torrents()
        total = len(active)
        logger.info(f"Removing {total} active torrents")

        for i, info_hash in enumerate(active, 1):
            self.wait_for_low_load()

            logger.info(f"Removing torrent {i}/{total}: {info_hash[:8]}...")
            self.remove_torrent(info_hash, delete_data)

            if i < total:
                self.throttled_sleep(
                    self.config["remove_delay"], "between removals"
                )

    def should_rotate(self) -> bool:
        """Check if it's time to rotate to the next batch."""
        if self.state["batch_started"] is None:
            return True

        started = datetime.fromisoformat(self.state["batch_started"])
        rotation_period = timedelta(days=self.config["rotation_days"])
        time_elapsed = datetime.now() - started

        if time_elapsed >= rotation_period:
            logger.info(f"Rotation period elapsed ({time_elapsed.days} days)")
            return True

        remaining = rotation_period - time_elapsed
        logger.info(
            f"Time until next rotation: {remaining.days} days, {remaining.seconds // 3600} hours"
        )
        return False

    def get_next_batch(self) -> list:
        """Get the next batch of torrent files to seed."""
        all_torrents = self.get_torrent_files()
        if not all_torrents:
            return []

        batch_size = self.config["batch_size"]
        start_idx = self.state["current_index"]

        if start_idx >= len(all_torrents):
            start_idx = 0
            self.state["current_index"] = 0
            logger.info("Wrapped around to beginning of torrent list")

        end_idx = min(start_idx + batch_size, len(all_torrents))
        batch = all_torrents[start_idx:end_idx]

        if len(batch) < batch_size and start_idx > 0:
            remaining = batch_size - len(batch)
            batch.extend(all_torrents[:remaining])

        logger.info(
            f"Next batch: indices {start_idx} to {end_idx} ({len(batch)} torrents)"
        )
        return batch

    def rotate(self, delete_old_data: bool = False):
        """Perform the rotation: remove old batch, add new batch with throttling."""
        logger.info("=" * 50)
        logger.info("Starting rotation")

        self.remove_all_active(delete_data=delete_old_data)

        logger.info(
            f"Waiting {self.config['startup_delay']}s for system to settle..."
        )
        self.throttled_sleep(
            self.config["startup_delay"], "post-removal cooldown"
        )

        new_batch = self.get_next_batch()
        if not new_batch:
            logger.warning("No torrents found to add!")
            return

        total = len(new_batch)
        added = []

        logger.info(
            f"Adding {total} torrents with {self.config['add_delay']}s delay between each"
        )

        for i, torrent_path in enumerate(new_batch, 1):
            current_load = self.wait_for_low_load()
            logger.info(
                f"[{i}/{total}] Adding: {Path(torrent_path).name} (load: {current_load:.2f})"
            )

            if self.add_torrent(torrent_path):
                added.append(torrent_path)
                file_hash = self.get_torrent_hash(torrent_path)
                if file_hash not in self.state["torrent_history"]:
                    self.state["torrent_history"][file_hash] = {
                        "times_seeded": 0,
                        "path": torrent_path,
                    }
                self.state["torrent_history"][file_hash]["times_seeded"] += 1
                self.state["torrent_history"][file_hash]["last_seeded"] = (
                    datetime.now().isoformat()
                )

            if i < total:
                self.throttled_sleep(
                    self.config["add_delay"], "between additions"
                )

        self.state["current_batch"] = added
        self.state["batch_started"] = datetime.now().isoformat()
        self.state["current_index"] += len(new_batch)
        self.state["completed_batches"] += 1

        self.save_state()
        logger.info(f"Rotation complete. Added {len(added)}/{total} torrents.")
        logger.info(f"Next rotation in {self.config['rotation_days']} days")

    def status(self):
        """Print current status."""
        all_torrents = self.get_torrent_files()
        active = self.get_active_torrents()
        current_load = self.get_system_load()

        print("\n" + "=" * 50)
        print("TORRENT ROTATOR STATUS")
        print("=" * 50)
        print(f"Total .torrent files:     {len(all_torrents)}")
        print(f"Currently active:         {len(active)}")
        print(f"Batch size:               {self.config['batch_size']}")
        print(f"Rotation period:          {self.config['rotation_days']} days")
        print(f"Completed batches:        {self.state['completed_batches']}")
        print(f"Current index:            {self.state['current_index']}")

        print("-" * 50)
        print("PERFORMANCE SETTINGS")
        print("-" * 50)
        print(f"Current system load:      {current_load:.2f}")
        print(f"Max load threshold:       {self.config['max_load']}")
        print(f"Add delay:                {self.config['add_delay']}s")
        print(f"Remove delay:             {self.config['remove_delay']}s")
        print(f"Load wait time:           {self.config['load_wait']}s")

        est_add_time = self.config["batch_size"] * self.config["add_delay"]
        print(
            f"Est. rotation time:       ~{est_add_time // 60:.0f}m {est_add_time % 60:.0f}s"
        )

        if self.state["batch_started"]:
            started = datetime.fromisoformat(self.state["batch_started"])
            elapsed = datetime.now() - started
            remaining = timedelta(days=self.config["rotation_days"]) - elapsed
            print("-" * 50)
            print(
                f"Batch started:            {started.strftime('%Y-%m-%d %H:%M')}"
            )
            print(
                f"Time elapsed:             {elapsed.days}d {elapsed.seconds // 3600}h"
            )
            if remaining.total_seconds() > 0:
                print(
                    f"Time remaining:           {remaining.days}d {remaining.seconds // 3600}h"
                )
            else:
                print("Status:                   READY TO ROTATE")
        else:
            print("-" * 50)
            print("Status:                   NOT STARTED")

        print("=" * 50 + "\n")

    def run(self, force: bool = False, delete_data: bool = False):
        """Main run method - check if rotation needed and perform if so."""
        if force:
            logger.info("Forced rotation requested")
            self.rotate(delete_old_data=delete_data)
        elif self.should_rotate():
            self.rotate(delete_old_data=delete_data)
        else:
            logger.info("No rotation needed at this time")


def main():
    """Main entry point - uses environment variables for configuration."""
    logger.info("Torrent Rotator starting")

    safe_config = CONFIG.copy()
    if get_env("RTORRENT_PASS"):
        parsed = urlparse(safe_config["rtorrent_url"])
        masked_netloc = f"{parsed.username}:****@{parsed.hostname}"
        if parsed.port:
            masked_netloc += f":{parsed.port}"
        safe_config["rtorrent_url"] = urlunparse(
            (
                parsed.scheme,
                masked_netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
    logger.info(f"Configuration: {json.dumps(safe_config, indent=2)}")

    rotator = TorrentRotator(CONFIG)

    if SHOW_STATUS:
        rotator.status()
    else:
        rotator.run(force=FORCE_ROTATION, delete_data=DELETE_DATA)


if __name__ == "__main__":
    main()
