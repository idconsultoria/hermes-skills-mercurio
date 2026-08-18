# Skills — Mercúrio (ID Consultoria)

Catálogo consolidado de skills do **Hermes · Mercúrio**, rama dedicada à **ID Consultoria**
(consultoria de gestão, augmentação de processos e produtos para PMEs). Fork independente
de `gustavomello9600/hermes-agent-skills` (`hermes-skills-mercurio`), **sem sincronia de
upstream**, já pruneado para foco 100% ID e com informação pessoal do operador removida.

Formatos: [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

**Total: 41 skills** em 7 categorias.

---

## business — Consultoria de negócio

| Skill | Type | Descrição |
|---|---|---|
| `analise-contratual` | Reference | Análise de contratos/minutas — subcontratação, LGPD, compliance. |
| `elaboracao-proposta-comercial` | Orchestrator | Propostas comerciais da ID — do contexto do cliente à proposta fechada. |
| `planejamento-estrategico-2h` | Orchestrator | Planejamento estratégico em 2h — EOS V/TO + One-Page Plan. |
| `proposta-comercial-consultoria` | Orchestrator | Proposta comercial de consultoria — princípios, pricing e estrutura. |
| `valuation-consultivo` | Orchestrator | Valuation consultivo de startup early-stage — rNPV, âncoras. |

## research — Pesquisa e augmentação

| Skill | Type | Descrição |
|---|---|---|
| `augmentacao-query` | Research | Busca semântica nas 97 soluções de augmentação de processos. |
| `augmentation-process-design` | Research | Design, research e curadoria de soluções de augmentação de processos. |
| `competitor-news-monitor` | Research | Monitorar concorrentes/empresas nomeadas por notícias relevantes (digests citados). |
| `deep-research` | Research | Pesquisa profunda multi-agente — decompõe, despacha, agrega com citações. |
| `grounded-citations` | ToolIntegration | Fundamentar respostas/documentos em fontes citadas e verificáveis. |
| `market-research-synthesis` | Research | Relatórios de análise de mercado — personas, jornadas, expectativas. |
| `systematic-research` | Research | Pesquisa profunda single-agent via URLs diretas. |
| `user-interview` | Research | Protocolo de entrevista de usuário/proxy estruturado para pesquisa de produto. |

## productivity — Documentos e entrega

| Skill | Type | Descrição |
|---|---|---|
| `document-to-action-items` | Orchestrator | Extrair obrigações/prazos/tarefas citadas de documentos. |
| `docx` | ToolIntegration | Criar, ler, editar documentos Word (.docx) e templates. |
| `google-docs-formatting` | ToolIntegration | Formatar Google Docs/Sheets via REST API (markdown, chips). |
| `google-sheets-automation` | ToolIntegration | Polir Google Sheets via API (dropdowns, fórmulas, KPIs). |
| `google-workspace` | ToolIntegration | Gmail/Drive/Docs/Sheets via gws CLI — OAuth2 (conta da ID). |
| `html-pdf-fidelity` | Orchestrator | HTML→PDF idêntico ao browser — fontes, layout, 1 página. |
| `html-report-hermes` | Template | Relatórios de pesquisa como HTML dark com gráficos SVG. |
| `html-to-pdf-chromium` | Template | HTML→PDF via Chromium headless — fallback ARM64. |
| `meeting-action-items` | Orchestrator | Notas de reunião → decisões citadas, donos, tickets. |
| `notion` | ToolIntegration | API Notion + CLI `ntn` — páginas, databases, import markdown. |
| `pdf` | ToolIntegration | Criar, mesclar, dividir, preencher e proteger PDFs. |
| `pdf-to-html` | ToolIntegration | PDF→HTML: gotchas de extração Type3/Figma + rebuild semântico. |
| `relatorio-de-custos` | Template | Relatórios de custo de projetos multi-agente com tokens reais. |
| `xlsx` | ToolIntegration | Criar, ler, editar planilhas Excel (.xlsx) e CSVs. |

## email — Correio da ID

| Skill | Type | Descrição |
|---|---|---|
| `email-inbox-triage` | Orchestrator | Triagem de inbox: priorizar threads, rascunhar respostas seguras. |

## software-development — Produto e processo

| Skill | Type | Descrição |
|---|---|---|
| `backlog-and-sprint` | Orchestrator | Gestão de backlog e execução de Sprint para iteração de produto. |
| `bpmn-diagram-renderer` | Template | Renderizar diagramas BPMN 2.0 (XML) para SVG/PNG via bpmn-js. |
| `dedalo-squad` | Orchestrator | Pipeline Dédalo Squad — mapeamento de processos com POPs. |
| `ideation-drilling` | Orchestrator | Ideação de produto (Fase 1) — refinar ideias brutas. |
| `pipeline-educacional` | Orchestrator | Pipeline de produto educacional — concepção pedagógica a entrega. |
| `process-augmentation-pipeline` | Orchestrator | Pipeline da ID: análise de processos, brainstorm e augmentação. |
| `skills-repo-curator` | Orchestrator | Gestão do repo de skills — ciclos de consolidação, MECE, OKF. |

## autonomous-ai-agents — Agentes & produto

| Skill | Type | Descrição |
|---|---|---|
| `autonomous-ai-agents` | Orchestrator | Delegar tarefas de codificação a agentes AI via Hermes (orquestração). |
| `hermes-agent` | Reference | Configurar/usar o Hermes Agent — setup, profiles, skills, CLI. |
| `messaging-platforms` | Reference | Mensageria cross-platform — Telegram, IDs, entrega de arquivos. |
| `pi-agent-coordination` | ToolIntegration | Invocar Pi Agent localmente via Hermes (hierarquia provider/model). |
| `product-pipeline` | Orchestrator | Pipeline multi-agente de produto — ideia a MVP via sprints. |

## infrastructure — Integrações de entrega

| Skill | Type | Descrição |
|---|---|---|
| `whatsapp-baileys-integration` | ToolIntegration | Integrar WhatsApp em Python via Baileys — lifecycle, QR, enums. |

---

## Relações e manutenção

- **index.md** é território de agente LLM (nunca scripts) — atualizado por `read_file`/`patch`/`write_file`.
- **log.md** é append-only com prefixos `update|evolve|offload`.
- Ciclo: `update → log → commit → evolve → log → offload → commit → push`.
- Fork **não** sincroniza com upstream; evoluir por conta própria nesta rama.
