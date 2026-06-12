---
name: skills-repo-curator
description: "Manage the Hermes skills repo — consolidation cycles, MECE analysis, offload, graph.

Load this skill when the skills repo needs maintenance — evolve cycles, description audits, relation rebuilding, orphan review, or installing community skills. Covers the full consolidation lifecycle: update, evolve, offload, commit, push, and interactive D3 graph generation."

Load this skill when the skills repo needs maintenance — evolve cycles, description audits, relation rebuilding, orphan review, or installing community skills. Covers the full consolidation lifecycle: update, evolve, offload, commit, push, and interactive D3 graph generation."
category: software-development
---

# Skills Repository Curator

> Gerencia o skills repo em `/opt/data/skills/` com controle de versão Git.
> Macro: **Ciclo de Consolidação** — `Update → log → commit → Evolve → log → Offload → commit → git push`.
> Sub-etapa: **evolve** (9 passos) — estudo → plano → execução → orphan review → report → grafo → commit.

## Visão Geral — Ciclo de Consolidação vs Evolve

**Não são a mesma coisa.** O **Ciclo de Consolidação** é o processo macro que coordena as 3 etapas na ordem fixa: **Update → Evolve → Offload**. Cada etapa tem seu próprio prefixo no log.md. O **evolve** é apenas uma das 3 etapas — a de consolidação inteligente.

```
┌───────────────────────────────────────────────────────┐
│                 Ciclo de Consolidação                  │
│                                                       │
│   Update ──→ Log ──→ Commit ──→ Evolve ──→ Log ──→ Offload ──→ Commit ──→ git push
│   (6 passos)           (9 passos)            (6 passos)
│                                                       │
│   As 3 etapas sempre rodam nesta ordem.               │
└───────────────────────────────────────────────────────┘
```

O ciclo é executado periodicamente (diariamente via cron às 02:00). Ele inicia os updates — não o contrário.

## Fases do Gerenciamento de Skills

Este skill cobre as **duas fases** do ciclo de vida de uma skill:

### Fase 1 — External Curation & Installation (Descobrir, Avaliar, Instalar)

**Quando usar:** O usuário quer descobrir, avaliar e instalar skills da comunidade ou de hubs externos.

Cobre o workflow completo de curadoria externa:
- Fontes confiáveis para encontrar skills (Awesome Hermes Agent, HermesHub, Hermes Atlas, GitHub)
- Rubrica de avaliação multi-critério (5-point checklist)
- Sistema de ranking por tiers (Elite/Strong/Utility)
- 6 métodos de instalação (Hub, Tap+Install, Raw URL, Vendor scripts, Docker, From source)
- Registro de MCP Server para ferramentas externas
- Verificação pós-instalação

**Trigger:** usuário diz "find skills for", "discover skills about", "install skill", "procurar skills", "adquirir skills", "melhores skills", ou pede para comparar/avaliar skills comunitárias.

**Fontes de curadoria (ranked by reliability):**
| Source | URL | Reliability |
|--------|-----|:-----------:|
| Awesome Hermes Agent | github.com/0xNyk/awesome-hermes-agent | ⭐⭐⭐⭐⭐ |
| EasyClaw rankings | easyclaw.com/blog/knowledge/best-hermes-agent-skills | ⭐⭐⭐⭐⭐ |
| Felo AI blog | felo.ai/blog/best-hermes-agent-skills-2026 | ⭐⭐⭐⭐ |
| HermesHub | hermeshub.xyz | ⭐⭐⭐⭐ |
| Hermes Atlas | hermesatlas.com | ⭐⭐⭐ |
| GitHub search | `site:github.com hermes-agent skill <topic>` | ⭐⭐⭐ |
| Official docs catalog | hermes-agent.nousresearch.com/docs/reference/skills-catalog | ⭐⭐⭐⭐⭐ |

**Rubrica de Avaliação (5-point checklist):**
1. Security scan: `hermes skills inspect <id>` — no badge = manual review
2. Last commit: >60 days = possible incompatibility
3. Install/usage count: <50 installs on >3mo old skill = suspicious
4. Open issues: last 5 unresponded = abandoned
5. Hermes version compat: pre-v0.9 may not work with v0.10+

**Métodos de Instalação (preferência decrescente):**

1. **Hub Install** `hermes skills install <skill-id> -y`
2. **Tap + Install** `hermes skills tap add <user>/<repo> && hermes skills install <skill-name>`
3. **Raw URL** `hermes skills install "https://raw.githubusercontent.com/..." --name <name> --category <cat> --yes`
4. **Vendor scripts** — verificar Content-Type primeiro (muitos sites SPA retornam HTML)
5. **Docker** — para ferramentas externas sem pacotes nativos
6. **From source** — para ferramentas que precisam de Node/npm específicos

**Pós-instalação:** `hermes skills list | grep <name> && skill_view(name='<skill-name>')` para verificar.

**MCP Server Registration:** Se a ferramenta instalada expõe MCP server, registre com `hermes config set mcp_servers.<name>...`.

Para detalhes completos, veja `references/external-tools-install-notes.md` e `references/deep-research-skills-ranking-2026-06.md`.

---

## Estrutura do Repositório

```
skills/
├── AGENTS.md           ← Regras, operações, prefixos de log, scripts
├── index.md            ← Catálogo orientado a conteúdo (evolui commit a commit)
├── log.md              ← Diário cronológico append-only
├── reports/            ← Planos (pré) e relatórios (pós) de cada ciclo evolve
├── scripts/            ← Scripts de apoio (generate_graph.py, etc.)
├── skills_graph.html   ← Grafo D3 interativo (regenerado a cada evolve)
├── graph_data.json     ← Dados estruturados do grafo
└── <category>/
    └── <skill-name>/
        ├── SKILL.md
        └── references/
```

## Trigger

- Usuário diz "gerencie suas skills", "limpe as skills", "rode evolve", "consolide skills"
- Usuário pede para revisar, fundir, deletar ou organizar skills
- Ao final de uma sessão com múltiplas correções de workflow
- Execução automática via cron diário

## Regra Absoluta: index.md é Território de Agente LLM

**O index.md NUNCA pode ser editado por scripts** — nem Python, sed, awk, regeneração automática. Toda edição no index.md deve passar por ferramentas de agente LLM (`read_file`, `write_file`, `patch`), garantindo que cada decisão editorial (merge, ajuste de descrição, relação) passe por julgamento humano-assistido.

**Scripts são permitidos para tarefas de apoio** — análise de conexões, extração de metadados dos SKILL.md, geração do grafo HTML, relatórios. O output desses scripts informa o agente, que então edita o index.md manualmente.

O index.md **evolui commit a commit** — nunca é regenerado do zero. O agente usa `git diff` entre o último commit e o estado atual para detectar mudanças, depois aplica patches cirúrgicos. Cada commit adiciona uma camada sem destruir o histórico.

---

## Etapa 1: Update (6 passos)

Sincroniza o index.md com o estado atual das skills.

### Passos

1. **Verifica mudanças** — `git status` + `git diff` entre o último commit e o estado atual. Identifica skills adicionadas, removidas, modificadas ou com metadados alterados. Este diff É o ponto de partida.
2. Escaneia todas as skills no repositório
3. **Atualiza o index.md** com as mudanças detectadas via patches cirúrgicos (adiciona, edita, remove entradas)
4. **Audita conformidade de descrições** — varre TODAS as SKILL.md, não apenas as modificadas:
   - **Sumário de uma linha (≤85 chars, SEM `...`):** descrição concisa e auto-contida. Quem lê entende na hora se deve carregar a skill.
   - **Parágrafo de resumo:** explica gatilhos de ativação ("Load this skill when...") e expande a descrição com capacidades específicas, ferramentas utilizadas e o que produz.
   - Lista **todas as skills fora do formato** com o problema específico, edita a SKILL.md original, depois atualiza o index.md.
   - **Sem exceção** — faz para todas as skills fora do formato.
5. Registra no log.md com prefixo `update` incluindo o resumo de tudo que foi alterado
6. **Stage + commit**

### Formato exato esperado da description

```yaml
description: "One-liner summary here (≤85 chars, no ...).

Load this skill when [activation trigger]. [Expanded capabilities,
tools used, what it produces, key workflows covered.]"
```

**Exemplo conforme:**
```yaml
description: "Geocode addresses, find POIs, calculate routes, and lookup timezones via OpenStreetMap and OSRM.

Load this skill when you need location-based data — converting addresses to coordinates, searching for points of interest, getting driving or walking directions with distance and ETA, or looking up timezone information. Uses free APIs (Nominatim, Overpass, OSRM) with no API key required."
```

⚠️ **YAML `>-` (folded with strip) quebra o parser do `generate_graph.py`.** O script lê o frontmatter com regex simples (`^---\n(.*?)\n---`), e `description:` com múltiplas linhas indentadas pode fazer o parser perder o texto, caindo no fallback que extrai comandos aleatórios do corpo do SKILL.md — resultando em resumos como `node --version` no index.md. **Sempre usar string quoted (`"..."`) com `\n` explícito para parágrafos de múltiplas linhas. Verificar: `grep -rn 'description:' SKILL.md`.**

---

## Etapa 2: Evolve (9 passos)

**Esta é uma etapa do ciclo de consolidação.** Executa DEPOIS do update e ANTES do offload.

Analisa o portfólio e propõe merges, remoções e spin-offs para manter as skills **MECE** (Mutually Exclusive, Collectively Exhaustive).

### Critério de Merge

Duas skills conectadas (similar/uses) só devem permanecer separadas se descreverem **fluxos de trabalho realmente distintos** — que não podem ou não faz sentido incorporar um ao outro. A conexão no grafo é **evidência, não sentença** — o julgamento final é sobre o workflow descrito.

### Passos

1. **Estuda** o index.md completo e elabora plano de evolução
2. **Salva** o plano em `reports/evolve-<YYYY-MM-DD-HHMM>.md`
3. **Executa** o plano (merges, deletes, consolidação de conteúdo):
   - Limpa aprendizados excessivamente específicos das skills (debugging, workarounds temporários, timestamps únicos)
   - **⚠️ NÃO remover info operacional reutilizável:** números de contato (telefones, WhatsApp JIDs/LIDs, group IDs de plataformas), IDs de usuário de sistemas externos, endereços de email usados para coleta periódica, tokens de serviço, chaves de API, URLs de webhook — tudo que o workflow consulta de novo em runs futuras. Só remova o estritamente inútil após a run (ex: `session_id` expirado, offset de paginação).
   - **Audita descrições** das skills afetadas
   - **PII vs operacional — distinção importante:** Dados pessoais reais (nome completo do usuário, endereço físico, CPF/CNPJ, telefone pessoal — NÃO de serviço) devem ser `[REDACTED]`. JIDs de grupo WhatsApp, emails de serviços, IDs de sistemas externos são **operacionais** e devem ser preservados se reutilizáveis. Skills são artefatos compartilháveis, mas dados operacionais não são PII.
   - **Limpeza de disco:** `rm -rf` de diretórios órfãos
4. **Revisa skills órfãs** — skills sem relações no grafo:
   - Tenta encontrar conexão semântica com outras skills (lendo ambos os SKILL.md — **profundidade 1**). Se encontrar, adiciona relação bilateral (frontmatter + index.md).
   - Se não encontrar conexão, avalia se a skill é importante o suficiente para existir isolada. Skills genuinamente de nicho podem ficar órfãs com justificativa.
   - Se não tem conexão E não é claramente importante, considera merge ou delete.
   - **Target: 0 órfãos.**
5. **Escreve relatório denso** em `reports/evolve-<YYYY-MM-DD>-report.md`
6. **Atualiza** o index.md pós-transformação
7. **Registra** no log.md com prefixo `evolve`
8. **Gera grafo HTML interativo** — `python3 scripts/generate_graph.py`
9. **Stage + commit** final

### Inferência Depth-1 de Relações (Padrão Obrigatório)

**Não confiar em scan automatizado de frontmatter.** A primeira passada rasa produz ~12 arestas fracas. Para relações semânticas de qualidade:

1. Dispare **3 subagentes paralelos** via `delegate_task(tasks=[...])`
2. Cada subagente analisa ~28 skills
3. **Cada subagente lê a skill principal E cada skill candidata a relação (profundidade 1)** — lê o SKILL.md de ambos os lados, confirma a conexão semântica antes de declará-la
4. **Cada subagente produz um RELATÓRIO de saída** (ex: `relations-batch1.md`) — NUNCA edita o index.md diretamente (evita conflito de escrita concorrente)
5. Um único agente central lê os relatórios e aplica **todos os patches sequencialmente** no index.md. Com 180+ arestas, use transformação em lote via Python (veja `references/batch-apply-relations.md`) — parseia os relatórios e gera o index.md atualizado em uma operação.

Resultado esperado: ~140+ arestas em 75+ skills com precisão validada nos dois sentidos.

**NÃO** parar no primeiro merge óbvio. Se um merge parece evidente (ex: 3 coding agents), isso não é desculpa para encerrar a análise. O ciclo evolve deve analisar **todas as skills**.

### Formato `|-` Quebra o Grafo

O script `generate_graph.py` usa o regex `r"- `(\w+)` → `(.+)`"` para parsear relações. Se uma relação começar com `|- ` (pipe-dash) em vez de `- ` (só dash), o regex não captura.

**Verificar SEMPRE antes de gerar o grafo:**
```bash
grep "|- \`" index.md
```

Se existir, corrigir com:
```bash
# Use patch tool com replace_all=true
patch(path='/opt/data/skills/index.md', old_string='|- `', new_string='- `', replace_all=True)
```

---

## Etapa 3: Offload (6 passos)

**Esta é uma etapa do ciclo de consolidação.** Executa DEPOIS do evolve.

Remove entradas da memória persistente que estejam redundantes com skills.

### Regra

Memória guarda **preferências do usuário e fatos estáveis do ambiente**. Skills guardam **procedimentos, receitas e workflows**. Tudo que é procedural e está numa skill pode sair da memória.

### Passos

1. Lista entradas da memória atual via `memory(action='list')`
2. Para cada entrada, verifica se existe skill cobrindo o mesmo assunto
3. Se sim, remove da memória com `memory(action='remove', old_text=...)`
4. Registra no log.md com prefixo `offload`
5. git add -A && git commit -m "offload: ..."
6. **git push origin master** — sobe tudo para o GitHub

---

## Padrão: Batch-Report-Then-Apply (Evita File Conflict)

Sempre que múltiplos subagentes precisarem modificar o index.md:

1. Cada subagente produz um **relatório de saída** (ex: `relations-batch1.md`) com as modificações
2. Relatórios são salvos via `write_file` em `/opt/data/skills/`
3. **Um único** agente principal lê os relatórios e aplica **todos os patches sequencialmente** no index.md

Isso garante atomicidade e evita corrupção do arquivo por escrita concorrente.

Para aplicar grandes volumes de relações (180+ arestas), veja `references/batch-apply-relations.md` — abordagem de transformação em lote que parseia relatórios e gera o index.md atualizado.

---

## Log Entries — Formato

```markdown
## [YYYY-MM-DD] update | <resumo detalhado>
## [YYYY-MM-DD] evolve | <resumo: skills N→M, merges, deletes, órfãos>
## [YYYY-MM-DD] offload | <entradas removidas>
```

Prefixos:

| Prefixo | Etapa do ciclo |
|---------|---------------|
| `update` | Sincronização de index.md — git diff, escaneia, patches, audita descrições, log, commit |
| `evolve` | Consolidação inteligente — análise, merges, órfãos, relações, grafo, commit |
| `offload` | Limpeza de memória — remoção de fatos procedurais redundantes com skills |

---

## Scripts de Apoio

### `scripts/generate_graph.py` — Grafo Interativo D3.js

```bash
cd /opt/data/skills
python3 scripts/generate_graph.py              # gera skills_graph.html + graph_data.json
python3 scripts/generate_graph.py --json       # só graph_data.json
```

Gera um force-directed graph com 83+ nós coloridos por categoria, modal com summary + description ao clicar, filtro por nome. Lê relações do index.md (formato `` `tipo` → `path` ``), varre todos os SKILL.md para metadados, injeta no template `skills_graph_template.html`.

Dependências: Python 3 stdlib. Nenhum pacote externo.

---

## Verification

```bash
cd /opt/data/skills
git log --oneline -5
python3 scripts/generate_graph.py
grep "|- \`" index.md  # deve retornar vazio
grep -rn 'description:' SKILL.md  # deve retornar vazio (YAML folded quebra o parser)
grep "^### " index.md | wc -l  # total de skills
grep -c "Relações" index.md  # skills com relações

# Check for leaked subagent commentary in relation lines
grep -n '(reason:' index.md  # deve retornar vazio — subagentes podem vazar notas nos relatórios
grep -n 'Reason:' index.md   # mesma verificação, capitalização alternativa
```

## Pitfalls

⚠️ **Depth-1 obrigatória para relações.** Scan automatizado (regex de frontmatter) produz ~12 arestas. Leitura bilateral (profundidade 1) produz ~140+. Sempre usar subagentes com leitura depth-1.

⚠️ **Formato `|- ` quebra o grafo.** Verificar SEMPRE antes de gerar o grafo.

⚠️ **Consolidation cycle ≠ evolve.** O macro-ciclo (Update→Evolve→Offload) **não** é a mesma coisa que evolve. Evolve é uma etapa de 9 passos dentro do macro-ciclo.

⚠️ **Descrição conforme requer escopo total — não incremental.** A auditoria de descrições varre **todas** as SKILL.md, sem exceção.

⚠️ **PII vs operacional — auditar no passo 3.** PII real (nome, CPF, endereço físico, telefone pessoal) deve ser `[REDACTED]`. JIDs de grupo, emails de serviço, IDs de sistemas externos são **operacionais** — preserve se reutilizável entre runs.

⚠️ **Batch-Report-Then-Apply.** Subagentes NUNCA editam o index.md diretamente — produzem relatórios. Um agente central aplica todos os patches.

⚠️ **Não parar no primeiro merge óbvio.** Analisar todas as skills, não apenas os alvos evidentes.

⚠️ **index.md nunca é regenerado do zero.** Apenas patches cirúrgicos via ferramentas LLM.

⚠️ **YAML `>-` quebra o parser de descrições.** O script `generate_graph.py` lê frontmatter com regex simples e não suporta YAML folded (`>-`). Descrições devem usar string quoted (`"..."`) com `\n` explícito. Verificar com `grep -rn 'description:' SKILL.md`.

⚠️ **Ciclo pode morrer no meio e deixar working directory sujo.** O cron job tem timeout — se o ciclo não completa, SKILL.md ficam modificados mas sem commit, index.md desatualizado, log.md sem entrada. **Recuperação:**

   1. **Diagnóstico** — `cronjob(action='list')` → ver `last_status: error`. O campo `last_error` no `jobs.json` (`/opt/data/cron/jobs.json`) tem a mensagem de erro completa. O output do cron está em `/opt/data/cron/output/<job_id>/<timestamp>.md` — contém o prompt completo + a seção `## Error` com o trace.
   2. **Avaliação** — `git status` + `git diff --stat` mostra quais skills foram tocadas. `git diff <file>` pra ver se as mudanças são válidas ou corrompidas.
   3. **Se válido** — complete o ciclo manualmente: `git add -A`, escreva entrada no `log.md`, atualize `index.md`, `git commit -m "update: ..."`, `git push`.
   4. **Se corrompido** — `git restore .` pra limpar o working directory. O próximo cron (02:00) recomeça do zero.
   5. **Causas raiz comuns:**
      - **Cota de ferramentas estourada** na auditoria de descrições (passo 4 do update: varre TODAS as SKILL.md). Ciclo com muitas skills precisa de paralelismo ou timeout maior.
      - **Provider fallback com quota free tier esgotada.** O cron pinou `model: null, provider: null` no momento da criação → usa o provider ativo na época. Se o provider principal falha (429 rate limit), cai no `fallback_providers` do config.yaml. Gemini free tier tem limite de 250k input tokens — ao varrer 83+ SKILL.md o ciclo estoura a cota e recebe HTTP 429. **Diagnóstico:** `last_error` contém `HTTP 429` + `quota exceeded` + nome do modelo Gemini. **Prevenção:** (a) setar `model` e `provider` explicitamente no cron job via `cronjob(action='update', job_id=..., model={"model": "...", "provider": "..."})` para bypassar o fallback; (b) adicionar `context_length: 250000` ao fallback Gemini no config.yaml para conter a janela dentro do limite free tier.
      - **Re-run deixou estado parcial.** `cronjob(action='run')` pode completar o Update mas falhar no Evolve, deixando batch reports e `_analyze.py` / outros scripts temporários no working dir. Após recuperação manual, esses artefatos podem ser commitados sem dano ou descartados com `git restore`.

⚠️ **Limpeza de scripts temporários.** Scripts de análise auxiliar (ex: `_analyze.py`, `_count_relations.py`) criados durante o ciclo DEVEM ser removidos antes do commit final. Eles poluem o repositório e não têm valor após o ciclo. Use `rm -f _analyze.py _*.py` como passo de limpeza antes do stage final.

⚠️ **Leaked commentary de subagentes no index.md.** Subagentes podem incluir notas informais como `(reason: ...)` em suas propostas de relação. Quando o agente central aplica as relações manualmente via patch, é fácil copiar acidentalmente o comentário junto com a relação. Isso quebra o formato limpo do index.md. **Sempre verificar** com `grep -n '(reason:' index.md` e `grep -n 'Reason:' index.md` depois de aplicar patches de relação, e remover qualquer linha contaminada.