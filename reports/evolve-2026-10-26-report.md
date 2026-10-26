# Relatório — Evolve 2026-10-26 (ciclo semanal de consolidação)

**Repo:** `idconsultoria/hermes-skills-mercurio` · **Execução:** 2026-10-26 17:30 UTC (14:30 BRT) · cron `8a7f5f65ed76`

## Estado inicial × final

| Métrica | Início | Fim |
|---|---:|---:|
| SKILL.md no disco | 166 | **165** |
| Entradas no index.md | 135 (header: 134) | **165** (header: 165) |
| Categorias no índice | 13 | **15** (mlops, smart-home) |
| Arestas no apêndice de relações | 223 | **268** (+45) |
| Grafo (`graph_data.json`) | — | **165 nós / 268 arestas / 1 órfão** |
| Drift disco × índice | 31 skills fora | **0** |
| `description` em block scalar | 4 | **0** |
| `description` plain (sem quotes) | 10 | **0** |
| Summary > 85 chars | 2 | **0** |
| `type:` ausente / inválido | 17 / 4 | **0 / 0** |
| `timestamp:` ausente | 18 | **0** |

## Merge

| Skill absorvida | Destino | O que foi absorvido |
|---|---|---|
| `ebook-epub-kindle` (7.231 chars) | `documento-para-leitura-mobile-e-kindle` (5.755 → 12.028 chars) | `references/segmentacao-de-texto-pdf.md`, `scripts/build_epub.py`, seções "Quando usar", HTML de leitura (viewport/dark/coluna única), EPUB (subset seguro de marcação, capa, um capítulo por seção), render+verificação por Chromium 390px e 7 pitfalls (título na mesma linha do corpo, mobília de página, badge→`<p>` aninhado, fonte remota no Kindle, declarar pronto sem abrir o arquivo). |

Critério MECE aplicado: mesmo fluxo (extrair → estruturar → renderizar → verificar → entregar) com o mesmo artefato de saída (par HTML+EPUB). Não havia distinção de nível de abstração nem de toolchain — separar era duplicação, não especialização.

## Relações (evolve)

45 novas arestas injetadas (42 `similar` + 3 `uses`), todas com leitura dos dois lados e zero duplicatas contra o apêndice (checagem simétrica antes de aplicar).

| Cluster | Arestas |
|---|---|
| Fomento / proposta pública | `analise-edital-fomento` → `analise-edital-fomento-id`; `-id` → `proposta-ente-publico`, `elaboracao-proposta-comercial` |
| Receita de serviço de campo | `metricas-financeiras-servico-campo` → `modelo-receita-servicos-campo`, `revenue-kpi-framework`, `padrao-dataviz-id`; `modelo-receita-servicos-campo` → `revenue-kpi-framework` |
| Jurídico ID | `prosa-peca-id` → `direito-civil-brasileiro`, `revisao-entrega-cliente`; `contrato-sustentacao-sla` → `contratos-justos-id`, `direito-empresarial-brasileiro`; `societario-id` → `direito-empresarial-brasileiro` |
| Documento / PDF | `documento-para-leitura-mobile-e-kindle` → `pdf` (uses), `html-pdf-fidelity`, `revisao-entrega-cliente`; `figuras-em-documento-pdf` → `documento-a4-marca-id` (uses), `padrao-dataviz-id`; `revisao-documento-a4` → `revisao-entrega-cliente`, `documento-a4-marca-id`; `nano-pdf` → `pdf` |
| Hermes / sessões | `session-librarian` → `hermes-session-forensics`, `hermes-agent`; `coordenacao-perfis-hermes` → `hermes-peer-profile-delegation`, `facilitacao-grupo-agentes`; `hermes-peer-profile-delegation` → `peer-session-audit`; `migracao-caminhos-proot-termux` → `hermes-cron-script-dispatch`, `hermes-agent` |
| GitHub | `github` → `github-pr-workflow`, `github-issues`, `github-code-review` |
| Pesquisa | `blogwatcher` → `competitor-news-monitor`; `research-paper-writing` → `deep-research`, `grounded-citations` |
| Criativo | `ascii-art`, `comfyui`, `excalidraw`, `pretext` → `sketch`; `comfyui` → `touchdesigner-mcp` |
| MLOps | `huggingface-hub` → `llama-cpp`; `evaluating-llms-harness` → `serving-llms-vllm`, `huggingface-hub` (uses); `weights-and-biases` → `evaluating-llms-harness`; `serving-llms-vllm` → `llama-cpp` |
| Dados / BI | `padrao-dataviz-id` → `kpi-dashboard-design`, `business-intelligence` |

## Órfãos

| Skill | Decisão |
|---|---|
| `padrao-dataviz-id` | resolvido — 2 arestas para o cluster de BI (`kpi-dashboard-design`, `business-intelligence`) |
| 30 demais | resolvidos por profundidade 1 (tabela acima) |
| `openhue` | **mantida órfã com justificativa** — única skill de smart-home/casa no fork ID; nenhum par semântico no catálogo (não faz parte do fluxo de consultoria nem de documento). Não é candidata a merge (não há com quem fundir) nem a delete (ferramenta integrada válida). |

**Target 0 órfãos:** 165 nós, 1 órfão justificado.

## Descrições — decisão editorial registrada

Estruturais zeradas (block scalar, quotes, summary > 85, type, timestamp). Permanecem **75 skills com descrição de uma linha** (sem o segundo parágrafo). Decisão: **não reescrever em lote** — as one-liners do fork ID são auto-contidas ("Use ao...", "Carregue esta skill..."), permitem a decisão de carregar pela própria linha e a informação extra viveria no corpo da skill (que o agente lê ao carregar). Reescrever 75 descrições num run geraria parágrafo genérico sem lastro no conteúdo real — pior que a one-liner. Backlog: expandir o parágrafo **quando a skill for editada por outro motivo** (custo marginal zero).

## Offload

**Pulado** — execução em cron sem memória pré-injetada e o tool `memory` não expõe `list`. Registrado no `log.md`. Rodar manualmente em sessão interativa quando necessário.

## Higiene

- `.locks/` (4 arquivos de lock de runtime) adicionado ao `.gitignore`.
- Scripts auxiliares de análise executados fora do repo (`$HOME/.tmpcur/`), nada temporário versionado.

## git diff summary

```
 9 SKILL.md (WIP de sessões anteriores — corpo, preservados)
30 SKILL.md (frontmatter: description/type/timestamp + merge)
 1 SKILL.md deletado (productivity/ebook-epub-kindle)
 index.md   (+~60 linhas: 30 entradas, 45 arestas, header 165/15 categorias)
 graph_data.json, skills_graph.html (regenerados: 165 nós / 268 arestas)
 .gitignore (+.locks/)
 reports/evolve-2026-10-26-1430.md, reports/evolve-2026-10-26-report.md
 log.md (update + evolve + offload-skipped)
```
