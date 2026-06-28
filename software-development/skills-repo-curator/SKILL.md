---
name: skills-repo-curator
description: "Manage the Hermes skills repo — consolidation cycles, MECE analysis, offload, graph.

Load this skill when the skills repo needs maintenance — evolve cycles, description audits, relation rebuilding, orphan review, or installing community skills. Covers the full consolidation lifecycle: update, evolve, offload, commit, push, and interactive D3 graph generation."

category: software-development
type: Orchestrator
timestamp: 2026-06-28T05:11:55Z
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

0. **Manual install from GitHub repo** — quando `hermes skills install` CLI não está disponível:
   ```bash
   # 1. Achar a skill no GitHub (ex: mattpocock/skills)
   # 2. Baixar SKILL.md
   curl -sL 'https://raw.githubusercontent.com/<user>/<repo>/main/skills/<cat>/<name>/SKILL.md' -o /tmp/SKILL.md
   # 3. Criar diretório e escrever
   mkdir -p /opt/data/skills/<category>/<skill-name>/references
   cp /tmp/SKILL.md /opt/data/skills/<category>/<skill-name>/SKILL.md
   # 4. Baixar references se houver (DEEPENING.md, HTML-REPORT.md, etc.)
   ```
   Se a skill tem dependências externas (`/codebase-design`, `/grilling`, etc.), baixe todas, leia, e consolide os vocabulários e workflows numa única SKILL.md autossuficiente — sem referências a skills externas. Arquivos de referência (formatos, templates) ficam em `references/` e são carregados com `skill_view(name, file_path='references/<file>')`.
1. **Hub Install** `hermes skills install <skill-id> -y`
2. **Tap + Install** `hermes skills tap add <user>/<repo> && hermes skills install <skill-name>`
3. **Raw URL** `hermes skills install "https://raw.githubusercontent.com/..." --name <name> --category <cat> --yes`
4. **Vendor scripts** — verificar Content-Type primeiro (muitos sites SPA retornam HTML)
5. **Docker** — para ferramentas externas sem pacotes nativos
6. **From source** — para ferramentas que precisam de Node/npm específicos

**Pós-instalação:** `hermes skills list | grep <name> && skill_view(name='<skill-name>')` para verificar.

Para skills comunitárias que dependem de outras skills (`/codebase-design`, `/grilling`, etc.), veja `references/self-contained-skill-consolidation.md` — padrão para fundir dependências em uma única skill autossuficiente com arquivos de referência no lugar de skills externas.

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

- Usuário diz "gerencie suas skills", "limpe as skills", "rode evolve", "consolide skills", "alinhar com OKF", "adicionar type", "criar index.md por categoria"
- Usuário pede para revisar, fundir, deletar ou organizar skills
- Usuário pergunta sobre OKF, progressive disclosure, ou formato de conhecimento agent-ready
- Usuário pede para adicionar/resumir/corrigir descrições de skills (summary >85 chars, trigger ausente, blank line separator faltando)
- Ao final de uma sessão com múltiplas correções de workflow
- Execução automática via cron diário

## Regra Absoluta: index.md é Território de Agente LLM

**O index.md NUNCA pode ser editado por scripts** — nem Python, sed, awk, regeneração automática. Toda edição no index.md deve passar por ferramentas de agente LLM (`read_file`, `write_file`, `patch`), garantindo que cada decisão editorial (merge, ajuste de descrição, relação) passe por julgamento humano-assistido.

**Scripts são permitidos para tarefas de apoio** — análise de conexões, extração de metadados dos SKILL.md, geração do grafo HTML, relatórios. O output desses scripts informa o agente, que então edita o index.md manualmente.

O index.md **evolui commit a commit** — nunca é regenerado do zero por scripts. O agente usa `git diff` entre o último commit e o estado atual para detectar mudanças, depois aplica patches cirúrgicos. Cada commit adiciona uma camada sem destruir o histórico.

**Exceção prática:** quando >30% das entradas mudam (ex: remoção em massa de skills arquivadas), a regeneração completa via `write_file` (ferramenta LLM) é **mais confiável** que dezenas de patches individuais que falham por deslocamento de linha. A proibição é contra scripts (Python/sed/awk) editarem o index.md — `write_file` é ferramenta de agente LLM e respeita a regra de julgamento humano-assistido. Ao regenerar, preserve a estrutura exata de cada bloco (nome, arquivo, tamanho, resumo, descrição, relações) e nunca perca metadados.

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
   - **`type:` presente e válido (OKF-aligned):** verifica se o campo `type` existe no frontmatter com um dos valores (Orchestrator, ToolIntegration, Reference, Template, Research, Media, Creative, Health). Skills sem `type` ou com type inválido devem ser corrigidas.
   - **`timestamp:` presente:** verifica se o campo `timestamp` ISO 8601 existe. Se ausente, extrair do git log.
   - **Gatilho de ativação presente (multi-idioma):** verifica se o parágrafo contém "Load this skill when" (EN) ou "Carregue esta skill quando" (PT-BR). Skills em português são válidas com trigger em PT-BR. Skills sem trigger em nenhum dos dois idiomas devem ser corrigidas.
   - **Separação sumário/corpo com linha em branco:** verifica se há `\n\n` entre o sumário e o parágrafo de descrição. Descrições sem linha em branco quebram o parser do generate_graph.py e audit-descriptions.py.
   - **Verifica duplicatas pós-aspas:** descrições que terminam com `"` mas têm texto idêntico repetido depois da aspa de fechamento são um bug comum. Detectar com `grep -A1 'description: "' SKILL.md | grep -v '^--$'` e inspecionar visualmente.
   - Lista **todas as skills fora do formato** com o problema específico, edita a SKILL.md original, depois atualiza o index.md.
   - **Sem exceção** — faz para todas as skills fora do formato.

### Como corrigir descrições com sumário >85 chars

Quando o audit apontar "Summary too long", o sumário (primeira linha da description) precisa ser truncado em ≤85 chars mantendo coerência:

**Técnica de truncamento inteligente:**
1. Encontre o último ponto de quebra natural antes da posição 85: prioridade `. ` (ponto+espaço) > ` — ` (em-dash) > `:` > `, ` > último espaço
2. Remova trailing punctuation (`,` `;` `:` `—` `-`)
3. O sumário NUNCA deve terminar com `...` — truncamento é sempre a um break point natural

**Separação sumário/corpo:** se o sumário e o parágrafo estiverem consecutivos sem linha em branco, adicione `\n\n` entre eles. Ex: `description: "Summary.\n\nBody."` ✓ vs `description: "Summary.\nBody."` ✗

**Multi-idioma:** Skills pt-BR usam "Carregue esta skill quando" em vez de "Load this skill when". O audit script aceita ambos.

**Pós-correção:** verificar com `grep -rn 'description:' SKILL.md` se descrições não foram truncadas. Se corrompeu, restaurar com `git checkout HEAD -- <file>` e re-fixar.

### Como sincronizar Resumo drift

Após corrigir SKILL.md, rode `audit-descriptions.py --drift`. Para cada DRIFT:
1. Index.md Resumo pode ser MAIS completo que o SKILL.md summary — aceitável
2. Se o Resumo estiver desatualizado (menos info que o SKILL.md summary), substitua no index.md pelo texto da SKILL.md
   - **Verifica Resumo drift no index.md** — após corrigir as SKILL.md, verifique se os campos `Resumo:` no index.md correspondem à primeira linha (sumário) do `description:` da SKILL.md. O index.md pode ter resumos truncados, desatualizados ou corrompidos — especialmente em skills cujo SKILL.md foi editado mas o index.md não foi sincronizado. Use um script para comparar:
     ```python
     # Extrai sumário de cada SKILL.md e compara com Resumo do index.md
     sk_desc = content[content.find('description: "')+14:]
     sk_desc = sk_desc[:sk_desc.find('"')]
     summary = sk_desc.split('\\n\\n', 1)[0] if '\\n\\n' in sk_desc else sk_desc.split('\\\\n\\\\n', 1)[0]
     ```
     Skills com `Resumo` que termina em `...` ou difere do sumário real devem ter o Resumo corrigido.
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

⚠️ **YAML formatos escalares (`|`, `|-`, `>`, `>-`) quebram o parser do `generate_graph.py`.** O script lê o frontmatter com regex simples (não é parser YAML completo). Qualquer block scalar (`|`, `|-`, `>`, `>-`) faz o parser perder o texto da descrição — resultando em resumos vazios ou truncados no index.md. **Usar string quoted (`"..."`) com QUEBRA DE LINHA REAL (não escape `\n`) para separar sumário do parágrafo:**

```yaml
description: "Summary line here (≤85 chars).

Load this skill when [trigger]. Expanded capabilities paragraph."
```

### Campos OKF no frontmatter

Além de `name`, `description` e `category`, toda SKILL.md **deve** ter:

```yaml
type: Orchestrator          # Obrigatório (OKF v0.1). Valores: Orchestrator, ToolIntegration,
                            # Reference, Template, Research, Media, Creative, Health
timestamp: 2026-06-21T05:11:49Z  # Recomendado. ISO 8601 do último commit via git log
```

O campo `type` é o único campo obrigatório no padrão [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) v0.1 da Google Cloud. Alinhar o skills repo com OKF permite que consumption agents OKF-compatíveis descubram e classifiquem skills Hermes sem integração adicional.

O `timestamp` permite avaliar frescor sem consultar git log — valioso em cron jobs e agents que priorizam informações atualizadas.

Isso é YAML válido, mais legível, e parseia corretamente tanto por parsers YAML quanto por regex simples. O script `generate_graph.py` lê a primeira linha após `description: "` como sumário e o restante até o `"` de fechamento como parágrafo. **Não usar `\n` literal** — parsers simples não expandem escapes. Verificar: `grep -rn '^description:\s*[|>]' SKILL.md` (apanha `|`, `|-`, `>`, `>-`).

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

### Como ler a memória atual

- **Sessão normal:** as seções `MEMORY` e `USER PROFILE` estão injetadas no prompt do agente. Leia diretamente dali — cada entrada é separada por `§`.
- **Sessão cron (`skip_memory=true`):** a memória **não** é pré-injetada. O tool `memory` não tem action `list` — o agente não consegue ver as entradas atuais via tool call. **Soluções:** (a) incluir as entradas da memória explicitamente no texto do prompt do cron, ou (b) aceitar que o offload não roda em cron — executar manualmente quando necessário. O workaround de "adicionar dummy para forçar rejeição" é frágil e não recomendado.

### Passos

1. Leia as entradas da memória a partir do prompt (sessão normal) ou do prompt do cron (se explicitamente incluídas)
2. Para cada entrada, verifique se existe skill em `/opt/data/skills/` cobrindo o mesmo assunto (conteúdo procedural, workflow, ou receita)
3. Remova da memória usando **operações em lote** — uma única chamada `memory(operations=[{action:'remove', old_text:...}, ...])` com múltiplos removes — em vez de chamadas individuais. Economiza tool calls e evita escritas redundantes.
4. Registre no log.md com prefixo `offload` listando as entradas removidas
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

### `scripts/audit-descriptions.py` — Auditoria de Descrições

```bash
cd /opt/data/skills
python3 software-development/skills-repo-curator/scripts/audit-descriptions.py           # escaneia todas as SKILL.md
python3 software-development/skills-repo-curator/scripts/audit-descriptions.py --drift   # compara Resumo index.md vs summary real
```

Verifica conformidade de descrições em todas as SKILL.md: formatação (quoted string vs block scalar), tamanho do sumário (≤85 chars, sem `...`), presença de gatilho ("Load this skill when..."), e detecção de `\\n\\n` escapes literais. Também detecta drift entre o Resumo no index.md e o sumário real da SKILL.md.

Use este script **antes** da auditoria manual (passo 4 do update) para identificar rapidamente quais skills precisam de correção. O output informa o agente LLM, que aplica as correções nas SKILL.md e index.md via ferramentas LLM.

Dependências: Python 3 stdlib. Nenhum pacote externo.

### OKF Alignment

The skills repo is aligned with Google's Open Knowledge Format (OKF) v0.1.
See `references/okf-format-reference.md` for the full spec reference, 8-type
taxonomy, progressive disclosure structure, and comparison matrix.

Operations that reference OKF:
- **Add type to all skills** — batch-edit every SKILL.md frontmatter to add
  `type:` with the correct value from the 8-type taxonomy.
- **Add timestamp to all skills** — extract last commit date via `git log -1
  --format=%cI -- <skill>/SKILL.md` and insert as `timestamp:`.
- **Create category index.md** — generate `index.md` per category directory so
  OKF consumption agents can discover skills progressively.
- **Regenerate graph** — `generate_graph.py` now reads `type` and displays it
  in node modals.

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

# Check for empty Relações blocks
grep -A1 'Relações:' index.md | grep -E '^--$|^Relações' -v | grep -E '^$' | head -3 && echo 'WARNING: empty Relações found'

# Check for duplicate Relações in same entry
python3 -c "
import re
with open('index.md') as f:
    # Count Relações vs skill entries
    relacoes = len(re.findall(r'\*\*Relações:\*\*', f.read()))
    skills = len(re.findall(r'^### ', open('index.md').read()))
    if relacoes > skills:
        print(f'WARNING: {relacoes} Relações blocks for {skills} skills (duplicates)')
    else:
        print(f'OK: {relacoes} Relações blocks for {skills} skills')
"

# Check for truncated descriptions in SKILL.md (description without closing quote)
grep -rn 'description:' SKILL.md | grep -v 'description: "' | head -5 && echo 'WARNING: descriptions without opening quote found'

# Check for Resumo drift — index.md Resumo vs actual SKILL.md summary
python3 software-development/skills-repo-curator/scripts/audit-descriptions.py --drift
```

## Pitfalls

⚠️ **Depth-1 inference não cabe no cron de 3 minutos.** O scheduler do cron tem hard interrupt de 3 min por run. A inferência depth-1 (disparar 3 subagentes paralelos, cada um lendo ~28 skills bilateralmente) exige mais tempo. **Workarounds:**
   - (a) Separar depth-1 em seu próprio cron job com prompt focado só em relações, ou
   - (b) Rodar `hermes chat -q '...'` via SSH no host com timeout de 10+ min, ou
   - (c) Executar depth-1 manualmente quando necessário (fora do cron).

⚠️ **Formato `|- ` quebra o grafo.** Verificar SEMPRE antes de gerar o grafo.

⚠️ **Consolidation cycle ≠ evolve.** O macro-ciclo (Update→Evolve→Offload) **não** é a mesma coisa que evolve. Evolve é uma etapa de 9 passos dentro do macro-ciclo.

⚠️ **Descrição conforme requer escopo total — não incremental.** A auditoria de descrições varre **todas** as SKILL.md, sem exceção.

⚠️ **PII vs operacional — auditar no passo 3.** PII real (nome, CPF, endereço físico, telefone pessoal) deve ser `[REDACTED]`. JIDs de grupo, emails de serviço, IDs de sistemas externos são **operacionais** — preserve se reutilizável entre runs.

⚠️ **Batch-Report-Then-Apply.** Subagentes NUNCA editam o index.md diretamente — produzem relatórios. Um agente central aplica todos os patches.

⚠️ **Não parar no primeiro merge óbvio.** Analisar todas as skills, não apenas os alvos evidentes.

⚠️ **index.md nunca é regenerado do zero.** Apenas patches cirúrgicos via ferramentas LLM.

⚠️ **YAML `>-` quebra o parser de descrições.** O script `generate_graph.py` lê frontmatter com regex simples e não suporta YAML folded (`>-`). Descrições devem usar string quoted (`"..."`) com quebra de linha real (não escape `\\n`). Verificar com `grep -rn 'description: >' SKILL.md`.

⚠️ **Relações vazias após filtragem de skills arquivadas.** Ao remover relações para skills arquivadas do index.md, algumas entradas podem ficar com `**Relações:**` vazio (0 relações). Detectar com `grep -A1 '**Relações:**' index.md | grep -B1 '^$'` ou script similar. Ação corretiva: ou remove o bloco vazio, ou adiciona novas relações com skills ativas.

⚠️ **Blocos `**Relações:**` duplicados no index.md fonte.** Algumas skills (ex: `pi-agent-coordination`) têm dois blocos `**Relações:**` consecutivos por histórico de edição. Verificar com `grep -c 'Relações' index.md | ...` se o total excede o número de skills. Se existirem, mesclar num único bloco durante o update.

⚠️ **Descrições SKILL.md com `\\n` literal vs quebra de linha real.** Arquivos que usam `\\n\\n` (escape literal) em vez de quebra de linha real dentro da string quoted do YAML não parseiam corretamente com parsers de frontmatter simples. Ao fazer batch-edit de descrições, SEMPRE usar quebra de linha real entre sumário e parágrafo, NUNCA `\\n` literal. Scripts de batch que fazem replace de descrições devem verificar o formato atual e tratar ambos os casos, sob risco de corromper o frontmatter YAML (truncar a descrição no meio).

⚠️ **Batch-edit de SKILL.md requer verificação pós-aplicação.** Scripts que editam múltiplas SKILL.md em lote (ex: para corrigir descrições) podem corromper arquivos com formato de descrição diferente do esperado. Após qualquer batch-edit, verificar com `grep -rn 'description:' SKILL.md` se alguma descrição ficou truncada (linha termina sem aspas de fechamento ou sem `---` na linha seguinte). Restaurar com `git checkout HEAD -- <file>` e re-fixar manualmente.

⚠️ **Offload em cron não funciona com skip_memory=true.** Cron jobs têm `skip_memory=true` por padrão — a seção `MEMORY` não é injetada no prompt do agente. O tool `memory` não tem action `list`. O agente não consegue ver quais entradas existem para decidir o que remover. **Soluções:** (a) incluir as entradas da memória explicitamente no prompt do cron job, ou (b) pular o offload em cron e executar manualmente quando necessário.

⚠️ **Ciclo pode morrer no meio e deixar working directory sujo.** O cron job tem timeout — se o ciclo não completa, SKILL.md ficam modificados mas sem commit, index.md desatualizado, log.md sem entrada. **Recuperação:** **Recuperação:**

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

⚠️ **Verificar index.md contra disco após regeneração.** Ao regenerar o index.md via `write_file` (>30% mudança), é fácil incluir skills que existiam no index antigo mas não têm SKILL.md no disco. Sempre cruzar a saída final contra `find . -name SKILL.md -not -path './.archive/*'` para garantir que cada entrada no index.md corresponde a um arquivo real. Skills sem SKILL.md no disco geram erros no gráfico e confundem agentes futuros.

⚠️ **Diretório read-only impede patches/write_file.** Quando `patch` ou `write_file` falha com "Permission denied" ao criar arquivo temp (`.hermes-tmp.*`), o diretório da skill pode estar read-only (modo `dr-xr-xr-x` / 555). Verificar com `stat <dir> | grep Access`. Corrigir com `chmod u+w <dir>`. Arquivos 444 individuais usam `chmod 664 <file>`.

⚠️ **`.curator_backups/` não deve ser versionado.** O diretório `.curator_backups/` na raiz contém backups automáticos de skills. Adicionar ao `.gitignore`: `echo '.curator_backups/' >> .gitignore && git add .gitignore`.

⚠️ **`audit-descriptions.py` precisa do SKILLS_DIR correto.** O script em `skills-repo-curator/scripts/audit-descriptions.py` precisa de SKILLS_DIR = 4 níveis acima do script (scripts → skills-repo-curator → software-development → skills/), não 3. Se só escaneia poucos arquivos, o path está errado. Corrigir com:

```python
SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
```

⚠️ **Patch falha na auditoria de descrições: diagnostique antes de re-aplicar.** Quando `patch` falha com "Could not find a match for old_string" durante o passo 4 do Update (auditoria de descrições), NÃO tente re-aplicar cegamente com um old_string diferente. Leia o SKILL.md atual (`read_file`), compare o texto real com o que você esperava — divergências comuns:

- Em dash `—` (unicode U+2014) vs `--` vs `-` hífen simples
- Palavras extras ou faltando (ex: `project pipeline` vs só `pipeline`)
- Whitespace invisível no final da linha
- Acentos ou caracteres especiais (ex: `Hephaistos` com acento vs sem)
- Descrições multi-linha sem blank line separator (o parser de FM simples não captura o valor completo)

Procedimento:
1. `read_file` no SKILL.md problemático — veja o texto **exato** da linha `description:`
2. Copie o trecho real como `old_string` no patch
3. **Explique o diagnóstico ao usuário** antes de aplicar a correção (ele prefere entender o problema primeiro)
4. Só então aplique o `patch` com o old_string verificado