# Session: Overdue Tasks Hidden on Today Page (2026-07-28)

## Root Causes Found & Fixed

### Fix 1: TaskList skeleton hiding overdue section

**Commit**: `1568a8b`
**Files**: `frontend/src/components/TaskList.tsx`

The `isLoading` early-return rendered only a `<TaskListSkeleton />`,
discarding the `overdueTasks` prop passed by the Today page. The
overdue section only appeared after the child's `useInfiniteQuery`
resolved — which could be after the parent's `useQuery` for overdue
data, creating a window where props were available but invisible.

**Pattern**: Parent `useQuery` + child `useInfiniteQuery` where the
child renders a skeleton during initial load. Any content passed as
props from the parent is lost until the child's own query resolves.

### Fix 2: `_to_local_date` using UTC instead of GMT-3

**Commit**: `1568a8b`
**Files**: `backend/taskflow/services/report_service.py`

```python
# Before (bug)
return dt.astimezone(timezone.utc).date()

# After (fix)
user_tz = timezone(timedelta(hours=-3))
return dt.astimezone(user_tz).date()
```

Date-only tasks are normalized to 23:59 in the user's timezone (BRT).
For "July 27" this becomes `2026-07-28T02:59:00+00:00` in UTC.
Converting to UTC.date() returns July 28, so the report never
considers these tasks overdue against a July 27 report_date.

## Diagnostic Flow Used

1. Read the source code on `sprint1-v2` branch → feature existed
2. Switched to `master`, confirmed feature was already deployed
3. Checked production DB directly via SSH → tasks present with past dates
4. Checked the SQL query against `due_before` boundary → matched correctly
5. Tested the API directly from the backend container → returned correct tasks
6. Checked frontend build in container → feature code was compiled in
7. Compared Today vs Upcoming component structure → TaskList skeleton was the differentiator
8. Identified the exact early-return that swallowed overdueTasks prop

## Key Learning

TanStack Query's `useInfiniteQuery` with `isLoading` skeleton is a
common pitfall when the parent passes separate query results as props
to the child. The timing between `useQuery` (parent) and
`useInfiniteQuery` (child) creates a race where the child renders its
loading state before incorporating the parent's already-fetched data.
