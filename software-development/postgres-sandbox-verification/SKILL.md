---
name: postgres-sandbox-verification
type: ToolIntegration
timestamp: 2026-08-23T00:00:00Z
description: "Verify features really persist against a throwaway Postgres."
---

# Postgres Sandbox Verification

> Verificar comportamento **real no banco** (não só leitura de código): montar um
> PostgreSQL 17 descartável a partir de `.deb`s do apt extraídos (sem instalar,
> sem docker-daemon, sem root), restaurar o dump/schema do projeto, subir o backend
> real contra ele e exercitar os fluxos via HTTP **confirmando o estado por SQL a
> cada passo**. Nunca tocar em produção: usar usuários/registros fictícios e banco
> descartável.

## Quando usar
- Pedidos do tipo "verifica se criar usuário realmente grava no banco de autenticação",
  "editar senha via master funciona no banco", "DELETE/ativar/desativar persiste".
- Qualquer validação end-to-end de API que dependa de um Postgres real, quando `docker`
  não tem daemon acessível e não há `sudo`/root no ambiente.
- Descobrir GAPs que só a execução real revela (rota inexistente → `405`, campo que o
  backend aceita sem validar → `201`, etc.).

## Passos (menos de 2 minutos de setup; Debian/APT)
```bash
# 1) Baixar e extrair postgres (não instala no sistema)
mkdir -p /opt/data/pgtest/debs && cd /opt/data/pgtest/debs
apt-get download postgresql-17 postgresql-client-17 libpq5 postgresql-common postgresql-client-common libicu76 liblz4-1 libzstd1
mkdir -p /opt/data/pgtest/ext && cd /opt/data/pgtest
for d in debs/*.deb; do dpkg -x "$d" ext/; done

PGBIN=/opt/data/pgtest/ext/usr/lib/postgresql/17/bin
export LD_LIBRARY_PATH=/opt/data/pgtest/ext/usr/lib/aarch64-linux-gnu:/opt/data/pgtest/ext/usr/lib/postgresql/17/lib
export PGDATA=/opt/data/pgtest/data PGHOST=/opt/data/pgtest/sock PGUSER=app PGPORT=55432

# 2) initdb NÃO roda como root — rode como usuário comum.
mkdir -p "$PGDATA" /opt/data/pgtest/sock
"$PGBIN/initdb" -D "$PGDATA" -U app --auth=trust --encoding=UTF8 --no-locale

# 3) sobe o servidor + cria o banco
"$PGBIN/pg_ctl" -D "$PGDATA" -l /opt/data/pgtest/pg.log -o "-p 55432 -k /opt/data/pgtest/sock" start
"$PGBIN/createdb" -h /opt/data/pgtest/sock -p 55432 -U app artemishub

# 4) restaura o dump do projeto (formato custom) com o BINÁRIO NATIVO
"$PGBIN/pg_restore" --no-owner --role=app -h /opt/data/pgtest/sock -p 55432 -U app -d artemishub db/artemishub.dump
```
5) Suba o backend real contra o banco (ex.: `ARTEMISHUB_DB_URL=postgresql://app@127.0.0.1:55432/artemishub uvicorn main:app --app-dir backend --port 18000`).
6) Para exercitar fluxos que exigem login (ex. master), **injete direto um usuário com
   hash de senha conhecido** e autentique pela API — não precisa saber a senha real do seed.
7) Apure cada afirmação consultando SQL (`psql -c`), não só o status HTTP.

## Pitfalls
- **Use o binário NATIVO `$PGBIN/pg_restore`/`pg_dump`/`psql`** — o wrapper em
  `ext/usr/bin/pg_restore` (do `postgresql-client-common`) é um script Perl que falha
  com `Can't locate PgCommon.pm` e restaura "vazio" silenciosamente.
- **`psql` precisa de `-c`**: um SQL passado como argumento posicional é tratado como
  **nome de database** → retorna nada. Sempre `psql ... -c "SELECT ..."`.
- **initdb/postgres exigem `libicu`** (`libicu76` provê `libicui18n`/`libicuuc`) e `libpq`.
  Baixe-as junto e aponte `LD_LIBRARY_PATH` para o dir extraído; confirme com
  `ldd $PGBIN/bin/postgres | grep "not found"` → deve mostrar "ALL PRESENT".
- **`initdb` recusa rodar como root.** Garanta que o worker é usuário comum.
- **Rate-limiter pode quebrar o teste** (ex. slowapi `login` 10/min): muitos logins num
  minuto → `429`. Reinicie o uvicorn (zera o contador in-memory) e/ou **reuse tokens de
  sessão** e poda logins redundantes; fique abaixo do teto.
- **Hash de senha PBKDF2 com salt**: replicável com
  `hashlib.pbkdf2_hmac('sha256', senha, bytes.fromhex(salt), iters).hex()` — mesmo
  esquema do backend para injetar um usuário autenticável.
- **Proteja o último-admin**: ao testar desativação/edição de master, inclua a checagem
  "último master ativo" (o app frequentemente bloqueia removê-lo — o teste deve respeitar).
- Trabalho real executado: ver `references/artemis-auth-verification.md`.

## Verificação da entrega
- Estado do banco mudou como esperado (linha criada/atualizada, `senha_hash` novo,
  `ativo=false`/`true`, sessão invalidada) via `SELECT` — não só `HTTP 200`.
- Rota inexistente retorna `405 Method Not Allowed` (prova de GAP de `DELETE`), não 500.
- Nenhuma fonte de produção foi alterada; tudo num banco descartável com registros fictícios (`*.local`).