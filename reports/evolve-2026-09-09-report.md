# Relatório evolve — 2026-09-09

## Estado inicial → final
- Skills: 94 → 94 (estável; disco 94 = index 94 = grafo 94 nós)
- Arestas: 118 → 118 (63 Similar + 55 Uses, 0 descartadas)
- Órfãos: 0 → 0

## Update (resumo do que foi feito antes do evolve)
- **Prune drift canônico (5ª ocorrência):** 9 paths untracked removidos via `git clean -fd`
  (20 arquivos): `apple/`, `creative/`, `media/`, `note-taking/`, `web/` (só DESCRIPTION.md);
  `research/rss-feeds/`, `social-media/` (+DESCRIPTION.md), `software-development/github/`,
  `software-development/codebase-inspection/`. Evidência de drift (não instalação deliberada):
  mtime bulk idêntico 08/09 02:34, formato canônico (`metadata.hermes`, sem `type:`/`timestamp:`),
  duplicatas de categoria tracked (`github/codebase-inspection` já existe no fork),
  zero referências a partir de skills tracked, zero entradas no `.curator_ledger.jsonl`.
- **Trabalho legítimo preservado e indexado:** `id-comunicacao-multiusuario` (gateway JSON
  autoritativo + Maxwell confirmado — sessão curator 08/09) e `proposta-biotechse`
  (modelo-v8 + templates v2–v8, sessão agente 09/09; 8 arquivos novos em stage).
- **Fix aplicado:** `proposta-biotechse` description colapsada single-line 170 chars →
  formato two-part (sumário 52 chars + trigger `Carregue esta skill quando` + blank line);
  index.md Descrição sincronizada (`HTML v5` → `HTML + minuta`).
- **Auditoria:** compliant 44→45/94 (49 single-line = padrão deliberado do fork);
  `--drift` 0; `type:`/`timestamp:` 94/94 OK; `|- \`` 0 ocorrências.
- **`.gitignore`:** adicionado `.curator_ledger.jsonl` (artefato runtime, precedente `.curator_backups/`).

## Evolve — merges/deletes
- 0 merges, 0 deletes. Pares próximos (`proposta-biotechse`×`elaboracao-proposta-comercial`,
  ×`brand-design-system-html`; `id-comunicacao-multiusuario`×`messaging-platforms`) reavaliados:
  workflows distintos, relações existentes mantidas. Nenhum fato novo desde 07/09.
- Depth-1 completo adiado (não cabe no cron — pitfall 12/08); próxima janela manual ou job dedicado.

## Órfãos
- 0 (confirmado pelo gerador: "ÓRFÃOS (0 arestas) no catálogo: 0").

## Git
- Commit único `update+evolve` (convenção 03–07/09) + push via `push-skills-mercurio.sh`.
- Arquivos: 3 modificados, 8 novos (proposta-biotechse), index.md (1 linha),
  `.gitignore` (1 linha), reports (2 novos), log.md (3 entradas), grafo regenerado.
