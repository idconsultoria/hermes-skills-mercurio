# API Testing: Isolated Test Infrastructure

When QA testing a web application that has a production database, **always spin up an isolated test stack** to avoid polluting or crashing production data.

## Docker Compose Test Stack Pattern

Create a standalone `docker-compose.test.yml` that mirrors production but with:

1. **Separate database** with its own volume
2. **Distinct ports** for every service
3. **A separate network** so production and test containers don't conflict
4. **Test credentials** (never reuse production secrets)
5. **Same build context** so the test stack mirrors production code

### Canonical Structure

```yaml
# docker-compose.test.yml — standalone, does NOT override production
services:
  db-test:
    image: postgres:16-alpine          # same version as production
    container_name: myapp-db-test      # distinct name
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: myapp_test
    ports:
      - "5433:5432"                    # distinct host port
    volumes:
      - pgdata_test:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testuser"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - test-net

  app-test:
    build: ./app                      # same build as production
    container_name: myapp-test
    environment:
      DATABASE_URL: postgresql+asyncpg://testuser:testpass@db-test:5432/myapp_test
      SECRET_KEY: test-secret-not-for-prod
      CORS_ORIGINS: '["*"]'           # permissive for testing
    ports:
      - "8001:8000"                   # distinct from production :8000
    depends_on:
      db-test:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - test-net

volumes:
  pgdata_test:

networks:
  test-net:
    driver: bridge
```

### Running

```bash
# Start test stack (standalone)
docker compose -f docker-compose.test.yml up -d

# Verify
docker compose -f docker-compose.test.yml ps
curl http://localhost:8001/api/v1/health

# Tear down
docker compose -f docker-compose.test.yml down -v
```

### Important Considerations

1. **NGINX**: if nginx config uses hardcoded upstream names (e.g., `server backend:8000`), the test stack's service name (e.g., `app-test`) won't match. Either:
   - Don't include nginx in the test stack (test the API directly on its port)
   - Or create a test-specific nginx config that references the test service names

2. **Migrations**: if the app runs migrations on startup via an entrypoint, the test stack will auto-migrate the test DB on first start. Verify this in the logs.

3. **Seed data**: consider adding a seed script for reproducible testing. Run it after migrations complete:
   ```bash
   docker exec myapp-test python scripts/seed_test_data.py
   ```

4. **Shared volumes**: if the app writes to a shared volume, give the test stack its own. The test nginx config's `upstream` block must reference the test service name, not the production one.

5. **Production stays up**: the `-f docker-compose.test.yml` without `-f docker-compose.yml` means the test stack is completely standalone — production containers keep running uninterrupted.

### ⚠️ Critical Pitfall: Frontend-Backend Routing

When doing **browser-based QA**, the frontend SPA may be configured to talk to the **production backend** URL, not your test backend. This means:
- Your seeded test data (on the test API port) won't appear in the browser
- User registration via the browser creates accounts on the production DB
- Stats/reports shown in the browser reflect production data

**Solutions:**
1. **Seed both backends**: create test data on the production backend too (via its API port)
2. **Point frontend to test backend**: override `VITE_API_URL` or the nginx `proxy_pass` to route to the test backend
3. **Accept the split**: use browser QA for UI/UX testing (flows, navigation, empty states, error handling) and API QA for functional correctness tests

### Browser Access via Docker Gateway

When the QA agent runs inside a Docker container (common with Hermes), `browser_navigate()` may not reach the host's public IP due to network isolation. The Docker gateway IP is the reliable alternative:

```bash
# Check which gateway IPs are reachable
timeout 3 bash -c 'echo > /dev/tcp/172.19.0.1/8080' 2>&1 && echo "gateway 172.19.0.1 reachable"
timeout 3 bash -c 'echo > /dev/tcp/172.17.0.1/8080' 2>&1 && echo "gateway 172.17.0.1 reachable"

# Use it in browser
browser_navigate("http://172.19.0.1:8080")
```

Find the correct gateway by inspecting the Hermes container's default route or `/etc/hosts` entries.
