# Caso: Artemishub — verificação de gestão de usuários (Postgres sandbox)

Contexto da verificação real feita com o sandbox. Stack: React/Vite + FastAPI +
PostgreSQL 17; schema de produção em `public` (dump `db/artemishub.dump`). Deploy:
push em `main` → GitHub Actions (`ci.yml`) faz build nativo no Oracle host e
`docker compose up -d` (produção em `artemis.idconsultoria.ai`).

## Schema de auth (verificado via sandbox)
- `public.usuarios(id uuid default gen_random_uuid(), email text UNIQUE, nome, senha_hash text, papel text, permissoes jsonb, ativo bool, criado_em, ultimo_login)`.
  Check `papel IN ('master','gestor','editor','leitor')`.
- `public.sessoes(token, usuario_id, expira_em)` com FK `ON DELETE CASCADE` →
  apagar usuário limpa sessões automaticamente.
- `perfil_usuarios` NÃO tem FK para `usuarios` (DELETE não quebra).
- Senha: `PBKDF2$600000$<salt_hex>$<hash_hex>`; hash =
  `pbkdf2_hmac('sha256', senha, bytes.fromhex(salt), 600000).hex()`.

## Endpoints de usuário (main.py)
- `POST /api/auth/login` (limiter 10/min) → cria sessão; `.logout` limpa por token;
  `trocar-senha` (self, exige senha_atual, invalida sessões).
- `GET/POST/PATCH /api/usuarios` (só master). `POST` usa `ON CONFLICT (email) DO UPDATE`
  (upsert). `PATCH` aceita nome/senha/papel/permissoes/ativo e protege o último master ativo.
- Adicionado no repo: `DELETE /api/usuarios/{id}` (só master; bloqueia self e o último
  master ativo) e `confirmar_senha` obrigatório em `UsuarioIn` na criação.

## Regras de prova (o que validar no banco, não só no código)
- Criar → linha em `usuarios` + login da senha nova OK + senha errada 401.
- Trocar senha via master → nova loga 200, antiga 401.
- `ativo=false` → login 401 + sessão já existente invalidada (401); `ativo=true` volta.
- `DELETE` → `200`, linha some, sessões em cascata = 0; self → 400; inexistente → 404.

## Nota de escopo LLM (chat por edital)
O motor é DeepSeek (via OpenCode `/api/ia/chat`), apesar do arquivo legado `qwen.ts`.
Risco real de mistura: o system prompt genérico injetava ≤30 editais + "Cenário 2026"
hardcoded. Correção: com `context.edital` presente, usar prompt escopado (edital
completo + portfólio de empresas, regra "não informado no edital" em vez de inventar) e
não injetar outros editais. O backend `/api/ia/chat` é proxy puro (não injeta contexto).