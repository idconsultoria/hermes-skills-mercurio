# Vault Construction from Research — Batch Engrama Creation

> Workflow completo para construir um vault Obsidian a partir de dados de pesquisa estruturados (JSON, HTML extraído, etc.). Usado em Sprints 1-3 do vault Tácio.

## Contexto

Pesquisas largas (97 coleções Awwwards em 170KB JSON, 100+ imagens de carroseis, pesquisa Lovable 28KB) NÃO devem ser processadas manualmente. O workflow correto usa processamento em lote.

## Workflow Completo

### Fase 1: Extrair dados estruturados

**Entrada:** Arquivo de pesquisa grande (JSON, markdown, etc.)
**Ferramenta:** `jq` para JSON, `execute_code` com Python para parsing complexo

```bash
# Verificar estrutura do JSON
jq '.sections | keys[]' collections-data.json
jq '.stats.top_by_items[] | {name, items, followers}' collections-data.json

# Extrair todas as collections para processamento
cat collections-data.json | jq -c '.sections[] | to_entries[] | .value.collections[]' > all-collections.jsonl
wc -l all-collections.jsonl
```

**Saída:** JSON lines (`.jsonl`) ou JSON array estruturado salvo em `/home/taciobrito/.hermes/<projeto>/`

### Fase 2: Criar engramas em lote via subagentes

**Divisão:**Não criar todos os engramas de uma vez — dividir em batches de 3-4 tarefas paralelas via `delegate_task`.

**Configuração de cada subagente:**
- `context`: caminho do arquivo de dados, formato esperado, convenções de nomenclatura
- `goal`: criar N engramas de um tema/cluster específico
- `toolsets`: `["terminal", "file"]`
- `output`: escrever diretamente em `/home/taciobrito/Documents/Obsidian Vault/engramas/<cluster>/`

**Exemplo de divisão (Awwwards 97 coleções → 11 engramas):**

| Batch | Foco | Engramas |
|-------|------|----------|
| 1 | Design Visual & Estilo (17 coleções) | ref-awwwards-design-visual.md |
| 2 | Animação & Movimento (13 coleções) | ref-awwwards-animation-motion.md |
| 3 | UX & UI Patterns (19 coleções) | ref-awwwards-ux-ui-patterns.md |
| 4 | Tecnologia & Dev (9 coleções) | ref-awwwards-technology.md |
| 5 | Indústria & Nichos (13 coleções) | ref-awwwards-industry-niches.md |
| 6 | Ferramentas & Recursos (7 coleções) | ref-awwwards-tools-resources.md |
| 7 | Conteúdo & Editorial (10 coleções) | ref-awwwards-content-editorial.md |
| 8 | Portfólios & Agências (5 coleções) | ref-awwwards-portfolios-agencies.md |
| 9 | Top Collections (20 coleções) | ref-awwwards-top-collections.md |
| 10 | Mega Analysis + Studio Showcase + Roadmap | ref-awwwards-mega-analysis.md + ref-awwwards-studio-showcase.md + ref-awwwards-collection-roadmap.md |

### Fase 3: Verificar e atualizar index

```bash
# Listar engramas criados
ls -la ~/Documents/"Obsidian Vault"/engramas/referencias/ | grep awwwards

# Contar por cluster
find ~/Documents/Obsidian\ Vault/engramas -name "*.md" ! -name "index.md" | wc -l
```

**Patch no index.md:**
1. Atualizar contagem do cluster (ex: 19 → 31 engramas em referências)
2. Listar todos os novos engramas com descrição
3. Atualizar estatísticas (total engramas, wikilinks únicos)

### Fase 4: Atualizar SPRINTS.md

Após cada sprint completa:
1. Patch timeline table com status ✅ e resultado (+N engramas)
2. Adicionar seção nova sprint com tarefas executadas, engramas criados, métricas
3. Atualizar estatísticas finais (total engramas, notas vault, wikilinks)

## Formato Engrama de Pesquisa

Cada engrama criado de pesquisa DEVE incluir:

```markdown
---
tags: [...]
created: YYYY-MM-DD
cluster: referencias
tipo: engrama
---

# Ref-Awwwards-[Nome]: Título Descritivo

> Descrição em uma linha.

## Dados Coletados

| Campo | Valor |
|-------|-------|
| Total de itens | N |
| Seguidores | +N |
| Curador | nome |

## Coleções Principais

| # | Nome | Items | Descrição |
|---|------|-------|-----------|
| 1 | Nome | N | Descrição |

## Exemplos Reais

- **Site Name** — O que faz, técnica usada
- ...

## Recursos e Tecnologias

- Ferramenta/ técnica 1
- Ferramenta/ técnica 2

## 🔗 Links

### Mesmo cluster
- [[ref-outro-engrama]] — descrição

### Cross-cluster
- [[engrama-outro-cluster]] — descrição

### Opostos/Tensões
- [[engrama-alternativa]] — quando NÃO usar
```

## Métricas das Sprints Realizadas

| Sprint | Tema | Engramas | Total Vault | Wikilinks |
|--------|------|----------|-------------|-----------|
| 1 | Fundação | +25 | 168 | 104 |
| 2 | Referências Visuais + Awwwards | +29 | 206 | 159 |
| 3 | Segurança & Cyber Defesa | +17 | 223 | 177 |
| 4 | Peachweb | +3 | 226 | 180 |
| 5 | Criadores/Cursos | +6 | 232 | 186 |
| 6 | Skills/Conectores | +2 | 234 | 188 |
| 7 | Limpeza/Verificação | 0 | 301 | 188 |

**Total acumulado:** 237+ engramas, 301 notas, 188 wikilinks (Sprint 7 completa)

## Evitar

- **Não criar engramas manualmente um por um** — usar batches e scripts
- **Não deixar de atualizar o index** — engramas sem entry no index são difíceis de encontrar
- **Não ignorar a estrutura de 3 links** — todo engrama precisa Same Cluster + Cross Cluster + Opostos
- **Não misturar clusters** — cada engrama vai no cluster correto (design/frontend/infra/etc.)

## Ferramentas de Suporte

```bash
# jq para JSON
jq '.key' file.json                    # extrair valor
jq '.sections | keys[]' file.json      # listar chaves
jq -c '.array[]' file.json             # JSON lines
jq '.stats.top_by_items[]' file.json   # array ordenado

# Python para parsing complexo
python3 -c "
import json
with open('file.json') as f:
    data = json.load(f)
for item in data['sections'].values():
    for coll in item['collections']:
        print(json.dumps(coll))
" > output.jsonl
```