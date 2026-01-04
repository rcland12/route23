#!/usr/bin/env python3
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def format_size(size_bytes_str: str) -> str:
    try:
        size_bytes = int(size_bytes_str)
    except (TypeError, ValueError):
        return "Unknown"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    return f"{size:.2f} {units[idx]}"


def build_html(
    event_type: str, name: str, path: str, size_bytes: str, torrent_hash: str, server_name: str
) -> str:
    size_human = format_size(size_bytes)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if event_type == "added":
        title = "New Torrent Added"
        title_color = "#2563eb"
    else:
        title = "Torrent Completed"
        title_color = "#16a34a"

    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background-color: #0f172a;
      color: #e5e7eb;
      padding: 24px;
    }}
    .card {{
      max-width: 640px;
      margin: 0 auto;
      background: radial-gradient(circle at top left, #1e293b, #020617);
      border-radius: 16px;
      border: 1px solid #1f2933;
      box-shadow: 0 18px 45px rgba(0,0,0,0.65);
      overflow: hidden;
    }}
    .header {{
      padding: 20px 24px 16px;
      border-bottom: 1px solid rgba(148,163,184,0.25);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .badge {{
      font-size: 11px;
      letter-spacing: .08em;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 999px;
      background-color: rgba(15,23,42,0.85);
      border: 1px solid rgba(148,163,184,0.4);
      color: #cbd5f5;
    }}
    .title {{
      margin: 4px 0 0;
      font-size: 20px;
      font-weight: 600;
      color: {title_color};
    }}
    .subtitle {{
      font-size: 12px;
      color: #9ca3af;
      margin-top: 2px;
    }}
    .content {{
      padding: 16px 24px 20px;
    }}
    .label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .11em;
      color: #9ca3af;
      margin-bottom: 4px;
    }}
    .torrent-name {{
      font-size: 16px;
      font-weight: 600;
      color: #e5e7eb;
      margin-bottom: 12px;
      word-break: break-word;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px 24px;
      font-size: 13px;
    }}
    .grid-label {{
      color: #9ca3af;
      font-size: 12px;
      margin-bottom: 2px;
    }}
    .grid-value {{
      color: #e5e7eb;
      word-break: break-all;
    }}
    .footer {{
      margin-top: 20px;
      padding-top: 12px;
      border-top: 1px dashed rgba(148,163,184,0.4);
      font-size: 11px;
      color: #6b7280;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .pill {{
      padding: 3px 9px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.3);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: .12em;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div>
        <div class="badge">rTorrent · {server_name}</div>
        <h1 class="title">{title}</h1>
        <div class="subtitle">{timestamp}</div>
      </div>
    </div>
    <div class="content">
      <div class="label">Torrent</div>
      <div class="torrent-name">{name or "Unknown"}</div>

      <div class="grid">
        <div>
          <div class="grid-label">Status</div>
          <div class="grid-value">{event_type.capitalize()}</div>
        </div>
        <div>
          <div class="grid-label">Size</div>
          <div class="grid-value">{size_human}</div>
        </div>
        <div>
          <div class="grid-label">Download Path</div>
          <div class="grid-value">{path or "Unknown"}</div>
        </div>
        <div>
          <div class="grid-label">Info Hash</div>
          <div class="grid-value">{torrent_hash or "Unknown"}</div>
        </div>
      </div>

      <div class="footer">
        <div>Generated automatically by your rTorrent notifier.</div>
        <div class="pill">VPN: Gluetun · rtorrent-rutorrent</div>
      </div>
    </div>
  </div>
</body>
</html>
"""


def send_email(
    event_type: str, name: str, path: str, size_bytes: str, torrent_hash: str
) -> None:
    smtp_host = get_env("SMTP_SERVER", required=True)
    smtp_port = int(get_env("SMTP_PORT", "25"))
    from_email = get_env("FROM_EMAIL", required=True)
    to_email = get_env("TO_EMAIL", required=True)
    server_name = get_env("SERVER_NAME", default="server")

    subject_prefix = (
        "[rTorrent] Torrent Added"
        if event_type == "added"
        else "[rTorrent] Torrent Completed"
    )
    subject = f"{subject_prefix}: {name or 'Unknown'}"

    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    html = build_html(event_type, name, path, size_bytes, torrent_hash, server_name)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
        server.sendmail(from_email, [to_email], msg.as_string())


def main(argv):
    """
    Args from rTorrent:
      argv[1] = event_type ("added" | "completed")
      argv[2] = torrent name
      argv[3] = download path (directory)
      argv[4] = size in bytes
      argv[5] = info hash
    """
    if len(argv) < 6:
        print(f"Not enough arguments, got {len(argv) - 1}", file=sys.stderr)
        return 1

    event_type = argv[1]
    name = argv[2]
    path = argv[3]
    size_bytes = argv[4]
    torrent_hash = argv[5]

    try:
        send_email(event_type, name, path, size_bytes, torrent_hash)
    except Exception as e:
        print(f"Error sending email: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
