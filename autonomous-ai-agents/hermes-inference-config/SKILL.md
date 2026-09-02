---
name: hermes-inference-config
description: "Configure Hermes model/provider/fallback; route crons."

Load this skill when selecting or switching a Hermes model/provider, setting fallback chains, or routing crons. Covers hermes config set/get, provider definition, pin-vs-inherit for crons, and reading model errors from logs."

Load this skill when: selecting/switching a model or provider, setting a fallback chain, making cron jobs follow (or break from) the global model ladder, or diagnosing model/provider failures. Covers `hermes config set/get` for model/provider/fallback_providers, defining providers, the critical pin-vs-inherit rule for crons, and reading model errors from the logs.
version: 1.0.0
author: Mercúrio
license: MIT
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [hermes, model, provider, fallback, cron, config, opencode]
    related_skills: [hermes-agent, messaging-platforms]
category: autonomous-ai-agents
type: Reference
timestamp: 2026-08-26T00:00:00Z
---

# Hermes Inference Config (models, providers, fallback chains, cron routing)

How to control which model/provider Hermes uses — the default, the ordered fallback
chain, and how cron jobs ride (or don't ride) that ladder. Also how to read model
failures out of the logs. Companion to the bundled `hermes-agent` skill (which is
off-limits to edit); this is the operational deep-dive for the class.

## When to use

- "Configurar modelo/provider", "muda o default", "cadeia de fallback"
- "O cron não usa a mesma cadeia", "cron usa modelo fixo"
- "Está dando 403 no modelo", "fallback não funcionou", "modelo não aceita imagem"

## Model & provider key reads

Read **one key at a time** — `hermes config get model providers fallback_providers`
fails with `unrecognized arguments`.

```bash
hermes config get model                  # default, provider, aliases
hermes config get providers              # defined provider entries
hermes config get fallback_providers     # ordered fallback chain
```

Set:

```bash
hermes config set model.default <model>
hermes config set model.provider <provider>
hermes config set fallback_providers '[{"base_url":"...","model":"...","provider":"..."}, ...]'
```

`HERMES_HOME=/opt/mercurio-data` — always set it so config edits land on the right
profile, not the default home.

## Defining a provider entry

`providers.<name>` blocks map a friendly name to a backend route + the provider that
owns the credential (the `.env` var key). Example:

```yaml
providers:
  opencode-free:
    api_mode: chat_completions
    base_url: https://opencode.ai/zen/v1
    model: muse-spark-1.2-contributor-free
    provider: opencode-zen      # backend that owns the cred (OPENCODE_ZEN_API_KEY)
```

Set field-by-field: `hermes config set providers.<name>.api_mode chat_completions`,
`.base_url`, `.model`, `.provider`. If no `.env` key covers a provider in the chain,
the **resolve fails** and the chain can't try it.

## Fallback chain mechanics

`fallback_providers` is an ordered list of `{base_url, model, provider}`. On primary
failure the scheduler walks it in order (only for `AuthError`/missing-cred and transient
network/DNS during resolve — not for a mid-stream model drop, which the agent loop
handles separately via the same global chain). Keep `model`+`provider` atomic per entry
— never swap just the provider while keeping a paid primary model.

## CRITICAL — cron jobs follow the chain only when UNPINNED

The trap. A cron job that carries explicit `model`/`provider` fields is **PINNED**: it
uses exactly that model and does **NOT** walk `fallback_providers`. Pin it to a model
that's no longer in the chain and it quietly runs off the ladder — if that model fails,
the job dies instead of falling back.

- **Make a cron inherit the global default + chain:**
  `hermes cron edit <id> --model "" --provider ""` (empty string clears the pin)
- **Force a cron onto a fixed reliable model:** `hermes cron edit <id> --model X --provider Y`

### Drift-guard (why unpin doesn't silently fail-closed)

`hermes config set model.default ...` warns:
`1 enabled unpinned cron job has stored model_snapshot values that differ...`. That's
the **model-drift guard** (#44585 spend-safety). An unpinned job with a creation-time
snapshot that no longer matches the default **fails closed** (skips run, loud alert) to
stop a global switch from silently sending a paid model.

- Unpinning **recalculates** `model_snapshot`/`provider_snapshot` to the new default →
  `snapshot == default`, guard no longer blocks. This is why unpin is safe here.
- A `no_agent` cron (script-only, `no_agent: true`) never touches inference — unaffected.

### Decision table

| Need | Action |
|------|--------|
| Cron rides the same ladder as interactive sessions | unpin: `--model "" --provider ""` |
| Cron must always use a specific reliable model | pin: `--model X --provider Y` |
| Confirm current pin state | read `jobs.json` under `$HERMES_HOME/cron/` (fields `model`, `provider`, `model_snapshot`, `provider_snapshot`) |

## Diagnosing model errors from logs

Logs at `$HERMES_HOME/logs/errors.log` and `agent.log`.

| Log line | Meaning / action |
|----------|------------------|
| `HTTP 403 ... requires explicit opt in` | Data-collection model (e.g. Muse Spark Contributor) needs a **one-time opt-in** at the provider's workspace URL. Provider-side consent, not a Hermes bug. After opt-in, use the model normally. |
| `Fallback to <X> failed: provider not configured` | A named provider in `fallback_providers` has no matching `providers.<name>` entry / no env key. Add it or fix the key. |
| `Model only supports text input; received unsupported content type 'image_url'` | That model has no vision. Images route through the auxiliary model (`auxiliary.vision`), not the main one. |
| `Stream ended with no finish_reason while a tool call's arguments were still incomplete` | Mid-tool-call stream drop by the model. Retry; do not treat as output-length truncation. |
| `Streaming failed before delivery: Connection error` / `Server disconnected` | Transient transport drop. Retry / let the fallback chain catch it. |

## After changing model / provider

Gateway needs a restart for config changes to apply to new sessions:
`/restart` (in gateway session) or `hermes gateway restart`. A model switch made via
OpenCode Go / session override applies to that session immediately; the config `default`
persists across restarts until changed.

## References

- `references/opencode-provider-setup.md` — OpenCode Zen/Go provider routes, `.env`
  keys, and the opt-in flow for Contributor models.
