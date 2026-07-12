# Session File Audit — Verificar se Pi Leu Arquivos Específicos

> **Quando usar:** Após Pi completar uma tarefa, para verificar SE ele realmente leu
> arquivos de referência (design HTMLs, specs, protótipos) que o prompt instruiu.
>
> Pi pode mencionar um arquivo num `ls` (listagem de diretório) sem nunca ter lido
> seu conteúdo. Esta referência mostra como distinguir "viu o nome" de "leu o conteúdo".

## Script de Auditoria

```python
import json, glob, os

def audit_file_reads(session_path: str, target_files: list[str]) -> dict:
    """
    Verifica se Pi leu (cat/read_file) vs apenas viu (ls) arquivos específicos.
    
    Returns: dict com {filename: 'READ'|'LISTED_ONLY'|'NOT_FOUND'}
    """
    text = open(session_path).read()
    result = {}
    
    for kw in target_files:
        if kw not in text:
            result[kw] = 'NOT_FOUND'
            continue
        
        # Check context lines around the match — READ vs LIST
        found_read = False
        found_list = False
        
        for line in text.split('\n'):
            if kw in line:
                lower = line.lower()
                if 'cat ' in lower or 'read_file' in lower or 'curl ' in lower or 'wget ' in lower:
                    found_read = True
                elif kw in line and ('rwx' in line or 'drwx' in line or 'rw-' in line):
                    found_list = True
        
        if found_read:
            result[kw] = 'READ'
        elif found_list:
            result[kw] = 'LISTED_ONLY'
        else:
            result[kw] = 'MENTIONED_UNKNOWN'
    
    return result


# Uso
session_dir = sorted(glob.glob(os.path.expanduser(
    '~/.pi/agent/sessions/--*projeto*--/*.jsonl'
)))[-1]

targets = ['design-system.html', 'prototype.html', 'index.html', 'specs.md']
result = audit_file_reads(session_dir, targets)

for fname, status in result.items():
    icon = {'READ': '✅', 'LISTED_ONLY': '⚠️', 'NOT_FOUND': '❌', 'MENTIONED_UNKNOWN': '❓'}
    print(f'{icon[status]} {fname}: {status}')
```

## Interpretação dos Resultados

| Status | Significado | Ação |
|--------|-------------|------|
| ✅ READ | Pi executou `cat`, `read_file` ou `curl` no arquivo | Contexto visual carregado |
| ⚠️ LISTED_ONLY | Pi viu o nome num `ls -la`, mas NÃO leu o conteúdo | **Recriar prompt** com instrução explícita de leitura |
| ❌ NOT_FOUND | Arquivo não apareceu na sessão | Verificar se o arquivo existe no disco |
| ❓ MENTIONED_UNKNOWN | Mencionado de forma ambígua (ex: em comentário do prompt) | Revisar manualmente |

## ⚠️ Pitfall: `read` tool no JSONL

Pi Agent NÃO usa a tool `read_file` no JSONL — ele usa `bash` com `cat >` heredocs para
escrever e `cat <path>` para ler. A auditoria acima busca pelo comando `cat` no contexto.

## Quando Aplicar

- **Sempre** após Pi gerar frontend — verificar se leu design-system.html e protótipo
- **Sempre** após Pi refatorar código — verificar se leu os arquivos existentes
- **Nunca** assumir que Pi leu algo só porque o prompt instruiu — verificar na sessão

## Resultado Real: Delfos F4b (2026-07-09)

Auditoria de 8 sessões Pi do projeto Delfos:

| Sessão | Provider | Entries | design-system.html | index.html |
|--------|----------|:-------:|:------------------:|:----------:|
| delfos-prd | MiniMax M3 | 20 | ❌ | ❌ |
| delfos-pm | MiniMax M3 | 47 | ❌ | ❌ |
| delfos-f4-design | MiniMax M3 | 39 | ⚠️ (prompt text) | ❌ |
| delfos-engineering | V4 Pro | 45 | ⚠️ (ls output) | ⚠️ (ls output) |
| delfos-layer1 | Flash Free | 202 | ⚠️ (ls output) | ⚠️ (ls output) |
| delfos-frontend | Flash Free | 124 | ❌ | ⚠️ (prompt text) |
| delfos-mcp | Flash Free | 179 | ❌ | ⚠️ (ls output) |

**Resultado: ZERO sessões leram o conteúdo dos HTMLs.** Tokens foram copiados manualmente para o prompt, mas o layout renderizado (glassmorphism, componentes, spacing) nunca foi visto pelo Pi.

**Consequência:** Frontend com tokens CSS corretos mas layout genérico — cards sólidos em vez de glassmorphism, timeline vertical em vez de horizontal, fontes erradas.

**Fix aplicado:** Prompt do agy review instruiu a ler os HTMLs e comparar com o código frontend. O agy encontrou 10 issues críticos de alinhamento visual.
