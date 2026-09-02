# OpenCode Zen / Go provider routes & Contributor opt-in

Hermes talks to OpenCode through two provider routes. Each maps to a `.env` key that
owns the credential.

| Provider name (in config) | base_url | `.env` key |
|---------------------------|----------|------------|
| `opencode-go` | `https://opencode.ai/zen/go/v1` | `OPENCODE_GO_API_KEY` |
| `opencode-zen` | `https://opencode.ai/zen/v1` | `OPENCODE_ZEN_API_KEY` |

A `providers.<name>` block names a friendly alias and points at the backend that owns
the key:

```yaml
providers:
  opencode-free:
    api_mode: chat_completions
    base_url: https://opencode.ai/zen/v1
    model: muse-spark-1.2-contributor-free
    provider: opencode-zen      # owns OPENCODE_ZEN_API_KEY
```

## Contributor models need a one-time opt-in (HTTP 403)

Some models collect usage data to improve quality and **require explicit consent** before
they serve any request. Symptom in `errors.log`:

```
HTTP 403: This model collects data used to improve its quality and requires explicit opt
in: https://opencode.ai/workspace/wrk_<WORKSPACE_ID>/go
```

- This is **provider-side consent**, not a Hermes bug. Opening the URL and accepting
  opt-in makes the model usable.
- Until opt-in is done, the model is unusable and the run falls back. If no fallback is
  configured, the session dies with `Fallback to <X> failed: provider not configured`.
- After opt-in, the free (and non-free) Contributor variants work; this is per-workspace,
  so a different workspace needs its own opt-in.

## Verifying which model is live

The header of a session (and `hermes config get model`) shows the active model/provider.
A session-level switch via OpenCode Go applies immediately; the config `default` only
applies to new sessions after a gateway restart.

## Common chain example (Mercúrio, 26/08/2026)

Default: `muse-spark-1.2-contributor-free` / `opencode-free`.
Fallbacks in order:
1. `muse-spark-1.2-contributor` / `opencode-go`
2. `deepseek-v4-flash-vision-exp` / `opencode-go`
3. `hy3-free` / `opencode-free`
