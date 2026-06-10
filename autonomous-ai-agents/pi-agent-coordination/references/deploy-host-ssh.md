# Deploy via Host SSH — UID Mismatch Workaround

Pi (uid 10000, hermes) **não consegue escrever** em diretórios owned por uid 1001
(projetos criados pelo container Pi antigo). Sintomas:

- `write_file()`, `patch()` retornam success mas arquivo não muda
- `cp` no terminal: `Permission denied` (dir 755, owner 1001)
- `git add`: `"insufficient permission for adding an object"`
- `git checkout`: `"unable to unlink old 'file.ts': Permission denied"`

## Volumes Montados

```yaml
host:/home/ubuntu/selfhost/shared/code/  →  container:/opt/data/code/
host:/home/ubuntu/selfhost/hermes/data/  →  container:/opt/data/
```

Working tree ativo: `host:/home/ubuntu/selfhost/shared/code/workstation/taskflow/`

## Solução Permanente — chmod no volume

```bash
ssh oracle-host 'sudo chmod -R o+w /home/ubuntu/selfhost/shared/code/workstation/taskflow/'
```

Muda de 755 → 777 em todo o repositório. `git add`, `git commit`, writes,
edits — tudo passa a funcionar do container (uid 10000).

### Aplicação seletiva (só git)

Se só git está bloqueado:

```bash
ssh oracle-host 'sudo chmod -R o+w /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git/objects/ /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git/refs/'
```

### Verificação

```bash
# No container — git add funciona?
cd /opt/data/code/workstation/taskflow
echo test > .git-perm-test
git add .git-perm-test && echo "OK" && git reset HEAD .git-perm-test && rm .git-perm-test

# Permissões corretas?
stat -c "%a %U:%G %n" .git/objects/ 
# Deve retornar: 777 hermes:hermes (ou 1001:1001, desde que world-writable)
```

## Solução Alternativa — Git clone writable

Quando `.git/objects/` não pode ser modificado (container sem SSH), clonar
o repoo para local writable, copiar as mudanças, commitar de lá:

```bash
# 1. Clonar do working tree
git clone /opt/data/code/workstation/taskflow /opt/data/taskflow-pr

# 2. Copiar todas as mudanças (excluindo __pycache__ e .pyc)
cd /opt/data/code/workstation/taskflow
git diff --name-only HEAD | grep -v __pycache__ | grep -v '\.pyc$' | \
  while IFS= read -r f; do
    mkdir -p "/opt/data/taskflow-pr/$(dirname "$f")"
    cp "$f" "/opt/data/taskflow-pr/$f"
  done

# 3. Commitar e push do clone
cd /opt/data/taskflow-pr
git remote set-url origin https://github.com/USER/REPO.git
git push -u origin BRANCH

# 4. PR
gh pr create --title "..." --body "..."
```

## Recuperação de Arquivos Perdidos

`git checkout <branch>` deleta untracked files que não existem na branch de
destino. Com UID 1001, o `Permission denied` impede a deleção mas o arquivo
some mesmo assim.

**Recuperação via clone:**

```bash
cd /opt/data/taskflow-pr
# Listar arquivos novos (diff-filter=A)
git diff --name-only origin/master HEAD --diff-filter=A | \
  while IFS= read -r f; do
    # Se o clone tem SSH host, copiar direto
    ssh oracle-host "mkdir -p /home/ubuntu/selfhost/shared/code/workstation/taskflow/\$(dirname \"$f\")"
    ssh oracle-host "cat > /home/ubuntu/selfhost/shared/code/workstation/taskflow/\$f" < "\$f"
  done
```

**Prevenção:** antes de `git checkout`, verificar untracked files:
```bash
git status --short | grep '^??' | wc -l
# Se > 0, fazer stash ou commit primeiro
```

## Por que acontece

O repositório foi criado pelo container Pi antigo (uid 1001). `mkdir -p`
cria subpastas com 755 e owner 1001. Hermes (uid 10000) não é owner nem
está no grupo 1001 → cai em "other" → permissão r-x (leitura, sem escrita).
