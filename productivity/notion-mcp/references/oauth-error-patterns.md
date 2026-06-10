# Notion MCP OAuth Error Patterns

Captured during a re-auth session on 2026-06-09. These are the actual error messages and recovery patterns.

## Error: 401 "API token is invalid" on Notion REST API

**When:** Using the MCP OAuth access_token against `api.notion.com/v1/...`
**Error:**
```json
{"object":"error","status":401,"code":"unauthorized","message":"API token is invalid."}
```
**Cause:** MCP OAuth token from `mcp.notion.com` is **not** a Notion REST API key. Two completely separate auth systems.
**Fix:** Use the MCP Python SDK (StreamableHTTP) or create a proper Notion Internal Integration token (`ntn_...`).

## Error: 403 "error code: 1010" on Token Refresh

**When:** Attempting to refresh an expired MCP OAuth token via `https://mcp.notion.com/token`
**Error:** HTTP 403 with body `error code: 1010`
**Cause:** The MCP OAuth `refresh_token` expired (Notion MCP does not support long-lived refresh tokens). The only fix is full re-auth via `hermes mcp login notion`.
**Fix:** Full paste-back re-auth flow.

## Error: 404 "object_not_found" on notion-fetch (URL input)

**When:** `notion-fetch` called with full Notion URL for a page the integration doesn't have access to.
**Error:**
```json
{
  "name": "APIResponseError",
  "code": "object_not_found",
  "status": 404,
  "body": "{\"object\":\"error\",\"status\":404,\"code\":\"object_not_found\",\"message\":\"Could not find page with ID: a5dd663c-1156-4ebd-a7b3-59a945c9ac64. Check that you have access and that you're authenticated to the correct workspace.\",\"additional_data\":{\"integration_id\":\"1f8d872b-594c-80a4-b2f4-00370af2b13f\"}}"
}
```
**Debugging value:** The `integration_id` in `additional_data` tells you which integration is making the call. The user needs to share the page with that specific integration.

## Silent Error: notion-fetch returns empty text (UUID input)

**When:** `notion-fetch` called with just the UUID of a page the integration doesn't have access to.
**Output:** `{"text": ""}` — zero-length content, no error, no status code.
**Danger:** Looks like a blank page, misleading. Only the full URL variant returns a proper 404.
**Fix:** Always use full URL format when debugging access issues.

## OAuth Timeout Masking Success

**Message:** `✗ Authentication failed: MCP call timed out after 40.0s (configured timeout: 40.0s)`
**Reality:** Token exchange completed and `notion.json` was written to disk. The 40s timeout is from a subsequent MCP connection test, not the OAuth flow itself.
**Check:** Verify `notion.json` exists with valid tokens before retrying.

## Circular OAuth Loop (stale redirect URL)

**Symptom:** Hermes prints a new authorization URL immediately after you submit a redirect URL, instead of completing.
**Cause:** User pasted a redirect URL from a previous OAuth flow (different `state`). Hermes detects state mismatch and silently starts a new flow.
**Fix:** Kill the stale process and start fresh. Get the new URL from the fresh process output. Tell the user explicitly to only open the new URL.

## Token File Wiped by New Login

**Symptom:** `notion.json` disappears after running `hermes mcp login notion` and killing the process.
**Cause:** `hermes mcp login` deletes `notion.json` at initialization, before the OAuth flow starts.
**Prevention:** Always `cp $HERMES_HOME/mcp-tokens/notion.json{,.bak}` before re-auth.
