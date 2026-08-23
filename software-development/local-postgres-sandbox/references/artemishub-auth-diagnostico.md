# Diagnóstico rápido de login do ArtemisHub (auth/multi-usuário)

Confirmado em 22/08/2026 ao diagnosticar "não consigo logar com a conta master".

## O sistema NÃO bloqueia múltiplos logins

- Cada login insere uma NOVA linha em `public.sessoes` (token opaco 12h,
  `SESSION_TTL_S=12*3600`). Sessões anteriores do mesmo usuário NÃO são invalidadas
  no login — só há housekeeping das expiradas (`DELETE ... WHERE expira_em < now()`).
- → login simultâneo em vários dispositivos funciona por design. Suspeita de
  "só permite um usuário por vez" está descartada.

## Causas reais de login falhando (checar nessa ordem)

1. Conta `ativo=false` → 401 "credenciais inválidas".
2. Senha errada → 401. `/auth/trocar-senha` invalida TODAS as sessões do usuário →
   precisa relogar.
3. Rate limit `10/minute` no `/auth/login` (limiter em memória) → 429. Testes que
   logam em loop batem; reiniciar o servidor zera o contador.
4. **Link/ambiente errado** — caso real: usuário tinha o problema "resolvido" sozinho,
   estava num preview de PR/URL antiga com credencial de outro ambiente. Conferir o
   host (`artemis.idconsultoria.ai`) antes de assumir bug.
5. Token expirado → 401 "sessão expirada — faça login novamente".

## Verificar contas/usuários sem acesso ao host

Não há SSH/docker ao host a partir do container do Mercúrio. Restaurar o dump local
num sandbox PG17 e consultar `public.usuarios`:

```bash
source pgenv.txt   # PGBIN, LD_LIBRARY_PATH, PGDATA=data, PGHOST=sock, PGUSER=app, PGPORT=55432
"$PGBIN/createdb" -h 127.0.0.1 -p 55432 -U app artemishub
"$PGBIN/pg_restore" --no-owner --role=app -h 127.0.0.1 -p 55432 -U app \
  -d artemishub /opt/data/artemishub/db/artemishub.dump
"$PGBIN/psql" -h 127.0.0.1 -p 55432 -U app -d artemishub \
  -c "SELECT email,nome,papel,ativo FROM public.usuarios ORDER BY criado_em;"
```

⚠️ **Dump é formato 1.16 = PG17** (snapshot: master `taciobrito.idteal@gmail.com`).
Postgres sandbox deve ser **17** — PG16 não lê 1.16.