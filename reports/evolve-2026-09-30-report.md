# Report Evolve — 2026-09-30

## Resultado
- **106 → 107 skills**, 0 merges, 0 deletes, 0 órfãos.
- Nova: `business/proposta-sergipetec-documento` (doc A4 P,D&I SergipeTec, Lei 14.133/2021).
- Arestas: 135 → 139 (+2 Similar, +2 Uses).

## Pares reavaliados (5, todos mantidos separados)
1. proposta-sergipetec-documento × elaboracao-proposta-comercial — doc do Parque (proponente
   SergipeTec, crivo PGE, art. 72) vs deck comercial da ID (proponente ID). Fronteira jurídica,
   não sobreposição. Similar cobre.
2. proposta-sergipetec-documento × proposta-biotechse — documento-resposta-a-parecer vs
   HTML+minuta comercial. Conectadas via elaboracao; sem merge direto.
3. proposta-sergipetec-documento × analise-contratual — art. 72/75-XV como requisito de
   conteúdo do documento, não análise de minuta. Similar cobre.
4. proposta-sergipetec-documento × revisao-de-proposta-existente — resposta-a-parecer
   (estrutura A→Anexo A) vs revisão deliberada preservando resto.
5. proposta-biotechse × elaboracao-proposta-comercial — revalidado (24–29/09), mantido.

## Métricas
- Tabela index: 107 linhas. Grafo: 107 nós / 139 arestas / 0 órfãos.
- Audit: tracked 107/107 type+timestamp OK; 0 block-scalar/too-long/trigger-missing.
- Drift 13ª ocorrência contido (guard bloqueia rm em lote no cron; grafo imune, lê só index).

## Git
- Commit: update+evolve 2026-09-30 (index.md + log.md + proposta-sergipetec-documento + reports).
- Push: via push-skills-mercurio.sh (ver seção PUSH da resposta).
