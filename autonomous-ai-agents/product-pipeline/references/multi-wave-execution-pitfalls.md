# Pitfalls de operação multi-onda (Zera 2026-08) — o que quebrou e como resolveu

## Shared volume: NUNCA `git reset --hard` no host (correção explícita do usuário)

- `/home/ubuntu/selfhost/shared/code/...` (host Oracle) e `/opt/data/code/...` (container) são o
  **MESMO diretório** — commit/push no container já aparece no host. `git reset --hard origin/main`
  no host é desnecessário e **destrutivo** (apaga trabalho não-commitado, ex.: o review que o agy
  acabou de escrever). O usuário bloqueou essa ação explicitamente — não repetir.
- O agy (roda como `ubuntu` no host) faz `chown` no `.git` (e às vezes em pastas de aplicação) para
  uid 1001/1000, quebrando a escrita do container (uid 10000). Fix (do host):
  `sudo chown -R 10000:10000 .../.git` (e `frontend scripts .github api tests product prompts`
  quando EACCES). Verificar com `git status`/`touch` antes de commitar.
- Depois do agy, o `feedbacks.md` é o único arquivo que ele toca (além de chowns). Commitar só o
  feedbacks; NÃO commitar arquivos untracked de outra linha de trabalho (ex.: posts de marca de um
  designer paralelo) sem instrução.

## Onda inteira de execução: orquestrar como fila

- Padrão que funcionou 7 ondas seguidas: **Pi best gera code-tasks (seção nova) → commit → Pi cost
  executa em lotes (1-3 por onda) → commit por lote → agy revisa (via SSH no host, com
  `--dangerously-skip-permissions`) → commit feedbacks → atualizar planilha Google Sheets →
  próxima onda**. Pi cost NÃO deve commitar (deixa para o orquestrador); quando ele commita sozinho,
  só confirmar o push.
- Rodar Pi cost com `--name` por lote (ex.: `zera-onda4-lote2`) e monitorar com o pi_follow.

## Pi cost travado em loop — detectar e assumir o controle

- Sintoma: mesmo comando bash com `timeout N` repetido por >30 min, JSONL não progride, últimas falas
  idênticas. Exemplo real: load test com `proc.stdout.read()` bloqueando para sempre.
- Ação: matar o processo Pi, **diagnosticar o bug lendo o script**, corrigir, validar, re-disparar.
- **Pitfall de subprocess:** `subprocess.Popen(stdout=PIPE)` + `proc.stdout.read()` **bloqueia para
  sempre** se o filho continua vivo (o pipe nunca fecha). Nunca `read()` completo; usar
  `readline()` best-effort + `terminate()` + `wait(timeout=5)`/`kill()`.
- **Pitfall de arg morto:** flags lidas mas nunca usadas (ex.: `base_url_explicito`) causam
  comportamento errado silencioso (healthcheck na porta errada). Ao debugar, `grep` o uso real da flag.

## SQLite single-writer limita load tests

- Instância efêmera SQLite só suporta **1 VU** no funil completo (register→login→consents→onboarding
  ≈ 9 escritas por VU serializam no lock single-writer → httpx timeout 30s estoura). Carga >1 VU
  exige PostgreSQL (`ZERA_TEST_PG_DSN` ou staging real). Documentar como limitação, não como bug.

## Postgres: `server_default=text("0")` em Boolean FALHA (SQLite passa)

- Migration/modelo com `server_default=text("0")` em coluna Boolean: SQLite tolera, Postgres rejeita
  (`DatatypeMismatchError: column is of type boolean but default expression is of type integer`).
  Fix: `server_default=text("false")`. O CI com PG pega o que o dev local (SQLite) não vê.
- Ao adicionar migrations, atualizar TAMBÉM os testes de integração PG (`test_migrations_pg.py`
  espera a cadeia completa — ficou em 0005 quando o head real era 0007).

## Decisões 🔴 no meio da onda: parar, reportar, registrar na política

- Pi best para e reporta 🔴 (tecnologia crítica, custo recorrente, deploy produção, escopo) sem
  implementar. Hermes apresenta via clarify com tabela de opções + recomendação.
- **clarify sem resposta em 10 min:** aplicar o default documentado como "aguardando confirmação"
  (ex.: D11 consentimento + retenção até exclusão + DPO provisório), registrar na política, e seguir
  com o que é 🟢 — nunca decidir matéria crítica em silêncio, nunca travar o resto da fila.
- Registrar cada decisão na `politica-decisao.md` (tabela D1–D18) + ADR quando estrutural.
- Terminologia de produto fixada pelo usuário: **"conversa" nunca "sessão"** na UI/copy (ADR-021).

## Revisão agy via SSH

- Comando que funciona (sem reset, sem tmux):
  `ssh oracle-host 'cd <repo> && /home/ubuntu/.local/bin/agy -p "$(cat prompts/agy-review-ondaN.md)" --dangerously-skip-permissions --print-timeout 15m > /tmp/agy-ondaN.log 2>&1'`
- O agy pode demorar e fazer chown; após rodar, conferir `git status` e consertar owner do `.git`.
- O prompt do agy deve listar commits por lote + o que revisar + critérios + formato da resposta
  (escrever em `product/engineering/feedbacks.md`, seção `## 🗨️ Turno 1 — @Antigravity — Onda N`).

## CI vermelho pós-lote: ler o log do job, não adivinhar

- `gh` não instalado no container → usar API do GitHub com token de `~/.config/gh/hosts.yml`
  (`grep oauth_token`), listar runs (`/actions/runs?per_page=N`), achar o job failure
  (`/runs/{id}/jobs`), baixar o log (`/jobs/{job_id}/logs`). Lint vs testes são jobs separados —
  "lint falhou" no email pode ser na verdade o teste de integração PG.

## Espelhamento Drive fora do fim de quinzena (padrão extra)

- AGENTS.md do repo manda espelhar `product/` no Drive **só com sinalização explícita de fim de
  quinzena** — mas o usuário pode pedir espelhamento extra a qualquer momento (ex.: após uma sessão
  longa de ondas). Procedimento: (1) rodar os 3 scripts oficiais (`espelhar_gestao.sh`,
  `espelhar_engenharia.sh`, `espelhar_design_v2.sh` — atualizam docs com `--doc-id`, preservam IDs);
  (2) criar os docs NOVOS não mapeados com `espelho_extra.py` (varre `product/`, usa `--parent` da
  pasta certa por subpasta — Gestão/Engenharia/Design/Pesquisa, extrai o ID criado do output e gera
  `espelhar_extra.sh` com `--doc-id` para o próximo run ser 1 comando). Excluir ruído interno:
  `-demo`, `feedbacks`, `auditoria-rastreabilidade`, `review-report`, `revisao-copys` — não são docs
  de produto.
- Docs legais (RIPD/termos/política) sobem como **rascunho**; quando o jurídico revisar, atualizar o
  MESMO doc via `--doc-id` (ID preservado). Verificar com Docs API
  (`GET /documents/{id}?fields=inlineObjects`) que imagens mermaid subiram.

## Mermaid com múltiplos nodes por linha falha SILENCIOSO no espelhamento

- `md-to-gdoc.py` (script do google-workspace) tem `_fix_mermaid()` que assumia UM par de colchetes
  por linha. Diagramas com `A[...] -->|...| B[...]` na mesma linha eram mutilados (perdia `]` do 1º e
  `[` do 2º node) → mmdc falha → **a imagem não entra no Google Doc, sem erro fatal**. Fix já aplicado
  no script (scanner de profundidade preservando nível 0). Sintoma pós-espelhamento: doc sem o
  diagrama; conferir `inlineObjects` do doc antes de confirmar.
