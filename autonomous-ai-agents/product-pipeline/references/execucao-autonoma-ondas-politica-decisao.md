# Execução autônoma por ondas + política de decisão (padrão Zera/CFP IA, ago/2026)

Quando o usuário aprova um plano de execução autônoma (ondas/lotes pré-checklist), o padrão comprovado
em execução real (Zera/ex-CFP IA, 13–14/ago/2026, 5 ondas de 7 executadas):

## Ciclo de code-tasks com modelos especializados (ordem fixa — decisão explícita do usuário)

| Papel | Modelo | Comando | Notas |
|---|---|---|---|
| **Code-tasks** (spec) | Pi **best** (deepseek-v4-pro) | `pi --name "proj-ondaN-code-tasks" -p ...` | Gera/atualiza `code-tasks.md` da onda; SEM thinking alto |
| **Execução** | Pi **cost** (deepseek-v4-flash) | `pi --name "proj-ondaN-loteM" -p ...` | Lotes sequenciais em background (`background=true` + `notify_on_complete=true`) |
| **Revisão** | agy (Turno 1) | `agy -p "$(cat prompts/agy-review-ondaN.md)" --dangerously-skip-permissions --print-timeout 15m` | Escreve `feedbacks.md` seção `## 🗨️ Turno 1 — @Antigravity — Onda N` |
| **Correção** | Pi **best max** (thinking xhigh) | `pi --session <mesmo jsonl> -p ...` | Retoma a MESMA sessão do executor; corrige issues do agy |
| **Re-revisão** | agy (Turno 3) | idem | Até `ACORDO: ONDA N FINALIZADA` |
| **Documentação** | Pi **cost max** (thinking xhigh) | `pi -p ...` | Atualiza SAD/ERD/api-contracts/test-plan + Histórico |

**Ajuste do usuário:** geração de code-tasks é Pi best (NÃO Max); execução é Pi cost (NÃO Max); correção
é Pi best max; documentação é Pi cost max. Análogo ao ciclo da skill /product-pipeline.

## Política de decisão (`product/management/politica-decisao.md`)

Todo prompt de agente (Pi best/cost/best max/cost max) DEVE carregar e respeitar a política:

- **🔴 REVISÃO OBRIGATÓRIA — parar e pedir aval ao usuário** (em lote via `clarify`, 3–5 linhas, opções + recomendação):
  1. Tecnologia crítica não especificada (lib/framework/serviço novo fora da Base Técnica/PRD/ADRs)
  2. Princípios de design do projeto (arquitetura, contrato API público, schema, identidade visual)
  3. Forma de implementação de funcionalidade crítica (auth, motor, LLM, LGPD, notificações)
  4. Custo recorrente (serviço/provedor pago novo)
  5. Deploy para produção (não-staging)
  6. Mudança de escopo do plano (novas tarefas, reordenação, atraso >1 dia)

- **🟢 EXECUÇÃO DIRETA — não parar** (reportar no relatório final):
  1. Implementação dentro de decisão já tomada
  2. Correções mecânicas (lint, formatação, typos, imports)
  3. QA e verificação (tsc, pytest, dogfood, E2E, auditorias OWASP/a11y/perf)
  4. Documentação técnica (via Pi cost max, com Histórico de atualizações)
  5. Infra de staging/CI (docker-compose, GitHub Actions, secrets locais)
  6. Atualização da planilha Roadmap (status das tarefas do escopo)
  7. Commits e push por onda

- **Checkpoints nomeados (D1..Dn)** com estado ✅/🔴 na política; ao resolver uma decisão, atualizar a
  política + criar ADR (ex.: ADR-018 frontend separado, ADR-019 bot canal, ADR-020 multi-etapas,
  ADR-021 múltiplas conversas).
- Vincular no AGENTS.md do repo: "verificar que cada prompt de Pi inclui a política antes de disparar".

## Regra de confirmação entre ondas

Usuário autorizou: **"Não precisa pedir confirmação entre ondas. Siga até a conclusão de tudo parando
apenas quando a política assim o instruir."** → parar SÓ em decisão 🔴; entre ondas, seguir direto.
Ao achar 🔴, apresentar em lote (clarify) com opções + recomendação e aguardar o aval.

## Pitfalls de infra do pipeline (validados em execução real)

- **NUNCA `git reset --hard` no shared volume do host** para "sincronizar" — é o MESMO diretório do
  container (bind mount); o reset destrói trabalho não commitado (ex.: feedbacks.md que o agy acabou de
  escrever). Usuário bloqueia essa ação. O volume compartilhado já reflete o estado após commit/push do
  container — reset é desnecessário E perigoso.
- **agy `chown`a o `.git` para ubuntu (UID 1000)** ao rodar no host → container (UID 10000) perde
  escrita no repo (`index.lock: Permission denied`). Fix: `sudo chown -R 10000:10000 <repo>/.git` pelo
  host antes de commitar no container.
- **agy em print-mode aborta em prompts de permissão** → SEMPRE usar
  `--dangerously-skip-permissions --print-timeout 15m`; sem isso ele para na primeira ação (só imprime
  "I will start by...") e não escreve o review. Também: `echo "n" | agy` não funciona para review longo
  (EOF fecha o stdin).
- **`docker exec` sem `-u` roda como root** → `~` resolve para `/root`; usar caminhos absolutos
  (`/opt/data/home/.pi/...`) em scripts que rodam via `docker exec`.
- **`docker exec -it` no Windows/PowerShell** exige `ssh -t` (força alocação de PTY no túnel); sem `-t`,
  erro "cannot attach stdin to a TTY-enabled container because stdin is not a terminal". Alternativa
  robusta: entrar no host (`ssh`), depois `docker exec -it` — 2 passos.
- **Boolean `server_default=text("0")` quebra PostgreSQL** (`DatatypeMismatchError: column "arquivada"
  is of type boolean but default expression is of type integer`) enquanto SQLite tolera — usar
  `text("false")` em colunas Boolean (no modelo E na migration).
- **Ao adicionar migration, atualizar as DUAS cadeias de teste**: `tests/test_migrations.py` (SQLite)
  E `tests/integration/test_migrations_pg.py` (head + lista de revisões + APP_TABLES) — o Pi cost
  costuma atualizar só uma, e o CI PG falha com `AssertionError` na cadeia.
- **O Pi cost commitou ele mesmo** em alguns lotes (ex.: `3605df0`, `931d591`) e deixou em outros —
  sempre conferir `git log --oneline -3` + `git status -s` antes de assumir que precisa commitar.

## GitHub Actions — verificação de falhas

- Ler runs: `curl -H "Authorization: Bearer $TOKEN" .../actions/runs?per_page=N` (token em
  `/opt/data/home/.config/gh/hosts.yml` → `oauth_token`).
- Job que falha ≠ lint: separar "Lint (ruff)" de "Testes (unit + integração PostgreSQL)" — o email pode
  dizer "check failed" mas a causa real estar nos testes PG.
- Baixar log do job: `.../actions/jobs/<id>/logs`; grep `AssertionError|FAILED|Error`.
- CI de commit antigo não re-roda ao corrigir — o fix precisa de push novo; runs antigos ficam
  `failure` no histórico mas a causa está curada.
