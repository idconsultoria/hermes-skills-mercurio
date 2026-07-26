---
name: supabase
description: "Manage Supabase from Hermes — run SQL, deploy Edge Functions, manage migrations.

Load this skill when working with any Supabase-backed project from a restricted environment. Covers running SQL without psql, linking projects, deploying Edge Functions, managing migrations, and refreshing materialized views."
version: 1.0.0
author: Hermes Agent
tags: [supabase, postgres, edge-functions, sql, database]
type: ToolIntegration
timestamp: 2026-07-26T05:05:12Z
---

# Supabase Operations

Class-level guide for managing Supabase projects from a restricted Linux environment (no psql, no Docker for local dev).

---

## Installation

```bash
npm config set prefix /opt/data/.npm-global
npm install -g supabase
export PATH="/opt/data/.npm-global/bin:$PATH"
```

---

## Project Linking

Link a local directory to a Supabase project:

```bash
cd /path/to/project
supabase link --project-ref <project_ref> --password "$SUPABASE_DB_PASSWORD"
```

The project ref is the alphanumeric ID (e.g., `eqbfntznrwizhmqawymw`).

---

## Running SQL Queries (no psql required)

The `supabase db query --linked` command runs SQL against the remote database via the Management API — no local PostgreSQL client needed.

```bash
# Single query
supabase db query --linked "SELECT matviewname FROM pg_matviews WHERE matviewname LIKE 'mv_%';"

# Execute a SQL file
supabase db query --linked -f path/to/migration.sql
```

Output is formatted as a table. Use this instead of `psql` when it's not installed.

### Alternative: Direct Management API (when CLI fails)

When `supabase db query --linked` fails with `failed to connect to postgres` (e.g., local Supabase stack not running), use the Management API directly with `SUPABASE_ACCESS_TOKEN`:

```bash
SUPABASE_ACCESS_TOKEN="sbp_..."
curl -s -X POST \
  "https://api.supabase.com/v1/projects/<project_ref>/database/query" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = '\''metas'\'';"}'
```

**Note:** Double-quotes inside the query must be single-quote-escaped for JSON. Pipe through `python3 -m json.tool` for human-readable output. Use `--data-binary` for multi-line queries saved to a file:

```bash
curl -s -X POST \
  "https://api.supabase.com/v1/projects/<project_ref>/database/query" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @- <<EOF
{"query": "SELECT COUNT(*) FROM metas;"}
EOF
```

---

## Materialized Views

```bash
# Create (via migration file)
supabase db query --linked -f supabase/migrations/20260717000000_kpi_materialized_views.sql

# Refresh
supabase db query --linked "REFRESH MATERIALIZED VIEW mv_faturamento_mensal; REFRESH MATERIALIZED VIEW mv_inadimplencia_atual;"

# Verify
supabase db query --linked "SELECT matviewname FROM pg_matviews WHERE matviewname LIKE 'mv_%';"
```

---

## Edge Functions

### Deploy

```bash
supabase functions deploy <function-name> --project-ref <ref>
```

Example:
```bash
supabase functions deploy dashboard-kpis --project-ref eqbfntznrwizhmqawymw
```

### Test

```bash
curl -s "https://<ref>.supabase.co/functions/v1/<function-name>" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

### Verify deployment

```bash
curl -s -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  "https://api.supabase.com/v1/projects/<ref>/functions"
```

---

## Migration Management

### Check migration status (local vs remote)

```bash
supabase migration list
```

This shows which migrations exist locally vs on the remote database.

### Repair out-of-sync migrations

When the remote has a migration not present locally (or vice versa):

```bash
# Mark a remote-only migration as reverted
supabase migration repair --status reverted <timestamp>

# Mark a local-only migration as applied on remote
supabase migration repair --status applied <timestamp>
```

### Push new migrations

```bash
supabase db push --password "$SUPABASE_DB_PASSWORD"
```

---

## Credentials

Required env vars (usually in project `.env`):

| Variable | Purpose |
|---|---|
| `SUPABASE_ACCESS_TOKEN` | Management API (for `supabase link`, `functions deploy`) |
| `SUPABASE_DB_PASSWORD` | Database connection (for `db push`, `db query --linked`) |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin access to database (for RLS-bypass queries) |
| `VITE_SUPABASE_URL` / `SUPABASE_URL` | Project URL (client-side and edge functions) |
| `VITE_SUPABASE_ANON_KEY` / `SUPABASE_ANON_KEY` | Anonymous key (client-side queries, edge function auth) |

---

## Pitfalls

<!-- reference files -->
See `references/frontend-crud-patterns.md` for React + Supabase CRUD patterns (upsert with onConflict, batch chunking, CSV import with Brazilian format, localStorage fallback).

### Pitfall: `db query --linked` fails with "failed to connect to postgres"

The `supabase db query --linked` command requires the local Supabase Docker stack OR direct remote connectivity. In restricted environments (no Docker, no direct PG access), it fails with:

```
effect/sql/SqlError: PgClient: Failed to connect
```

**Fix:** Use the [Direct Management API](#alternative-direct-management-api-when-cli-fails) with curl and `SUPABASE_ACCESS_TOKEN` instead — no local Postgres needed.

### Pitfall: Migration history out of sync after manual SQL

If you run SQL directly via `db query` instead of through migrations, the migration history table won't reflect the changes. Subsequent `db push` or `db pull` may fail.

**Fix:** Use `supabase migration repair` to align local and remote state, or always execute schema changes via migration files.

### Pitfall: `db push` rejects new migrations when remote has unknown ones

```
Remote migration versions not found in local migrations directory.
supabase migration repair --status reverted <timestamp>
```

**Fix:** Pull the missing remote migration first, or use `migration repair` to tell Supabase the state:
```bash
supabase migration repair --status reverted <missing_remote_timestamp>
supabase migration repair --status applied <your_new_timestamp>
```

### Pitfall: `vercel build` copies `public/` data into output before `.vercelignore` filters

When deploying a Supabase-backed SPA that also ships local JSON data for offline/fallback use, `vercel build` copies the entire `public/` directory (including large JSON datasets) into `.vercel/output/static/` BEFORE `.vercelignore` rules are applied. The prebuilt deploy then fails with:

```
Error: File size limit exceeded (100 MB)
```

**Fix:** Remove data directories from build output after `vercel build`, before `vercel deploy`:

```bash
vercel build --yes
rm -rf .vercel/output/static/data/erp/
du -sh .vercel/output/static/              # verify under 50MB
vercel deploy --prebuilt --yes
```

**Prevention:** For Supabase-backed projects, rely on Edge Functions or the Supabase client at runtime rather than shipping raw data as static files. Keep only essential offline/fallback data in `public/`.
