#!/usr/bin/env python3
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PID_FILE = ROOT / ".scidash-server.pid"


def main() -> None:
    if not PID_FILE.exists():
        print("SciDash server is not running")
        return

    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, 15)
        print(f"Stopped SciDash server: {pid}")
    except OSError:
        print("SciDash server process was not found")
    finally:
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
