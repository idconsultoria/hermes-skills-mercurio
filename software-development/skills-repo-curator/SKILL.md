---
name: skills-repo-curator
description: "Gerencia o repositório Git de skills do Hermes com ciclo evolve de consolidação MECE.\n\nLoad this skill when the skills repo needs maintenance — evolve cycles (analysis, merge, delete, report, commit), index.md/log.md/reports updates, memory offload, orphan review, and AGENTS.md upkeep. Executes the full consolidation lifecycle: analyze portfolio, propose merges, delete redundant skills, review orphans, write reports, offload learned facts to skills, and commit changes."
---

# Skills Repository Curator

> Gerencia o skills repo em `/opt/data/skills/` com controle de versão Git.
> Ciclo principal: `evolve` — análise → plano → execução → orphan review → report → offload → commit.

## Trigger
- User diz "gerencie suas skills", "limpe as skills", "rode evolve", "consolide skills"
- User pede para revisar, fundir, deletar ou organizar skills
- Ao final de uma sessão com múltiplas correções de workflow que merecem ser capturadas

## Estrutura do Repositório

```
skills/
├── AGENTS.md           ← Regras, operações, prefixos de log
├── index.md            ← Catálogo orientado a conteúdo de todas as skills
├── log.md              ← Diário cronológico append-only
├── reports/            ← Planos (pré) e relatórios (pós) de cada ciclo evolve
│   ├── evolve-<YYYY-MM-DD-HHMM>.md       ← plano
│   └── evolve-<YYYY-MM-DD>-report.md     ← relatório denso pós-execução
├── .gitignore          ← Cache files excluded
├── <category>/
│   └── <skill-name>/
│       ├── SKILL.md
│       └── references/
├── templates/          ← (opcional) boilerplate
└── scripts/            ← (opcional) validadores
```

## ⚠️ Regra Absoluta: index.md é Território de LLM

O arquivo `index.md` **não pode ser editado por scripts** — nem Python, nem sed, nem awk, nem regeneração automática. Toda edição no index.md deve passar por ferramentas de agente LLM (`read_file`, `write_file`, `patch`), garantindo que cada decisão editorial passe por julgamento humano-assistido.

**Scripts são permitidos para tarefas de apoio** — análise de conexões, extração de metadados dos SKILL.md, geração do grafo HTML, relatórios. O output desses scripts informa o agente, que então edita o index.md manualmente.

**Violação detectada:** Se uma sessão anterior fabricou a edição do index.md via script, reverter imediatamente e refazer manualmente com patch.

## ⚠️ Pattern: Batch-Report-Then-Apply (Evita File Conflict)

Quando múltiplos subagentes precisam modificar o index.md (ex: adicionar relações para centenas de skills), **NUNCA** mande todos escreverem no index.md diretamente — eles vão conflitar e corromper o arquivo.

**Padrão correto:**

1. Cada subagente produz um **relatório de saída** (ex: `relations-batch1.md`) com as modificações a fazer
2. Os relatórios são salvos via `write_file` em `/opt/data/skills/`
3. Um único subagente (ou o agente principal) lê os relatórios e aplica **todos os patches sequencialmente** no index.md

Isso garante atomicidade e evita corrupção do arquivo por escrita concorrente.

## Ciclo Evolve (14 passos)

**⚠️ Batch-Report-Then-Apply:** Quando múltiplos subagentes precisam modificar o index.md (ex: adicionar relações para dezenas de skills), **NUNCA** mande todos escreverem no index.md diretamente — eles vão conflitar. Cada subagente produz um **relatório de saída** (ex: `relations-batch1.md`) com as modificações a fazer. Um único agente principal então lê os relatórios e aplica **todos os patches sequencialmente** no index.md. Isso garante atomicidade e evita corrupção do arquivo por escrita concorrente.

### 1. Lista mudanças desde último ciclo
```bash
git diff --stat HEAD~1 HEAD || git log --oneline -1
```
Compare estado atual com o último commit do Git para detectar skills adicionadas, removidas ou com metadados alterados. A index.md é regenerada do zero e a diff é comparada com o último commit para extrair resumo de mudanças.

### 2. Atualiza index.md com mudanças
Regenera o catálogo completo escaneando todos os `SKILL.md` no disco. Inclui: nome, título, tamanho, resumo (~80 chars), descrição completa, categoria, e relações.

**Para relações semanticamente inferidas (não regex):** usar o padrão de subagentes com análise **depth-1** — cada subagente lê a skill principal **e** cada skill candidata a relação (lendo o SKILL.md de ambos os lados), confirmando a conexão semântica antes de declará-la. 3 subagentes analisam ~28 skills cada em paralelo, cada um produzindo um **relatório de saída** (`relations-batchN.md`) em vez de editar o index.md diretamente. Um agente central então consolida todos os patches no index.md. Isso evita conflitos de escrita concorrente e garante precisão bilateral. Resultado: ~140+ arestas em 75+ skills com precisão validada nos dois sentidos.

**⚠️ Não parar no primeiro merge óbvio.** Se uma skill parece alvo óbvio de merge (ex: coding agents), isso não é desculpa para encerrar a análise. O ciclo evolve deve analisar **todas** as skills, não apenas as que têm alvos evidentes. O usuário pode chamar a atenção se isso acontecer.

**Formato exato do index.md:** cada skill segue o template documentado em `references/index-md-spec.md` — bullet metadata + description paragraph + relations list.

### 3. Registra no log.md
Entrada única com prefixo `## [YYYY-MM-DD] update | ...`

### 4. Stage + commit (checkpoint pré-plano)
```bash
git add -A && git commit -m "update: pre-evolve checkpoint"
```

### 5. Estuda index.md e elabora plano MECE
Analisa todo o portfólio buscando:
- **Cluster de redundância:** skills que cobrem o mesmo território (ex: 5 newsletters)
- **Skills mortas:** ferramentas sem GPU, CLI que não existe mais, utilidades que nunca foram usadas
- **Sobreposição de trigger:** skills que disparam no mesmo comando do usuário
- **Alinhamento com memória:** facts procedurais na memória que deveriam estar em skills

**Critério de merge:** Duas skills conectadas (similar/uses) só devem permanecer separadas se descreverem fluxos de trabalho realmente distintos — que não podem ou não faz sentido incorporar um ao outro. Se ambas descrevem o mesmo domínio com padrões de orquestração idênticos, devem ser fundidas. Se operam em níveis de abstração diferentes (receita técnica vs workflow estratégico) ou com toolchains fundamentalmente distintas, devem permanecer separadas. A conexão no grafo (`similar`, `uses`) é evidência, não sentença — o julgamento final é sobre o workflow descrito.

**Ferramenta:** Usar `delegate_task` com 3 subagentes paralelos para ler skills em lotes e determinar merge viability. Cada subagente lê ~28 skills, analisa semanticamente, retorna JSON com recomendações.

Regra MECE: cada skill com responsabilidade única. Se duas skills compartilham o mesmo domínio com padrões idênticos, é candidato a merge.

### 6. Salva plano em reports/evolve-<YYYY-MM-DD-HHMM>.md
Documenta: alvos de delete, alvos de merge, impacto estimado (skills perdidas vs mantidas).

### 7. Executa o plano
Para cada operação:
- **Delete:** `skill_manage(action='delete', name=..., absorbed_into=...)` — sempre registrar o absorbed_into para rastreabilidade
- **Merge:** ler skill alvo + skill fonte → construir novo conteúdo mesclado → `skill_manage(action='edit')` no alvo → delete da fonte com absorbed_into
- **Limpeza de aprendizado específico:** Durante merges, remover das skills:
  - Debug transcripts de sessões passadas
  - Error messages específicas de um bug que já foi resolvido
  - Workarounds temporários que não são padrão reutilizável
  - Timestamps de eventos únicos, nomes de arquivos temporários
  Manter: padrões gerais, workflows reutilizáveis, comandos estáveis.
- **Auditoria de descrições:** Verificar se cada skill afetada tem frontmatter `description` adequado — resumo de 1 linha (~80 chars) seguido de parágrafo descritivo completo. Skills com descrições ausentes, truncadas ou genéricas demais devem ser corrigidas para alimentar bem o index.md. Skills consolidadas (merges) têm prioridade.
- **Limpeza de disco:** `rm -rf` dos diretórios órfãos (referências, templates, scripts das skills deletadas)

**⚠️ PII em skills — auditar no passo 7.**

### 8. Revisa skills órfãs
Skills sem relações no grafo. Para cada uma:
- Tenta encontrar conexão semântica com outras skills (lendo ambos os SKILL.md — profundidade 1). Se encontrar, adiciona relação bilateral no frontmatter e no index.md.
- Se não encontrar conexão, avalia se a skill é importante o suficiente para existir isolada. Skills genuinamente de nicho (API de terceiros, CLI específico, data source exótico) podem ficar órfãs com justificativa.
- Se a skill não tem conexão E não é claramente importante, considera merge com skill genérica ou delete.
- **Target:** 0 órfãos. Toda skill deve ter pelo menos uma relação.

**⚠️ Formato `|-` quebra o grafo.** O script `generate_graph.py` usa regex `r"- \`(\w+)\` → \`(.+)\`"` para parsear relações. Se uma relação começar com `|- ` (pipe-dash) em vez de `- ` (só dash), o regex não captura. Verificar antes de gerar o grafo: `grep "|- \`" index.md`. Se existir, corrigir com `patch(replace_all=True, old_string='|- \`', new_string='- \`')`.

### 9. Offload — limpa memória de fatos procedurais
Regra: **memória** = preferências do usuário + fatos estáveis do ambiente. **Skills** = procedimentos. Remover da memória persistente entradas que já estão documentadas em skills — configurações de ferramentas, versões, paths de instalação, schedules de cron, detalhes de API. Manter: preferências de estilo, IDs de grupos/contas, regras de permissão, convenções de projeto.

### 10. Escreve relatório denso pós-evolução
Arquivo: `reports/evolve-<YYYY-MM-DD>-report.md`
Conteúdo:
- Estado inicial vs final (skills, memória, chars)
- Tabela de deletions com motivo
- Tabela de merges com conteúdo absorvido
- Mudanças no AGENTS.md / index.md / log.md
- Resultado do offload (o que saiu, o que ficou)
- Git diff summary

### 11. Atualiza index.md pós-transformação
Regenera o catálogo completo com as skills pós-merge/delete.

### 12. Registra no log.md com prefixo `evolve`
Entrada de 1 linha detalhando o que foi feito:
```
## [YYYY-MM-DD] evolve | <resumo: skills N→M, merges, deletes, offload>
```

### 13. Gera grafo HTML interativo
Ao final de cada ciclo evolve, gerar o grafo D3.js para visualização das relações:

```bash
cd /opt/data/skills
python3 scripts/generate_graph.py
```

O script extrai dados do index.md (com fallback para LLM-inferred JSON se o index não tiver relações), constrói JSON com nodes/edges, e injeta no template `skills_graph_template.html` → `skills_graph.html`.

Features do grafo:
- Nodes coloridos por categoria (14 cores), tamanho proporcional ao arquivo
- Similar: linha tracejada cinza | Uses: linha sólida azul com seta
- Hover: destaca nó + conexões | Click: modal com summary, description, relations
- Filtro por texto, zoom/pan, drag, mobile-responsive, resize handler
- Deduplicação de arestas bidirecionais (parent/child, uses/used_by)

### 14. Stage + commit final
```bash
cd /opt/data/skills
git add -A
git commit -m "evolve: <resumo de uma linha>"
```

## Log Entries — Formato

Toda entrada no log.md deve ser concisa mas detalhada — 1-3 linhas no máximo, começando com o formato parseável:

```markdown
## [YYYY-MM-DD] <prefixo> | <resumo de 1 linha detalhando o que foi feito na operação>
```

O resumo de 1 linha deve conter detalhes específicos o suficiente para que `grep "^## \[" log.md | tail -5` reconte a história completa. Exemplos reais:

```
## [2026-06-10] evolve | Merged 11 skills into 4, deleted 10 skills. 113→92. Offload pending.
## [2026-06-10] offload | Memory cleaned: 11→6 entries (94%→47%). Procedural facts moved to skills.
## [2026-06-10] update | AGENTS.md updated: evolve steps now include report writing
```

Prefixos:
| Prefixo | Quando |
|---------|--------|
| `update` | Sincronização de index.md, mudanças manuais |
| `evolve` | Ciclo completo de consolidação (plano → execução → report → offload → commit) |
| `offload` | Limpeza de memória — remoção de fatos procedurais redundantes com skills |

A entrada deve ser detalhada o suficiente para que um `tail -5` no log reconte a história, mas concisa — 1-3 linhas no máximo.

## Relatórios Pós-Evolve

Relatórios densos são mandatórios após cada ciclo evolve. Eles devem conter:
- Métricas comparativas (antes/depois) em tabela
- Tabela de deletions com motivo individual
- Tabela de merges com conteúdo específico absorvido
- Impacto no index.md, AGENTS.md, log.md
- Resultado do offload de memória
- Git log do ciclo

## Verification
```bash
cd /opt/data/skills && git log --oneline -5
wc -l index.md log.md
ls reports/
```

## Grafo Interativo (D3.js)

Após regenerar o index.md com relações semanticamente inferidas, gerar um grafo interativo HTML:

```bash
cd /opt/data/skills
python3 scripts/generate_graph.py         # HTML + JSON
python3 scripts/generate_graph.py --json  # JSON only
```

O script lê o index.md para relações; se não encontrar (fallback), usa `/opt/data/skills_relations_merged.json` (LLM-inferred).

Arquivos:
- `scripts/generate_graph.py` — script standalone
- `skills_graph_template.html` — template D3.js com placeholder `__DATA_PLACEHOLDER__`
- `skills_graph.html` — output final (~55KB)

Features: nodes por categoria, arestas tracejadas (similar) e sólidas (uses), modal com summary+description, filtro, zoom, mobile.

## Pitfalls

⚠️ **Relations regex vs LLM:** A primeira passada de geração de relações (scan automatizado por regex) produz relações fracas. Sempre usar o padrão de subagentes paralelos (`references/llm-relations-inference.md`) para inferência semântica. Resultado: 207 relações semanticamente corretas vs ~138 heurísticas imprecisas.

⚠️ **index.md pode perder relações na regeneração.** O script de regeneração do index.md pode não incluir relações se não for explicitamente instruído. O grafo e a análise do evolve dependem delas. Solução: manter `/opt/data/skills_relations_merged.json` como fallback. O `generate_graph.py` já implementa o fallback automático — se o index.md tiver 0 relações, carrega do JSON.

⚠️ **Log entries devem ser resumos de UMA LINHA.** Formato: `## [YYYY-MM-DD] prefixo | resumo detalhado`. O resumo deve incluir números, ações, impacto. Exemplo correto: `## [2026-06-10] evolve | Merged 11 skills into 4, deleted 10. 113→92.` Exemplo fraco: `## [2026-06-10] evolve | Updated skills.`

⚠️ **Offload ≠ limpeza de skills.** Offload remove fatos procedurais da memória persistente. Limpeza de aprendizado excessivamente específico DENTRO das skills acontece no passo 7 (execução). Não confundir.

⚠️ **Descrições de skills são auditadas no passo 7**, não depois. Skills consolidadas (merges) têm prioridade na auditoria de description. Skills não modificadas podem ser corrigidas em lote se tiverem descrições pobres.

⚠️ **Formato `|-` quebra o grafo.** O script `generate_graph.py` espera `- \`type\` → \`path\`` — se um subagente escrever `|- \`type\` → \`path\`` (pipe-dash), a aresta não é capturada. Verificar SEMPRE antes de gerar o grafo: `grep "|- \`" index.md`. Se existir, corrigir com `patch(replace_all=True, old_string='|- \`', new_string='- \`')`.

⚠️ **Não parar no primeiro merge óbvio.** Quando um merge parece evidente (ex: 3 coding agents com mesmo padrão de orquestração), o agente tende a declarar vitória e parar. Isso é erro — o ciclo evolve deve analisar **todas as skills**. O usuário explicitamente pediu "skill a skill" e detectou o shortcut. Mesmo que o merge seja válido, a análise completa continua sendo necessária.

- **Limpeza de disco:** `rm -rf` dos diretórios órfãos (referências, templates, scripts das skills deletadas)

**⚠️ PII em skills — auditar no passo 7.** Durante a auditoria de descrições e limpeza de detalhes efêmeros, verificar também: números de telefone reais, usernames (ex: `gustavomello9600`), JIDs/LIDs de WhatsApp, IPs públicos, nomes de grupos reais ("IA que Funciona"), e marcas/empresas do usuário ("ID Consultoria"). Skills são artefatos compartilháveis — dados pessoais devem ser substituídos por `[REDACTED]` ou placeholders genéricos.
