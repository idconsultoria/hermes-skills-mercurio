# ArtemisHub — estado de sessão (22/08/2026)

Detalhe específico de sessão por trás do padrão do executor interno (ver SKILL.md).
Útil quando retomar manutenção do ArtemisHub; menos relevante para novos projetos.

## Infra (host Oracle 129.146.163.107)
- Repo: `github.com/nosterviz/artemishub` (privado, branch `main`).
- Compose dir no host: `/home/ubuntu/selfhost/artemishub`.
- Contêineres: `artemishub-frontend` (nginx :80), `artemishub-backend`
  (FastAPI :8000), `artemishub-db` (postgres:17).
- Redes: `artemishub_app-net` (interna), `proxy_network` (NPM, externa),
  `ai_mesh` (agentes/Firecrawl, externa). O backend entra em `ai_mesh` para
  alcançar `firecrawl_api:3002`.

## .env (só no host; nunca no repo)
Chaves gerenciadas localmente (modelo `.env.example` versionado):
- `POSTGRES_USER=app`, `POSTGRES_PASSWORD`, `POSTGRES_DB=artemishub`
- `ARTEMISHUB_API_KEY`, `ARTEMISHUB_CORS_ORIGINS=https://artemis.idconsultoria.ai`
- `OPENCODE_API_KEY` (DeepSeek via OpenCode), `OPENCODE_BASE`,
  `DEEPSEEK_MODEL`
- `FIRECRAWL_BASE_URL=http://firecrawl_api:3002/v2` (self-hosted na ai_mesh)
- `ARTEMISHUB_PIPELINE_SCHEDULE=seg,qua,sex 03:00` (agendador interno, BRT)
- `NPM_EMAIL`/`NPM_PASSWORD` (API do NPM p/ registro de proxy/cert)

Backup completo do `.env` com secrets reais vive no zip de entrega
`artemishub-manual-entrega-2026-08-22-v1.zip` (gerado por Mercúrio p/ Tácio).

## NPM (padrão ID atual)
- Registro de proxy host/cert é por **API** (`POST /api/tokens`, depois
  `POST /api/nginx/certificates` + `POST /api/nginx/proxy-hosts`), não INSERT
  direto no SQLite `.sqlite` (este não persiste / sobrescreve).
- Let's Encrypt no NPM é só **HTTP-01** → sem wildcard: cada preview
  `<N>.artemis.idconsultoria.ai` precisa do próprio cert.
- Schema NPM v2.15: payload de cert exato
  `{"provider":"letsencrypt","nice_name":..,"domain_names":[..],"meta":{"dns_challenge":false}}`
  — sem campos extras (`additionalProperties:false`).

## Preview por PR
- Stack autônoma por PR (não overlay), banco de teste dedicado
  `artemishub_pr_<N>` no Postgres de produção, containers sufixados `-<N>`.
- Credencial de teste FIXA (usuário dedicado, hash PBKDF2 fixo no seed):
  email `preview@artemishub.local` / senha `PreviewArtemis@123!` (papel master).
- SQL de seed roda com `docker exec -i` (senão o heredoc é descartado).

## Banco
- Dump do repo `db/artemishub.dump` é formato **1.16 = Postgres 17**. O compose
  precisa ser `postgres:17-alpine` (16 dá `unsupported version (1.16)`).
- Restaurado na 1ª subida via `/docker-entrypoint-initdb.d/01-restore.sh`;
  volume `artemishub_pgdata` garante persistência.

## Pendências abertas
- Modelo DeepSeek no `zen/go/v1` requere **opt-in de região China** na conta
  OpenCode (a chave autentica; erro `RegionError` com link de opt-in). A rota
  `zen/v1` retorna `CreditsError` (sem saldo). O backend tenta as 3 rotas em
  fallback.
- Firecrawl self-hosted devolve `SCRAPE_ALL_ENGINES_FAILED` em sites que
  bloqueiam (SEBRAE, Embrapa, FAPERN, FAPEPI, EC Europa...) — tratado como
  fallback, não é falha do executor.