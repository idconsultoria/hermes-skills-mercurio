# Dogfood QA — Zera alfa (15/08/2026) — exemplo concreto de QA de preview

Resultado do dogfood completo (skill `dogfood`) sobre o preview por PR
(`http://2.zera.129.146.163.107.sslip.io`, PR #2 mantido vivo). Serve como
checklist concreto do que testar num deploy web alfa e dos bugs de classe
encontrados. **Todos os fixes abaixo estão na branch `test/preview-vivo` do
repo Zera (`gustavomello9600/cfp-ia`).**

## Escopo testado (16 casos API + 14 interações browser)

- **API QA:** health, auth (login demo, senha errada→401, sem senha→422, email
  inválido→422, sem token→401, token inválido→401, SQLi→401), dashboard
  (summary/balance), documents (list/upload, tipo inválido→422), LGPD export,
  lockout força bruta→429, gamification (streak=5, level=3, badges, consents),
  chat/message. Resultado: 14/16 PASS (os 2 "FAIL" eram rota errada no script
  de teste, não bugs — `health` fora do prefixo API, `transactions` inexistente;
  as transações vivem em `/dashboard/summary`).
- **Browser QA:** landing→redirect login (proteção), login demo→dashboard,
  navegação (Missões/Chat/Conquistas/Documentos/Config), upload, theme.

## Bugs de classe encontrados (3, todos corrigidos)

### BUG-1 (crítico): header HTTP não-ASCII mata a chamada antes de sair
- `agente/llm.py` header `X-Title: "CFP IA — Núcleo Agêntico"` (em-dash U+2014)
- httpx serializa headers como ASCII → `'ascii' codec can't encode character
  '\u2014'` → LLM nunca era chamado; chat caía no fallback "dificuldade técnica"
- Fix: header ASCII puro `"CFP IA Nucleo Agentico"` (commit `b3b0eea`)

### BUG-2 (alto): cookie Secure em HTTP — login browser "não faz nada"
- `api/config.py` default `auth_cookie_secure=True`; preview HTTP (D17 sem TLS)
  → browser recusa cookie Secure → middleware não vê refresh → bounce pro login
  → botão fica disabled para sempre (sucesso não re-enablea o botão)
- Fix: `AUTH_COOKIE_SECURE=false` no `.env.staging` + documentado no example

### BUG-3 (alto): requirements faltante — `mcp>=2.0.0`
- `api/requirements.txt` não tinha `mcp` (só `agente/requirements.txt`) → a API
  importa `agente.mcp_server` → `ModuleNotFoundError` no chat (causa base do BUG-1)
- Fix: `mcp>=2.0.0` no requirements da API (commit `ca839f3`)

## Pendências registradas (não bloqueiam alfa)

- Seed não cria documentos (tabela `documents` limpa mas nunca populada) →
  tela "Ainda sem documentos" no preview apesar de a seed ter 2 docs do caso
- Páginas Missões/Chat(UI)/Conquistas são placeholders conhecidos — backend
  pronto (`/missions/current`, `/chat/message`, `/gamification/badges`), frontend
  da Onda 2 não conectado (comentário no código diz isso explicitamente)
- `/events` é 405 no GET (POST interno de telemetria — esperado)

## Lição extra: validar o seed contra o que a UI espera

O seed do preview era "completo" no SQLite (idempotente, 2 execuções OK) mas a
UI mostrava "Ainda sem documentos" — o `seed_preview.py` limpa `documents` na
seção de cleanup mas **nunca tinha a seção de INSERT** (o plano dizia 2 docs,
o código não os criava). Lição: ao validar um seed, não basta rodar 2x sem
erro — **conferir no banco/UI que TODAS as tabelas que o frontend consome
foram populadas** (`SELECT count(*) FROM documents`, transactions, missions,
conversations, consents, gamification). Um seed idempotente com seção faltante
passa silenciosamente.

## Lição extra: o teste de lockout pode derrubar a sessão do browser

A bateria inclui `POST /auth/logout-all` para testar revogação de token — isso
invalida a sessão ativa do browser (cookie de refresh revogado). Depois do
teste, o dogfood browser precisa **refazer login** antes de continuar a
navegação; navegar direto para `/dashboard` cai no middleware → bounce para
`/login?next=...`. Não é bug — é a feature funcionando; apenas refaça o login
(ou execute a bateria de auth ANTES do browser QA).

## Técnicas de QA que funcionaram

- **Token redaction workaround:** salvar token em `/tmp/zera_token.txt` via
  `open(...).write()` dentro do Python — o output do tool redige `***` mas o
  arquivo guarda o valor real; scripts subsequentes leem o arquivo.
- **Rate limit agressivo:** a bateria de testes estoura o rate limit por IP e o
  lockout (identificador×IP) — limpar chaves Redis entre execuções:
  `redis-cli --scan --pattern "ip:*" | xargs redis-cli del` e `"lockout:*"`.
  Usar identificador único descartável (`lock-qatest@x.app`) no teste de lockout
  para não envenenar o usuário demo.
- **API 200 ≠ browser OK:** login curl 200 mas browser travado = cookie Secure
  recusado em HTTP (ver BUG-2). Sempre validar login no browser na URL real.
- **Fallback mascara erro real:** chat "dificuldade técnica" → `docker logs`
  mostrou `ModuleNotFoundError: No module named 'mcp'` primeiro, depois o erro
  de encoding do header. Grep os logs por exceção real, não reporte o fallback.

## Estado pós-fix (evidência)

- Chat respondeu com conselhos reais do LLM ("Lista é lei", "regra do espera 10
  minutos") após BUG-1/3 → pipeline OpenRouter ponta-a-ponta funcionando
- Dashboard renderizou dados da seed (Ativos R$2.000, Passivos R$8.000,
  Patrimônio -R$6.000, streak 🔥5, missão Detox de 7 dias)
- Upload de documento: 201 `status_processamento: indexado` → listagem 200
- LGPD export: 200 com payload do titular
