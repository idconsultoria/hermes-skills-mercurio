# Report evolve 2026-10-03 (fork Mercúrio)

## Estado inicial → final
- Skills: 114 → 114 (0 merges, 0 deletes, 0 novas).
- Arestas: 174 → 179 (+5, 0 descartadas).
- Órfãos: 0 → 0. Grafo: 114 nós / 179 arestas / 0 órfãos via `scripts/generate_catalog_graph.py`.

## Depth-1 em lote: FALHA operacional
- 3 subagentes paralelos via `delegate_task`: 2 timeouts (600s, ~26-28 API calls cada) + 1 erro de provider (resposta inválida após 3 retries).
- Nenhum relatório produzido; nenhum resíduo em disco (verificado `ls _rel_batch*.md`).
- Lição: depth-1 paralelo não cabe no orçamento do cron (confirma pitfall da skill). Fallback: evolve manual focado.

## Evolve manual (depth-1 central, 5 arestas validadas lendo ambos os SKILL.md)
1. `auxiliar-adm-id` → `inter-api-id-consultoria` (Similar) — fluxo mensal de coleta usa extrato do Inter.
2. `gestao-financeira-id` → `xlsx` (Uses) — backfill e relatórios manipulam xlsx/csv além do Sheets.
3. `meeting-action-items` → `document-to-action-items` (Uses) — decisões citadas alimentam extração de obrigações/prazos.
4. `reunioes-diarizadas` → `meeting-action-items` (Similar) — encaminhamentos de diarizadas PT-BR vs decisões citadas EN; fluxos distintos, só Similar.
5. `md-to-timbrado-id` → `html-to-pdf-chromium` (Uses) — fallback de fidelidade antes do Docs-nativo (receita 02/10).

## MECE
- Nenhum merge/delete proposto: todos os pares reavaliados têm workflows distintos.
- Duplicata intencional auxiliar-adm × gestao-financeira (reconciliação Symplexis) mantida — documentada no update 02/10.

## Verificações
- `grep (reason:` vazio; `grep |- \`` 0; grafo 0 órfãos, 0 descartadas.
