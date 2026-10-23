# PRD — checklist de revisão e ciclo de correção

Hermes revisa o PRD **antes** de apresentar ao usuário. PRD é documento de decisão: erro nele
custa caro depois, porque vira contrato de escopo.

## Checklist antes de enviar

- [ ] **Timeline no tempo** — sistema de gestão precisa de prazo, etapa, calendário ou Gantt.
      Se não houver, perguntar se entra no MVP.
- [ ] **Categorização** — interno vs. cliente, `type`/`category` no schema. Em consultoria é
      necessidade operacional básica.
- [ ] **O schema resolve o problema real?** As entidades (Task, Project…) cobrem o vocabulário
      do dia a dia da equipe, não só o conceito abstrato.
- [ ] **Consistência interna** — resumo executivo, features do MVP e critérios de aceite usam a
      mesma contagem de views? Números batem? Feature citada no resumo aparece na tabela?
- [ ] **Nomes e versão** — cabeçalho com versão e data atuais; histórico de atualizações presente.

Se falhar em qualquer item, corrigir antes de mandar.

## Ciclo de revisão (depois da primeira entrega)

Quando o usuário pede ajuste, aplicar **em todas as seções impactadas** — não só na tabela de
features. Este é o erro clássico: resumo, riscos e anexos ficam inconsistentes.

- [ ] Resumo executivo reflete o novo conjunto? Contagem de views bate?
- [ ] Features do MVP (tabela) atualizadas?
- [ ] Fora do MVP — item movido para V2/futuro registrado?
- [ ] Critérios de aceite das novas features?
- [ ] Features pós-MVP — renumeradas?
- [ ] Riscos — menções a escopo, contagem, features ainda válidas?
- [ ] Anexo de decisões — novas decisões; status das antigas atualizado?
- [ ] Cabeçalho — versão bumpada (v1.0 → v1.1)?
- [ ] Histórico de atualizações — entrada da revisão?
- [ ] Consistência numérica — "4 views" vs "5 views" em todo o documento?

## Sync com Google Docs — a direção é uma só

Depois que o doc é compartilhado, ele é a **fonte da verdade colaborativa**. O fluxo é
**Google Docs → markdown local**, nunca o contrário.

1. Extrair texto via Docs API (`documents.get` → `body.content` → `paragraph.elements.textRun`).
2. Comparar com o markdown local: seções novas, renomeações, decisões.
3. Aplicar no local preservando tabelas, negrito e listas.
4. **Não sobrescrever o doc** — inserir markdown puro destrói a formatação feita pela equipe.
5. Registrar no histórico com autor "Equipe ID (edição no Google Docs)".

Código, fluxo de OAuth e padrões de edição: `references/google-docs-prd-delivery.md`.
