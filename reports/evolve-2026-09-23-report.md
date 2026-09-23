# Evolve — relatório 2026-09-23 (fork Mercúrio 94→104)

## Estado inicial vs final
| Métrica | Antes (b93dc5b, 10/09) | Depois |
|---|---|---|
| Skills (disco) | 94 | 104 (+10 ID legítimas 11–22/09) |
| Skills (index) | 94 | 104 |
| Categorias | 11 | 12 (+creative) |
| Arestas | 118 (63 Similar + 55 Uses) | 131 (+4 Similar, +9 Uses) |
| Órfãos | 0 | 0 (humanizer ligada mid-cycle) |
| Bad targets | 0 | 0 |
| Compliant (audit) | 45/94 | 45/104 (59 single-line = padrão deliberado do fork) |
| Drift Resumo | 0 | 0 |
| Type/timestamp | 94/94 | 104/104 OK |

## Skills indexadas (+10, 0 merges, 0 deletes)
| Skill | Type | Por que separada (MECE) |
|---|---|---|
| business/formalizacao-acordo-cliente | Orchestrator | Fecha negociação por e-mail com gates; elaboracao cria proposta do zero |
| business/negotiation | Orchestrator | Framework Voss (empatia tática) — precede e alimenta a formalização |
| business/painel-metas-id | Reference | Dashboard + slide Phronesis; gestao-financeira-id é a planilha-fonte |
| business/revisao-de-proposta-existente | Orchestrator | Cirurgia em doc entregue (copiar+editar); nunca regenerar |
| productivity/html-deck-to-pptx | ToolIntegration | Deck→PPTX editável; HTML→PDF é outro pipeline |
| productivity/reunioes-diarizadas | Orchestrator | Minera transcrição ruidosa; meeting-action-items parte de ata limpa |
| productivity/revisao-entrega-cliente | Orchestrator | Audita peça (ler+reportar); document-to-action-items extrai tarefas |
| creative/humanizer | Creative | Voz/texto EN anti-AI-slop; usa process-augmentation-pipeline |
| infrastructure/stack2-mesh-failback | Runbook | Runbook HA mesh; usa cron-dispatch como ferramenta |
| software-development/skills-library-audit | Research | Triagem de portabilidade; repo-curator governa o ciclo |

## Fixes de conformidade (pré-index)
- revisao-de-proposta-existente: += `timestamp: 2026-09-17`
- html-deck-to-pptx: description unquoted→quoted + category/type/timestamp
- humanizer: += category/type (Creative)/timestamp
- emissao-nfse: description 62→78 chars (≤85 OK) + linha da tabela sync

## Trabalho ID preservado e commitado (14 modified + refs/scripts novos)
NFS-e SergipeTec (auxiliar-adm-id + cobranca-nfse-clientes.md), Symplexis vínculo por transação (gestao-financeira-id), monitor gate + drift pin/unpin (cron-dispatch, inference-config), timbrado SergipeTec (md-to-timbrado-id + scripts), extrair_fontes.py, dossiês parceria/produto, STT hardening + credential diagnosis refs, extrair_geo/pptx scripts.

## Não feito (justificado)
- Prune 7ª ocorrência (6 DESCRIPTION.md canônicos): guard do cron bloqueia `rm` em lote (2 tentativas bloqueadas); grafo imune (lê só index). Deixar para sessão interativa.
- Offload: SKIP (memória não injetada no cron).
- Depth-1 via subagentes: provider Codex sem resposta (2 falhas); depth-1 manual executado no lugar.
- Merges/deletes: 0 candidatos — pares próximos têm workflows distintos.

## Git
- Commit único `update+evolve 2026-09-23` (ciclo combinado: update indexou + evolve relacionou; mesma mudança lógica).
- Arquivos: index.md, 3 SKILL.md fix, 14 modified ID, ~25 untracked ID, reports ×2, grafo + JSON.
- Excluído do commit: .locks/ (lixo), 6 DESCRIPTION.md drift (prune pendente).
- Push via /opt/data/scripts/push-skills-mercurio.sh.
