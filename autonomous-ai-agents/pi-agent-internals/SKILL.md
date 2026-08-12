---
name: pi-agent-internals
description: "How Pi Agent works internally — settings, sessions, compaction, costs.

Load this skill when asked how the Pi Agent works internally — its settings.json hierarchy, session JSONL layout (--session append semantics), compaction, provider/model selection and the pi-cost wrapper. Reference for debugging Pi behavior and auditing sessions."
version: 1.0.0
author: Hermes
license: MIT
category: autonomous-ai-agents
type: Reference
timestamp: 2026-08-12T03:15:00Z
metadata:
  hermes:
    tags: [pi, agent, internals, harness, tools, system-prompt, skills, extensions]
    related_skills: [autonomous-ai-agents/pi-agent-coordination, autonomous-ai-agents/pi-session-audit, autonomous-ai-agents/product-pipeline]
---

# Pi Agent — Funcionamento Interno

> **Complementa** `pi-agent-coordination` (que cobre providers/modelos/invocação/sessões do ponto de vista operacional).
> Esta skill cobre o **interior do harness**: o que o modelo vê (tools, system prompt), como skills/extensões/settings funcionam no runtime, e onde fica cada mecanismo no código-fonte.

## When to Use

- Usuário pergunta "como o Pi funciona por dentro", "quais tools/plugins/prompts base o Pi tem", "como está configurado o agente".
- Precisar estender o Pi (extensão TS, SYSTEM.md, APPEND_SYSTEM.md, settings) ou depurar comportamento estranho pós-upgrade.
- **Preferência do usuário (Gustavo, 12/08/2026):** quando ele pede "análise profunda de como está setada a harness/agente", ele quer o **funcionamento interno** (tools, plugins, prompts base) — não só providers, custos e sessões. Na primeira entrega foquei na camada externa e ele redirecionou: *"Quero um relatório mais focado no funcionamento interno do agente. Quais tools tem, quais plugins, como estão seus prompts base."* Em análises futuras do Pi, cubra a anatomia interna primeiro.

## Fatos-chave (v0.78.1, instalado local)

- Pacote: `@earendil-works/pi-coding-agent` (pi.dev). Código: `/opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent/dist/`
- **Filosofia:** "minimal terminal coding harness" — **sem subagents e sem plan mode** por design (orquestração é externa, Hermes).
- **Tools built-in (default 4):** `read` (texto+imagem, truncate 2000 linhas/100KB, offset/limit), `bash` (sem timeout default), `edit` (multi-point exact match), `write`. Existem também `grep`, `find`, `ls` (fora do default) e `edit-diff` (auxiliar).
- **System prompt:** identidade + "Available tools" (snippets de 1 linha) + Guidelines (dedup, sempre "Be concise" + "Show file paths clearly") + refs à doc do pi + [append] + [project_context] + [available_skills] + date/cwd.
- **Precedência de extensão do prompt:** `--system-prompt`/`SYSTEM.md` **substitui** tudo → `--append-system-prompt`/`APPEND_SYSTEM.md` **adiciona** → context files (AGENTS.md/CLAUDE.md, do agentDir + subindo do cwd) → skills → prompt templates → themes (só TUI).
- **Skills:** injetadas como catálogo `<available_skills>` (name/description/location); o modelo carrega SKILL.md via `read` sob demanda. Frontmatter rico (intent/best_for/scenarios) melhora a seleção.
- **Extensões:** podem registrar tools custom, slash commands, flags, interceptar `user_bash`. Instalação atual tem **0 extensões** (100% stock).
- **Settings:** global `~/.pi/agent/settings.json` + projeto `.pi/settings.json`, deep merge (projeto vence). Campos: `defaultModel`, `theme`, `quietStartup`, `skills`, `themes`, `thinkingBudgets`, `httpIdleTimeoutMs`.
- **Auth:** 4 providers (openrouter, deepseek, opencode, opencode-go), todos `type: api_key`. **opencode e opencode-go usam a MESMA chave** — dois endpoints da mesma conta (Zen free vs Go cota 5h/mês).
- **Estado real da instalação (12/08/2026):** settings.json = 39 bytes (só lastChangelogVersion → tudo default); **defaultModel NÃO setado** → invocação sem flags cai no tier mais caro (deepseek v4-pro direto); sem SYSTEM.md/APPEND_SYSTEM.md/AGENTS.md global/prompt templates/themes.

## Recomendações que saíram da análise (12/08/2026)

1. Setar `defaultModel: "deepseek/deepseek-v4-flash"` no settings.json global — elimina o risco do tier caro em invocações fora do padrão.
2. Criar `~/.pi/agent/APPEND_SYSTEM.md` com convenções da ID (zero emojis na UI, sempre `--name`, formato de saída) — blinda contra upgrades do prompt default.
3. Enriquecer frontmatter das 21 skills da raiz (intent/best_for/scenarios) — melhora a seleção do modelo.
4. Versionar settings.json e APPEND_SYSTEM.md nos pi-dotfiles.

## Detalhe completo

- `references/pi-internals-anatomy.md` — anatomia completa: tabela de tools com snippets, template do system prompt, mecanismo de skills/extensões/settings/sessões, comandos de inspeção rápida.

## Relatório entregue ao usuário

A análise completa foi entregue como PDF em `/opt/data/reports/pi-harness-report/pi-harness-interno-v1.pdf` (HTML Hermes Official → Chromium do host, fluxo IAF).
