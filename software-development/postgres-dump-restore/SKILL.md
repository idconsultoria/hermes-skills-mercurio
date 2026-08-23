---
name: postgres-dump-restore
description: "Seed Postgres de dump; evita falha 'unsupported version'."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [postgres, pg_dump, pg_restore, docker, seed, db]
---

# Postgres dump & restore — compatibilidade e seeding

Armadilhas ao restaurar dumps `pg_dump` (custom, header `PGDMP`) e usar o Postgres como seed
de produção/preview em Docker. Origem: incidente do Artemis (22/08/2026) — dump do repo não
restaurava e o banco subia vazio.

## 1. Quando usar
- Restaurar `*.dump` como seed de banco (produção ou preview) em container Postgres.
- `pg_restore` falha com `unsupported version (N.NN) in file header`.
- Escolher a tag de imagem Postgres quando o repo traz um dump versionado.
- Banco "subiu vazio" por initdb que falhou silenciosamente.

## 2. Pitfall 1 — versão do formato do dump vs versão do Postgres
**Sintoma:** `pg_restore: error: unsupported version (1.16) in file header`; tabelas não
aparecem (banco vazio) apesar do container `healthy`.

**Causa:** dump criado com `pg_dump` mais novo que o Postgres do compose. Formatos:
1.13=PG10-13, 1.14=PG14, 1.15=PG15-16, **1.16=PG17+**. `pg_restore` de versão mais nova não
lê dump mais novo.

**Ler versão do dump** (bytes 5-6 do header; robusto sem `xxd`):
```bash
python3 - <<'PY'
import struct
d = open('db/app.dump','rb').read()
print('magic:', d[:5])                          # b'PGDMP'
print('formato:', struct.unpack('>HH', d[5:9])) # (256,4) => 1.16
PY
```
**Corrigir:** alinhar a imagem (ex.: `1.16` → `postgres:17-alpine`). Conferir versão real:
`docker exec <db> pg_restore --version`.

## 3. Pitfall 2 — initdb só roda com volume vazio; falha silenciosa
`/docker-entrypoint-initdb.d/` (official image) só executa na 1ª inicialização (volume
vazio); depois é "Skipping initialization". Falha ali deixa o banco **vazio mas container
`healthy`** (`pg_isready` passa mesmo sem tabelas).

**Diagnóstico:** `docker logs <db> | grep -iE "restor|error|pg_restore"` e conferir tabelas:
`docker exec <db> psql -U <user> -d <db> -tAc "SELECT tablename FROM pg_tables WHERE
schemaname='public'"`.

**Correção ao mudar versão/re-seedar (banco descartável — apagar volume destrói dados):**
```bash
docker compose down --remove-orphans
docker rm -f <db-container>
docker volume rm <proj>_pgdata
docker compose up -d --remove-orphans
```

## 4. Seed de produção (script initdb)
Montar o dump no initdb + `pg_restore --no-owner --role=<owner>`:
```bash
# db/init/01-restore.sh (montado em /docker-entrypoint-initdb.d/ :ro)
#!/bin/bash
set -euo pipefail
pg_restore --no-owner --role="${POSTGRES_USER:-app}" \
  -U "${POSTGRES_USER:-app}" -d "${POSTGRES_DB:-app}" \
  /docker-entrypoint-initdb.d/app.dump
```
```yaml
db:
  image: postgres:17-alpine          # alinhada ao dump (Pitfall 1)
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-app}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: app
  volumes:
    - ./db/init/01-restore.sh:/docker-entrypoint-initdb.d/01-restore.sh:ro
    - ./db/app.dump:/docker-entrypoint-initdb.d/app.dump:ro
    - pgdata:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app} -d app"]
    interval: 10s
    timeout: 5s
    retries: 12
```

## 5. Preview: banco dedicado no Postgres de produção
Reutilizar o Postgres de prod com db `app_pr_<N>` seedada do mesmo dump; erros do pg_restore
viram aviso (roles/owners divergem em preview):
```bash
docker exec <db-prod> psql -U app -d postgres -c "DROP DATABASE IF EXISTS app_pr_${N} WITH (FORCE)"
docker exec <db-prod> psql -U app -d postgres -c "CREATE DATABASE app_pr_${N} TEMPLATE template0"
docker cp app.dump <db-prod>:/tmp/seed.dump
docker exec <db-prod> pg_restore --no-owner --role=app -U app -d app_pr_${N} /tmp/seed.dump || \
  echo "aviso: itens skipped em preview (esperado)"
```

## 6. Verificação
1. `docker logs <db>` mostra "Dump restaurado com sucesso." (ou sem erro).
2. `\dt public.*` lista as tabelas esperadas.
3. `SELECT count(*)` nas tabelas principais > 0 quando o dump tinha dados.
4. `pg_restore --version` no container bate com a versão que gerou o dump.