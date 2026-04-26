#!/bin/sh
set -eu

OUTPUT_DIR="${DOCKER_LOG_AGENT_OUTPUT_DIR:-logs/docker-log-agent}"
INTERVAL_SECONDS="${DOCKER_LOG_AGENT_INTERVAL_SECONDS:-60}"
TAIL_LINES="${DOCKER_LOG_AGENT_TAIL:-160}"
SERVICES="${DOCKER_LOG_AGENT_SERVICES:-}"
REGISTRY_FILE="$OUTPUT_DIR/registry.jsonl"

mkdir -p "$OUTPUT_DIR"

while true; do
  RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
  SNAPSHOT_FILE="$OUTPUT_DIR/$RUN_ID.md"

  {
    echo "# Docker Log Agent Snapshot $RUN_ID"
    echo
    echo "- services: \`${SERVICES:-all}\`"
    echo "- tail: \`$TAIL_LINES\`"
    echo "- interval_seconds: \`$INTERVAL_SECONDS\`"
    echo
    echo "## Compose Status"
    echo
    echo '```text'
    docker compose ps 2>&1 || true
    echo '```'
    echo
    echo "## Logs"
    echo
    echo '```text'
    # shellcheck disable=SC2086
    docker compose logs --no-color --timestamps --tail "$TAIL_LINES" $SERVICES 2>&1 || true
    echo '```'
  } > "$SNAPSHOT_FILE"

  printf '{"run_id":"%s","snapshot":"%s","services":"%s","tail":%s,"created_at":"%s"}\n' \
    "$RUN_ID" "$SNAPSHOT_FILE" "${SERVICES:-all}" "$TAIL_LINES" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$REGISTRY_FILE"

  echo "registered $SNAPSHOT_FILE"
  sleep "$INTERVAL_SECONDS"
done
