# Kusto / Internal Telemetry Investigation

> Extracted from deep-research SKILL.md — patterns for investigating bugs via Azure Data Explorer (Kusto) telemetry databases.

## Internal Data Source Investigation (Phase 0.5 variant)

When the research target is an internal database (Kusto, SQL, internal API) rather than public web sources:
1. **Skip the standard 4-agent pipeline entirely.** Web/GitHub/News/Academic agents add no value for internal telemetry investigation.
2. **Phase 0.5 becomes the primary phase**: Hermes directly queries the data source via REST API or SDK.
3. **Browser-based data explorers are unreliable** for automation: Azure Data Explorer web UI has VPN dialogs, trust dialogs, virtual scrolling. Always prefer REST API from terminal.
4. **Subagent timeout risk**: Kusto queries on large tables (billions of rows) can take 1-5 minutes each. Subagent default timeout (600s) may not be enough if multiple queries are needed sequentially. Prefer running queries directly in the main session or give subagents very specific, pre-tested queries.
5. **Start narrow, expand**: Query 1 day first, then expand to 7 or 30 days. Use `event_time > ago(1d)` to avoid scanning full table.
6. **Azure Data Explorer web UI pitfalls**: Two modal dialogs block interaction — "Adding connection" (click Trust) and "VPN Connection Required" (click Approve and Continue). These are NOT in the accessibility tree — must use `browser_console` with JS: `document.querySelectorAll('button').find(b => b.innerText.trim() === 'Trust')?.click()`. Results grid uses virtual scrolling (only ~7 rows rendered). **Always prefer REST API from terminal over browser automation.**

Pattern: Phase 0 (decompose questions) → Phase 0.5 (direct API queries, iterative) → Phase 4 (report). No external agents needed.

## Iterative Kusto Investigation Pattern

When investigating telemetry data to diagnose a bug, follow this proven progression:
1. **Schema discovery**: `.show tables`, `Table | getschema`, `Table | take 5`
2. **Event inventory**: `summarize count() by event_name | order by count_ desc` with keyword filters
3. **Sample inspection**: `take 3 | project event_time, key_fields, event_data` for each relevant event
4. **Distribution analysis**: `summarize count() by dimension` (platform, market, version, unitSource)
5. **Anomaly detection**: Cross-tabulate dimensions to find mismatches (e.g., market vs unit, platform vs mismatch rate)
6. **Timeline reconstruction**: For specific devices/users, order events by time to understand state transitions
7. **Root cause confirmation**: Find the code path that produces the telemetry pattern, verify hypothesis

Key insight: each query's results inform what to query next. This is inherently sequential and poorly suited to subagent parallelization.

## Slow Data Sources (Kusto, BigQuery, etc.)

When "research" means querying a slow internal database (30-300s per query):
- **Do NOT delegate to subagents** — 600s timeout is insufficient when each query takes 30-300s and you need 5-10 queries.
- **Run queries directly from parent agent** using execute_code or terminal.
- **Phase 0.5 is the right fit**: treat it as local codebase analysis but against a database. Hermes runs the queries, builds understanding iteratively, and synthesizes findings.
- **Optimize queries aggressively**: filter by time range first (`where event_time > ago(1d)`), avoid full-table scans, use `summarize` server-side instead of fetching raw rows.
- **IntRaw vs Int vs Prod tables**: Raw tables have lower latency but queries often timeout returning empty HTTP body. Int tables are more reliable for recent data. Debug/dev builds emit to Int, production to Prod.
- **Empty response debugging**: Kusto curl can return HTTP 200 but empty body on timeout. Add `-w "\nHTTP_%{http_code}"` to curl to distinguish timeout from auth failure. Use `execute_code` with explicit error handling rather than terminal pipe-to-python.
- **Device identifier pitfall**: `headers_dvhashid` can be empty string for all events — always verify with `dcount()` before using as group-by key; `headers_installid` is more reliable.
- **Iterative investigation pattern**: Start with event discovery (`.show tables`, `summarize count() by event_name`), then narrow to specific events, then cross-correlate. Each query informs the next — don't try to write the perfect query upfront.
- **Kusto REST API helper pattern**:
  ```python
  def kusto(query, db="SapphireNRT", timeout_min=5):
      token = subprocess.check_output(["az","account","get-access-token","--resource",
          "https://bingviznrt.eastus.kusto.windows.net","--query","accessToken","-o","tsv"],
          text=True, stderr=subprocess.DEVNULL).strip()
      body = json.dumps({"db":db,"csl":query,"properties":{"Options":{"servertimeout":f"00:{timeout_min:02d}:00"}}})
      r = subprocess.check_output(["curl","-s","--max-time",str(timeout_min*60+30),"-X","POST",
          "https://bingviznrt.eastus.kusto.windows.net/v1/rest/query",
          "-H",f"Authorization: Bearer {token...ype: application/json; charset=utf-8","-d",body],
          text=True, stderr=subprocess.DEVNULL)
      d = json.loads(r)
      return [c['ColumnName'] for c in d['Tables'][0]['Columns']], d['Tables'][0]['Rows']
  ```
- **Use management endpoint for .show commands**: POST to `/v1/rest/mgmt` (not `/v1/rest/query`) for `.show tables`, `.show table X schema` etc.
- **String matching in KQL for cross-platform data**: iOS and Android may serialize the same field differently (e.g., JSON `"key":"1"` vs Swift Dictionary `"key": 1`). Use multiple `contains` patterns in a `case` expression to handle both.
- **Prefer `execute_code` with a reusable helper function** over raw terminal curl. Define a `kusto_query(kql)` wrapper once and reuse it — avoids repeated token fetch, JSON escaping issues, and pipe-to-interpreter blocks. Save result to file then parse separately if needed.
- **Iterative narrowing pattern**: start with schema exploration (`.show tables`, `getschema`), then event name discovery (`summarize count() by event_name`), then targeted sampling (`take 5`), then aggregation. Each step informs the next query.
- **Device identity pitfall**: `headers_dvhashid` may be empty for certain events — always check. Use `headers_installid` as fallback device identifier and verify with `dcount()` before grouping.
- **Cross-referencing events**: When investigating a data flow (e.g., user sets preference → syncs to server → server sends notification), query each event type separately first, then join by `headers_installid` or `userId` to trace the full path. Don't try to join in a single query — it will timeout.

### Kusto-specific execution tips

- **execute_code timeout**: default 300s may not be enough for a script that runs multiple sequential Kusto queries. If a single query takes 200s+, use terminal with explicit `--max-time` on curl instead.
- **Azure Data Explorer browser UI is unreliable for automation**: VPN dialogs, trust dialogs, virtual scrolling hide results. Always prefer REST API from terminal.
- **Pre-test queries before delegating**: If you must use subagents for parallel queries, run each query once yourself first to verify it completes within timeout. Give subagents pre-tested, specific queries with known execution times.

## Kusto REST API from Terminal

When querying Azure Data Explorer from the terminal (instead of browser UI which has VPN dialogs, trust popups, virtual scrolling issues):

```bash
TOKEN=$(az account get-access-token --resource https://<cluster>.kusto.windows.net --query accessToken -o tsv 2>/dev/null)
curl -s --max-time 400 -X POST "https://<cluster>.kusto.windows.net/v1/rest/query" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"db":"<database>","csl":"<KQL>","properties":{"Options":{"servertimeout":"00:05:00"}}}'
```

Key details:
- `/v1/rest/query` for data queries, `/v1/rest/mgmt` for management commands (`.show tables` etc.)
- v2 (`/v2/rest/query`) returns JSON frames array, supports progressive mode — use for large results
- Response: `.Tables[0].Rows` (array of arrays), `.Tables[0].Columns` for schema
- Default timeout: 4 min. Max: 1 hour via `servertimeout` property.
- Default truncation: 500K rows / 64MB. Disable with `"notruncation": true`.
- Token expires in ~1 hour; re-fetch before each query in long sessions.
- For `execute_code`, wrap in a Python helper function to keep queries clean.
- Save results to `/tmp/` files and parse separately to avoid pipe-to-interpreter blocks.

## Kusto Investigation Pitfalls

- **dvhashid may be empty** — use `headers_installid` as device identifier instead. Always verify aggregation keys before drawing conclusions.
- **Sample rate matters**: check `sample` field in telemetry event definitions (e.g. `sample=10` means only 10% of events are logged). Multiply observed counts accordingly.
- **Start with 1-day window**, expand to 7 or 30 days only after confirming query completes in time.
- **execute_code timeout is 300s** — for queries taking 200+s, use `terminal` with explicit `--max-time` on curl instead.
- **Browser-based Kusto explorers** (Azure Data Explorer web UI) are unreliable for automation: VPN dialogs, trust dialogs, virtual scrolling that hides data. Always prefer REST API.

## Subagent Pitfalls for Kusto

- `execute_code` has a 300s hard timeout. For multi-query Kusto investigations (each query 30-300s), use `terminal()` with explicit `--max-time` on curl instead. Write results to `/tmp/*.json` and parse in a separate step.
- When investigating internal databases, the parent session is almost always more reliable than subagents: no timeout pressure, can iterate on queries, can adjust based on intermediate results. Reserve subagents for parallel independent web searches, not sequential database exploration.
- **Subagent model availability failures**: delegate_task can fail with `model_not_supported` errors when the configured model is temporarily unavailable on the provider. When this happens, don't retry — fall back to running the queries/tasks directly in the parent session. This is especially important for internal data source investigations where each query takes 30-300s and the parent agent can run them sequentially without timeout risk.
- **Kusto queries in subagents**: Even when the model works, Kusto queries are too slow for subagents (600s timeout, each query 30-300s, need 5-10 queries). Always prefer running Kusto queries directly. Use `scripts/kusto_query.py` as the reusable helper.
- **Subagent model failures**: Copilot provider may return `model_not_supported` for subagent model selection, failing the entire batch. When this happens, don't retry subagents — fall back to running the work directly in the parent session. This is especially common for Kusto/database investigation where the parent session already has auth context and query helpers set up.
- **Kusto/database queries in subagents**: Even when subagents launch successfully, each Kusto query takes 30-300s. A subagent with 5 queries will likely hit the 600s timeout. Prefer the `execute_code` helper function pattern in the parent session.
