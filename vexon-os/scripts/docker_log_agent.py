#!/usr/bin/env python3
"""Capture Docker Compose diagnostics into local files.

This runs on the host machine, not inside the API container, so it can use the
local Docker CLI without exposing the Docker socket to the app.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "logs" / "docker-log-agent"
DEFAULT_PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"


def docker_command() -> str:
    env_path = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{DEFAULT_PATH}:{env_path}" if env_path else DEFAULT_PATH
    docker = shutil.which("docker")
    if not docker:
        raise FileNotFoundError("docker was not found in PATH")
    return docker


def run_command(args: list[str], timeout: int) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return 124, output.strip()

    output = completed.stdout
    if completed.stderr:
        output += "\n" + completed.stderr
    return completed.returncode, output.strip()


def slug_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture Docker Compose service status and logs into a registered local snapshot.",
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=160,
        help="Number of recent log lines per service to capture.",
    )
    parser.add_argument(
        "--service",
        action="append",
        default=[],
        help="Service to capture. Can be passed multiple times. Defaults to all services.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where snapshots and the registry file are written.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for each Docker command.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    docker = docker_command()

    run_id = slug_timestamp()
    snapshot_path = output_dir / f"{run_id}.md"
    registry_path = output_dir / "registry.jsonl"

    ps_code, ps_output = run_command([docker, "compose", "ps"], args.timeout)
    log_command = [
        docker,
        "compose",
        "logs",
        "--no-color",
        "--timestamps",
        "--tail",
        str(args.tail),
        *args.service,
    ]
    logs_code, logs_output = run_command(log_command, args.timeout)

    snapshot = "\n".join(
        [
            f"# Docker Log Agent Snapshot {run_id}",
            "",
            f"- repo: `{REPO_ROOT}`",
            f"- services: `{', '.join(args.service) if args.service else 'all'}`",
            f"- tail: `{args.tail}`",
            f"- docker compose ps exit: `{ps_code}`",
            f"- docker compose logs exit: `{logs_code}`",
            "",
            "## Compose Status",
            "",
            "```text",
            ps_output or "<no output>",
            "```",
            "",
            "## Logs",
            "",
            "```text",
            logs_output or "<no output>",
            "```",
            "",
        ]
    )
    snapshot_path.write_text(snapshot, encoding="utf-8")

    registry_entry = {
        "run_id": run_id,
        "snapshot": str(snapshot_path.relative_to(REPO_ROOT)),
        "services": args.service or ["all"],
        "tail": args.tail,
        "compose_ps_exit_code": ps_code,
        "compose_logs_exit_code": logs_code,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with registry_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(registry_entry) + "\n")

    print(f"registered {snapshot_path.relative_to(REPO_ROOT)}")
    print(f"registry {registry_path.relative_to(REPO_ROOT)}")
    return 0 if ps_code == 0 and logs_code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
