#!/usr/bin/env python3
"""SciDash local dev server.

Pure static file server -- app.js reads data directly from
site-data/publications.json (the file scripts/sync_scopus.py writes), the
same way it would when served from GitHub Pages. There is no dynamic API
anymore: run scripts/sync_scopus.py (locally, or on a schedule) whenever you
want fresh data, then just reload the page.
"""
import http.server
import os
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PID_FILE = ROOT / ".scidash-server.pid"
LOG_FILE = ROOT / ".scidash-server.log"
HOST = "0.0.0.0"
PORT = 4173


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def run_server() -> None:
    os.chdir(ROOT)
    with ReusableTCPServer((HOST, PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()


def main() -> None:
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
        except ValueError:
            pid = 0
        if pid and is_running(pid):
            print(pid)
            return
        PID_FILE.unlink(missing_ok=True)

    pid = os.fork()
    if pid:
        PID_FILE.write_text(str(pid))
        print(pid)
        return

    os.setsid()

    sys.stdin.close()
    with LOG_FILE.open("ab", buffering=0) as log:
        os.dup2(log.fileno(), sys.stdout.fileno())
        os.dup2(log.fileno(), sys.stderr.fileno())
        run_server()


if __name__ == "__main__":
    main()
