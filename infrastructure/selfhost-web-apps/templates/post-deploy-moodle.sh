#!/bin/bash
# Moodle post-deploy — rebuild theme CSS for performance.
# Run after: docker compose up, purge_caches, or version upgrades.
# No warm scripts needed for JS/fonts/images — they serve correctly
# on first request after the reverseproxy fix.
set -e

CONTAINER="${CONTAINER:-moodle-app}"

echo "=== Moodle post-deploy ==="
echo "Rebuild theme CSS..."
docker exec "$CONTAINER" php /var/www/html/admin/cli/build_theme_css.php
echo "=== Done ==="
