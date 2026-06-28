# Docker Maintenance — Storage Analysis, Image Inspection, Update Checking

Load this reference when you need to analyze Docker disk usage, investigate image sizes, check for available updates, or clean up space on the Oracle host.

## Quick Reference

```bash
# ============================
# DISK USAGE OVERVIEW
# ============================

# Fast — top-level dirs on host
ssh oracle-host 'sudo du -sh /var/lib/containerd /var/lib/docker /home/ubuntu /usr /var 2>/dev/null'

# Docker's own breakdown
ssh oracle-host 'docker system df'

# ============================
# IMAGE SIZE INVESTIGATION
# ============================

# List all images with sizes
ssh oracle-host 'docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"'

# Per-layer breakdown (find which layer is fat)
ssh oracle-host 'docker history <image>:<tag> --no-trunc --format "table {{.Size}}\t{{.CreatedBy}}"'

# Top-10 heaviest layers
ssh oracle-host 'docker history <image>:<tag> --no-trunc --format "{{.Size}}\t{{.CreatedBy}}" | grep -E "^[0-9]" | sort -rh | head -10'

# Actual unique image size vs virtual (inherited) size
ssh oracle-host 'docker inspect <image>:<tag> --format "Size={{.Size}} VirtualSize={{.VirtualSize}}"'

# ============================
# CHECK FOR UPDATES (read-only, no pull)
# ============================

# Works for Docker Hub and GHCR images
ssh oracle-host 'docker buildx imagetools inspect <image>:<tag>'

# Full comparison — local digest vs remote digest:
ssh oracle-host '
local=$(docker images --digests --format "{{.Repository}}:{{.Tag}}\t{{.Digest}}" | grep "^<image>:<tag>" | awk "{print \$2}" | cut -d"@" -f2)
remote=$(docker buildx imagetools inspect <image>:<tag> 2>/dev/null | grep "Digest:" | awk "{print \$2}")
if [ "$local" = "$remote" ]; then echo "✅ Atualizado"; else echo "🔴 NOVA VERSÃO"; fi
'

# ============================
# CLEANUP
# ============================

# Full cleanup — prune all unused images, containers, volumes, build cache
ssh oracle-host 'docker system prune --all --volumes -f'

# Build cache only (safe, no containers harmed)
ssh oracle-host 'docker builder prune --all -f'

# Orphaned volumes
ssh oracle-host 'docker volume prune -f'
```

## Pitfalls

- **`docker manifest inspect` requires experimental CLI mode** — use `docker buildx imagetools inspect` instead (no config needed on Docker ≥ 29.x).
- **`sudo du -sh /*` from root takes forever** — target specific dirs (`/var/lib/containerd`, `/var/lib/docker`, `/home`, `/usr`, `/var`).
- **`docker system prune --all --volumes -f` is aggressive** — removes ALL unused images, stopped containers, unused volumes, and dangling build cache. Only run when user explicitly authorizes.
- **GHCR images need auth** — check `~/.docker/config.json` contains `ghcr.io` before inspecting private packages.
- **Local builds** (e.g. `vulcano-vulcano`, `fish-speech-s2-server`) have no remote registry — skip update checking.
