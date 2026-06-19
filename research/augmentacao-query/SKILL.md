---
name: augmentacao-query
description: "Busca semântica nas 97 soluções de Aumentação de Processos com IA via Vulcano MCP. Use esta skill quando quiser encontrar soluções relevantes por significado, ler documentos completos, ou navegar por setor."
category: research
metadata:
  hermes:
    related_skills: [vulcano, aumentacao-referencias, hephaistos, deep-research]
---

# Aumentação — Consulta ao Vault de Soluções

## Trigger

Use esta skill sempre que o usuário perguntar sobre **soluções de aumentação de processos com IA**, pedir para **pesquisar casos concretos**, ou quiser **navegar na base de referências** de 97 soluções documentadas.

## Ferramentas disponíveis

O Vulcano MCP expõe estas ferramentas (use diretamente):

| Ferramenta | Descrição | Quando usar |
|---|---|---|
| `vulcano_search(query, top_k=5)` | Busca semântica FAISS | Pergunta vaga, conceitual, exploratória |
| `search_engrams(query, cluster="")` | Full-text híbrido | Palavra exata que deve aparecer no texto |
| `read_engram(path)` | Lê solução completa | Usuário quer detalhes de uma solução específica |
| `list_cluster(cluster="")` | Lista setores ou soluções de um setor | Usuário quer filtrar por setor |
| `follow_links(path, depth=1)` | Segue wikilinks (não usado neste vault) | — |
| `vulcano_hot()` | Top soluções mais acessadas | Ver o que está sendo mais usado |
| `vulcano_unused(days=30)` | Soluções não acessadas | Manutenção da base |

## Workflow recomendado

### 1. Busca exploratória (usuário não sabe o que quer)

```python
# 1. Busca semântica — captura intenção
vulcano_search("reduzir tempo de documentação em saúde")

# 2. Lê o resultado mais relevante
read_engram("abridge-documentacao-de-enfermagem")

# 3. Se quiser afunilar por setor
list_cluster("saude")
```

### 2. Busca direcionada (usuário sabe o setor)

```python
# 1. Ver soluções de um setor
list_cluster("vendas-b2b")

# 2. Busca semântica dentro do setor
search_engrams("qualificação de leads", "vendas-b2b")

# 3. Lê a melhor
read_engram("slug-da-solucao")
```

### 3. Síntese de múltiplas soluções

```python
# Busca ampla
resultados = vulcano_search("customer success retenção", top_k=5)
# → Leia os top 3 e sintetize para o usuário
```

## Setores disponíveis (clusters)

```
saúde, vendas-b2b, consultoria, seguros, jurídico,
customer-success, customer-service, finanças, educação,
marketing/seo, operações/productivity, rh, produtividade
```

Para listar todos: `list_cluster()`

## Estrutura de cada solução

Cada arquivo `.md` em `solucoes/` segue:

```markdown
---
id: slug-da-solucao
titulo: Nome da solução
case_pai: Empresa + Fornecedor
categoria: A (reengenharia) ou B (otimização)
tipo: I (agente), II (assistente), III (automação)
setor: Saúde | Vendas B2B | ...
ferramentas: [lista de ferramentas]
fonte: URL da pesquisa
data_pesquisa: 2026-06-18
human_in_the_loop: sim
ganho_principal: ...
processo_original: "..."
processo_augmentado: "..."
---

## Contexto
## A Solução em Detalhe
## Resultados Obtidos
## Como Replicar
## Onde Seria Relevante
```

## ⚠️ Terminologia crítica: soluções ≠ engramas

O vault `aumentacao-referencias/` contém **97 documentos de referência** (casos reais de augmentação), não engramas no sentido Hephaistos. Engramas seriam **skills/padrões acionáveis** que um agente executa. As soluções são **conhecimento para consulta** — a busca semântica encontra significado, não dispara ações.

- `write_engram` está desabilitado propositalmente — vault read-only.
- Não há wikilinks neste vault — `follow_links` retorna conteúdo puro.
- Cluster names compostos viram `customer-success---saas-b2b` (hífen triplo).

## Pitfalls

- **Preferir `vulcano_search` sobre `search_engrams`** para perguntas abertas — FAISS captura significado, não palavra exata.
- **Usar `search_engrams` para busca booleana** — quando o usuário cita um termo técnico específico (ex: "alucinação", "HIPAA").
- **A busca FAISS não entende operadores booleanos** — para "saúde E vendas", faça duas buscas separadas.

## Exemplos rápidos

```
vulcano_search("agente autônomo para atendimento ao cliente")
vulcano_search("redução de custos com IA generativa", top_k=3)
list_cluster("seguros")
read_engram("klarna-humano-de-volta-em-casos-sensiveis")
```
