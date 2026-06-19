# Vault Cleanup Pattern

> Workflow para limpeza e otimização de vaults Obsidian/Hephaistos.

## Quando Usar

- Vault com muitos arquivos (>200 .md)
- Wikilinks quebrados
- Arquivos com espaços no nome
- Arquivos muito grandes (>200 linhas)
- Dados irrelevantes (pricing, dados temporários)

## Checklist de Limpeza

### 1. Renomear Arquivos com Espaços

```bash
# Encontrar arquivos com espaços
find vault/ -name "* *" -type f

# Renomear (substituir espaços por hifens, lowercase)
for file in $(find vault/ -name "* *" -type f); do
  dir=$(dirname "$file")
  base=$(basename "$file")
  newname=$(echo "$base" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
  mv "$file" "$dir/$newname"
done
```

### 2. Corrigir Wikilinks Quebrados

```python
# Script Python para corrigir wikilinks
import os

vault_path = "/path/to/vault"
replacements = {
    "[[old-link]]": "[[new-link]]",
    "[[MOC Old Name]]": "[[new-index|New Name]]",
}

for root, dirs, files in os.walk(vault_path):
    for file in files:
        if file.endswith(".md"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            modified = False
            for old, new in replacements.items():
                if old in content:
                    content = content.replace(old, new)
                    modified = True
            if modified:
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"[OK] {filepath}")
```

### 3. Condensar Arquivos Grandes

Para arquivos >200 linhas:
1. Ler o arquivo completo
2. Identificar seções temáticas
3. Criar 3-5 engramas atômicos (max 100 linhas cada)
4. Adicionar wikilinks entre eles
5. Atualizar index.md
6. Deletar arquivo original

### 4. Remover Dados Irrelevantes

- Tabelas de pricing/preços
- Dados temporários (temp, backup, old)
- Arquivos vazios (0 bytes)
- MOCs antigos sem referências

### 5. Verificação Final

```bash
# Contar arquivos
find vault/ -name "*.md" -type f | wc -l

# Verificar wikilinks quebrados
grep -roh '\[\[[^]]*\]\]' vault/engramas/ | sort | uniq -c | sort -rn | head -10

# Verificar arquivos com espaços
find vault/ -name "* *" -type f | wc -l
```

## Métricas de Qualidade

| Métrica | Meta |
|---------|------|
| Arquivos com espaços | 0 |
| Wikilinks quebrados | 0 |
| Arquivos >200 linhas | 0 (condensados) |
| Dados irrelevantes | 0 |

## Exemplo Praticado

**Sprint 7 (2026-06-17):**
- 34 arquivos renomeados (espaços → hifens)
- 127 wikilinks MOC antigos corrigidos
- 1 arquivo condensado (Pesquisa_lovable.md: 660 linhas → 3 engramas)
- 1 arquivo condensado (pesquisa-exaustiva-orquestracao.md: 2198 linhas → 5 engramas)
- 0 dados de pricing removidos
- Resultado: 305 arquivos, 0 problemas de qualidade
