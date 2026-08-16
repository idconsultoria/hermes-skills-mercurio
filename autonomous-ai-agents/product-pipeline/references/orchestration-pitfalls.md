# Pitfalls de orquestração multi-agente (product-pipeline)

> Aprendidos em 14/08/2026 durante a execução das 7 ondas do Zera (CFP-IA), via contrato
> product-pipeline (Pi best gera → Pi cost executa → agy revisa → Hermes orquestra).
> São correções de workflow que o usuário sinalizou OU erros reais que custaram CI/horas.

## Shared volume (container ↔ host Oracle) — REGRAS DO USUÁRIO

- **NUNCA `git reset --hard` no host** para "sincronizar" o shared volume
  (`/opt/data/code/...` no container = `/home/ubuntu/selfhost/shared/code/...` no host).
  O volume É o mesmo diretório — commit/push do container já é visível no host. Reset é
  desnecessário E destrutivo (pode comer trabalho não commitado do agy, ex.: `feedbacks.md`).
  **O usuário bloqueou esta ação DUAS VEZES em 14/08.** Não repetir, nunca.
- **Owner quebra após agy rodar no host:** o agy (e alguns Pi) fazem `chown` para uid 1000
  (ubuntu) em arquivos/`.git`; o container roda como uid 10000 e perde escrita → `git add`/
  `write_file` falham com "Permission denied". Fix pelo host (não é `reset`, é chown):
  ```bash
  ssh oracle-host 'sudo chown -R 10000:10000 <repo>/.git <repo>/prompts <repo>/product 2>/dev/null'
  ```
  Vira passo rotineiro após cada revisão do agy (o agy também cria arquivos fora do escopo —
  revisar `git status` antes de commitar e commitar só o esperado, ex.: `feedbacks.md`).

## Pi cost travado em loop — quando tomar o controle

- **Sintoma:** JSONL para de crescer e o Pi repete a MESMA tool call (ex.: `timeout 100` no mesmo
  teste) por ~15+ min. O subprocess travou num deadlock; o Pi NÃO vai resolver sozinho.
- **Ação:** matar o job (`process kill`), diagnosticar a causa raiz (ler o script/processo),
  corrigir, validar localmente e re-disparar. Depois devolver o controle ao usuário com o resumo.
- **Exemplo real (Q08 load test):** `proc.stdout.read()` num subprocess vivo = deadlock (pipe
  nunca fecha). Fix: `readline()` best-effort + `terminate()` + `wait(timeout=5)`/`kill()`,
  nunca `read()`. Também: config morta (`args.base_url_explicito` definido e nunca usado) →
  `--auto-up --port 8123` healthcheckava a porta errada.
- **Pi que trava por permissão de arquivo:** o Pi cost PÁRA e reporta em vez de contornar —
  correto. O orquestrador corrige o chown e aplica o pacote staging que ele deixou pronto
  (ex.: `prompts/onda5-lote1-staging/`).

## Instância efêmera SQLite (e2e_boot) — limitação de concorrência

- Setup concorrente (register/login/consents/onboarding, ~9 escritas por VU) serializa no lock
  single-writer do SQLite → >1 VU = lock-storm e timeout do httpx (30s). **Só 1 VU funciona em
  SQLite.** Carga 50/100 VUs exige PostgreSQL ou staging real. Documente como limitação do driver
  de teste, não como bug do produto.
- Porta 3000 local = WhatsApp bridge (infra do usuário — NUNCA matar); porta 8000 no host =
  taskflow-backend. E2E usa `PORT`/`E2E_BASE_URL` custom (3100) — `playwright.config.ts` já
  antecipa. `ZERA_API_PORT` configura a porta do e2e_boot.

## Postgres é estrito onde SQLite tolera (CI)

- `server_default=text("0")` numa coluna **Boolean** passa no SQLite e quebra no PG com
  `DatatypeMismatchError: column ... is of type boolean but default expression is of type integer`.
  Use `text("false")` para Boolean. O `0` só é válido para Integer.
- **Ao adicionar migration, atualize TAMBÉM `tests/integration/test_migrations_pg.py`** (cadeia de
  revisões + head). O Pi cost atualiza o teste SQLite (`test_migrations.py`) e esquece o de PG →
  2 falhas de CI nesta sessão (fix `6a4edc9`).

## Revisão do agy que trava

- Se o agy insiste em rodar E2E/build no host e o ambiente não sobe (porta ocupada, browser
  faltando), ele entra em loop de "timeout waiting for response". Re-disparar com **modo estático**:
  instruir explicitamente "NÃO rode testes/E2E/build — suíte já verde no CI; revise os arquivos".
- `--print-timeout 15m` não basta para revisões grandes; revisões estáticas terminam rápido.

## Drive mirroring fora do fim de quinzena

- Regra do AGENTS.md: espelhar docs de produto no Drive SÓ após sinalização explícita de fim de
  quinzena. Usuário pode pedir espelhamento extra (ex.: "espelhe tudo que não for código").
- Script reutilizável: `/opt/data/igor-docs-md/espelho_extra.py` — varre `product/` e cria no Drive
  (md-to-gdoc.py) os docs .md NÃO mapeados pelos scripts existentes (espelhar_gestao/engenharia/
  design_v2), com filtro de exclusão para ruído interno (feedbacks.md, `-demo`,
  auditoria-rastreabilidade, review-report). Rodar os scripts existentes primeiro (preservam IDs),
  depois o extra (cria com `--parent`); anti-429 com `sleep 3`.
- ID da pasta Produto pai: `1sl-uFwjOnGQAsk-LYl3tcbFK87nOrpuQ` (subpastas Gestão/Engenharia/
  Design/Pesquisa/Ideação).
