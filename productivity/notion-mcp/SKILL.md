---
name: notion-mcp
description: "Interact with the Notion MCP server via Hermes Agent — OAuth setup, tool catalog, Python scripting patterns."
version: 1.1.0
author: Hermes Agent (learning session)
tags: [notion, mcp, oauth, productivity]
---

# Notion MCP — Hermes Agent Integration

The official Notion MCP server (hosted at `https://mcp.notion.com/mcp`) provides 14 tools for AI agents to read, search, create, and manage Notion pages, databases, views, comments, and users.

This skill documents how to set up, authenticate, and programmatically call the Notion MCP server from within Hermes Agent.

---

## Prerequisites

- `mcp` Python package installed in the Hermes venv:
  ```bash
  /opt/hermes/.venv/bin/pip install mcp
  ```
- Network access to `mcp.notion.com`
- A Notion account with pages shared to the integration

---

## Configuration

Add to `$HERMES_HOME/config.yaml` (already done if you followed Option A):

```yaml
mcp_servers:
  notion:
    url: "https://mcp.notion.com/mcp"
    auth: oauth              # REQUIRED — triggers OAuth 2.1 PKCE flow
    timeout: 180
    connect_timeout: 60
```

The `auth: oauth` key is **required**. Without it, Hermes treats the server as plain HTTP — tools appear discoverable but every call silently fails.

---

## OAuth Authentication (Headless / Paste-Back)

Since this runs on a **headless remote server**, use the paste-back flow:

```bash
# Start the OAuth flow (will wait for paste-back)
HERMES_HOME=/opt/data /opt/hermes/bin/hermes mcp login notion
```

The command prints an authorization URL like:
```
https://mcp.notion.com/authorize?response_type=code&client_id=...&...
```

**Steps:**

1. **Open the printed URL** in your local browser
2. **Authorize** the Notion connection
3. The browser redirects to `http://127.0.0.1:PORT/callback?...` — **connection error is expected** on a remote server
4. **Copy the full redirect URL** from the address bar (or just `?code=...&state=...`)
5. **Paste it** at the Hermes prompt that says "Or paste the redirect URL here…"

Tokens are cached at `$HERMES_HOME/mcp-tokens/notion.json`.

### Paste-Back from Within a Hermes Session (no second terminal)

When you're inside an active Hermes agent session and don't have a second terminal, use a **background PTY process**:

```python
from hermes_tools import terminal, process

# 1. Start OAuth in background PTY (keeps stdin open for paste-back)
result = terminal(
    command="hermes mcp login notion",
    background=True, pty=True, timeout=600
)
session_id = result["session_id"]

# 2. Poll to get the authorization URL
poll = process(action="poll", session_id=session_id)
# URL is in poll["output_preview"]

# 3. Present the URL to the user — they open in browser, authorize,
#    copy the redirect URL, and paste it back

# 4. Submit the redirect URL when provided
process(action="submit", session_id=session_id, data="http://127.0.0.1:PORT/callback?code=xxx&state=yyy")

# 5. Wait for completion
process(action="wait", session_id=session_id, timeout=120)
```

**Key detail:** `background=true` + `pty=true` together is essential — this makes the interactive paste-back prompt work from within a non-interactive terminal call. Running foreground will time out waiting for input.

### ⚠️ Pitfall: The 40-Second Timeout That Actually Succeeds

The `hermes mcp login notion` command can print `"Authentication failed: MCP call timed out after 40.0s"` even though the token exchange **actually completed** and tokens were saved to disk. This happens when Notion's token endpoint takes longer than the default 40s connect_timeout.

**Do NOT retry on timeout — first check if tokens were saved:**

```bash
# 1. Verify token file exists with valid tokens
ls -la $HERMES_HOME/mcp-tokens/notion.json

# 2. Validate token
python3 -c "
import json, time
with open('$HERMES_HOME/mcp-tokens/notion.json') as f:
    tok = json.load(f)
print('Valid:', len(tok.get('access_token','')) > 20 and len(tok.get('refresh_token','')) > 20)
print('Expired:', time.time() > tok.get('expires_at', 0))
print('Expires in:', round((tok['expires_at'] - time.time())/60, 1), 'min')
"

# 3. Test connection — if this succeeds, OAuth worked despite the timeout message
/opt/hermes/bin/hermes mcp test notion
```

If `hermes mcp test notion` reports `✓ Connected` with tools discovered, the flow succeeded. Ignore the timeout message.

### Important: Each Login Is a Fresh OAuth Session

Every `hermes mcp login` invocation generates a new `state` + `code_challenge`. If the login times out, the old redirect URL becomes invalid. You MUST start a fresh `hermes mcp login notion` and ask the user to re-authorize with the new URL — reopening the old URL in the browser will fail.

### ⛔ Pitfall: Circular OAuth loop (stale redirect URL)

When the user pastes a redirect URL from a **previous** OAuth flow (different `state` parameter), Hermes detects the mismatch and silently starts a **new** OAuth flow instead of failing clearly. This creates a confusing cycle:

1. You start `hermes mcp login notion` → prints URL-A (port N, state X)
2. User opens a **different URL-B** (from a prior run — different port, different state) in their browser, authorizes, gets redirect URL-B
3. You submit redirect URL-B → state doesn't match URL-A → Hermes prints URL-C (brand new flow)
4. User thinks they need to authorize again → opens URL-B (still stale) → loop

**Visual symptom:** the process prints a **new** authorization URL immediately after you submitted a redirect URL, instead of completing with a success message.

**Breaking the loop:**
1. Kill the stale process and start fresh: `terminal(command="hermes mcp login notion", background=true, pty=true, timeout=600)`
2. Poll to get the **new** URL — send it to the user and explicitly tell them to open only this one (not an old one from earlier in the chat)
3. When the user submits the redirect back, submit it immediately

**In messaging sessions (Telegram/Discord):** the user may be looking at an old message URL while the process already moved to a new port/state. Always send the latest URL explicitly and ask them to open it *now* — not scroll up. The port number in the URL changes each run (e.g., `48207` → `57433` → `45511`) — this is the most visible signal that a new flow started.

### Verify Connection

```bash
/opt/hermes/bin/hermes mcp test notion
```

Expected output:
```
✓ Connected (1505ms)
✓ Tools discovered: 14
  notion-search           ...
  notion-fetch            ...
```

### Re-authentication

```bash
/opt/hermes/bin/hermes mcp login notion    # force re-auth
hermes mcp list                             # check server status
```

### ⚠️ Pitfall: Token file wiped by re-auth attempt

**`hermes mcp login notion` deletes the existing `notion.json` token file when it starts a new flow.** If the login is killed mid-flow (timeout, process kill, user abandons), the file is gone and you lose the valid tokens you had.

**Always back up tokens before re-authenticating:**

```bash
cp $HERMES_HOME/mcp-tokens/notion.json{,.bak}   # backup before starting
```

After re-auth succeeds:
```bash
diff $HERMES_HOME/mcp-tokens/notion.json{,.bak} > /dev/null && echo "tokens unchanged" || echo "tokens renewed"
```

After verifying the new token works, remove the backup:
```bash
rm $HERMES_HOME/mcp-tokens/notion.json.bak
```

**Concurrent login danger:** Even checking `ls -la $HERMES_HOME/mcp-tokens/notion.json` before starting a new login doesn't help — the delete happens when the command initializes. The only defense is a pre-emptive backup.

---

## Available Tools (14 total)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `notion-search` | Semantic search over workspace + connected sources | `query` (min 1 char), `page_size` (1-25), `source`, `filters`, `page_url` |
| `notion-fetch` | Fetch page/database/datasource content + metadata | `id` (UUID or URL) |
| `notion-create-pages` | Create one or more pages | `pages` array with parent + properties + markdown |
| `notion-update-page` | Update page properties/content | `id`, properties |
| `notion-move-pages` | Move pages to new parent | pages + parent |
| `notion-duplicate-page` | Duplicate a page | `id`, target |
| `notion-create-database` | Create database from SQL DDL | DDL schema string |
| `notion-update-data-source` | Update data source schema | data source ID + DDL |
| `notion-create-comment` | Add comment to page | `page_id`, `content` |
| `notion-get-comments` | List comments on page | `id` |
| `notion-get-teams` | List teams/teamspaces | None |
| `notion-get-users` | List workspace users | None |
| `notion-create-view` | Create database view | `database_id` or `parent_page_id` |
| `notion-update-view` | Update view config | view config |

---

## Python Scripting Patterns

To call MCP tools programmatically from Hermes Agent (e.g., via `terminal` or `execute_code`), use the **StreamableHTTP** transport from the `mcp` Python SDK.

### Basic Connection Pattern

```python
import asyncio, json
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

async def main():
    with open('/opt/data/mcp-tokens/notion.json') as f:
        tok = json.load(f)

    headers = {'Authorization': f'Bearer {tok["access_token"]}'}

    async with streamablehttp_client(
        url='https://mcp.notion.com/mcp',
        headers=headers,
        timeout=30
    ) as streams:
        # StreamableHTTP returns 3 values (NOT 2):
        read, write, close_fn = streams  # ← 3-tuple!

        async with ClientSession(read, write) as session:
            await session.initialize()

            # Call any tool
            result = await session.call_tool('notion-search', {
                'query': 'some topic',
                'page_size': 25
            })

            # Results are in result.content[0].text
            print(result.content[0].text)

asyncio.run(main())
```

### Important Gotchas

1. **3-tuple unpacking**: `streamablehttp_client` yields `(read, write, close_fn)` — 3 values, not 2.
2. **Tool names include `notion-` prefix**: e.g. `notion-search`, `notion-fetch` — this is the actual internal tool name.
3. **`notion-search` query minimum**: The `query` parameter requires min 1 character. Use `'a'` for broad results.
4. **`notion-fetch` parameter**: The only required param is `id` (not `url_or_id`). Accepts UUID or full URL.
5. **Fetch response**: Returns JSON with `text` field containing XML-like markdown with `<ancestor-path>` showing page hierarchy:
   ```xml
   <ancestor-path>
   <parent-page url="..." title="Parent Page Name"/>
   </ancestor-path>
   ```
   Pages **without** `<parent-page>` in the ancestor-path are root-level pages.
6. **`notion-fetch` silent empty response on inaccessible pages**: When the integration has **no access to a page** (page not shared with the MCP integration), behavior differs by input format:
   - **UUID** → returns `{"text": ""}` (empty string, no error, no status code) — misleading, looks like a blank page
   - **Full URL** → returns a proper `APIResponseError` with `code: "object_not_found"` (404)
   
   **Always pass the full URL** to `notion-fetch` when debugging access issues. A UUID that returns empty text means the integration doesn't have access, not that the page is empty.
7. **Search response**: Returns JSON with `results` array, each item having `id`, `title`, `url`, `type`, `timestamp`, `highlight`.
8. **Rate limiting**: Each tool call takes ~1-2s. Be conservative with batch calls (don't fetch 150+ pages in a loop — use targeted queries).
9. **Direct HTTP POST does NOT work**: The Notion MCP server uses StreamableHTTP transport, not plain HTTP POST. You must use the `mcp` Python SDK.
10. **Run from Hermes venv**: Use `/opt/hermes/.venv/bin/python3` — the `mcp` package is installed there.

Use `inspect_database.py` to quickly understand an unknown database's schema and status workflow:

```bash
/opt/hermes/.venv/bin/python3 scripts/inspect_database.py <data_source_uuid>
```

Output: property names/types, select options, status groups with workflow states, relation targets, rollup config.

### Listing Root Pages

To find workspace root-level pages (no parent):

```python
async with streamablehttp_client(url, headers=headers) as streams:
    read, write, close_fn = streams
    async with ClientSession(read, write) as session:
        await session.initialize()

        # Search broadly
        result = await session.call_tool('notion-search', {
            'query': 'a',
            'page_size': 25
        })
        data = json.loads(result.content[0].text)

        # Check each page's parent
        root_pages = []
        for p in data['results']:
            fetch = await session.call_tool('notion-fetch', {'id': p['id']})
            text = json.loads(fetch.content[0].text)['text']
            if '<parent-page' not in text:
                root_pages.append(p)
```

---

## CLI Quick Reference

```bash
# List MCP servers
hermes mcp list

# Test connection
hermes mcp test notion

# OAuth login (paste-back)
hermes mcp login notion

# List tools from CLI (non-interactive)
hermes mcp test notion | grep "notion-"

# Check token status
cat $HERMES_HOME/mcp-tokens/notion.json
```

---

## DDL Reference for `notion-create-database`

The `schema` parameter uses SQL DDL syntax. Key rules:

### ✅ Correct Syntax

```sql
CREATE TABLE "Name" (
    "title_field" title,
    "select_field" select('Option A', 'Option B', 'Option C'),
    "multi_select_field" multi_select,
    "text_field" rich_text,
    "date_field" date,
    "number_field" number,
    "url_field" url,
    "email_field" email
)
```

### ⚠️ Critical Rules

| Rule | Correct | Incorrect |
|------|---------|-----------|
| Select options use **single quotes** | `select('Opcao A', 'Opcao B')` | `select("Opcao A")` or `select` with double quotes |
| Multi-select without predefined options | `multi_select` | `multi_select('A', 'B')` |
| No trailing commas | `"a" title, "b" number` | `"a" title, "b" number,` |
| Table/column names double-quoted | `"My Table"` | `My Table` |

### Creating Under a Parent

Always pass `parent` at the top level with `page_id` and `type`:

```python
await session.call_tool('notion-create-database', {
    'parent': {'page_id': parent_page_id, 'type': 'page_id'},
    'title': 'Database Name',
    'description': 'Optional description',
    'schema': 'CREATE TABLE "X" ("Name" title, ...)'
})
```

### Parsing the Response

The response is JSON with a `result` field containing XML:

```text
{"result":"Created database: <database url=\"{{\"https://app.notion.com/p/...\"}}\">..."}
```

Extract IDs with regex:

```python
import re
# Database ID (raw hex)
m = re.search(r'database url="\{\{https://app\.notion\.com/p/([a-f0-9]+)', text)
# Data source ID (UUID)
m = re.search(r'collection://([a-f0-9-]+)', text)
```

### Creating Views with `notion-create-view`

```python
await session.call_tool('notion-create-view', {
    'data_source_id': '<uuid from create-database response>',
    'database_id': '<database uuid>',
    'name': 'Kanban',
    'type': 'board',  # table, board, list, calendar, timeline, gallery
    'configure': 'GROUP BY "Status"'  # optional DSL
})
```

### Creating Pages in a Database

```python
await session.call_tool('notion-create-pages', {
    'parent': {'database_id': db_id, 'type': 'database_id'},
    'pages': [
        {'properties': {'ColumnName': 'value', 'NumberCol': 42}}
    ]
})
```

### Updating Page Content

Use `notion-update-page` with the `command` parameter:

```python
# Replace entire content
await session.call_tool('notion-update-page', {
    'page_id': page_id,
    'command': 'replace_content',
    'new_str': '# New content here'
})

# Search-and-replace specific sections (safer)
await session.call_tool('notion-update-page', {
    'page_id': page_id,
    'command': 'update_content',
    'content_updates': [
        {'old_str': '## Old Section', 'new_str': '## New Section'}
    ]
})

# Update properties only
await session.call_tool('notion-update-page', {
    'page_id': page_id,
    'command': 'update_properties',
    'properties': {'title': '# New Title'}
})
```

> ⚠️ `replace_content` can DELETE child pages and databases. Use `update_content` (search-and-replace) when the page has children.

## Troubleshooting

Full error transcript library with recovery steps: `references/oauth-error-patterns.md`
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `MCP SDK not available` | `mcp` package missing | `pip install mcp` or `uv pip install mcp` |
| OAuth silently skipped | Missing `auth: oauth` in config | Add `auth: oauth` under the server entry |
| Tools return nothing / 403 | No OAuth tokens | Run `hermes mcp login notion` |
| `400 Bad Request` via SSE | Wrong transport | Use `streamablehttp_client` not `sse_client` |
| `ValueError: too many values to unpack` | Wrong unpack count | Unpack 3 values: `read, write, close_fn` |
| `Tool ... not found` | Wrong tool name | Use full name including `notion-` prefix |
| `Too small: expected string >=1` | Empty query | Use minimum 1 character for search |

---

## Token Storage

Tokens are auto-refreshed. Located at:
- `$HERMES_HOME/mcp-tokens/notion.json` — access + refresh tokens
- `$HERMES_HOME/mcp-tokens/notion.client.json` — OAuth client metadata
- `$HERMES_HOME/mcp-tokens/notion.meta.json` — OAuth provider metadata
