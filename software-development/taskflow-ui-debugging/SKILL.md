---
name: taskflow-ui-debugging
description: "Debug TaskFlow UI when API returns data but frontend hides.

Load this skill when diagnosing a TaskFlow frontend issue where the backend API returns correct data but the page doesn't render what is expected. Pipeline: verify DB data via psql, test the API directly with curl, verify the frontend build for expected strings, and check date/timezone handling (UTC vs BRT). Includes diagnostic queries and curl examples."
type: ToolIntegration
timestamp: 2026-08-02T00:00:00Z
---

# TaskFlow UI Debugging

Use this when diagnosing a TaskFlow frontend issue where the backend
API returns correct data but the page doesn't render what is expected.

## Diagnostic Pipeline

### 1. Verify DB Data

```bash
ssh -i <key> ubuntu@<host> 'docker exec taskflow-db psql -U taskflow -d taskflow -c "
SELECT id, title, status, due_date, due_date_has_time, t.user_id, u.email
FROM tasks t JOIN users u ON t.user_id = u.id
WHERE t.status IN ('"'"'inbox'"'"','"'"'next_action'"'"','"'"'waiting'"'"')
  AND t.due_date IS NOT NULL ORDER BY t.due_date;"
```

### 2. Test the API Directly

```bash
curl -s http://localhost:8000/api/v1/auth/token -H "Content-Type: application/json" \
  -d '{"email":"<email>","password":"<pass>"}'
curl -s "http://localhost:8000/api/v1/tasks/\
?status=inbox,next_action,waiting&due_before=<ISO>&limit=20" \
  -H "Authorization: Bearer <TOKEN>"
```

### 3. Verify Frontend Build

```bash
docker exec taskflow-frontend sh -c \
  'grep -o "overdue-today" /app/dist/assets/index-*.js'
```

### 4. Compare Page Structure

| Aspect | Working | Broken |
|--------|---------|--------|
| Query type | | |
| Inline or child? | | |
| Skeleton hides children? | | |

## Pitfalls

### Skeleton hides prop content
Parent `useQuery` → child `useInfiniteQuery`. Child's `isLoading`
early-return swallows props. Fix: render prop content before skeleton.

### _to_local_date timezone
Date-only tasks normalize to 23:59 BRT (~02:59 UTC).
`astimezone(utc).date()` shifts day forward. Fix: use GMT-3.

### TanStack key prefix collision
Refetches both queries under same prefix.

### Axios response interceptor
Appends "Z" to naive dates. Only for SQLite dev, no-op in prod.
