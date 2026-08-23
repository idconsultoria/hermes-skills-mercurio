---
name: internal-python-job-executor
type: ToolIntegration
timestamp: 2026-08-23T00:00:00Z
description: "Executor interno Python p/ pipeline no backend FastAPI."
version: 1.0.0
author: "ID Consultoria (Hermes Agent)"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [fastapi, background-thread, scheduler, pipeline, oracle-host, python, cron-migration]
    related_skills: [cicd-oracle-preview]
---

# Executor interno de jobs em Python no backend FastAPI

Padrão da ID (validado no ArtemisHub, 22/08/2026) para **remover executores
externos** de um pipeline de dados/automação (cron jobs, GitHub Actions, `npx
tsx`, scripts Node) e rodar **tudo dentro do backend FastAPI**, em Python, como
uma **thread em background** + **agendador interno** (daemon thread).

**Por que:** elimina serviço/manutenção externa, porta o pipeline para a mesma
runtime do backend e tira dependência de Node/npx/binários que não existem no
container Python.

## 1. Quando usar

- O pipeline/automação hoje roda via `npx tsx ...`, `node script.mjs`, cron do
  host, ou GitHub Actions, e o mantenedor quer **tudo interno e em Python**.
- O container do backend é Python puro e o executor externo falha com
  `FileNotFoundError: ... 'npx'` (Node não instalado na imagem).
- O backend já tem a stack de dados (Postgres, provider LLM, fetch HTTP) e só
  precisa executar o mesmo fluxo em background.

**Não usar para:** automação que precisa de bins não-portáveis pra Python, ou
quando a arquitetura pede isolamento do pipeline num serviço separado (aí use
container dedicado, não thread no backend).

## 2. Arquitetura

```
FastAPI backend (Python)
├── /api/pipeline/run    → start_run() → threading.Thread(Runner.run)
├── /api/pipeline/status → Runner.snapshot() (estado thread-safe)
├── /api/pipeline/stop   → Runner.request_stop() (Event)
└── backend/pipeline/
    ├── batches.py   → fontes/config (porta do config TS)
    ├── llm.py       → chamada LLM (OpenAI-compat) c/ fallback de providers
    ├── content.py   → fetch (Firecrawl/crawler) + pré-filtragem + rule-based fallback
    ├── runner.py    → orquestrador (thread, estado c/ lock, stop Event, upsert direto no DB)
    └── scheduler.py → daemon thread de agenda (substitui cron)
```

Princípios:
1. **Estado do job vive num singleton no processo** (`RUNNER`), NÃO reaproveitável
   entre `docker exec python -c` (cada exec é processo novo → runner "vazio").
   Para ler estado real, use o endpoint HTTP com auth, não um processo separado.
2. **Thread daemon** — não trava shutdown do app.
3. **Upsert direto no DB** (psycopg) em vez de HTTP próprio — evita loop/recursão
   e é mais barato. Reaproveite a MESMA lógica SQL do endpoint existente.
4. **Agendador interno substitui cron** independente: aceita dia-da-semana +
   horário (ex.: `seg,qua,sex 03:00` em BRT).

## 3. Passos (migração de `npx tsx` → executor Python)

1. **Mapear o pipeline TS** (batch defs, fetch, LLM, rule-based, validação,
   upsert) e portar 1:1 para módulos `backend/pipeline/` (pacote no MESMO dir do
   `main.py`, para `import pipeline.runner` resolver no WORKDIR `/app/backend`).
2. **Reescrever os endpoints** `/run|status|stop` para `RUNNER`/`start_run`
   (sem `subprocess.Popen(["npx",...])`).
3. **Scheduler**: ler env `ARTEMISHUB_PIPELINE_SCHEDULE` no startup
   (`@app.on_event("startup")`); vazio = desligado (só manual); parse de
   `DIA,DIA HH:MM` ou `HH:MM` (BRT).
4. **Remover executores externos** do repo: workflow GH de cron, `render.yaml`,
   `scripts/*-cron.sh`, `*.mjs` de crawl, e TS/API mortos (`run-pipeline.ts`,
   `pipeline.ts`, `llm.ts`, `config.ts`, `api/*.ts`). Checar com grep que a SPA
   não importa os arquivos removidos antes de apagar (o frontend Vite só
   typecheck `src/`, `api/` fica de fora do tsconfig).
5. **Validação:** rodar o módulo direto no container (`docker exec ... python
   test.py <batch>`) para provar o fluxo sem HTTP; depois disparar via UI e
   conferir os logs `[pipeline]`.

## 4. Pitfalls (todos mordidos — soluções testadas)

| Sintoma | Causa | Correção |
|---|---|---|
| `npx: not found` no container | Endpoint herdou `subprocess` Node, imagem é Python pura | Portar p/ Python; nunca `subprocess` de bin que não está na imagem |
| Seed SQL não aplica (banco/usuário teste vazio) | `docker exec` SEM `-i` descarta o heredoc do stdin → SQL some em silêncio (`>/dev/null 2>&1`) | Sempre `docker exec -i container psql ... <<SQL` |
| Job interno não alcança serviço auxiliar (Firecrawl) no mesmo host | Serviço auxiliar em rede Docker diferente (ex.: `ai_mesh`); porta não publicada | Anexar a rede externa ao compose do backend (`networks: ai_mesh: external: true`) |
| Detecção de "self-hosted" Firecrawl falha por hostname Docker | Checar só `localhost`/`127.0.0.1`, mas serviço é `firecrawl_api` (nome de container na rede) | `self_hosted = "api.firecrawl.dev" not in base and bool(BASE_URL)` |
| `docker exec python -c` mostra status job "vazio" | Estado real vive no processo uvicorn; exec separado cria runner novo | Ler estado via endpoint autenticado, não processo isolado |
| Scheduler não liga | Só inicia via `__main__`, mas produção roda `uvicorn main:app` | Disparar no `@app.on_event("startup")` (evento real) |

## 5. Validação (provar que migrou)

1. `docker exec <backend> python -c "import pipeline.runner"` OK (pacote presente).
2. Rodar 1 batch real: `docker exec <backend> python test.py <batch>` imprime
   `RESULT: {"status":"ok","editais":N,"method":"deepseek"|"rule-based",...}` e o
   banco ganha N editais.
3. Disparar via UI → `POST /api/pipeline/run` 200, logs `[pipeline] [batch] ... salvos no PG`.
4. Confirmar scheduler: log `[scheduler] dias BRT: [0,2,4] | janelas: [(3,0)]` e
   `próximo run: <data> <fuso> BRT`.
5. Confirmar que endpoints `/stop` e idempotência `409` (já rodando) funcionam.

## 6. Referência

- `references/artemishub-2026-08-22.md` — estado do ArtemisHub: host paths, redes,
  `.env` keys, NPM-orientado (HTTP-01 sem wildcard), credencial de preview fixa,
  pendência do opt-in de região do OpenCode. Detalhe específico de sessão.