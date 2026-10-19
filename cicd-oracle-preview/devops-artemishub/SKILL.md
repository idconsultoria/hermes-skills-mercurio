---
name: devops-artemishub
type: Orchestrator
timestamp: 2026-08-23T00:00:00Z
description: "Operar/deployar o ArtemisHub no Oracle host."
version: 1.0.0
author: "ID Consultoria (Mercúrio / Hermes), 22/08/2026"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [artemishub, devops, oracle, deploy, postgres, fastapi, pipeline, nginx-proxy-manager, preview-pr, firecrawl, opencode]
    related_skills: [cicd-oracle-preview, motor-nfse-id]
---

# DevOps ArtemisHub — Skill operacional

## When to Use

Carregue quando precisar **operar, deployar, diagnosticar ou manutenir o ArtemisHub**
(sistema de editais da ID no Oracle host): rodar build/deploy, resolver problema de
banco/pipeline/NPM, validar o crawl ou recuperar o ambiente após recriação. É o caso
real da migração de 22/08/2026 (build nativo no host + pipeline 100% interno Python).

Operação, deploy e manutenção do **ArtemisHub** (artemis.idconsultoria.ai): sistema
de monitoramento de editais de fomento (React frontend + FastAPI backend +
PostgreSQL), hospedado no Oracle host da ID.

> 💡 Para o **padrão genérico de CI/CD** de outros projetos use
> `cicd-oracle-preview`. Esta skill é o **caso real Artemis** com todos os detalhes
> operacionais do dia 22/08/2026 (migração para build nativo no host + pipeline
> totalmente interno em Python).

## 1. Visão geral

| Item | Valor |
|---|---|
| Produção | `https://artemis.idconsultoria.ai` |
| Repo | `github.com/nosterviz/artemishub` (privado, branch `main`) |
| Host Oracle | `129.146.163.107` (usuário `ubuntu`) |
| Compose dir (host) | `/home/ubuntu/selfhost/artemishub` |
| Stack | `artemishub-frontend`, `artemishub-backend`, `artemishub-db` |
| DB | PostgreSQL 17 (volume `artemishub_pgdata`) |
| Enriquecimento | Firecrawl self-hosted (`firecrawl_api:3002`) + OpenCode/DeepSeek |
| Repasse | Tácio → Cleverton (próxima fase) |

## 2. Estado histórico (o que mudou em 22/08/2026)

1. **Supabase removido por completo.** Persistência 100% no PostgreSQL próprio.
   Removidos `@supabase/supabase-js`, `supabase-db.ts`, `supabase.ts`, todos os
   branches online do frontend. → código único offline (FastAPI + PG).
2. **Deploy: build nativo no Oracle host** (padrão atual da ID, sem GHCR/QEMU).
   GH Config SO faz qualidade; deploy sincroniza via `scp-action` e roda
   `docker compose build` nativo (ARM64) + `up -d`.
3. **Banco restaurado do dump** (`db/artemishub.dump`, formato **1.16 = PG17**).
   ⚠️ Postgres precisa ser **17** (PG16 não lê 1.16 — `unsupported version`).
4. **Pipeline de crawl 100% interno em Python** — substituiu `npx tsx`/cron/GH Actions.
5. **Firecrawl self-hosted conectado** via rede `ai_mesh`.
6. **NPM**: proxy produção + preview por PR (via API, HTTP-01, sem wildcard).

## 3. Arquitetura de rede (host)

- `artemishub_app-net` — interna do compose (frontend↔backend↔db).
- `proxy_network` — externa, compartilhada com o **Nginx Proxy Manager** (NPM).
- `ai_mesh` — externa, alcança `firecrawl_api:3002` e `searxng-core:8080`.

Containers:
- `artemishub-frontend`: nginx SPA, proxy `/api` → backend (env `BACKEND_HOST`).
- `artemishub-backend`: FastAPI uvicorn :8000.
- `artemishub-db`: postgres:17-alpine.

## 4. Comandos operacionais (no host, `ssh ubuntu@129.146.163.107`)

```bash
cd /home/ubuntu/selfhost/artemishub

docker compose ps                     # status
docker compose logs -f artemishub-backend   # logs do backend + pipeline ([pipeline] ...)
curl -sk https://artemis.idconsultoria.ai/api/health   # saúde externa

# Build + deploy manual
docker compose build && docker compose up -d --remove-orphans

# Backups do banco
docker exec artemishub-db pg_dump -U app -d artemishub -Fc > artemishub_$(date +%Y%m%d).dump
```

**Diagnóstico rápido de deploy:**
- Verificar redes do backend:
  `docker inspect artemishub-backend --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'`
  → deve conter `artemishub_app-net proxy_network ai_mesh`.
- Firecrawl alcançável? `docker exec artemishub-backend sh -c 'echo > /dev/tcp/firecrawl_api/3002'`
- OpenCode ok? `curl -sk https://artemis.idconsultoria.ai/api/health`

## 5. Pipeline interno de crawl (executor Python)

Todo o crawl roda **no backend**, sem executor externo. Pacote:
`backend/pipeline/`:
- `batches.py` — fontes de editais (nacional/internacional) + env.
- `llm.py` — DeepSeek flash via OpenCode (fallback zen→go→zen-go).
- `content.py` — Firecrawl fetch + pré-filtragem + extração rule-based + validação.
- `runner.py` — orquestrador (thread) + upsert direto no PG.
- `scheduler.py` — agendador interno.

Endpoints:
- `POST /api/pipeline/run` — dispara (body opcional `batch_ids`, `force_rule_based`).
- `GET /api/pipeline/status` — progresso.
- `POST /api/pipeline/stop` — para a fila.

Agendamento interno (sem cron): `ARTEMISHUB_PIPELINE_SCHEDULE` no `.env`.
Formatos:
- `03:00` diário; `seg,qua,sex 03:00` com dias (PT ou EN); `06:30,18:30` múltiplos.

**Diagnóstico contido no container:**
```bash
docker exec artemishub-backend sh -c "cd /app/backend && python test_pipeline.py federal-nucleo --rule-based"
```
`test_pipeline.py` está em `backend/` (utilitário de diagnóstico versionado no repo).
Roda um batch e mostra no log os registros de qualidade gravados.

### 5.1 Qualidade da extração e retenção (09/10/2026)

- `backend/pipeline/descartes.py` — sinais de qualidade (título que é só
  `Fonte: domínio`, órgão/url ausente, valor improvável, prazo ilegível/fora da
  janela) e **registro mínimo** em `public.pipeline_descartes` (sem conteúdo
  bruto: motivo, batch, método, título, url, órgão, prazo, valor, `sinais[]`).
  Motivos: `qualidade_entrada`, `reprovado_na_validacao`, `duplicado_no_batch`,
  `retencao_fora_da_janela`.
- **Retenção:** edital com prazo fechado há mais de `ARTEMISHUB_RETENCAO_MESES`
  (padrão 2) sai da base; item com candidatura em andamento é preservado. Roda
  no fim de cada execução do pipeline e sob demanda.
- Endpoints: `GET /api/pipeline/descartes` (resumo por motivo) e
  `POST /api/pipeline/limpar-expirados?meses=2` (só master).
- DDL versionado em `db/migrations/2026-10-09-pipeline-descartes.sql` (o backend
  também garante em runtime via `ensure_schema`) — aplicar é idempotente:
  `docker exec -i artemishub-db psql -U app -d artemishub < db/migrations/<arquivo>.sql`.
- `ARTEMISHUB_VALOR_MAX_PLAUSIVEL` (padrão R$ 5 bi) define o corte de valor
  absurdo.
- **Antes de rodar a retenção, tirar dump** (`pg_dump -Fc` em `/home/ubuntu/backups`).
  Primeira execução (09/10/2026): 55 de 182 editais fora da janela → removidos,
  55 registros gravados; sem preservados (candidaturas = 0).

**Pitfall Firecrawl self-hosted:** a detecção de self-hosted considera a **base custom**
(não só `localhost`/`127.0.0.1`). Se `FIRECRAWL_BASE_URL=http://firecrawl_api:3002/v2`,
o código trata como self-hosted (não exige API key) — corrigido em `content.py`.
⚠️ Não regredir para a checagem restrita a `localhost`.

## 6. Banco (PostgreSQL 17)

- Dump do repo restaurado na 1ª subida (`db/init/01-restore.sh` + `db/artemishub.dump`).
- **Formato do dump = `PGDMP 01 10` = 1.16 = PG17.** Checar antes de trocar a imagem:
  `head -c 9 db/artemishub.dump` → `PGDMP` + versão.
- Postgres deve ser **`postgres:17-alpine`** no compose (PG16 → `unsupported version`).
- Volume `artemishub_pgdata` persiste; não recriar sem necessidade.

**Logins:**
- Produção: usuários do dump (ex.: `taciobrito.idteal@gmail.com` — senha só no dump/hash).
- Preview: **credencial fixa de teste** `preview@artemishub.local` / `PreviewArtemis@123!`
  (papel master) — criada pelo `scripts/seed_preview.sh` em `artemishub_pr_<N>`.

## 7. NPM (proxy + certificados)

- **Produção:** proxy host `artemis.idconsultoria.ai` → `artemishub-frontend:80`,
  cert Let's Encrypt, SSL forçado + HTTP/2.
- **Preview por PR:** cada PR sobe stack autônoma (`artemishub-backend-<N>` etc.) com
  banco de teste `artemishub_pr_<N>`; registro no NPM via API.
- ⚠️ **Registrar no NPM é via API** (`POST /api/tokens` + `POST /api/nginx/certificates`
  + `POST /api/nginx/proxy-hosts`). INSERT direto no SQLite **não persiste** — o NPM
  regen/ignora. Scripts: `scripts/register-preview.sh`, `register-prod-npm.sh`,
  `unregister-preview.sh`. Creds do NPM lidas do `.env` do host (`NPM_EMAIL`/`NPM_PASSWORD`).

**Cert Let's Encrypt no NPM (v2.15) — schema estrito:**
```bash
curl -s -X POST "$NPM_BASE/api/tokens" -H "Content-Type: application/json" \
  -d '{"identity":"<email>","secret":"<senha>"}'   # → token
# payload EXATO do cert (adicionalProperties:false — SEM letsencrypt_agree):
curl -s -X POST "$NPM_BASE/api/nginx/certificates" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider":"letsencrypt","nice_name":"sub.dominio","domain_names":["sub.dominio"],"meta":{"dns_challenge":false}}'
```
- **HTTP-01 não emite wildcard** → cada subdomínio de preview precisa do próprio cert.

## 8. .env do host (secrets locais, NUNCA no repo)

### 8.1 Acesso SSH direto (chave em `references/deploy_key.pem`)

A chave privada ED25519 de deploy do host (`ubuntu@129.146.163.107`) vive **só** em
`references/deploy_key.pem` dentro desta skill. Foi adicionada ao `.gitignore` do repo de
skills (`**/references/*.pem`, `**/references/*_deploy_key*`) — **NUNCA commitar**.

> 🔒 **Escopo de uso (meio de acesso condicional):** esta chave é uma credencial do
> **projeto ArtemisHub**, e seu **uso exclusivo** é executar **trabalho de
> desenvolvimento/devops no projeto Artemishub** (build/deploy/diagnóstico/manutenção do
> sistema em `129.146.163.107`). **Não** usar para acesso genérico ao host, adulteração de
> outros serviços/containers, leitura de dados fora do projeto, ou qualquer operação que
> não esteja a serviço do ArtemisHub. Operação fora desse escopo exige ok explícito do
> principal da ID.

Uso correto (o conteúdo do doc `artemishub_deploy_ed25519_v1.txt` é íntegro; não
re-codificar/re-parsear — testar sempre direto do arquivo):

```bash
K=/data/data/com.termux/files/home/capitolium/skills/cicd-oracle-preview/devops-artemishub/references/deploy_key.pem
chmod 600 "$K"
timeout 25 ssh -i "$K" -o StrictHostKeyChecking=no -o BatchMode=yes \
  -o ConnectTimeout=15 ubuntu@129.146.163.107 'comando...'
```

Validar antes de operar: `ssh-keygen -y -f "$K"` → deve devolver a pub
`ssh-ed25519 AAAAC3…UWCw deploy-artemishub-ci` (exit 0).

> ⚠️ Lição (22/08/2026): ao copiar/gravar a chave, NÃO re-parssear/re-encodar o PEM.
> Um parser-manual mal-escrito rotulou a chave de "corrompida" por engano — o conteúdo
> original sempre abriu em `ssh-keygen`. **Sempre testar o arquivo como veio, antes de
> concluir que está quebrado.**

Vivem só em `/home/ubuntu/selfhost/artemishub/.env` (não são secrets do Actions):
- `POSTGRES_USER`/`POSTGRES_PASSWORD`
- `ARTEMISHUB_API_KEY`, `ARTEMISHUB_CORS_ORIGINS`
- `OPENCODE_API_KEY`, `OPENCODE_BASE`, `DEEPSEEK_MODEL`
- `FIRECRAWL_BASE_URL=http://firecrawl_api:3002/v2`
- `ARTEMISHUB_PIPELINE_SCHEDULE`
- `NPM_EMAIL`/`NPM_PASSWORD` (API do NPM)

Modelo versionado: `.env.example`. Manual entregue em 22/08/2026 (zip) contém backup.

## 9. GitHub secrets / workflows

- **Secrets (repo):** `SSH_PRIVATE_KEY`, `GHCR_TOKEN` (legado), `SECRET_KEY`.
- **Workflows:**
  - `ci.yml` — qualidade + build nativo no host + `up -d`.
  - `preview.yml` — preview por PR (deploy + cleanup) + comentário com credencial de teste.
  - `rollback.yml` — rebuild a partir de SHA (via SCP).
- O fluxo de deploy não usa GHCR_TOKEN (build local no host); GHCR fica só legado.

## 10. Pitfalls (já mordidos)

| Sintoma | Causa | Correção |
|---|---|---|
| `pg_restore: unsupported version (1.16)` | dump é PG17, compose usava PG16 | `postgres:17-alpine` |
| Banco vazio mas container healthy | restore falhou silenciosamente no init | conf. formato do dump + recriar volume vazio |
| `Temporary failure in name resolution` p/ firecrawl | backend fora da `ai_mesh` | adicionar rede `ai_mesh` no compose do backend |
| `FIRECRAWL_API_KEY não configurada` no self-hosted | detecção self-hosted limitada a localhost | base custom ≠ cloud = self-hosted (fix em content.py) |
| `npx: not found` no backend | subprocess externo (legado) | executor interno Python `backend/pipeline/`; não reinstalar node |
| Proxy host NPM some | INSERT direto no SQLite não persiste | usar API do NPM |
| `data must NOT have additional properties` no NPM | payload com campo não-schema | payload exato (sem `letsencrypt_agree`) |
| HTTPS 000 ao testar em localhost | cert cobre só o domínio | testar contra o domínio real resolvido |
| Preview sobe mas `deploy-preview` falha em `03:00: command not found` | `register-preview.sh` faz `source .env` e a linha `ARTEMISHUB_PIPELINE_SCHEDULE=seg,qua,sex 03:00` é lida como comando | não usar `source` no `.env`; extrair só `NPM_EMAIL`/`NPM_PASSWORD` via `grep`/`cut` (mesmo padrão do fallback manual) |
| Backend entra em **crash-loop** no boot: `No "request" or "websocket" argument on function` | endpoint decorado com `@limiter.limit` (slowapi) **sem** o parâmetro `request: Request` | todo endpoint com `@limiter.limit` deve declarar `request: Request` como primeiro parâmetro (ex.: `def create_empresa(request: Request, emp: EmpresaIn)`) |
| `POST /api/empresas` / fluxo público (onboarding) retorna 401 | middleware global `enforce_api_key` exige credencial em tudo, exceto `/api/health` e `/api/auth/login` | liberar rotas públicas método-específicas via `_is_public_onboarding(path, method)` (só criação; GET/edição seguem protegidos) |
| `POST /api/empresas` com `porte=ICT` → `500` + frontend `Unexpected token 'I', "Internal S"... is not valid JSON` | `empresas` aceita `ICT`, `empresas_parque` só aceitava `Média` → `psycopg.errors.CheckViolation: empresas_parque_porte_check` não tratado vira `500 Internal Server Error` texto puro (21B) que `await res.json()` tenta parsear | mapear `ICT → NaoInformado` via `_porte_para_parque()` em `empresa_parque_defaults` + `create_empresa` + migrar `ALTER TABLE empresas_parque DROP/ADD CHECK` incluindo `ICT`; envolver `create_empresa` em `try/except` que devolve `400 {"detail":"Dado inválido: ..."}`; frontend usar `res.text()`+safe `JSON.parse` fallback (ver `references/onboarding-2026-08-31.md`) |
| `PUT /api/empresas/{id}/complemento` → `500 the connection is closed` ou `invalid input syntax for type integer: "Ate 360 mil"` | após envolver `with db()` em `try`, o corpo das etapas 3-10 ficou **fora** do `with` (indentação) → cursor fechado; `conn.commit()` estava dentro de `if c.etapa9:` apenas | `try` deve envolver o `with` inteiro (indentar `with` 4→8 espaços); `conn.commit()` **fora** dos `if`s; `except HTTPException: raise` antes do genérico; `qtd_colaboradores_aprox` é `integer` — não passar por `_FAIXA_MAP` (detalhe em `references/onboarding-2026-08-31.md`) |
| Pipeline roda mas **`DeepSeek extraiu 0`** em todos os batches (resultado sai só do rule-based, com títulos-lixo tipo `Fonte: worldbank.org`) | o OpenCode Go passou a exigir o header **`x-opencode-session`** para rotear a chamada; sem ele a API responde `400 MissingSessionID`, `call_deepseek` devolve `None` e o runner cai no rule-based **em silêncio** (139 batches assim entre ~11/09 e 09/10/2026) | enviar `x-opencode-session: <uuid4>` em TODA chamada ao OpenCode — `backend/pipeline/llm.py` (`call_deepseek`) e `backend/main.py` (`_llm_headers()`, usado pelo proxy `/api/ia/chat`, pelo enriquecimento e por `POST /api/config/testar-llm`); logar a falha total (`[llm] falha total ...`) em vez de devolver `None` mudo; `testar-llm` com `max_tokens=8` sempre falha em modelo de reasoning → usar ≥1024 |
| `POST /api/pipeline/run` → `{"detail":"API key inválida ou ausente"}` usando a chave do `.env` | `ARTEMISHUB_API_KEY` está **vazia** em produção; com `API_KEY=""` nenhum `X-API-Key` casa e o caminho máquina-a-máquina fica morto (só sessão de usuário passa) | disparar a busca sem sessão rodando o runner **dentro do container** (não mexe no estado do processo do servidor): `docker cp` de um script que chama `start_run()` e imprime `RUNNER.state`, depois `docker exec -d artemishub-backend sh -c 'cd /app/backend && python -u /tmp/run_pipeline.py > /tmp/pipeline_run.log 2>&1 < /dev/null'`; a saída vai para o arquivo, **não** para `docker logs` |
| Deploy pelo CI **reverteria produção** | a cópia de produção no host (`/home/ubuntu/selfhost/artemishub`) tem arquivos que **não existem no GitHub main** (trabalho aplicado direto no host, ex. hotfix ICT do onboarding, `src/lib/report/*`, `src/lib/cadastro-hints.ts`, `src/lib/config.ts`, `InfoTooltip`, `ExportEmpresaMatchReportButton`) | **sempre diffar antes de qualquer deploy**: `find src backend -type f ! -path "*/__pycache__/*" -exec md5sum {} +` no host contra o clone do main; se divergir, NÃO deixar o CI deployar (push em branch + deploy manual no host) e levar a reconciliação ao principal |
| **401 intermitente** com sessão válida: login retorna 200 e a tela volta para `/auth?sessao=expirada`; nos logs, 200 e 401 na MESMA rota no MESMO segundo | a stack de **preview** (por PR) sobe na mesma rede `artemishub_app-net` e publica o alias de serviço `backend`; o nginx do frontend de produção resolvia `backend` para vários IPs e **alternava entre produção e preview** — as chamadas que caíam no backend de preview consultavam o banco de TESTE (`artemishub_pr_<N>`), não achavam a sessão e devolviam 401 | apontar sempre para o **nome único do container** (`BACKEND_HOST=artemishub-backend`, nunca `backend`); ao subir preview, derrubar stacks antigas (`docker compose -p artemishub_pr_<N> -f docker-compose.preview.yml down`); diagnosticar com N chamadas seguidas à mesma rota usando a mesma sessão válida — 200/401 alternando = alias compartilhado (`docker inspect <c> --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}={{.Aliases}} {{end}}'` mostra o alias) |

## 10.1 Deploy manual no host quando produção diverge do main (padrão de 09/10/2026)

1. `scp` do arquivo do host para `/tmp/host_*` e aplicar o patch **localmente** (preserva o que só existe no host).
2. `python3 -m py_compile` / conferir o diff; no host `cp arquivo arquivo.bak.$(date +%Y%m%d_%H%M%S)`.
3. `scp` de volta → `docker compose build <serviço> && docker compose up -d <serviço>` (~1 min backend, ~3 min frontend).
4. Verificar pelo lado do servidor (o container do agente pode não resolver o domínio): `curl -sk --resolve artemis.idconsultoria.ai:443:127.0.0.1 https://artemis.idconsultoria.ai/` e comparar o hash do asset servido com o do container (`docker exec artemishub-frontend ls /usr/share/nginx/html/assets/`).
5. Registrar o fix no GitHub em **branch** (nunca em `main` enquanto a divergência existir).

Detalhes de UI/escala e a técnica de QA visual sem login: `references/ui-escala-global-e-qa-visual-2026-10-09.md`.

### 10.2 Diagnóstico rápido de sessão/login (13/10/2026)

Sintomas que parecem "senha errada" e não são: o usuário diz que a senha está certa e a
plataforma volta para o login. Sequência de diagnóstico (do mais barato ao mais caro):

1. `docker logs -t artemishub-backend | grep -E 'auth/login|/api/'` — ver se o POST devolveu
   **200** (senha correta) e se os GETs seguintes ficaram **mistos 200/401** na mesma rota.
2. Misto 200/401 = alias de rede compartilhado com preview (§10). Conferir
   `docker ps | grep artemishub` (deveria existir só a stack de produção) e derrubar previews.
3. Confirmar com N chamadas seguidas numa sessão válida (script no host): 12/12 em 200 = resolvido.
4. Só depois suspeitar de credencial. Conta inativa também devolve 401 no login — checar
   `select email, papel, ativo, left(senha_hash,20) from usuarios;` (formato esperado:
   `PBKDF2$600000$...`, 111 chars).
5. O botão **"Esqueci minha senha" não tem fluxo implementado** (não existe endpoint de reset) —
   se a senha realmente se perdeu, é preciso criar o fluxo antes de prometer recuperação.

Sessão temporária para QA sem senha (o hash é o que fica no banco; token opaco em `sessoes`):

```sql
insert into sessoes (token, usuario_id, expira_em)
select md5(random()::text || clock_timestamp()::text), id, now() + interval '30 minutes'
  from usuarios where email='<email-de-teste>' returning token;
```

Depois basta setar `artemishub_token` + `artemishub_usuario` no localStorage e abrir o app.
**Apagar a sessão ao terminar** e registrar o uso.

Defesas que ficaram no código depois deste incidente (não regredir):

- `src/lib/offline-api.ts` — o handler de 401 guarda o **token que a chamada enviou** e só
  expulsa quando (a) a chamada levou token e (b) esse token ainda é o atual. Chamada
  pré-login (sem token) e token trocado no meio do caminho **não** expulsam.
- `src/lib/app-data-context.tsx` — não busca dados em `/auth` nem em rota pública.
- `backend/main.py` — `_auth_context` devolve **503** em falha de banco (não 401) e o
  middleware não rebaixa 5xx para 401: qualquer 401 vira logout no cliente, então 401 só
  com sessão realmente inválida.

## 11. Pendências atuais
- Conta OpenCode: modelo DeepSeek no `zen/go/v1` requer **opt-in região China**
  (Link no erro da API). A chave atual autentica.
- Fontes bloqueadas (SEBRAE, Embrapa, FAPERN, FAPEPI, EC Europa...) devolvem
  `SCRAPE_ALL_ENGINES_FAILED` — o pipeline trata como fallback; não é falha.

## 12. Verificação pós-deploy (+ caso 31/08/2026)
> Detalhe completo do incidente de onboarding em `references/onboarding-2026-08-31.md` (porte ICT, 500 texto puro, indentação do `with`).

1. `curl -sk https://artemis.idconsultoria.ai/api/health` → `{"status":"ok"}`
2. Backend nas 3 redes (`app-net`, `proxy_network`, `ai_mesh`).
3. `Firecrawl` alcançável de dentro do backend.
4. Pipeline manual via botão do Dashboard / `POST /api/pipeline/run` salva editais no PG.
5. Scheduler log: `[scheduler] dias BRT: [0,2,4] | janelas: [(3,0)]`.
6. Log `(nome=main)` sem `npx`/`FileNotFoundError`; só `[pipeline]` sãos.