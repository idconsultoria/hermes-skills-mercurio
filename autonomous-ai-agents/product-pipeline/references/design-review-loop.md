# Design Review Loop — Workflow Padrão

> Extraído da primeira execução real (TaskFlow, Jun 2026)

## Contexto

O Antigravity CLI (agy) requer OAuth Google armazenado no keyring do host. O token não persiste no container Docker. Portanto, agy só funciona via SSH no host Oracle.

## Path Mapping

| Ambiente | Path base |
|----------|-----------|
| **Container Hermes** | `/opt/data/code/workstation/PROJETO/` |
| **Container Pi** | `/workspace/code/workstation/PROJETO/` |
| **Host Oracle** | `/home/ubuntu/selfhost/shared/code/workstation/PROJETO/` |

## Loop de Revisão (2-3 turnos típicos)

Cada turno segue o formato **conversa multi-turno** — ver `## Formato do feedbacks.md` na SKILL.md principal.

### 🗨️ Turno 1 — agy

```bash
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
  /home/ubuntu/.local/bin/agy -p "Review design-system.html. \
  Evaluate all components. Write feedback in product/design/feedbacks.md \
  under ## 🗨️ Turno 1 — @Antigravity, \
  with explicit ⬆️ O que espero de @Pi section"'
```

### 🗨️ Turno 2 — Pi

```bash
ssh oracle-host "LC_DIR=code/workstation/PROJETO pi-agent 'pi -c -p \
  \"Leia ## 🗨️ Turno 1 — @Antigravity em product/design/feedbacks.md. \
  Responda em ## 🗨️ Turno 2 — @Pi no formato conversa multi-turno \
  (Para:, Em resposta ao:, ⬆️ O que espero). \
  Aplique correções no design-system.html.\"'"
```

### 🗨️ Turno 3 — agy (re-review + decisão final)

```bash
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
  /home/ubuntu/.local/bin/agy -p "Re-review design-system.html. \
  Verify all corrections. If satisfied, append ## 🗨️ Turno 3 — @Antigravity \
  to product/design/feedbacks.md with: \
  **✅ Decisão final:** ACORDO: DESIGN SYSTEM FINALIZADO"'
```

## Correções Comuns da Iteração 1

Baseado na primeira execução, agy costuma apontar:

1. **Contraste P2** — Texto branco sobre `#FFB800` tem contraste baixo. Corrigir para texto escuro (`#1C1C1E`).
2. **Foco no Quick Add** — `box-shadow` sutil não é suficiente. Usar `outline: 2px solid #0000FF`.
3. **Sombra isométrica** — Botão ghost/outline precisa da mesma sombra 3x3px do primário para manter linguagem coesa.
4. **Kanban "Feito"** — Precisa de background sutilmente diferente (`#EAECF0` vs `#F5F7FA`) para sinalizar conclusão.
5. **Badges de contagem** — Com 2+ dígitos, padding horizontal precisa ser maior (8px em vez de 6px).
6. **Sugestão Hermes** — Borda `#CCD9FF` é quase invisível. Usar `#0000FF` sólido + `border-left: 3px`.
7. **Sidebar indentação** — Projetos e Contextos se misturam. Aumentar indentação de Contextos (44px vs 36px) + opacidade reduzida.

## Correções Extras

- **Datepicker keyboard nav** — Adicionar `:focus-visible` outline nos dias
- **Widget alinhamento** — Horários à direita com `text-align: right` + `min-width`
- **"+ N mais"** — Estilizar como botão (border, hover state)
- **Tabela técnica** — Adicionar coluna de escala com nomes sistêmicos (`text-sm`, `space-4`, etc.)
