# Skills — Mercúrio (ID Consultoria)

Catálogo consolidado de skills do **Hermes · Mercúrio**, rama dedicada à **ID Consultoria**
(consultoria de gestão, augmentação de processos e produtos para PMEs). Fork independente
de `gustavomello9600/hermes-agent-skills` (`hermes-skills-mercurio`), **sem sincronia de
upstream**, pruneado para foco 100% ID + skills operacionais da ID (NFS-e, Inter, financeiro,
timbrado, devops ArtemisHub). Fork real criado em `idconsultoria/hermes-skills-mercurio` (23/08).

Formatos: [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

**Total: 85 skills** em 11 categorias.

---

## business — Consultoria de negócio

| Skill | Type | Descrição |
|---|---|---|
| `analise-contratual` | Reference | Análise de contratos/minutas — subcontratação, LGPD, compliance. |
| `auxiliar-adm-id` | Orchestrator | Auxiliar admin da ID: contratos, planilhas, NFS-e, Drive. |
| `elaboracao-proposta-comercial` | Orchestrator | Propostas comerciais da ID — do contexto do cliente à proposta fechada. |
| `emissao-nfse` | ToolIntegration | Emitir NFS-e/NF-e da ID via motor nfelib (NFS-e Nacional). |
| `gestao-financeira-id` | Reference | Operar planilhas/Google da ID e fazer backfill de extrato. |
| `inter-api-id-consultoria` | ToolIntegration | Consultar extrato/saldo da conta Inter da ID. |
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
| `id-papel-timbrado` | Reference | Use ao criar doc da ID com timbrado no Google Docs. |
| `md-to-timbrado-id` | ToolIntegration | Gerar Google Doc no timbrado da ID a partir de Markdown. |
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
| `baas-offline-migration` | Orchestrator | Migrar SPA que usa Supabase p/ backend próprio offline. |
| `backlog-and-sprint` | Orchestrator | Gestão de backlog e execução de Sprint para iteração de produto. |
| `bpmn-diagram-renderer` | Template | Renderizar diagramas BPMN 2.0 (XML) para SVG/PNG via bpmn-js. |
| `dedalo-squad` | Orchestrator | Pipeline Dédalo Squad — mapeamento de processos com POPs. |
| `dogfood` | Research | Exploratory QA of web apps: find bugs, evidence, reports. |
| `hermes-agent-skill-authoring` | Template | Author in-repo SKILL.md files: frontmatter and structure. |
| `ideation-drilling` | Orchestrator | Ideação de produto (Fase 1) — refinar ideias brutas. |
| `inspecting-hermes-desktop-dom` | ToolIntegration | Read the live Hermes desktop DOM/CSS over CDP. |
| `internal-python-job-executor` | ToolIntegration | Executor interno Python p/ pipeline no backend FastAPI. |
| `local-postgres-sandbox` | ToolIntegration | Verify DB behavior via local Postgres sandbox from app dump. |
| `motor-nfse-id` | Orchestrator | Resume/update the ID NFS-e emission motor (living state). |
| `node-inspect-debugger` | ToolIntegration | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| `pipeline-educacional` | Orchestrator | Pipeline de produto educacional — concepção pedagógica a entrega. |
| `plan` | Template | Write a markdown plan to .hermes/plans/; no execution. |
| `postgres-dump-restore` | ToolIntegration | Seed Postgres de dump; evita falha 'unsupported version'. |
| `postgres-sandbox-verification` | ToolIntegration | Verify features really persist against a throwaway Postgres. |
| `process-augmentation-pipeline` | Orchestrator | Pipeline da ID: análise de processos, brainstorm e augmentação. |
| `python-debugpy` | ToolIntegration | Debug Python: pdb REPL + debugpy remote (DAP). |
| `react-fastapi-debugging` | ToolIntegration | Patch fallback silencioso e bugs de UI em app React+FastAPI. |
| `requesting-code-review` | Orchestrator | Pre-commit review: security scan, quality gates, auto-fix. |
| `simplify-code` | Orchestrator | Parallel 4-agent cleanup of recent code changes. |
| `skills-repo-curator` | Orchestrator | Gestão do repo de skills — ciclos de consolidação, MECE, OKF. |
| `spike` | Research | Throwaway experiments to validate an idea before build. |
| `static-spa-vercel` | Orchestrator | Build static SPA prototypes and deploy to Vercel. |
| `supabase-to-selfhost` | Orchestrator | Use ao abandonar Supabase: backend próprio offline único. |
| `systematic-debugging` | ToolIntegration | 4-phase root cause debugging: understand bugs before fixing. |
| `test-driven-development` | Template | TDD: enforce RED-GREEN-REFACTOR, tests before code. |

## autonomous-ai-agents — Agentes & produto

| Skill | Type | Descrição |
|---|---|---|
| `autonomous-ai-agents` | Orchestrator | Delegar tarefas de codificação a agentes AI via Hermes (orquestração). |
| `claude-code` | ToolIntegration | Delegate coding to Claude Code CLI (features, PRs). |
| `codex` | ToolIntegration | Delegate coding to OpenAI Codex CLI (features, PRs). |
| `computer-use` | ToolIntegration | Drive the desktop in the background without stealing focus. |
| `hermes-agent` | Reference | Configurar/usar o Hermes Agent — setup, profiles, skills, CLI. |
| `hermes-environment-replication` | Orchestrator | Replicar instância Hermes viva p/ nova VM. |
| `merge-reconciler` | Orchestrator | Neutral third-party resolution of agent merge conflicts. |
| `messaging-platforms` | Reference | Mensageria cross-platform — Telegram, IDs, entrega de arquivos. |
| `opencode` | ToolIntegration | Delegate coding to OpenCode CLI (features, PR review). |
| `pi-agent-coordination` | ToolIntegration | Invocar Pi Agent localmente via Hermes (hierarquia provider/model). |
| `product-pipeline` | Orchestrator | Pipeline multi-agente de produto — ideia a MVP via sprints. |

## infrastructure — Integrações de entrega

| Skill | Type | Descrição |
|---|---|---|
| `hermes-agent-replication` | Method | Replicar instância Hermes (rama ID) numa VM nova. |
| `whatsapp-baileys-integration` | ToolIntegration | Integrar WhatsApp em Python via Baileys — lifecycle, QR, enums. |

## cicd-oracle-preview — Deploy & preview

| Skill | Type | Descrição |
|---|---|---|
| `cicd-oracle-preview` | Orchestrator | Replicar CI/CD: GHCR arm64, deploy SSH, preview por PR. |
| `devops-artemishub` | Orchestrator | Operar/deployar o ArtemisHub no Oracle host. |
| `git-fork-isolation` | Orchestrator | Isolar fork de rama do canônico com push guardado seguro. |

## devops — Revisão de entrega

| Skill | Type | Descrição |
|---|---|---|
| `sdlc-review` | Orchestrator | Review Kanban handoffs and route verified outcomes. |

## github — Workflows GitHub

| Skill | Type | Descrição |
|---|---|---|
| `codebase-inspection` | ToolIntegration | Inspect codebases w/ pygount: LOC, languages, ratios. |
| `github-auth` | ToolIntegration | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. |
| `github-code-review` | ToolIntegration | Review PRs: diffs, inline comments via gh or REST. |
| `github-issue-to-pr` | Orchestrator | Carry a GitHub issue to a verified PR with honest CI state. |
| `github-issues` | ToolIntegration | Create, triage, label, assign GitHub issues via gh or REST. |
| `github-pr-workflow` | Orchestrator | GitHub PR lifecycle: branch, commit, open, CI, merge. |
| `github-repo-management` | Orchestrator | Clone/create/fork repos; manage remotes, releases. |

---

## Relações entre skills (curadoria evolve 2026-08-23)

Relações semânticas do catálogo. Formato `type` → `alvo` (similar = bidirecional; uses = A usa B).

Similar:
- `elaboracao-proposta-comercial` → `proposta-comercial-consultoria`
- `deep-research` → `systematic-research`
- `deep-research` → `market-research-synthesis`
- `augmentation-process-design` → `augmentacao-query`
- `augmentation-process-design` → `process-augmentation-pipeline`
- `process-augmentation-pipeline` → `dedalo-squad`
- `pipeline-educacional` → `process-augmentation-pipeline`
- `product-pipeline` → `backlog-and-sprint`
- `dedalo-squad` → `bpmn-diagram-renderer`
- `document-to-action-items` → `meeting-action-items`
- `pdf` → `pdf-to-html`
- `html-pdf-fidelity` → `html-to-pdf-chromium`
- `html-report-hermes` → `relatorio-de-custos`
- `google-docs-formatting` → `google-sheets-automation`
- `google-docs-formatting` → `notion`
- `xlsx` → `google-sheets-automation`
- `docx` → `xlsx`
- `valuation-consultivo` → `analise-contratual`
- `planejamento-estrategico-2h` → `proposta-comercial-consultoria`
- `competitor-news-monitor` → `deep-research`
- `user-interview` → `market-research-synthesis`
- `hermes-agent` → `messaging-platforms`
- `autonomous-ai-agents` → `pi-agent-coordination`
- `whatsapp-baileys-integration` → `messaging-platforms`
- `skills-repo-curator` → `hermes-agent`
- `claude-code` → `codex`
- `codex` → `opencode`
- `systematic-debugging` → `test-driven-development`
- `test-driven-development` → `requesting-code-review`
- `auxiliar-adm-id` → `gestao-financeira-id`
- `emissao-nfse` → `inter-api-id-consultoria`
- `id-papel-timbrado` → `md-to-timbrado-id`
- `dogfood` → `systematic-debugging`
- `hermes-agent-skill-authoring` → `skills-repo-curator`
- `node-inspect-debugger` → `python-debugpy`
- `react-fastapi-debugging` → `systematic-debugging`
- `react-fastapi-debugging` → `dogfood`
- `local-postgres-sandbox` → `postgres-sandbox-verification`
- `plan` → `spike`
- `simplify-code` → `requesting-code-review`
- `hermes-environment-replication` → `hermes-agent-replication`
- `computer-use` → `autonomous-ai-agents`
- `merge-reconciler` → `codex`
- `github-issues` → `github-issue-to-pr`
- `github-repo-management` → `github-pr-workflow`
- `codebase-inspection` → `github-code-review`
- `auxiliar-adm-id` → `google-workspace`
- `git-fork-isolation` → `cicd-oracle-preview`
- `git-fork-isolation` → `github-repo-management`
- `claude-code` → `product-pipeline`
- `email-inbox-triage` → `document-to-action-items`
- `docx` → `pdf`
- `dogfood` → `requesting-code-review`
- `user-interview` → `ideation-drilling`

Uses:
- `process-augmentation-pipeline` → `deep-research`
- `augmentation-process-design` → `deep-research`
- `document-to-action-items` → `google-docs-formatting`
- `meeting-action-items` → `google-workspace`
- `email-inbox-triage` → `google-workspace`
- `pi-agent-coordination` → `hermes-agent`
- `product-pipeline` → `backlog-and-sprint`
- `ideation-drilling` → `product-pipeline`
- `html-pdf-fidelity` → `html-to-pdf-chromium`
- `html-report-hermes` → `html-pdf-fidelity`
- `relatorio-de-custos` → `xlsx`
- `grounded-citations` → `deep-research`
- `google-docs-formatting` → `google-workspace`
- `google-sheets-automation` → `google-workspace`
- `elaboracao-proposta-comercial` → `planejamento-estrategico-2h`
- `proposta-comercial-consultoria` → `elaboracao-proposta-comercial`
- `dedalo-squad` → `bpmn-diagram-renderer`
- `process-augmentation-pipeline` → `bpmn-diagram-renderer`
- `augmentation-process-design` → `augmentacao-query`
- `augmentacao-query` → `process-augmentation-pipeline`
- `github-issue-to-pr` → `github-pr-workflow`
- `github-code-review` → `github-pr-workflow`
- `github-auth` → `github-pr-workflow`
- `codex` → `product-pipeline`
- `opencode` → `product-pipeline`
- `baas-offline-migration` → `supabase-to-selfhost`
- `supabase-to-selfhost` → `postgres-dump-restore`
- `postgres-dump-restore` → `postgres-sandbox-verification`
- `devops-artemishub` → `cicd-oracle-preview`
- `cicd-oracle-preview` → `skills-repo-curator`
- `motor-nfse-id` → `emissao-nfse`
- `emissao-nfse` → `inter-api-id-consultoria`
- `md-to-timbrado-id` → `id-papel-timbrado`
- `md-to-timbrado-id` → `google-docs-formatting`
- `inspecting-hermes-desktop-dom` → `hermes-agent`
- `internal-python-job-executor` → `skills-repo-curator`
- `static-spa-vercel` → `cicd-oracle-preview`
- `sdlc-review` → `github-code-review`
- `hermes-agent-replication` → `hermes-agent`
- `gestao-financeira-id` → `google-sheets-automation`
- `inter-api-id-consultoria` → `gestao-financeira-id`
- `react-fastapi-debugging` → `devops-artemishub`
- `merge-reconciler` → `opencode`
- `sdlc-review` → `plan`

---

## Relações e manutenção

- **index.md** é território de agente LLM (nunca scripts) — atualizado por `read_file`/`patch`/`write_file`.
- **log.md** é append-only com prefixos `update|evolve|offload`.
- Ciclo: `update → log → commit → evolve → log → offload → commit → push`.
- Fork real em `idconsultoria/hermes-skills-mercurio` (23/08/2026) — push só para ele; não sincroniza com upstream/canônico.