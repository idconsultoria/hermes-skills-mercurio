---
name: local-postgres-sandbox
description: Verify DB behavior via local Postgres sandbox from app dump.
---

# Local Postgres sandbox verification (no Docker daemon, no sudo)

Verificar, com **prova real no banco**, que funcionalidades do backend gravam/lêem
corretamente — sem tocar produção e numa máquina onde o Docker daemon não está
acessível e o usuário não tem sudo. Abordagem: **extrair binaries do Postgres de
`apt-get download` + `dpkg -x`**, subir um cluster local, **restaurar o dump oficial
do app**, rodar o backend real contra ele e exercitar os fluxos via HTTP com
confirmação do estado persistido via SQL em cada passo.

## Quando usar
- O usuário pede "verifica se X realmente funciona no banco" (criar usuário grava?
  status persiste? DELETE remove?) e a resposta correta exige rodar contra um
  PostgreSQL de verdade, não só ler código.
- Docker daemon inacessível (`Cannot connect to the Docker daemon`), sem `sudo`,
  mas `apt-get` funciona como usuário comum.
- O repo tem um dump (`pg_dump -Fc`) que reproduz o schema/data de produção.

## Passos (sem Docker/sudo)
1. **Baixe e extraia o Postgres localmente** (não instala no sistema):
   ```bash
   mkdir -p /opt/.../pgtest/debs && cd debs
   apt-get download postgresql-17 postgresql-client-17 libpq5 postgresql-common postgresql-client-common
   apt-get download libicu76        # essencial: libicui18n/libicuuc (postgres server NÃO roda sem)
   cd .. && for d in debs/*.deb; do dpkg -x "$d" ext/; done
   ```
2. **Rode com binário nativo + LD_LIBRARY_PATH** (ver pitfall do wrapper Perl):
   ```bash
   export PGBIN=ext/usr/lib/postgresql/17/bin
   export LD_LIBRARY_PATH=ext/usr/lib/aarch64-linux-gnu:ext/usr/lib/postgresql/17/lib
   "$PGBIN/initdb" -D data -U app --auth=trust --encoding=UTF8 --no-locale   # roda como usuário comum
   "$PGBIN/pg_ctl" -D data -o "-p 55432 -k sock" start
   ```
3. **Crie o banco e restaure o dump com o BINÁRIO NATIVO** (não o wrapper Perl):
   ```bash
   "$PGBIN/createdb" -h sock -p 55432 -U app artemishub
   "$PGBIN/pg_restore" --no-owner --role=app -h sock -p 55432 -U app -d artemishub db/app.dump
   ```
4. **Suba o backend real contra esse banco** (env `DATABASE_URL`/`..._DB_URL` → local),
   tipo `uvicorn backend.main:app --port 18000`. Verifique health primeiro.
5. **Driver HTTP de teste** em Python (urllib) que, a cada passo, consulta o banco via
   `psql` para provar a persistência. Não dependa de credenciais de produção:
   **semeie direto no banco** um master de teste com senha hashada e entre por ele.
   (ex.: PBKDF2 `pbkdf2_hmac('sha256', senha, bytes.fromhex(salt), 600000)`).

## Pitfalls (aprendidos na prática)
- **`pg_restore`/`psql` de `/usr/bin` pode ser um wrapper Perl** (`Can't locate
  PgCommon.pm`) que falha/retorna vazio silenciosamente → use SEMPRE o binário nativo
  em `$PGBIN/`. Verifique com `file`/checksum se desconfiar.
- **O server `postgres` exige lib ICU** (`libicuuc.so.76`/`libicui18n.so.76`); baixe o
  pacote `libicu76`. `psql`/`pg_restore` (só libpq) funcionam sem — então um `ldd` só
  do `initdb`/`postgres` aponta exatamente o que falta.
- **initdb recusa rodar como root**; rodar como usuário comum (ex.: uid `hermes`) OK.
- **`psql -At` em subprocess**: passar a query com `-c`; sem `-c` o SQL vira nome de
  banco e retorna vazio (bug real). Não troque stdout vazio por `"ERR"` — vazio pode
  ser o resultado legítimo (0 linhas); marque erro só quando `returncode != 0`.
- **Rate limit**: endpoints de login costumam ter limiter (ex.: `10/minute`) em memória;
  drivers que fazem muitos logins batem no 429. Reuse tokens já obtidos e reinicie o
  servidor antes do run final para zerar o contador.
- **ON CONFLICT (email) upsert** na criação → re-rodar o driver é idempotente.
- **FKs**: antes do DELETE, confira `information_schema` para conhecer a `delete_rule`
  (CASCADE em sessoes→usuarios limpa sessões; sem CASCADE o DELETE estoura 500).
- **Dump pode conter schema fora de `public`**: liste com `pg_restore -l` (nativo) e
  `\d`/`information_schema` após restaurar antes de assumir onde está a tabela.

## Verificação
- `pg_isready` deve dizer accepting connections; `curl /api/health` do backend deve
  retornar os dados do banco local; driver termina com os PASS/resumo. Nada é alterado
  em produção.

Suporte: `references/artemishub-auth-usuarios.md` (caso de uso com endpoints e schema).