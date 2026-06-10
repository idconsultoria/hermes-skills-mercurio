#!/bin/bash
set -euo pipefail

cd /home/ubuntu/selfhost/$(basename $(pwd))

echo "[deploy] $(date) — Pulling new images..."
docker compose pull

echo "[deploy] Recreating containers..."
docker compose up -d --remove-orphans

echo "[deploy] Pruning old images..."
docker image prune -f --filter "until=24h" 2>/dev/null || true

echo "[deploy] Done. Checking status..."
docker compose ps --format "table {{.Name}}\t{{.Status}}"
