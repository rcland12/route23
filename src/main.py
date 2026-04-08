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
    DELETE_DATA         - Set to "true" to delete downloaded files on rotation (default: false)
    SHOW_STATUS         - Set to "true" to only show status (default: false)
    REPRELOAD           - Set to "true" to re-run preload against the current batch (default: false)
    SORT_ORDER          - Order to cycle through torrents: alphabetical, reverse, random, date_added (default: alphabetical)
    LOG_LEVEL           - Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)

    Preload Settings (optional):
    PRELOAD_ENABLED     - Set to "true" to copy files from a remote machine before seeding (default: false)
    PRELOAD_HOST        - Hostname or IP of the remote machine
    PRELOAD_USER        - SSH username for the remote machine
    PRELOAD_SSH_KEY     - Path to SSH private key inside the container (default: /keys/id_rsa)
    PRELOAD_REMOTE_DIR  - Directory on the remote machine to search for matching files

    Notification Settings (optional):
    SMTP_SERVER         - Postfix hostname (default: route23-postfix)
    SMTP_PORT           - Postfix port (default: 25)
    FROM_EMAIL          - Sender address (default: torrents@website.com)
    NOTIFY_EMAIL        - Recipient address for preload digest emails
    SERVER_NAME         - Server label shown in email headers (default: route23)
"""

import hashlib
import json
import logging
import os
import random
import re
import shutil
import smtplib
import subprocess
import time
import xmlrpc.client
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlparse, urlunparse


def _bdecode(data: bytes, idx: int = 0):
    """Minimal bencode decoder."""
    b = data[idx : idx + 1]
    if b == b"d":
        d, idx = {}, idx + 1
        while data[idx : idx + 1] != b"e":
            k, idx = _bdecode(data, idx)
            v, idx = _bdecode(data, idx)
            d[k] = v
        return d, idx + 1
    elif b == b"l":
        lst, idx = [], idx + 1
        while data[idx : idx + 1] != b"e":
            v, idx = _bdecode(data, idx)
            lst.append(v)
        return lst, idx + 1
    elif b == b"i":
        end = data.index(b"e", idx + 1)
        return int(data[idx + 1 : end]), end + 1
    else:
        colon = data.index(b":", idx)
        n = int(data[idx:colon])
        s = colon + 1
        return data[s : s + n], s + n


def _bdecode_torrent(data: bytes) -> dict:
    result, _ = _bdecode(data, 0)
    return result


def parse_torrent(torrent_path: str) -> dict:
    """Return torrent name and expected file list from a .torrent file."""
    with open(torrent_path, "rb") as f:
        data = f.read()
    info = _bdecode_torrent(data)[b"info"]
    name = info[b"name"].decode("utf-8", errors="replace")
    if b"files" in info:
        files = [
            {
                "path": "/".join(
                    p.decode("utf-8", errors="replace") for p in entry[b"path"]
                ),
                "length": entry[b"length"],
            }
            for entry in info[b"files"]
        ]
    else:
        files = [{"path": name, "length": info[b"length"]}]
    return {"name": name, "files": files, "multi_file": b"files" in info}


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
    "sort_order": get_env("SORT_ORDER", "alphabetical").lower(),
    "download_dir": get_env("DOWNLOAD_DIR", "/downloads/route23"),
    "add_delay": get_env_float("ADD_DELAY", 30.0),
    "remove_delay": get_env_float("REMOVE_DELAY", 5.0),
    "max_load": get_env_float("MAX_LOAD", 4.0),
    "load_wait": get_env_float("LOAD_WAIT", 30.0),
    "startup_delay": get_env_float("STARTUP_DELAY", 10.0),
    "preload_host": get_env("PRELOAD_HOST", ""),
    "preload_user": get_env("PRELOAD_USER", ""),
    "preload_ssh_key": get_env("PRELOAD_SSH_KEY", "/keys/id_rsa"),
    "preload_remote_dir": get_env("PRELOAD_REMOTE_DIR", ""),
    "smtp_server": get_env("SMTP_SERVER", "route23-postfix"),
    "smtp_port": get_env_int("SMTP_PORT", 25),
    "from_email": get_env("FROM_EMAIL", "torrents@website.com"),
    "notify_email": get_env("NOTIFY_EMAIL", ""),
    "server_name": get_env("SERVER_NAME", "route23"),
}


FORCE_ROTATION = get_env_bool("FORCE_ROTATION", False)
DELETE_DATA = get_env_bool("DELETE_DATA", False)
SHOW_STATUS = get_env_bool("SHOW_STATUS", False)
PRELOAD_ENABLED = get_env_bool("PRELOAD_ENABLED", False)
REPRELOAD = get_env_bool("REPRELOAD", False)


log_level = get_env("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _format_size(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.2f} {units[idx]}"


@dataclass
class PreloadResult:
    torrent_name: str
    success: bool
    remote_dir: str = ""
    staged_files: list[dict] = field(default_factory=list)
    reason: str = ""

    def total_bytes(self) -> int:
        return sum(f["size"] for f in self.staged_files)


class PreloadManager:
    """Copies files from a remote machine to pre-seed newly added torrents."""

    VIDEO_EXTENSIONS = {
        ".mkv",
        ".mp4",
        ".avi",
        ".m4v",
        ".mov",
        ".wmv",
        ".ts",
        ".m2ts",
    }

    def __init__(self, config: dict):
        self.host = config["preload_host"]
        self.user = config["preload_user"]
        self.key = config["preload_ssh_key"]
        self.remote_dir = config["preload_remote_dir"]

    def _ssh(self, cmd: str, timeout: int = 30) -> tuple[bool, str]:
        result = subprocess.run(
            [
                "ssh",
                "-i",
                self.key,
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "BatchMode=yes",
                f"{self.user}@{self.host}",
                cmd,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout.strip()

    def _normalize(self, text: str) -> str:
        text = re.sub(r"[._\-]", " ", text)
        text = text.lower().replace("&", "and")
        text = re.sub(r"[^a-z0-9 ]", "", text)
        return " ".join(text.split())

    def _extract_title_year(self, torrent_name: str) -> tuple[str, int | None]:
        """Parse a torrent name like 'Movie.Title.2020.1080p...' into (title, year).

        Uses the last year-like token found so that titles beginning with a
        year (e.g. '2001: A Space Odyssey') don't get mistaken for the release year.
        """
        normalized = re.sub(r"[._]", " ", torrent_name)
        matches = list(re.finditer(r"\b((?:19|20)\d{2})\b", normalized))
        if matches:
            match = matches[-1]
            year = int(match.group(1))
            title = self._normalize(normalized[: match.start()])
            return title, year
        return self._normalize(normalized), None

    def _parse_plex_dirname(self, dirname: str) -> tuple[str, int | None]:
        """Parse a Plex dir name like 'Movie Title (2020) {imdb-id}' into (title, year)."""
        match = re.match(r"^(.+?)\s*\((\d{4})\)", dirname)
        if match:
            return self._normalize(match.group(1)), int(match.group(2))
        return self._normalize(dirname), None

    def find_remote_match(self, torrent_name: str) -> str | None:
        """Return the remote directory name that best matches the torrent."""
        title, year = self._extract_title_year(torrent_name)
        logger.debug(f"Preload: searching for title='{title}' year={year}")

        ok, output = self._ssh(f'ls -1 "{self.remote_dir}"')
        if not ok or not output:
            logger.warning("Preload: could not list remote directory")
            return None

        for dirname in output.splitlines():
            rtitle, ryear = self._parse_plex_dirname(dirname)
            if year and ryear and year != ryear:
                continue
            if title == rtitle:
                logger.info(f"Preload: matched '{dirname}'")
                return dirname

        logger.debug(f"Preload: no match found for '{torrent_name}'")
        return None

    def _list_remote_video_files_with_sizes(
        self, remote_path: str
    ) -> dict[int, str]:
        """Return a {size_bytes: remote_filepath} map for video files in remote_path.

        If two files share the same size (ambiguous), that size key is set to None
        so the caller can detect and skip the collision.
        """
        ext_pattern = "|".join(
            re.escape(e.lstrip(".")) for e in self.VIDEO_EXTENSIONS
        )
        cmd = (
            f'find "{remote_path}" -type f -printf "%s\\t%p\\n"'
            f' | grep -Ei "\\.({ext_pattern})$"'
        )
        ok, output = self._ssh(cmd, timeout=15)
        if not ok or not output:
            return {}

        size_map: dict[int, str | None] = {}
        for line in output.splitlines():
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            try:
                size = int(parts[0])
            except ValueError:
                continue
            path = parts[1]
            if size in size_map:
                logger.warning(
                    f"Preload: two remote files share size {size} bytes "
                    f"({size_map[size]} and {path}) — will not use either"
                )
                size_map[size] = None
            else:
                size_map[size] = path

        return size_map

    def fetch_and_stage(
        self, remote_dirname: str, torrent_info: dict, download_dir: str
    ) -> tuple[list[dict] | None, str]:
        """Match torrent files to remote files by size, SCP, and rename in place.

        Returns (staged_files, reason) where staged_files is None on failure.
        """
        remote_path = f"{self.remote_dir}/{remote_dirname}"
        torrent_name = torrent_info["name"]
        is_multi = torrent_info["multi_file"]

        torrent_videos = [
            f
            for f in torrent_info["files"]
            if Path(f["path"]).suffix.lower() in self.VIDEO_EXTENSIONS
        ]
        if not torrent_videos:
            return None, "torrent contains no video files"

        size_map = self._list_remote_video_files_with_sizes(remote_path)
        if not size_map:
            reason = f"no video files found in remote '{remote_dirname}'"
            logger.warning(f"Preload: {reason} — skipping '{torrent_name}'")
            return None, reason

        pairs = []
        for tf in torrent_videos:
            expected_size = tf["length"]
            remote_file = size_map.get(expected_size)
            if remote_file is None:
                if expected_size in size_map:
                    reason = f"size {_format_size(expected_size)} is ambiguous (two remote files match)"
                else:
                    reason = f"no remote file matches expected size {_format_size(expected_size)} for '{Path(tf['path']).name}'"
                logger.warning(
                    f"Preload: {reason} — skipping '{torrent_name}'"
                )
                return None, reason
            pairs.append((tf, remote_file))

        staged_files = []
        for torrent_file, remote_file in pairs:
            if is_multi:
                dest = Path(download_dir) / torrent_name / torrent_file["path"]
            else:
                dest = Path(download_dir) / torrent_file["path"]

            dest.parent.mkdir(parents=True, exist_ok=True)

            logger.info(
                f"Preload: {Path(remote_file).name} ({_format_size(torrent_file['length'])})"
                f" → {dest.relative_to(download_dir)}"
            )
            result = subprocess.run(
                [
                    "scp",
                    "-i",
                    self.key,
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"{self.user}@{self.host}:{remote_file}",
                    str(dest),
                ],
                capture_output=True,
                text=True,
                timeout=7200,
            )
            if result.returncode != 0:
                reason = f"scp failed: {result.stderr.strip()}"
                logger.error(f"Preload: {reason}")
                return None, reason

            staged_files.append(
                {"name": dest.name, "size": torrent_file["length"]}
            )

        logger.info(
            f"Preload: staged {len(staged_files)} file(s) for '{torrent_name}'"
        )
        return staged_files, ""

    def preload(self, torrent_path: str, download_dir: str) -> PreloadResult:
        """Try to find and stage files for a torrent from the remote machine."""
        try:
            torrent_info = parse_torrent(torrent_path)
        except Exception as e:
            name = Path(torrent_path).stem
            logger.warning(f"Preload: could not parse torrent file — {e}")
            return PreloadResult(
                torrent_name=name,
                success=False,
                reason=f"could not parse torrent: {e}",
            )

        torrent_name = torrent_info["name"]

        remote_dirname = self.find_remote_match(torrent_name)
        if not remote_dirname:
            return PreloadResult(
                torrent_name=torrent_name,
                success=False,
                reason="no matching directory found on remote",
            )

        staged_files, reason = self.fetch_and_stage(
            remote_dirname, torrent_info, download_dir
        )
        if staged_files is None:
            return PreloadResult(
                torrent_name=torrent_name,
                success=False,
                remote_dir=remote_dirname,
                reason=reason,
            )

        return PreloadResult(
            torrent_name=torrent_name,
            success=True,
            remote_dir=remote_dirname,
            staged_files=staged_files,
        )


class NotificationQueue:
    """Collects preload results during a rotation and sends one digest email at the end."""

    def __init__(self, config: dict):
        self.config = config
        self._results: list[PreloadResult] = []

    def add(self, result: PreloadResult):
        self._results.append(result)

    def flush(self):
        """Send digest email and clear the queue. No-op if nothing to report."""
        if not self._results:
            return

        to_email = self.config.get("notify_email", "")
        if not to_email:
            logger.debug(
                "Notifications: NOTIFY_EMAIL not set, skipping digest"
            )
            self._results.clear()
            return

        smtp_host = self.config["smtp_server"]
        smtp_port = self.config["smtp_port"]
        from_email = self.config["from_email"]
        server_name = self.config["server_name"]

        successes = [r for r in self._results if r.success]
        failures = [r for r in self._results if not r.success]

        subject = f"[Route23] Preload Report — {len(successes)} matched, {len(failures)} missed"
        html = self._build_html(successes, failures, server_name)

        msg = MIMEMultipart("alternative")
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.sendmail(from_email, [to_email], msg.as_string())
            logger.info(
                f"Notifications: digest sent to {to_email} "
                f"({len(successes)} preloaded, {len(failures)} missed)"
            )
        except Exception as e:
            logger.error(f"Notifications: failed to send digest — {e}")
        finally:
            self._results.clear()

    def _build_html(
        self,
        successes: list[PreloadResult],
        failures: list[PreloadResult],
        server_name: str,
    ) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def success_item(r: PreloadResult) -> str:
            total = _format_size(r.total_bytes())
            files_html = "".join(
                f'<div class="file-row">'
                f'{f["name"]}<span class="file-size">{_format_size(f["size"])}</span>'
                f"</div>"
                for f in r.staged_files
            )
            return (
                f'<div class="item">'
                f'<div class="item-name">{r.torrent_name}</div>'
                f'<div class="item-meta">Matched: {r.remote_dir} &nbsp;·&nbsp; '
                f"{len(r.staged_files)} file(s) &nbsp;·&nbsp; {total}</div>"
                f"{files_html}"
                f"</div>"
            )

        def failure_item(r: PreloadResult) -> str:
            remote = (
                f'<div class="item-meta">Remote: {r.remote_dir}</div>'
                if r.remote_dir
                else ""
            )
            return (
                f'<div class="item item-fail">'
                f'<div class="item-name">{r.torrent_name}</div>'
                f"{remote}"
                f'<div class="reason">{r.reason}</div>'
                f"</div>"
            )

        success_html = ""
        if successes:
            items = "".join(success_item(r) for r in successes)
            success_html = f'<div class="section-title">&#10003; Successfully Preloaded</div>{items}'

        failure_html = ""
        if failures:
            items = "".join(failure_item(r) for r in failures)
            failure_html = f'<div class="section-title">&#10007; No Match Found</div>{items}'

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body{{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background-color:#0f172a;color:#e5e7eb;padding:24px;margin:0}}
    .card{{max-width:680px;margin:0 auto;background:radial-gradient(circle at top left,#1e293b,#020617);border-radius:16px;border:1px solid #1f2933;box-shadow:0 18px 45px rgba(0,0,0,.65);overflow:hidden}}
    .header{{padding:20px 24px 16px;border-bottom:1px solid rgba(148,163,184,.25)}}
    .badge{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;padding:4px 10px;border-radius:999px;background-color:rgba(15,23,42,.85);border:1px solid rgba(148,163,184,.4);color:#cbd5f5;display:inline-block;margin-bottom:8px}}
    h1{{margin:0 0 2px;font-size:20px;font-weight:600;color:#e5e7eb}}
    .subtitle{{font-size:12px;color:#9ca3af}}
    .content{{padding:20px 24px}}
    .summary{{display:flex;gap:16px;margin-bottom:20px}}
    .stat{{flex:1;padding:12px 16px;border-radius:10px;text-align:center}}
    .stat-num{{font-size:28px;font-weight:700}}
    .stat-label{{font-size:11px;text-transform:uppercase;letter-spacing:.1em;margin-top:2px}}
    .stat-success{{background:rgba(22,163,74,.15);border:1px solid rgba(22,163,74,.3)}}
    .stat-success .stat-num{{color:#4ade80}}
    .stat-success .stat-label{{color:#86efac}}
    .stat-miss{{background:rgba(220,38,38,.12);border:1px solid rgba(220,38,38,.25)}}
    .stat-miss .stat-num{{color:#f87171}}
    .stat-miss .stat-label{{color:#fca5a5}}
    .section-title{{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#9ca3af;margin:20px 0 8px;padding-bottom:6px;border-bottom:1px solid rgba(148,163,184,.15)}}
    .item{{background:rgba(255,255,255,.03);border:1px solid rgba(148,163,184,.1);border-radius:8px;padding:12px 14px;margin-bottom:8px}}
    .item-fail{{border-color:rgba(220,38,38,.2);background:rgba(220,38,38,.04)}}
    .item-name{{font-size:14px;font-weight:600;color:#e5e7eb;margin-bottom:4px;word-break:break-word}}
    .item-meta{{font-size:12px;color:#6b7280;margin-bottom:4px}}
    .file-row{{font-size:11px;color:#94a3b8;padding:4px 0;border-top:1px solid rgba(148,163,184,.08);font-family:monospace;display:flex;justify-content:space-between}}
    .file-size{{color:#64748b}}
    .reason{{font-size:12px;color:#f87171;margin-top:4px}}
    .footer{{margin-top:20px;padding-top:12px;border-top:1px dashed rgba(148,163,184,.2);font-size:11px;color:#6b7280;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}}
    .pill{{padding:3px 9px;border-radius:999px;border:1px solid rgba(148,163,184,.3);font-size:10px;text-transform:uppercase;letter-spacing:.12em}}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="badge">Route23 &nbsp;·&nbsp; {server_name}</div>
      <h1>Preload Report</h1>
      <div class="subtitle">{timestamp}</div>
    </div>
    <div class="content">
      <div class="summary">
        <div class="stat stat-success">
          <div class="stat-num">{len(successes)}</div>
          <div class="stat-label">Preloaded</div>
        </div>
        <div class="stat stat-miss">
          <div class="stat-num">{len(failures)}</div>
          <div class="stat-label">No Match</div>
        </div>
      </div>
      {success_html}
      {failure_html}
      <div class="footer">
        <div>Generated by route23 after rotation.</div>
        <div class="pill">Preload &nbsp;·&nbsp; SCP</div>
      </div>
    </div>
  </div>
</body>
</html>"""


class TorrentRotator:
    def __init__(self, config: dict, preloader: PreloadManager | None = None):
        self.config = config
        self.state = self.load_state()
        self.rtorrent = xmlrpc.client.ServerProxy(config["rtorrent_url"])
        self.preloader = preloader
        self.notifier = NotificationQueue(config)

    def find_rtorrent_hash(
        self, torrent_name: str, retries: int = 6
    ) -> str | None:
        """Find the rtorrent info hash for a torrent by its name, with retries."""
        for attempt in range(retries):
            for h in self.get_active_torrents():
                try:
                    if self.rtorrent.d.name(h) == torrent_name:
                        return h
                except Exception:
                    pass
            if attempt < retries - 1:
                time.sleep(3)
        return None

    def trigger_hash_check(self, info_hash: str):
        """Ask rtorrent to recheck a torrent's files against what's on disk."""
        try:
            self.rtorrent.d.check_hash(info_hash)
            logger.info(f"Preload: triggered hash check for {info_hash[:8]}")
        except Exception as e:
            logger.error(f"Preload: hash check failed — {e}")

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
                state = json.load(f)
            # One-time migration: backfill seeded_this_cycle from torrent_history
            # so existing installs don't re-seed already-processed files.
            if "seeded_this_cycle" not in state:
                state["seeded_this_cycle"] = [
                    info["path"]
                    for info in state.get("torrent_history", {}).values()
                    if "path" in info
                ]
                if state["seeded_this_cycle"]:
                    logger.info(
                        f"Migrated {len(state['seeded_this_cycle'])} previously seeded "
                        f"torrents into cycle tracking"
                    )
            return state
        return {
            "current_index": 0,
            "batch_started": None,
            "current_batch": [],
            "completed_batches": 0,
            "sort_seed": None,
            "seeded_this_cycle": [],
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
        """Get list of all .torrent files ordered by SORT_ORDER."""
        torrent_dir = Path(self.config["torrent_dir"])
        if not torrent_dir.exists():
            logger.error(f"Torrent directory not found: {torrent_dir}")
            return []

        sort_order = self.config["sort_order"]
        torrents = list(torrent_dir.glob("*.torrent"))

        if sort_order == "alphabetical":
            torrents = sorted(torrents)
        elif sort_order == "reverse":
            torrents = sorted(torrents, reverse=True)
        elif sort_order == "date_added":
            torrents = sorted(torrents, key=lambda t: t.stat().st_mtime)
        elif sort_order == "random":
            if self.state.get("sort_seed") is None:
                self.state["sort_seed"] = random.randint(0, 2**32)
            rng = random.Random(self.state["sort_seed"])
            rng.shuffle(torrents)
        else:
            logger.warning(
                f"Unknown SORT_ORDER '{sort_order}', falling back to alphabetical"
            )
            torrents = sorted(torrents)

        logger.info(f"Found {len(torrents)} torrent files (sort: {sort_order})")
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
        """Remove a torrent from rtorrent, optionally deleting downloaded files."""
        try:
            base_path = None
            if delete_data:
                try:
                    base_path = self.rtorrent.d.base_path(info_hash)
                except Exception as e:
                    logger.warning(
                        f"Could not get base path for {info_hash[:8]}: {e}"
                    )

            self.rtorrent.d.stop(info_hash)
            self.rtorrent.d.close(info_hash)
            self.rtorrent.d.erase(info_hash)
            logger.info(f"Removed torrent: {info_hash}")

            if delete_data and base_path:
                self._delete_path(base_path)

            return True
        except Exception as e:
            logger.error(f"Failed to remove torrent {info_hash}: {e}")
            return False

    def _delete_path(self, path: str):
        """Delete a file or directory left behind by a removed torrent."""
        p = Path(path)
        if not p.exists():
            logger.debug(f"Nothing to delete, path does not exist: {path}")
            return
        try:
            if p.is_dir():
                shutil.rmtree(p)
                logger.info(f"Deleted directory: {path}")
            else:
                p.unlink()
                logger.info(f"Deleted file: {path}")
        except Exception as e:
            logger.error(f"Failed to delete {path}: {e}")

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
        """Get the next batch of torrent files to seed, skipping already-seeded ones."""
        all_torrents = self.get_torrent_files()
        if not all_torrents:
            return []

        seeded = set(self.state.get("seeded_this_cycle", []))
        eligible = [t for t in all_torrents if t not in seeded]

        if not eligible:
            logger.info(
                f"All {len(all_torrents)} torrents seeded this cycle — starting new cycle"
            )
            self.state["seeded_this_cycle"] = []
            if self.config["sort_order"] == "random":
                self.state["sort_seed"] = random.randint(0, 2**32)
                all_torrents = self.get_torrent_files()
            eligible = all_torrents

        batch = eligible[: self.config["batch_size"]]
        logger.info(
            f"Next batch: {len(batch)} torrents "
            f"({len(eligible)} eligible, {len(seeded)} seeded this cycle)"
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

                if self.preloader:
                    preload_result = self.preloader.preload(
                        torrent_path, self.config["download_dir"]
                    )
                    self.notifier.add(preload_result)
                    if preload_result.success:
                        try:
                            rt_hash = self.find_rtorrent_hash(
                                preload_result.torrent_name
                            )
                            if rt_hash:
                                self.trigger_hash_check(rt_hash)
                            else:
                                logger.warning(
                                    f"Preload: could not find rtorrent hash for "
                                    f"'{preload_result.torrent_name}' to trigger recheck"
                                )
                        except Exception as e:
                            logger.warning(
                                f"Preload: hash check step failed — {e}"
                            )

            if i < total:
                self.throttled_sleep(
                    self.config["add_delay"], "between additions"
                )

        self.state["current_batch"] = added
        self.state["batch_started"] = datetime.now().isoformat()
        self.state.setdefault("seeded_this_cycle", [])
        self.state["seeded_this_cycle"].extend(added)
        self.state["current_index"] = len(self.state["seeded_this_cycle"])
        self.state["completed_batches"] += 1

        self.save_state()
        logger.info(f"Rotation complete. Added {len(added)}/{total} torrents.")
        logger.info(f"Next rotation in {self.config['rotation_days']} days")

        self.notifier.flush()

    def repreload(self):
        """Re-run preload against the currently active batch.

        Useful when the original rotation could not reach the remote machine
        (e.g. it was offline) and the torrents are still seeding empty. For
        each torrent in the saved current batch, this re-attempts the SCP
        copy and triggers an rtorrent hash recheck on success.
        """
        if not self.preloader:
            logger.error("Repreload requested but PRELOAD_ENABLED is not set")
            return

        batch = self.state.get("current_batch", [])
        if not batch:
            logger.warning("Repreload: no current batch in state, nothing to do")
            return

        logger.info(f"Repreload: re-attempting {len(batch)} torrent(s)")

        for i, torrent_path in enumerate(batch, 1):
            if not Path(torrent_path).exists():
                logger.warning(
                    f"[{i}/{len(batch)}] torrent file missing: {torrent_path}"
                )
                continue

            self.wait_for_low_load()
            logger.info(f"[{i}/{len(batch)}] Repreload: {Path(torrent_path).name}")

            result = self.preloader.preload(
                torrent_path, self.config["download_dir"]
            )
            self.notifier.add(result)

            if result.success:
                try:
                    rt_hash = self.find_rtorrent_hash(result.torrent_name)
                    if rt_hash:
                        self.trigger_hash_check(rt_hash)
                    else:
                        logger.warning(
                            f"Repreload: could not find rtorrent hash for "
                            f"'{result.torrent_name}' to trigger recheck"
                        )
                except Exception as e:
                    logger.warning(f"Repreload: hash check step failed — {e}")

        logger.info("Repreload complete")
        self.notifier.flush()

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
        seeded_count = len(self.state.get("seeded_this_cycle", []))
        print(f"Seeded this cycle:        {seeded_count} / {len(all_torrents)}")

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

    preloader = None
    if PRELOAD_ENABLED:
        if (
            not CONFIG["preload_host"]
            or not CONFIG["preload_user"]
            or not CONFIG["preload_remote_dir"]
        ):
            logger.error(
                "PRELOAD_ENABLED=true but PRELOAD_HOST, PRELOAD_USER, or PRELOAD_REMOTE_DIR is not set"
            )
        else:
            preloader = PreloadManager(CONFIG)
            logger.info(
                f"Preload enabled: {CONFIG['preload_user']}@{CONFIG['preload_host']}:{CONFIG['preload_remote_dir']}"
            )

    rotator = TorrentRotator(CONFIG, preloader=preloader)

    if SHOW_STATUS:
        rotator.status()
    elif REPRELOAD:
        rotator.repreload()
    else:
        rotator.run(force=FORCE_ROTATION, delete_data=DELETE_DATA)


if __name__ == "__main__":
    main()
