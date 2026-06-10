---
name: skills-repo-curator
description: Gerencia o repositório git de skills do Hermes — ciclo evolve de consolidação MECE, index.md/log.md/reports, offload de memória, e manutenção de AGENTS.md. Executa o processo completo de análise, merge, delete, relatório e commit.
---

# Skills Repository Curator

> Gerencia o skills repo em `/opt/data/skills/` com controle de versão Git.
> Ciclo principal: `evolve` — análise → plano → execução → report → offload → commit.

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

## Ciclo Evolve (12 passos)

### 1. Lista mudanças desde último ciclo
```bash
git diff --stat HEAD~1 HEAD || git log --oneline -1
```
Compare estado atual com o último commit do Git para detectar skills adicionadas, removidas ou com metadados alterados. A index.md é regenerada do zero e a diff é comparada com o último commit para extrair resumo de mudanças.

### 2. Atualiza index.md com mudanças
Regenera o catálogo completo escaneando todos os `SKILL.md` no disco. Inclui: nome, título, tamanho, resumo (~80 chars), descrição completa, categoria, e relações.

**Para relações semanticamente inferidas (não regex):** usar o padrão de subagentes paralelos documentado em `references/llm-relations-inference.md`. 3 subagentes leem ~31 skills cada e retornam JSON com relações do tipo `similar`, `uses`, `used_by`, `parent`. O merge gera ~200 relações em 70+ skills com precisão muito superior à heurística automatizada.

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

Regra MECE: cada skill com responsabilidade única. Se duas skills compartilham >40% do conteúdo ou gatilho, é candidato a merge.

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
  - Caminhos absolutos que só existem neste ambiente
  Manter: padrões gerais, workflows reutilizáveis, comandos estáveis, regras de formato.
- **Limpeza de disco:** `rm -rf` dos diretórios órfãos (referências, templates, scripts das skills deletadas)

### 8. Offload — limpa memória de fatos procedurais
Regra: **memória** = preferências do usuário + fatos estáveis do ambiente. **Skills** = procedimentos.
Remover da memória persistente entradas que já estão documentadas em skills — configurações de ferramentas, versões, paths de instalação, schedules de cron, detalhes de API.
Manter: preferências de estilo, IDs de grupos/contas, regras de permissão, convenções de projeto.
Isso NÃO inclui limpeza de conteúdo de skills — aprendizado excessivamente específico é removido no passo 7 (execução do plano), não no offload.

### 9. Escreve relatório denso pós-evolução
Arquivo: `reports/evolve-<YYYY-MM-DD>-report.md`
Conteúdo:
- Estado inicial vs final (skills, memória, chars)
- Tabela de deletions com motivo
- Tabela de merges com conteúdo absorvido
- Mudanças no AGENTS.md / index.md / log.md
- Resultado do offload (o que saiu, o que ficou)
- Git diff summary

### 10. Atualiza index.md pós-transformação
Regenera o catálogo completo com as skills pós-merge/delete.

### 11. Registra no log.md com prefixo `evolve`
Entrada de 1 linha detalhando o que foi feito:
```
## [YYYY-MM-DD] evolve | <resumo: skills N→M, merges, deletes, offload>
```

### 12. Stage + commit final
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

1. **Extrair dados** do index.md → JSON com nodes (id, label, title, size, category, summary, description) e edges (source, target, type)
2. **Deduplicar arestas:** parent/child e uses/used_by viram uma única aresta direcionada
3. **Gerar HTML** com D3.js force-directed graph:
   - Nodes coloridos por categoria, tamanho proporcional ao arquivo
   - Similar: linha tracejada cinza
   - Uses/used_by: linha sólida azul com seta
   - Hover: destaca nó + conexões
   - Click: modal com summary, description, relations
   - Filtro por texto, zoom/pan, drag, mobile-responsive
4. **Template:** injetar JSON no placeholder `__DATA_PLACEHOLDER__` do template em `templates/graph.html`

Comando:
```bash
python3 scripts/build_graph.py  # parse index.md → graph_data.json
python3 scripts/inject_graph.py  # merge template + data → skills_graph.html
```

Arquivos de output: `/opt/data/skills_graph.html` (standalone, ~55KB)

## Pitfalls

⚠️ **Relations regex vs LLM:** A primeira passada de geração de relações (scan automatizado por regex no conteúdo) produz relações fracas — menciona skills que nem sempre são semanticamente relacionadas. Sempre que possível, usar o padrão de subagentes paralelos (`references/llm-relations-inference.md`) para inferência semântica de relações. A diferença é visível: 207 relações semanticamente corretas em 76 skills vs ~138 heurísticas imprecisas.

⚠️ **Log entries devem ser resumos de 1 linha detalhando a operação.** Não apenas "updated index.md" — incluir números, merges, deletes, impacto. O log é parseável com `grep "^## \[" log.md | tail -5` e deve recontar a história.


