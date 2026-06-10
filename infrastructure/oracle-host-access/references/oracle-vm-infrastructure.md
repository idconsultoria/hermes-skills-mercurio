# Oracle VM - Reference Infrastructure

Descoberto durante sessão de setup SSH (2026-06-05).

## Host Specs
- **Provider:** Oracle Cloud (VM)
- **OS:** Ubuntu 24.04 LTS, aarch64
- **Kernel:** 6.17.0-1016-oracle
- **RAM:** 23 GB (3.7 used, 19 avail)
- **Disk:** 200G (193G partição, 17G used)
- **Docker:** 29.5.3

## Network
- **Docker bridge subnet:** 172.19.0.0/16
- **Gateway (host):** 172.19.0.1
- **Container network:** ai_mesh (external bridge)
- **Container IP:** 172.19.0.7

## Containers
| Name | Image | Ports |
|---|---|---|
| hermes_agent | nousresearch/hermes-agent:latest | 8642, 9119 |
| nginx_proxy_manager | jc21/nginx-proxy-manager:latest | 80, 81, 443 |
| firecrawl_api | ghcr.io/firecrawl/firecrawl:latest | 3002, 8080 |
| firecrawl_worker | ghcr.io/firecrawl/firecrawl:latest | 8080 |
| firecrawl_postgres | postgres:17-alpine | 5432 |
| firecrawl_rabbitmq | rabbitmq:3-management-alpine | 5671-5672, 15671-15672 |
| firecrawl_redis | redis:alpine | 6379 |
| firecrawl_playwright | ghcr.io/firecrawl/playwright-service:latest | — |

## Hermes Container
- **Imagem:** nousresearch/hermes-agent:latest (acce1a24)
- **Entrypoint:** `/init /opt/hermes/docker/main-wrapper.sh`
- **User:** root | **Restart:** unless-stopped
- **Criado:** 2026-06-05T01:33:21Z
- **Bind mount:** `/home/ubuntu/selfhost/hermes/data:/opt/data:rw`
- **HOME (shell):** /opt/data/home | **HOME (SSH):** /opt/data
- **Compose:** `/home/ubuntu/selfhost/hermes/docker-compose.yml`

## Auto-Update Cron
- Instalado 2026-06-05 (cron não vinha no Ubuntu 24.04 minimal)
- Toda segunda 03:00 UTC
- `cd /home/ubuntu/selfhost/hermes && docker compose pull hermes >> /tmp/hermes-update.log 2>&1 && docker compose up -d hermes >> /tmp/hermes-update.log 2>&1`
- Log: `/tmp/hermes-update.log`
