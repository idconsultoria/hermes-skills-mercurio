# Evolve Report — 2026-06-10

**Ciclo:** #1
**Período:** 2026-06-10 09:00–09:40 BRT
**Estado inicial:** 113 skills · 11 memórias (94%)
**Estado final:** 92 skills · 6 memórias (47%)

---

## 1. Deletions (11 skills)

| Skill | Path | Chars | Motivo |
|-------|------|-------|--------|
| godmode | `red-teaming/godmode` | 20,044 | Jailbreak LLMs — zero uso |
| requesting-code-review | `software-development/requesting-code-review` | 8,465 | Redundante: github-code-review cobre |
| segment-anything | `mlops/models/segment-anything` | 13,372 | SAM sem GPU no Oracle ARM |
| audiocraft | `mlops/models/audiocraft` | 16,189 | MusicGen sem GPU |
| obliteratus | `mlops/inference/obliteratus` | 15,464 | Abliteration — nicho extremo |
| gif-search | `media/gif-search` | 2,704 | Utilitário atomizado |
| heartmula | `media/heartmula` | 6,412 | Music gen — nunca usado |
| songsee | `media/songsee` | 2,336 | Espectrogramas — nunca usado |
| openhue | `smart-home/openhue` | 2,713 | Sem Hue conectado |
| kanban-orchestrator | `devops/kanban-orchestrator` | 15,831 | TaskFlow MCP substitui |
| kanban-worker | `devops/kanban-worker` | 10,979 | TaskFlow MCP substitui |

**Total deletado:** ~114,509 chars

## 2. Merges (11 source → 4 target skills)

### Merge A: antigravity-design → agy
**Target:** `software-development/agy` (7,048 → ~5,200 chars após compressão)
**Absorbed:** `creative/antigravity-design` (20,779 chars)
**O que veio:**
- HTML report generation patterns (Mode A/B)
- Hermes Style Guide tokens (#0000FF, Spectral, Space Mono)
- Image generation & retrieval workflows
- Base64/logo JS variable pattern
- DOMContentLoaded fix for interactive slides

### Merge B: Newsletter cluster → iaf-newsletter-pipeline
**Target:** `content-production/iaf-newsletter-pipeline` (13,211 → ~10,500 chars)
**Absorbed:**
- `content-production/daily-ai-digest` (12,656) → seção Daily AI Digest Patterns
- `creative/iaf-newsletter` (12,164) → conteúdo integrado
- `creative/newsletter-curation` (8,229) → seção Editorial Curation
- `productivity/cron-newsletter-pipeline` (7,199) → seção Cron Design Patterns
- `productivity/daily-briefing-pipeline` (12,714) → seção Briefing Pipeline Patterns

### Merge C: TTS cluster → text-to-speech
**Target:** `content-production/text-to-speech` (11,343 → ~8,900 chars)
**Absorbed:**
- `content-production/hermes-tts-voice` (10,224) → seção Hermes TTS Command Provider Chain
- `creative/voice-design` (7,960) → seção Voice Design Process + stripped debugging noise

### Merge D: notion-mcp → notion
**Target:** `productivity/notion` (15,359 chars)
**Absorbed:** `productivity/notion-mcp` (17,529 chars)
Notion skill já tinha seção MCP no final; apenas descrição atualizada.

### Merge E: brand-aesthetic-analysis → brand-studio-forge
**Target:** `creative/brand-studio-forge` (16,032 → ~17,500 chars)
**Absorbed:** `creative/brand-aesthetic-analysis` (7,740 chars)
- Adicionado comando `forge_analyze` à tabela de comandos
- Adicionada seção completa de análise via browser
- Adicionado user preferences (Gustavo Mello: PT-BR, MEDIA delivery)

## 3. AGENTS.md Changes

- Offload step adicionado ao ciclo evolve (passo 8)
- Prefixo `offload` adicionado à tabela de log
- descrição: limpeza de memória pós-evolve

## 4. Memory Offload

**Antes:** 11 entradas, 2,168/2,200 chars (94%)
**Depois:** 6 entradas, 1,055/2,200 chars (47%)

### Removidos (5) — procedural → coberto por skill:
| Entry | Coberto por |
|-------|-------------|
| agy CLI v1.0.5 + OAuth tmux | `agy` skill |
| Pi v0.78.1 providers + wrapper | `pi-agent-coordination` skill |
| IAF pipeline v1.4 CRON schedules | `iaf-newsletter-pipeline` skill |
| Fish Speech q8_0 port + comando | `text-to-speech` + `ai-voice-selfhost` skills |
| Gemini TTS modelo + payload | `text-to-speech` skill |
| Charon persona + tags | `text-to-speech` skill |

### Mantidos (6) — preferências/fatos de ambiente:
- GitHub auth (gh CLI, token path)
- WhatsApp groups (IDs Núcleo + IAF)
- Permission error rule (PARE IMEDIATEMENTE)
- Pi & git conventions (branch naming, commit fase)
- OpenCode Go (base_url, modelos)
- Google Workspace (token path, venv)

## 5. Git History

```
074a938 init: seed skills repository with index.md + AGENTS.md + log.md
  629 files, 168,440 insertions

3968596 evolve: merge+delete cycle #1 — 113→92 skills
  75 files changed, 642 insertions(+), 16,280 deletions(-)
```

## 6. Impact Summary

| Métrica | Antes | Depois | Δ |
|---------|-------|--------|---|
| Skills registradas | 113 | 92 | -21 (18.6%) |
| Memória | 94% (11 entries) | 47% (6 entries) | -47% |
| Commits | 1 | 2 | +1 |
| Reports | — | 1 (`evolve-2026-06-10-0920.md`) | +1 |
| AGENTS.md operações | update, evolve | update, evolve, offload | +1 |
