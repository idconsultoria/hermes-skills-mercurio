# UID Mismatch Workaround — Alembic/Protected Directories

## O Problema

Pi local roda como uid 10000. O shared volume `workstation/` contém arquivos/diretórios **legados** criados pelo antigo container Docker Pi (uid 1001). Diretórios como `backend/alembic/versions/` são 755 owned por 1001:

```
drwxr-xr-x 2 1001 1001 4096 Jun  7 17:29 alembic/versions/
```

Pi (uid 10000) **não consegue criar arquivos novos** em diretórios 755 owned por 1001. Pi não crasha — ele escreve num local alternativo (ex: `backend/taskflow/migrations/`) com exit code 0, silenciosamente.

## Sintoma

Pi reporta "Arquivos criados em `backend/taskflow/migrations/`" quando deveria ser `backend/alembic/versions/`.

## Workarounds (em ordem de preferência)

### 1b. Host SSH chmod (leve, para arquivos específicos)

Quando só alguns arquivos estão bloqueados (não o diretório inteiro), um `sudo chmod o+w` via SSH resolve sem mexer no ownership:

```bash
ssh oracle-host 'sudo chmod o+w /home/ubuntu/selfhost/shared/code/workstation/PROJETO/arquivo/bloqueado.py'
```

Útil quando Pi trava num PHASE_COMPLETE ou num único arquivo de doc/product. Menos invasivo que chown geral porque não altera o owner — só dá permissão de escrita pra "others".

### 1c. Fix em lote para arquivos específicos

```bash
ssh oracle-host 'sudo chmod o+w \
  /home/ubuntu/selfhost/shared/code/workstation/PROJETO/docker-compose.preview.yml \
  /home/ubuntu/selfhost/shared/code/workstation/PROJETO/.github/workflows/ci.yml \
  /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/engineering/api-contracts.yaml'
```

```bash
ssh oracle-host "cp /host/path/source.py /host/path/dest/"
```

Pi escreve no local alternativo (ex: `backend/taskflow/migrations/`), depois copiamos:

```bash
ssh oracle-host "for f in 011 012 013; do
  cp /home/ubuntu/selfhost/shared/code/workstation/PROJETO/backend/taskflow/migrations/\${f}_*.py \
     /home/ubuntu/selfhost/shared/code/workstation/PROJETO/backend/alembic/versions/
done"
```

### 2. Fix permanente (chown do projeto)

```bash
ssh oracle-host "sudo chown -R ubuntu:ubuntu /home/ubuntu/selfhost/shared/code/workstation/PROJETO/"
```

Só funciona se o usuário tem sudo. Resolve de uma vez.

### 3. Python3 shutil (se o diretório alvo for world-writable)

```bash
python3 -c "
import shutil, os
src = '/path/to/source.py'
dst = '/path/to/dest/'
os.chmod(dst, 0o777)  # se permitido
shutil.copy2(src, dst)
os.chmod(dst, 0o755)  # restaurar
"
```

## Frontend Permission Issue (EACCES em frontend/src/)

O mesmo problema ocorre em `frontend/src/` — arquivos owned por uid 1001 com mode 644/755 bloqueiam Pi (uid 10000) de escrever componentes novos:

```
-rw-rw-rw- 1 1001 1001 15005 Jun  7 17:29 frontend/src/components/TaskList.tsx
```

Pi não crasha — ele simplesmente pula o arquivo e continua (exit 0), mas o arquivo nunca é criado.

### Fix

```bash
find /opt/data/code/workstation/PROJETO/frontend/src -type d -exec chmod 777 {} \;
find /opt/data/code/workstation/PROJETO/frontend/src -type f -exec chmod 666 {} \;
```

Também vale para `tests/`:

```bash
find /opt/data/code/workstation/PROJETO/tests -type d -exec chmod 777 {} \;
find /opt/data/code/workstation/PROJETO/tests -type f -exec chmod 666 {} \;
```

## Git add bloqueado por arquivo 600 owned por 1001

Quando `git add -A` encontra um arquivo com 600 owned por 1001, falha inteiro:

```
error: open("prompts/pi-fix-agy-ressalvas.md"): Permission denied
fatal: adding files failed
```

### Fix

```bash
# Opção 1: remover o arquivo (se for lixo temporário)
rm -f /opt/data/code/workstation/PROJETO/prompts/pi-fix-agy-ressalvas.md

# Opção 2: corrigir permissão (se o dono permitir)
chmod 644 /opt/data/code/workstation/PROJETO/prompts/pi-fix-agy-ressalvas.md

# Opção 3: ignorar o arquivo (se não for necessário no commit)
git add --all -- :!prompts/pi-fix-agy-ressalvas.md
```

## O que NÃO funciona

- `write_file()` no alvo — Hermes precisa criar `.hermes-tmp.N` no mesmo diretório, e o diretório 755 owned por 1001 bloqueia
- `cp` do container — mesmo UID mismatch
- `python3 open()` para criar arquivo novo — cria no diretório, mas o diretório 755 owned por outro uid bloqueia
- `patch()` — mesma limitação do `write_file()`
