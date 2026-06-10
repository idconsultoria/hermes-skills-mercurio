# Agy Design Review — Prompt Pattern

> Prompt testado e aprovado para revisão de designs de Sprint com o Antigravity CLI (agy).
> Enviado via `tmux send-keys` em 3 partes (rate-limited ~3 send-keys, com sleep 2 entre eles).

## Prompt (3 send-keys)

```bash
# send-key 1 — localização + output
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "Review Sprint N design at /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/design/. Write feedback in /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/feedbacks_sprint_N.md" Enter'
sleep 2

# send-key 2 — critérios de revisão
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "Check visual consistency (colors, fonts, spacing, design system), verify all user stories are covered, spot missing flows or usability issues." Enter'
sleep 2

# send-key 3 — marcador de aprovação
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "When satisfied, end the file with: ACORDO: AVANCAR PARA ENGENHARIA" Enter'
```

## O Que o agy Produziu (exemplo real)

Na Sprint 1 do TaskFlow, o agy gerou `feedbacks_sprint_1.md` com 4 seções:

### 1. Visual Consistency Verification
- Cores (azul, âmbar, vermelho, verde) mapeadas corretamente
- Fontes (Inter, Space Mono, Syncopate) aplicadas conforme design system
- 7 estados GTD modelados consistentemente

### 2. User Stories Coverage Check (17 stories)
- Cada US-001 a US-017 mapeada para wireframe (W-xx) e user flow (F-xx) específico
- Links cruzados entre user stories e artefatos de design

### 3. Usability & Technical Enhancements
- 5 melhorias concretas com localização (W-xx / US-xx)
- Cada uma com: observação → recomendação (ex: "bulk selection cap de 200 tasks")
- Sugestões focadas em implementação, não opinativas

### 4. Final Alignment
- Parágrafo resumindo aprovação
- `ACORDO: AVANCAR PARA ENGENHARIA` como linha final

## Checklist (o que o agy DEVE verificar)

- [ ] Paleta de cores consistente com o design system do projeto
- [ ] Tipografia aplicada corretamente (títulos, corpo, mono)
- [ ] Todos os estados de cada componente (default, hover, loading, erro, vazio)
- [ ] Cobertura de todas as user stories da Sprint (c/ referência US-xxx)
- [ ] Fluxos alternativos e edge cases mapeados
- [ ] Acessibilidade básica (teclado, foco, aria)
- [ ] Performance (limites de batch, timeouts, TTLs)
- [ ] Marcador `ACORDO: AVANCAR PARA ENGENHARIA` ao final

## Após Aprovação

O feedback fica em `product/sprint_N/feedbacks_sprint_N.md`. Se o agy sugeriu melhorias, Hermes decide se itera com Pi ou leva como tech-debt para a engenharia.