# Persistir Patches do Container na Fonte

> Padrão validado no TaskFlow: correções aplicadas no container running (nano, docker cp) precisam voltar para a fonte no shared volume antes do rebuild, senão somem no próximo `docker compose up -d`.

## O Problema

Durante o loop de debug (F4c → F4d), é comum editar arquivos diretamente no container:

```bash
# Editar dentro do container (rápido, sem rebuild)
docker exec -it taskflow-backend bash
nano app/taskflow/main.py  # TrailingSlashMiddleware, IdStr, etc.
```

Isso funciona imediatamente, mas o próximo `docker compose build --no-cache` sobrescreve as alterações com o código-fonte antigo.

## O Padrão: docker cp do Container para a Fonte

SEMPRE copiar as alterações de volta para a fonte ANTES de rebuildar:

```bash
# 1. Identificar arquivos alterados dentro do container
# (comparar com git diff da fonte, ou listar por data de modificação)

# 2. Copiar do container para a fonte no shared volume
docker exec taskflow-backend cat /app/taskflow/main.py > backend/taskflow/main.py
docker exec taskflow-backend cat /app/taskflow/schemas/task.py > backend/taskflow/schemas/task.py
docker exec taskflow-backend cat /app/taskflow/schemas/common.py > backend/taskflow/schemas/common.py

# 3. Verificar diff
git diff --stat
git diff backend/taskflow/main.py | head -30

# 4. Commitar antes de rebuildar
git add -A && git commit -m "fix: persist container patches"

# 5. Rebuildar
docker compose build backend --no-cache
```

## Pré-requisito de Permissão

Os arquivos no shared volume podem estar owned por uid 1001 (Pi). O `>` falha com Permission denied. Antes de copiar, corrigir permissão do diretório pai:

```bash
# Se o diretório for owned por uid 1001 (755) e Hermes (uid 10000) não consegue escrever:
ssh oracle-host 'pi-shell "chmod o+w /workspace/code/workstation/PROJETO/backend/taskflow"'

# Ou mais abrangente (toda a tree do projeto):
ssh oracle-host 'pi-shell "chmod -R o+rwX /workspace/code/workstation/PROJETO/backend/taskflow 2>/dev/null"'
```

## Quais Arquivos Verificar (checklist)

Depois de uma sessão de debug no container, verificar SEMPRE:

- [ ] `main.py` — middleware, event handlers, lifespan
- [ ] `schemas/*.py` — IdStr, Optional[IdStr], field types
- [ ] `models/*.py` — TypeDecorator vs UUID nativo, bool defaults
- [ ] `docker-entrypoint.sh` — comando de inicialização
- [ ] `Dockerfile` — bcrypt pin, dependências extras
- [ ] `api/routes/*.py` — rotas adicionadas ou alteradas
- [ ] `api/middleware/*.py` — novos middlewares

## Alternativa: Editar a Fonte Diretamente

Se o Hermes tem permissão de escrita no diretório alvo (`chmod o+w` já aplicado), usar `patch` ou `write_file` diretamente na fonte e recarregar só o backend:

```bash
# 1. Corrigir na fonte
patch -p1 < fix.diff  # ou write_file diretamente

# 2. Recarregar no container (sem rebuild)
docker cp backend/taskflow/main.py taskflow-backend:/app/taskflow/main.py
docker exec taskflow-backend kill -HUP 1  # reload workers
```

Isso evita o passo extra de copiar de volta, mas requer que a fonte já esteja editável.

## O que NÃO Funciona

- ❌ `docker restart` recarrega .env? Não, só recarrega o processo.
- ❌ Rebuild sem `--no-cache` pega a versão em cache? Sim, usar `--no-cache` sempre.
- ❌ `git stash` no container? Não tem git dentro do container.
