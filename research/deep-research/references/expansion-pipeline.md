# Post-Research Content Production Pipeline

> Use **after** `deep-research` completes Phase 4 (synthesis). Turns research findings into structured reference files with parallel subagent orchestration.

## When to Use This Pipeline

Use when the user asks for a **reference library** / **pasta de soluções** / **catálogo de cases** / **base de conhecimento** built from research data. NOT for single reports — those are the output of the main deep-research skill directly.

## Workflow

### Phase 0: Define Granularity (CRITICAL — confirm with user!)

Ask the user before writing any files:

```
"Posso confirmar a unidade de solução: cada alteração isolada e replicável
dentro de um processo, com seu próprio input/output/ganho, conta como uma
solução distinta. Para o case X com N agentes ou N subprocessos, isso
significa N soluções. Posso seguir com essa interpretação?"
```

**Lição validada:** Allianz Nemo (7 agentes) = 7 soluções. Harvey (4 capabilities) = 4 soluções. McKinsey Lilli (pesquisa + tone-of-voice + CaseAI) = 3+ soluções.

### Phase 1: Template Each Finding

Each solution becomes a standalone `.md` file with frontmatter + 5 body sections.

**Template (per `solution-template-yaml.md`):**

```yaml
---
id: slug-identificador
titulo: Título descritivo da alteração isolada
case_pai: Empresa/projeto
categoria: A (reengenharia) | B (otimização)
tipo: I (agente IA) | II (assistente IA) | III (automação)
setor: Setor
porte_empresa: PME | Enterprise | Variado
ferramentas: [Ferramenta 1, Ferramenta 2]
fonte: URL principal
data_pesquisa: AAAA-MM-DD
human_in_the_loop: sim | não | parcial
ganho_principal: Métrica chave
processo_original: "Como era antes."
processo_augmentado: "Como ficou depois."
---
```

Body sections (each 120-200 lines total):

| Section | Content |
|---------|---------|
| `## Contexto` | 3 paragraphs: organization (porte, setor), problem (gargalo específico com números), approach (por que essa solução) |
| `## A Solução em Detalhe` | Fluxo operacional (etapas), arquitetura técnica (modelos, integrações), interface humano-máquina (papel do humano) |
| `## Resultados Obtidos` | Métricas concretas + tabelas comparativas + impactos qualitativos (mudança na rotina) |
| `## Como Replicar` | Pré-requisitos • Passo a passo (8-10 etapas) • Ferramentas e custos (tabela com alternativas) • Armadilhas comuns (5-8 itens com mitigação) |
| `## Onde Seria Relevante` | Cenários ideais • Onde NÃO aplicar • Variações do padrão |

### Phase 2: Dispatch Subagents (3 Parallel, 1 Case Each)

**Pattern (validated by user):**
- **1 subagent = 1 case_pai** (all files under that case)
- **3 subagents in parallel** (max_concurrent_children=3)
- Each subagent gets: list of files, context about the case, template guide, and sources

DO NOT do:
- ❌ 1 subagent per file (too slow, too many dispatches)
- ❌ 1 subagent for many cases/files (context pollution, timeouts)

**Subagent dispatch template:**
```
delegate_task(
    goal="Expanda N arquivos .md do case {NOME} (~{N} linhas cada para 120-200 linhas). Leia o guia, leia cada arquivo, escreva versão expandida com write_file. Mantenha frontmatter YAML intacto.",
    context="CASE: {nome} — {N} arquivos\nARQUIVOS:\n- {path1}\n- {path2}\n...\nCONTEXTO: {summary of case}\nGUIA: /opt/data/aumentacao-referencias/EXPANSAO-GUIA.md (or reference file). Leia antes.",
    toolsets=["file","terminal","web"]
)
```

### Phase 3: Quality Verification

After each batch returns:
1. Check `wc -l` for each file — target is 120-200+ lines
2. Spot-check frontmatter integrity (first 3 lines)
3. If files are under target, expand in next batch or with direct patches
4. User wants progress reports: "N/m casos concluídos. Restam X."

**Known quality trap:** Writing compressed files (~30-50 lines) to "deliver fast" is worse than not delivering — the user will notice and ask for a redo. Always prioritize depth over speed.

### Phase 4: Build Index + Archive

- Generate `index.md` with all solutions (use headings per solution + metadata table, not long descriptions)
- Create `tar.gz` of the entire folder for delivery
- Remove any guide/template files from the delivery folder

## Debugging Subagent Issues

### Timeout Recovery
- Subagents timeout at 600s. When they do, salvage partial work from state.db
- See `references/subagent-session-recovery.md` for SQLite queries
- If web_search failed for a subagent, run direct search from parent

### Model Choice
- MiniMax M3: better quality, slower (~3-5 min/case)
- DeepSeek v4 Flash: faster (~1.5-2 min/case), adequate quality with rich context
- User preference: Flash for subagents with quality oversight

### Web Search Workaround
- Quoted phrases in `web_search` break Bing (returns dictionary definitions)
- For exact-name search, use `web_extract(urls=[URL])` directly
- Pass this instruction to subagent contexts
