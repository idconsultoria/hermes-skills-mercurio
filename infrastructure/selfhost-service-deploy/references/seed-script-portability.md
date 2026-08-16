# Seed Script Portability — SQLite (dev) vs Postgres (preview/prod)

Reference from Zera `scripts/seed_preview.py` (14/08/2026). A seed script that must run against
both SQLite (local dev, `create_all`) and Postgres (preview `zera_pr_N`, prod) with raw SQL
`text()` inserts hits these dialect differences:

## 1. UUID columns

- **SQLite:** binding a `uuid.UUID` object fails (`type 'UUID' is not supported`).
  Pass the **string** form: `str(uuid.UUID(...))` always.
- **Postgres (asyncpg):** REJECTS a plain `str` for a `uuid` column in a bound param
  (`operator does not exist: uuid = character varying`) — it needs a `uuid.UUID` object.
  (Older note said "accepts both" — wrong under asyncpg; caught by agy INFRA-27/28.)

**Rule:** build all ID params as strings (`def _uid(n) -> str`) and pass them through a
dialect-aware `b()` helper on EVERY bind (inserts AND deletes):

```python
dialect = s.bind.dialect.name
if dialect == "postgresql":
    b = lambda v: uuid.UUID(v) if isinstance(v, str) else v   # transparent if already UUID
else:
    b = lambda v: str(v) if isinstance(v, uuid.UUID) else v
# ... {"id": b(_uid(300)), "uid": b(U), ...}
# ... DELETE ... WHERE user_id = :u  → {"u": b(U)}   ← deletes too!
```

The `isinstance(v, str)` guard matters: `uuid.UUID(uuid.UUID(...))` raises AttributeError
(detox lookup returns an already-typed UUID on PG).

## 2. JSON columns (JSONFlexible / JSONB)

- **SQLite:** binding a `dict` fails (`type 'dict' is not supported`). Must `json.dumps(...)`.
- **Postgres:** `'{}'::jsonb` inline works, BUT binding a `json.dumps` string to a jsonb column
  WITHOUT a cast fails under asyncpg (`can't adapt type 'str'` / type mismatch). Use a
  dialect-aware placeholder for every JSON column:

```python
if dialect == "postgresql":
    jc = lambda col: f"CAST(:{col} AS jsonb)"
else:
    jc = lambda col: f":{col}"
# INSERT ... f"VALUES (:id, :uid, {jc('brutos')}, ...)"
```

Never build `j('brutos')` into the SQL text — `j('brutos')` renders as a literal function call
in the SQL string, not a bound param. `CAST(:col AS jsonb)` is the only form that keeps the
placeholder AND casts for PG.

## 3. Numeric(14,2) / Decimal

- **SQLite:** binding `Decimal` fails (`type 'decimal.Decimal' is not supported`).
  Pass `float(valor)`.
- **Postgres:** accepts Decimal.

## 4. CHECK constraints are real in both

The app's CHECK enums (`tipo IN ('preditiva','lembrete','elogio','alerta')`, status enums, etc.)
apply on SQLite too. A seed using a wrong enum value (e.g. `'missao'` for notifications) fails
with `IntegrityError: CHECK constraint failed` on SQLite — but Postgres raises the same. Match
exact enum values from `api/models.py`.

## 5. Table columns differ per model — read models.py first

- `users` has `id` (not `user_id`); dependent tables use `user_id`.
- `chat_messages` has **no** `user_id` — clean via
  `DELETE FROM chat_messages WHERE session_id IN (SELECT id FROM chat_sessions WHERE user_id=:u)`.
- `streaks` has `atualizado_em` but **no** `criado_em`.
- `user_missions` requires BOTH `criado_em` and `atualizado_em`.
- `verification_tokens` has `user_id` but is NOT cascade-cleaned by default — add it to the
  manual delete list.

## 6. Idempotency pattern

Delete user-scoped rows in dependency order before inserting (children first), commit, then
insert. For `chat_messages` (no user_id) handle specially. Test by running the seed twice in a row.

## 7. Catalog seeding inside the preview seed

If the preview needs catalog rows (tracks/missions/badges/plans), call the app's own
`seed_catalog(session)` and **commit** before querying for specific slugs — otherwise the lookup
returns nothing (the flush happened but the select ran in a fresh implicit transaction).

## 8. Timeline must be dynamic

Production seeds with hardcoded dates (`2026-08-09`) are only valid the week they're written.
Use `datetime.now(timezone.utc)` and normalize the baseline day to `00:00:00`:
```python
NOW = datetime.now(timezone.utc)
D0 = datetime.combine(NOW.date() - timedelta(days=7), datetime.min.time(), tzinfo=timezone.utc)
```
Then `_ts(day_offset, hour)` = `D0 + timedelta(days=day_offset, hours=hour, minutes=minute)`
— do NOT subtract 12h (`hours=hour - 12`), which pushes morning events to the previous day
after D0 is normalized.

**Clamp future timestamps (agy INFRA-33/41):** a seed run in the morning with events at
`hour=20` on the LAST day would write future rows. Clamp any `criado` that exceeds `NOW`:

```python
criado = _ts(d, 20)
if criado > NOW:
    criado = NOW
```
