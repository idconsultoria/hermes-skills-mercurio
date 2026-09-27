# Relatório evolve — 2026-09-27

## Resultado
106 skills MECE estáveis, **0 merges, 0 deletes, 0 splits, 0 órfãos**.
Arestas 134 mantidas (73 Similar + 61 Uses, 0 descartadas).
Grafo: 106 nós / 134 arestas / 0 órfãos via generate_catalog_graph.py.

## Pares reavaliados (7, todos mantidos)
- `emissao-nfse` × `motor-nfse-id`: emissão operacional vs living-state do motor — workflows distintos.
- `auxiliar-adm-id` × `gestao-financeira-id`: auxiliar geral vs backfill de extrato — distintos; Similar cobre.
- `emissao-nfse` × `inter-api-id-consultoria`: a nova trava de cobrança (§5, "só cobra após extrato") reforça a separação produtor-vs-fonte — Uses bidirecional já cobre.
- `auxiliar-adm-id` × `google-workspace`: ponte operacional vs ferramenta — distintos.
- `formalizacao-acordo-cliente` × `elaboracao-proposta-comercial`: revalidado 24/09 — mantidos.
- `local-postgres-sandbox` × `postgres-sandbox-verification`: revalidado 26/09 — mantidos.
- `hermes-agent-replication` × `hermes-environment-replication`: revalidado 26/09 — mantidos.

## MECE
Ciclo sem mutação estrutural: o update trouxe conteúdo procedural (cobrança SM1) dentro de skills existentes, sem sobreposição nova. Depth-1 completo adiado (não cabe no cron 3 min — pitfall 12/08); última inferência profunda 23–24/09 + manual 26/09.

## Prune drift
10ª ocorrência ADIADA (guard bloqueia rm em lote no cron — `.locks/` + 6 DESCRIPTION.md canônicos `apple/creative/media/note-taking/social-media/web`, formato canônico sem type/timestamp). Grafo imune (lê só index).

## Git
- Plano: reports/evolve-2026-09-27-0200.md
- Este relatório: reports/evolve-2026-09-27-report.md
- Grafo: skills_graph.html (69,789 bytes) + graph_data.json (106/134)

## Diff do ciclo
```
update: commita cobrança SM1 + fix unicode/ponteiros, sync index (106 estáveis) (9228cf5)
evolve: 106 MECE, 0 merges, grafo 106/134/0 (este commit)
```
