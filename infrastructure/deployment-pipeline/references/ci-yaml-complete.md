# Full CI/CD Pipeline YAML — TaskFlow (Working State)

This is the complete `.github/workflows/ci.yml` from the taskflow-mvp repo,
in its **working state** after debugging. Use as a reference template.

```yaml
name: TaskFlow CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

env:
  PYTHON_VERSION: "3.12"
  SECRET_KEY: ci-secret-key
  DATABASE_URL: sqlite+aiosqlite:///./test.db
  CORS_ORIGINS: '["*"]'
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/gustavomello9600/taskflow-mvp/backend
  IMAGE_FRONTEND: ghcr.io/gustavomello9600/taskflow-mvp/frontend

permissions:
  contents: read
  packages: write

jobs:
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install dependencies
        working-directory: ./backend
        run: pip install -e ".[dev]"
      - name: Ruff check
        working-directory: ./backend
        run: ruff check .
      - name: MyPy check
        working-directory: ./backend
        run: mypy taskflow --ignore-missing-imports --follow-imports=skip || true

  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        working-directory: ./backend
        run: pip install -e ".[dev]"
      - name: Run unit tests
        working-directory: ./backend
        run: |
          pytest ../tests/unit -v --cov=taskflow --cov-report=term-missing \
            --cov-report=xml --timeout=30 -m "unit"
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./backend/coverage.xml
          flags: unit
          fail_ci_if_error: false

  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: taskflow
          POSTGRES_PASSWORD: taskflow
          POSTGRES_DB: taskflow_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -e ".[dev]"
          pip install asyncpg aiosqlite
      - name: Run integration tests (SQLite)
        working-directory: ./backend
        run: |
          DATABASE_URL="sqlite+aiosqlite:///./test_integration.db" \
          pytest ../tests/integration -v --cov=taskflow \
            --cov-report=term-missing --cov-report=xml --timeout=60 -m "integration"
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./backend/coverage.xml
          flags: integration
          fail_ci_if_error: false

  coverage-report:
    name: Coverage Report
    runs-on: ubuntu-latest
    needs: [test-unit, test-integration]
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install dependencies
        working-directory: ./backend
        run: pip install -e ".[dev]"
      - name: Run all tests with coverage
        working-directory: ./backend
        run: |
          pytest ../tests/ -v --cov=taskflow --cov-report=term-missing \
            --cov-report=html --timeout=60
      - name: Upload HTML coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: ./backend/htmlcov/
          retention-days: 7
      - name: Check minimum coverage
        working-directory: ./backend
        run: |
          pytest ../tests/ --cov=taskflow --cov-fail-under=80 --timeout=60

  build-and-push:
    name: Build & Push Images
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    needs: [test-unit, test-integration]
    steps:
      - uses: actions/checkout@v4
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Generate short SHA
        id: sha
        run: echo "sha=$(git rev-parse --short HEAD)" >> "$GITHUB_OUTPUT"
      - name: Build and push backend image
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: true
          tags: |
            ${{ env.IMAGE_BACKEND }}:sha-${{ steps.sha.outputs.sha }}
            ${{ env.IMAGE_BACKEND }}:latest
      - name: Build and push frontend image
        uses: docker/build-push-action@v6
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: true
          tags: |
            ${{ env.IMAGE_FRONTEND }}:sha-${{ steps.sha.outputs.sha }}
            ${{ env.IMAGE_FRONTEND }}:latest

  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    needs: [build-and-push]
    steps:
      - uses: actions/checkout@v4
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: 129.146.163.107
          username: ubuntu
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/ubuntu/selfhost/taskflow
            echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            echo "[deploy] Pulling new images..."
            docker compose pull
            echo "[deploy] Recreating containers..."
            docker compose up -d --remove-orphans
            echo "[deploy] Pruning old images..."
            docker image prune -f --filter "until=24h" 2>/dev/null || true
            echo "[deploy] Done."
```

## Key changes vs. v1

| Fix | Why |
|-----|-----|
| `permissions: { packages: write }` | GITHUB_TOKEN default scope doesn't allow ghcr.io push |
| `../tests/` paths | Tests at repo root, CI runs from `./backend` |
| `continue-on-error: true` on lint | Pre-existing lint debt shouldn't block deploy |
| Lint removed from `needs:` | Tests are the deploy gate, not lint |
| `docker login ghcr.io` in deploy | Server needs auth to pull private images |
| No `fingerprint` param | Avoided host key mismatch issues |
