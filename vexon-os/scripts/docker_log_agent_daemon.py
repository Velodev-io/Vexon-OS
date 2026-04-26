#!/usr/bin/env python3
"""Run the Docker log agent repeatedly for local diagnostics."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_SCRIPT = REPO_ROOT / "scripts" / "docker_log_agent.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Periodically capture Docker Compose logs.")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between snapshots.")
    parser.add_argument("--tail", type=int, default=160, help="Log lines per service per snapshot.")
    parser.add_argument(
        "--service",
        action="append",
        default=[],
        help="Service to capture. Can be passed multiple times. Defaults to all services.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    while True:
        command = [str(AGENT_SCRIPT), "--tail", str(args.tail)]
        for service in args.service:
            command.extend(["--service", service])

        subprocess.run(command, cwd=REPO_ROOT, check=False)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
