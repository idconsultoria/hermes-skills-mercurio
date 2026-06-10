# Agy Multi-Round Design Workflow

> Numa Sprint, a fase de design pode exigir múltiplas rodadas do agy com objetivos diferentes.
> Este documento descreve o padrão usado na Sprint 1 do TaskFlow, que funcionou bem.

## Rodada 1 — Design Review (obrigatório)

**Objetivo:** Revisar os 3 artefatos gerados pelo Pi (wireframes.md, user-flows.md, prototype.html)

**Prompt (3 send-keys via tmux):**
```bash
# 1. Localização + output
tmux send-keys -t agy-sprint \
  "Review Sprint N design at /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/design/. Write feedback in .../feedbacks_sprint_N.md"

# 2. Critérios
tmux send-keys -t agy-sprint \
  "Check visual consistency (colors, fonts, spacing), verify all user stories covered, spot missing flows or usability issues."

# 3. Marcador
tmux send-keys -t agy-sprint \
  "When satisfied, end the file with: ACORDO: AVANCAR PARA ENGENHARIA"
```

**Saída esperada:** `feedbacks_sprint_N.md` com 5-10 melhorias identificadas

## Rodada 2 — Redesign Técnico (quando necessário)

**Objetivo:** Reconstruir um artefato específico seguindo regras estritas (ex: trocar design system V1 → V2)

**Quando disparar:** Após Hermes detectar que o Pi usou o design system errado (ver `references/design-system-version-check.md`)

**Prompt:**
```bash
tmux send-keys -t agy-sprint \
  "Rebuild prototype.html strictly using DESIGN SYSTEM V2. First read design-system-v2.html, then read current prototype.html for structure. Keep ALL functionality, replace every color token."

tmux send-keys -t agy-sprint \
  "Apply the inversion technique. Use V2 palette. Add missing V2 fonts. Remove all V1 colors (#0000FF, #FFB800)."
```

**⚠️ Pitfall — agy pode estourar o output token limit.** Prototypes grandes (>70KB) podem falhar com "model's generation exceeded the maximum output token limit". agy faz retry automático com versão menor. Verificar se o arquivo foi escrito e se todas as views/overlays originais estão presentes.

## Rodada 3 — Feature Adicional (quando solicitada)

**Objetivo:** Adicionar uma nova funcionalidade/feature nos 3 artefatos ao mesmo tempo

**Quando disparar:** Quando o usuário pede um acréscimo após aprovar o review (ex: "adicione uma página educacional GTD")

**Prompt:**
```bash
# Descrever a feature com clareza nos 3 artefatos:
tmux send-keys -t agy-sprint \
  "1. In prototype.html: add a new view/section for [feature description]"
tmux send-keys -t agy-sprint \
  "2. In wireframes.md: add a new wireframe W-16 for [feature name]"
tmux send-keys -t agy-sprint \
  "3. In user-flows.md: add a new flow F-10 for [feature name]"
tmux send-keys -t agy-sprint \
  "Use the ABSOLUTE path: /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/design/"
```

## Padrões que Funcionam

1. **Path absoluto + longo**: Sempre usar `/home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/design/prototype.html`, nunca `product/sprint_N/design/prototype.html`. agy pode estar em CWD diferente.

2. **3 send-keys no máximo**: agy processa a fila de prompts em ordem. Mais de 3 send-keys sem pausa podem ser perdidos ou interpretados como um bloco só.

3. **Verificar saída entre rodadas**: Sempre checar `ls -la prototype.html` (tamanho, timestamp) e `grep -c` para features esperadas antes de encerrar a sessão tmux.

4. **Correções de path**: Se agy ler o arquivo errado, enviar `STOP. Use /path/correto/`. Aguardar a fila drenar (30-60s) antes de verificar se a correção foi aplicada.
