# Relatório evolve — 2026-10-19

Fork `idconsultoria/hermes-skills-mercurio` · ciclo semanal (segunda 02:00 UTC).
Plano: `reports/evolve-2026-10-19-0509.md`.

## Estado inicial → final

| Métrica | Inicial (12/10) | Final (19/10) |
|---|---|---|
| Skills no catálogo | 118 | **123** |
| Categorias | 13 | 13 |
| Arestas no grafo | 193 | **206** |
| Órfãos | 0 | **0** |
| SKILL.md no disco | 135 | 140 |
| SKILL.md no disco fora do catálogo (drift canônico) | 17 | 17 |
| SKILL.md no catálogo sem arquivo no disco | 0 | 0 |

## Entregas do ciclo

### 1. Migração de paths (commit `362b5e8`)

161 arquivos tracked reescritos: `/opt/data/**` e `/opt/mercurio-data/**` →
`/data/data/com.termux/files/home/capitolium/**`. Consequência direta da mudança de
instalação (proot Termux). Padrões afetados: `.playwright`, `node_modules/playwright`,
`venvs/google/bin/python`, `state.db`, `config.yaml`, `google_token.json`, `skills/`,
`work/idata`, `mmdc`, scripts de push, além de caminhos de trabalho em receitas e pitfalls.
Sem mudança de conteúdo semântico — só caminho.

### 2. Skills indexadas (5 novas, todas ID/Mercúrio)

| Skill | Type | Fonte da marca / mecanismo |
|---|---|---|
| `business/documento-a4-marca-id` | Orchestrator | Fontes Neulis/Nunito base64 + logo do template da proposta; `render_a4.mjs`; gate de overflow |
| `infrastructure/auditoria-automacoes-google-script` | ToolIntegration | `Message-ID: autogen-java` → acionador na conta remetente → desativar (clique humano) |
| `infrastructure/hermes-gateway-stall-diagnosis` | Reference | `session_turn_leases` no state.db; watchdog exit 75; ordem de apuração read-only |
| `infrastructure/hermes-memory-file-curation` | Reference | Limites 2200/1375; loader não trunca; medir com `MemoryStore` |
| `infrastructure/hermes-session-forensics` | Orchestrator | `state.db` read-only de outros perfis/instalações |

Tabelas: business 21→22 linhas, infrastructure 7→11. Total 118→123.

### 3. Conformidade de frontmatter

- `autonomous-ai-agents/hermes-agent` (tracked, catálogo): faltavam `type` e `timestamp` →
  `type: Orchestrator`, `timestamp: 2026-09-26T02:14:34Z` (git log).
- `infrastructure/auditoria-automacoes-google-script`: `type: Skill` (fora da taxonomia
  OKF) → `type: ToolIntegration`.
- `hermes-gateway-stall-diagnosis`, `hermes-memory-file-curation`: ganharam `timestamp`.
- Cobertura final: **123/123 skills do catálogo com `type` + `timestamp`**.

### 4. Relações — +13 arestas (193 → 206)

Similar (9): `documento-a4-marca-id`→`md-to-timbrado-id`/`html-pdf-fidelity`/`brand-design-system-html`;
`auditoria-automacoes-google-script`→`auxiliar-adm-id`;
`hermes-gateway-stall-diagnosis`→`hermes-session-forensics`/`telegram-group-bot-diagnosis`/`messaging-platforms`;
`hermes-memory-file-curation`→`id-comunicacao-multiusuario`; `hermes-session-forensics`→`peer-session-audit`.

Uses (5): `documento-a4-marca-id`→`html-to-pdf-chromium`/`elaboracao-proposta-comercial`;
`auditoria-automacoes-google-script`→`google-workspace`;
`hermes-session-forensics`→`hermes-gateway-stall-diagnosis`; `hermes-memory-file-curation`→`hermes-session-forensics`.

Removida **1 aresta duplicada**: `organizacao-drive-id` → `formalizacao-acordo-cliente`
aparecia duas vezes no bloco Uses.

### 5. Deleções e merges

Nenhum. Tabelas de merges/deleções vazias — ver justificativa par a par em
`reports/evolve-2026-10-19-0509.md` (10 pares reavaliados, todos mantidos). Nenhuma aresta
descartada por dangling.

## Órfãos

| Skill | Arestas | Decisão |
|---|---|---|
| — | — | **0 órfãos** no grafo de 123 nós |

As 5 skills novas já entraram com 1–5 relações cada, derivadas de leitura central
(profundidade 1 onde o alvo é skill catalogada).

## Depth-1 em lote

Não disparado nesta run (orçamento de tempo do cron; precedente de falha em 03/10 com 3
subagentes: 2 timeouts de 600 s + 1 erro de provider). Relações derivadas centralmente —
método registrado no plano, seção 4.

## Git diff summary

```
362b5e8 update: migra paths /opt/* -> <termux>/capitolium em 161 arquivos  (161 files, +1358/-1409)
b47c751 update: indexa 5 skills ID 118->123 + 13 arestas + grafo 123/206/0  (45 files, +3961)
<evolve> evolve: 123 MECE estáveis, 0 merges, 0 órfãos, grafo 123/206/0
```

## Drift canônico (fora do catálogo, 18ª ocorrência)

17 SKILL.md permanecem untracked e fora do catálogo, por escopo (prune 41, foco 100% ID):
`creative/` 6 (ascii-art, comfyui, excalidraw, pretext, sketch, touchdesigner-mcp),
`mlops/` 5 (evaluating-llms-harness, weights-and-biases, huggingface-hub, llama-cpp,
serving-llms-vllm), `productivity/` 2 (nano-pdf, session-librarian), `research/` 2
(blogwatcher, research-paper-writing), `smart-home/openhue`, `software-development/github`.
Além disso `.locks/`, `apple/`, `media/`, `note-taking/`, `social-media/`, `web/` (vazios ou
só DESCRIPTION.md) e os DESCRIPTION.md de `creative/` e `github/`. O grafo é imune (lê só o
index.md), e a varredura disco×catálogo confirma 0 entradas do catálogo sem arquivo real.

## Verificações

- `grep -c '|- \`` index.md → 0 (formato do grafo OK)
- `grep -nE '\(reason:|Reason:' index.md` → vazio (sem comentário vazado de subagente)
- linhas de tabela do index.md = 123 = nós do grafo
- 0 órfãos, 0 arestas dangling
- scripts temporários (`_analyze.py`) removidos antes do commit
