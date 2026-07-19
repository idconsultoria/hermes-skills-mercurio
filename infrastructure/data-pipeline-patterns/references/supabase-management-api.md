# Supabase Management API — Remote SQL without CLI

When the Supabase CLI is unavailable but you have the access token and/or service_role key,
use the Management REST API to run SQL, inspect tables, and manage the database.

## Quick reference

```bash
# List tables in public schema
curl -s -X POST 'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query' \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT table_name FROM information_schema.tables WHERE table_schema='\''public'\'' ORDER BY table_name;"}'

# Run a migration
curl -s -X POST 'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query' \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE TABLE IF NOT EXISTS ..."}'

# Count rows in a table
curl -s -X POST 'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query' \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) FROM notas_fiscais"}'
```

## Auth requirements
- **Access token** (`sbp_...`) from Supabase dashboard → Settings → API or `supabase login`
- The token is in `SUPABASE_ACCESS_TOKEN` env var or `~/.supabase/access-token`

## SQL escaping in shell (single quotes)

Single quotes inside JSON strings require awkward escaping in shell:

```bash
# Use '"'"' to escape a single quote inside a single-quoted string:
curl ... -d '{"query": "SELECT ... WHERE col = '"'"'VALUE'"'"';"}'

# Better: use a temp file or heredoc for multi-line SQL:
SQL=$(cat migration.sql | tr '\n' ' ')
curl ... -d "{\"query\": \"$SQL\"}"
```

## Pitfalls
- SQL must be a single statement (no semicolons in the middle)
- `CREATE TABLE IF NOT EXISTS` is safe for idempotent migrations
- The API returns `[]` for DDL statements (CREATE/ALTER/DROP) — this means SUCCESS
- For SELECT statements, results are returned as a JSON array of row objects
- Table name case: PostgreSQL folds unquoted identifiers to lowercase. Use double quotes for
  CamelCase table names: `SELECT * FROM "notas_fiscais"`

## When to use this vs Supabase client SDK
- **Management API**: DDL, schema inspection, ad-hoc queries during debugging
- **Supabase client SDK** (`@supabase/supabase-js`): application queries, RLS-enforced access, real-time subscriptions
