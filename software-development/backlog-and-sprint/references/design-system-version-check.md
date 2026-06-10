# Design System Version Check — Pós-Pi

> **Problema detectado:** Pi gerou prototype.html rotulado como "Design System v2" mas
> usando cores e estrutura do v1. Hermes precisa verificar e corrigir.

## O que verificar no prototype gerado pelo Pi

| Característica | V1 (obsoleto) | V2 | Sinal de alerta |
|---------------|---------------|-----|-----------------|
 | `--blue` | `#0000FF` | `#2563EB` | Se for `#0000FF`, está copiando V1 |
 | `--amber` | `#FFB800` | `#F59E0B` | Se for `#FFB800`, está copiando V1 |
 | `--bg-sidebar` | `#1A1A2E` | `#0F172A` | Se for `#1A1A2E`, está copiando V1 |
 | `--success` | `#2E7D32` | `#10B981` | V2 é mais vibrante |
 | `--danger` | `#D32F2F` | `#EF4444` | V2 é mais vibrante |
 | Inversão CSS | ❌ direto | ✅ invertido | V2 usa `--color-*-coded:` com inversão |
 | Cormorant Garamond | ✅ tem | ✅ tem | V2 tem `ital,wght` mais rico |
 | `--font-serif` | ❌ | ✅ `Cormorant Garamond` | V2 adicionou variável serif |

## Local dos arquivos de referência

```bash
# Design System V2 (ativo)
product/design/design-system-v2.html

# Design System V1 (obsoleto)
product/design/design-system-v1-obsoleto.html
```

## Quando suspeitar

- Prototype comenta "Design System v2" mas as cores são `#0000FF`, `#FFB800`
- Não tem variáveis invertidas (`--color-*-coded`)
- Sidebar com fundo `#1A1A2E` (V1) em vez de `#0F172A` (V2)

## O que fazer

Se o Pi usou V1 em vez de V2:

**Opção A — agy rebuild (recomendado se tempo disponível):**
```bash
# agy pode refazer o prototype estritamente em V2 via tmux interativo
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'
ssh oracle-host 'tmux new-session -d -s agy-sprint "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'
sleep 8
ssh oracle-host 'tmux send-keys -t agy-sprint "Rebuild the prototype at [path]/prototype.html strictly using the DESIGN SYSTEM V2 specification." Enter'
sleep 2
ssh oracle-host 'tmux send-keys -t agy-sprint "First read [path]/design-system-v2.html for correct colors (inversion technique, #2563EB blue, #F59E0B amber). Then read the current prototype for structure. Rewrite keeping ALL functionality but using V2 tokens." Enter'
```
agy pode estourar token de output (>70KB). Aguardar retry automático com versão compacta. Verificar se todas as views/overlays foram preservadas.

**Opção B — documentar e seguir (rápido):**
1. **Não refazer o design inteiro** — a diferença é cosmética (cores, não estrutura)
2. Documentar que o prototype é baseado em V1 com atualizações seletivas
3. Na engenharia, alinhar para V2 se houver tempo
4. Atualizar o comentário no prototype de "Design System v2" para "Design System Sprint 1 (fork V1)"
