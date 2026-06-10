#!/bin/bash
# Rollback to a specific SHA tag
# Usage: ./rollback.sh sha-<target-commit>
set -euo pipefail

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  echo "Usage: $0 sha-<target-commit>"
  echo ""
  echo "Available tags for backend:"
  docker images ghcr.io/gustavomello9600/taskflow-mvp/backend --format "table {{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | head -10
  exit 1
fi

cd /home/ubuntu/selfhost/$(basename $(pwd))

echo "[rollback] Switching to $TARGET..."
sed -i "s/:latest\$/:$TARGET/" docker-compose.yml

echo "[rollback] Pulling specific tag..."
docker compose pull

echo "[rollback] Recreating containers..."
docker compose up -d

echo "[rollback] Restoring :latest in compose file..."
sed -i "s/:$TARGET\$/:latest/" docker-compose.yml

echo "[rollback] Done."
