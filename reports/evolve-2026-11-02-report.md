# Relatório — ciclo de consolidação 2026-11-02 (semanal)

## Estado inicial → final

| Métrica | Início | Fim |
|---|---|---|
| Skills no index.md | 165 | **167** |
| SKILL.md no disco | 166 | **167** |
| Drift disco×índice | 1 (nda) + 1 dir sem SKILL.md (fathom) | **0** |
| Arestas do grafo | 268 | **276** |
| Órfãos | 1 (openhue, justificado) | **1 (openhue, justificado)** |
| Categoria/index.md com gap | 9 arquivos (42 entradas) + 2 categorias sem index | **0** |
| `type`/`timestamp` ausentes | 0 | **0** |
| Block scalar / plain scalar / sumário >85 | 0 / 0 / 0 | **0** |
| Resumo drift (index × SKILL.md) | 0 | **0** |

## Skills adicionadas (2)

- `legal/nda-confidencialidade-id` (Orchestrator) — NDA unilateral de acesso a código de cliente:
  esqueleto de 13 cláusulas (objeto fechado, vedação de IA pública, incidente em 24 h, PI do
  cliente, "no estado em que se encontra", LGPD como operadora, sigilo 5 anos + indeterminado para
  código-fonte, devolução em 10 dias, multa sugerida R$ 20.000, foro Aracaju/SE), entrega rápida
  com placeholders nomeados e blocos de pendência por dono. Estava no disco desde 30/10 sem
  indexação.
- `productivity/fathom` (ToolIntegration) — **criada neste ciclo** a partir do shim
  `scripts/fathom_api.py` (recriado em 27/10 depois que a skill original desapareceu e o
  `phronesis_weekly.py` quebrou em `from fathom_api import FathomClient`). Documenta auth
  (`FATHOM_API_KEY` em `.secrets/fathom.env`, header `X-Api-Key`), `/meetings` e
  `/meetings/{id}`, flags de peso (`include_transcript` domina o payload), cursor, backoff
  4 tentativas e não-retry em 401/403/404. O diretório tinha script e `__pycache__` sem SKILL.md —
  opção de commitar script solto foi rejeitada (diretório malformado no catálogo).

## Deleções / merges

Nenhum. Nenhum par passou o critério de merge — os 8 pares avaliados têm fluxo e toolchain
distintos (ver plano `evolve-2026-11-02-0500.md`).

## Relações (+8)

- Similar (6): `nda-confidencialidade-id` → contratos-justos-id, analise-contratual,
  direito-empresarial-brasileiro, formalizacao-acordo-cliente; `fathom` → reunioes-diarizadas,
  meeting-action-items.
- Similar (1): `gestao-financeira-id` → invoice-chase (rotina ID de cobrança recorrente × estratégia
  genérica de ledger estrangeiro — vizinhos, não substitutos).
- Uses (1): `nda-confidencialidade-id` → md-to-timbrado-id (entrega em timbrado Google Docs).

Correção de classificação: `nda`→`formalizacao-acordo-cliente` foi proposto inicialmente como
`uses` e movido para `similar` (o NDA não usa o e-mail de acordo fechado), removendo a duplicata.

## Órfãos

- `openhue` — mantido órfão com justificativa (única skill de smart-home do fork; sem par
  semântico, sem motivo para deletar). Mesmo status de 26/10.

## Trabalho ID commitado (não é curadoria, é o diff da semana)

- `business/gestao-financeira-id`: nova `references/cobranca-diaria-cliente.md` — cobrança
  recorrente de parcela em atraso (3 fontes antes de cobrar, thread da NFS-e, gate financeiro
  no extrato com `valor_min_credito`, dia útil, rotação de 8 textos, escalonamento).
- `business/formalizacao-acordo-cliente`: `references/pedido-de-dados-ao-cliente.md`.
- `legal/contrato-sustentacao-sla`: `scripts/pos_passe_contrato.py` + 71 linhas.
- `productivity/edicao-incremental-de-gdoc`: `references/edicao-cirurgica-e-leitura-api.md`.
- `infrastructure/moodle-id-operacoes` (+69), `business/auxiliar-adm-id` (+19),
  `business/contratos-justos-id` (+36), `productivity/md-to-timbrado-id` (+17),
  `business/emissao-nfse` (+ref cobranca-nfse-clientes).

## Verificação

```
SKILL.md files: 167
MISSING type: none | INVALID type: none | MISSING timestamp: none
BLOCK SCALAR: none | UNQUOTED: none | SUMMARY >85 or ...: none
index rows: 167 | disk skills: 167 | disk-not-index: none | index-not-disk: none
relations: 276 | self-relations: none | dangling targets: none
categoria/index.md gaps: 0
graph: 167 nós / 276 arestas / 1 órfão justificado
```

## Descrições de uma linha

Mantida a decisão editorial de 26/10/2026: 88 skills seguem com descrição de uma linha
(auto-contida) e não foram expandidas em lote — expansão mecânica produz parágrafo genérico sem
lastro. Backlog oportunístico: expandir quando a skill for editada por outro motivo.
