"""A pretend attacker website on 127.0.0.1:18926 for lesson 9.

It answers every request with a tiny image and writes down the full address,
query string included. That is all an attacker needs to receive data that a
chat page leaks through an image link. Open http://127.0.0.1:18926/ to see
what it has collected.  Run:  python -m attacks.attacker_site
"""
import base64
import datetime
import html
import http.server
import pathlib

from common import config

LOG_PATH = pathlib.Path(__file__).resolve().parent / "runs" / "attacker-site.log"
# The smallest valid PNG: one transparent pixel.
PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._show_log()
            return
        LOG_PATH.parent.mkdir(exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as log:
            log.write(f"{datetime.datetime.now():%H:%M:%S} {self.path}\n")
        self._send("image/png", PIXEL)

    def _show_log(self):
        lines = LOG_PATH.read_text(encoding="utf-8").splitlines() if LOG_PATH.exists() else []
        rows = "".join(f"<li><code>{html.escape(line)}</code></li>" for line in lines) or "<li>Nothing yet.</li>"
        page = (
            "<!DOCTYPE html><html><head><title>Attacker site (lab)</title>"
            "<style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#5c1a1a}"
            "li{margin:6px 0}code{font-size:15px}</style></head>"
            f"<body><h1>Pretend attacker site: requests received</h1><ul>{rows}</ul></body></html>"
        )
        self._send("text/html; charset=utf-8", page.encode())

    def _send(self, content_type, body):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # the log file is the record; keep the terminal quiet


if __name__ == "__main__":
    print(f"Pretend attacker site (lab) on http://{config.BIND_HOST}:{config.ATTACKER_SITE_PORT}")
    http.server.HTTPServer((config.BIND_HOST, config.ATTACKER_SITE_PORT), Handler).serve_forever()
