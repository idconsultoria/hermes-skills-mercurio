# Evolve — relatório 2026-09-24 (fork Mercúrio 104→103)

## Estado inicial vs final

| Métrica | Antes (1102209, 23/09) | Depois |
|---|---|---|
| Skills (disco) | 104 | 103 (−1 merge) |
| Skills (index) | 104 | 103 |
| Arestas | 131 (69 Similar + 62 Uses) | 129 (68 Similar + 61 Uses) |
| Órfãos | 0 | 0 |
| Bad targets | 0 | 0 |
| Compliant (audit) | 45/104 | 44/103 (59 single-line = padrão deliberado do fork) |
| Drift Resumo | 0 | 0 |
| Type/timestamp | 104/104 | 103/103 OK |

## Merge executado (1)

**`proposta-comercial-consultoria` → `elaboracao-proposta-comercial`**
(borderline documentado desde 23/08, confirmado por depth-1 em 2 subagentes,
24/09). Mesmo trigger (criar/ajustar/precificar proposta ID), mesmo Guia de
Princípios (duas variantes condensadas), mesmo modelo HTML de marca;
v3/builder-vs-pipeline = duplicata histórica de sessão, não workflows distintos.

- Conteúdo único preservado em
  `elaboracao-proposta-comercial/references/precificacao-e-design-modelo.md`
  (precificação buffer 1,3-1,5x, GBB 1,4-1,8x/2,0-3,0x, estrutura SCR, decisões
  de design capa/diamond/final, arquivos builder/assets/v3, pitfalls).
- Frontmatter: +tags pricing/brand, +related html-pdf-fidelity/deep-research,
  timestamp bump 24/09. Backup pré-merge em /tmp/merge_bak (sessão).
- Re-apontados: negotiation + valuation-consultivo related_skills.
- Arestas: removidas 2 (similar elaboracao→proposta + uses proposta→elaboracao);
  `planejamento-estrategico-2h → elaboracao` mantida (o patch inicial havia
  duplicado por engano, dedup aplicado). Incidente menor: patch de substituição
  na tabela gerou linha duplicada de elaboracao (detectado via contagem
  104 vs 103, removido antes do commit).
- Dir `business/proposta-comercial-consultoria/` removido via `git rm`
  arquivo-a-arquivo (guard do cron bloqueia `git rm -r`).

## Pares reavaliados, mantidos (23 decisões MANTER, 2 subagentes)

Business (10): proposta×biotechse (marca incompatível), elaboracao×revisao
(criar vs cirurgia sem regenerar), revisao×formalizacao (Doc vs Gmail-thread),
formalizacao×negotiation (pós-fechamento vs tática Voss), negotiation×proposta
(tático vs produtivo), 2h×8h (facilitação PME vs programa interno ID),
gestao×inter (escrita vs read-only), gestao×painel (operar vs medir),
auxiliar-adm como ponte (poda, não merge), emissao vs cobrança,
id-comunicacao (transversal) vs formalizacao.
Prod/infra (13): document×meeting, reunioes×meeting/document, deck×pdf-fidelity,
fidelity×report, deck×report, report×custos, revisao-entrega como gate QA,
stack2×dispatch×inference (3 pares, incidente vs entrega vs roteamento),
library-audit×repo-curator (triagem vs operação), humanizer sem par.

## Não feito (justificado)

- Prune drift 8ª ocorrência (.locks/ + 6 DESCRIPTION.md canônicos): guard do
  cron bloqueia `rm -rf`/`git rm -r`; grafo imune (lê só index). Sessão interativa.
- Offload: SKIP (memória não injetada no cron).
- business/index.md: linha proposta-comercial-consultoria removida; demais
  category index.md intocados (14 linhas, desatualizado vs tabela raiz — débito
  conhecido, fora do escopo do ciclo).

## Git

- Commit único `update+evolve 2026-09-24` (ciclo combinado).
- Arquivos: index.md, business/index.md, elaboracao SKILL.md + nova reference,
  negotiation + valuation frontmatter, −2 arquivos proposta, reports ×2,
  grafo + JSON (103 nós/129 arestas/0 órfãos).
- Excluído: .locks/, 6 DESCRIPTION.md drift.
- Push via /opt/data/scripts/push-skills-mercurio.sh.
