#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$ROOT_DIR/api"

cd "$API_DIR"
alembic upgrade head

cd "$ROOT_DIR"
docker compose up --build redis api worker shell
