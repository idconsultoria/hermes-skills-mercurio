# PostgreSQL Seed Script Compatibility

When writing seed scripts that must run on both SQLite (dev) and PostgreSQL (prod/preview), 
the following type differences cause silent successes on SQLite but crashes on PostgreSQL.

## 1. Datetime: always pass objects, never strings

| Column type | SQLite accepts | PostgreSQL accepts |
|-------------|---------------|-------------------|
| `DateTime(timezone=True)` | `'2026-05-25T08:00:00+00:00'` (str) | `datetime(2026,5,25,8,0, tzinfo=timezone.utc)` |
| `Date` | `'2026-05-25'` (str) | `date(2026,5,25)` |
| `DateTime` | `'2026-05-25T08:00:00'` (str) | `datetime(2026,5,25,8,0)` |

**Pattern — `_ts()` helper:**
```python
# ❌ BROKEN on PostgreSQL
def _ts(day_offset, hour=12, minute=0):
    d = MONDAY + timedelta(days=day_offset, hours=hour-8, minutes=minute)
    return d.isoformat()  # ← string

# ✅ WORKS on both
def _ts(day_offset, hour=12, minute=0):
    d = MONDAY + timedelta(days=day_offset, hours=hour-8, minutes=minute)
    return d  # ← datetime object
```

For **date-only** columns (like `report_date`):
```python
# ❌ BROKEN on PostgreSQL
"report_date": (MONDAY + timedelta(days=day)).date().isoformat(),  # string

# ✅ WORKS on both
"report_date": (MONDAY + timedelta(days=day)).date(),  # date object
```

## 2. Booleans: use Python `True`/`False`, not integers 0/1

| Column type | SQLite accepts | PostgreSQL accepts |
|-------------|---------------|-------------------|
| `Boolean` | `0`, `1`, `True`, `False` | Only `True`, `False` or `'true'`, `'false'` |
| `Integer` | `0`, `1`, `True`, `False` | Only `0`, `1` |

> **SQLite is lenient:** writes `1` to a Boolean column and it works.  
> **PostgreSQL is strict:** writes `1` to a Boolean column and raises:
> `DatatypeMismatchError: column "is_active" is of type boolean but expression is of type integer`

**Common culprits in seed scripts:**

```sql
-- ❌ BROKEN on PostgreSQL
INSERT INTO webhooks (...) VALUES (..., 1, :criado, :criado);
INSERT INTO mcp_action_tokens (...) VALUES (..., 0, :criado);
INSERT INTO users (...) VALUES (..., 1, :criado, :criado);  -- token_version is INTEGER, not bool!

-- ✅ WORKS on both (use named parameters or Python values)
INSERT INTO webhooks (...) VALUES (..., True, :criado, :criado);
INSERT INTO users (...) VALUES (..., 1, :criado, :criado);  -- token_version=1 IS correct (int)
```

**⚠️ Watch out for sed over-correction:** `sed 's/, 1, :criado/, True, :criado/g'` catches `token_version=1` too, turning it into `token_version=True` which breaks the INTEGER column. Be specific about which columns are boolean vs integer.

## 3. Quick diagnostic — check a seed run's failure

Error message tells you exactly which parameter failed:

| Error fragment | Problem | Fix |
|---------------|---------|-----|
| `expected a datetime.date or datetime.datetime instance, got 'str'` | ISO string where datetime needed | Return `datetime` object |
| `'str' object has no attribute 'toordinal'` | ISO date string where `date()` needed | Return `date` object |
| `column "X" is of type boolean but expression is of type integer` | `1`/`0` where `True`/`False` needed | Use Python booleans |
| `column "X" is of type integer but expression is of type boolean` | `True` where `1` needed | Use Python integers (common in `token_version`) |
