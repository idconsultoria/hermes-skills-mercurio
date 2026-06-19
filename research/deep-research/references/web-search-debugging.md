# Debugging do `web_search` Tool

> Documentado em sessão 18 de junho de 2026, após sequência de 4 chamadas retornando arrays vazios que pareciam indicar backend offline, mas a causa real era má-formação de query.

## Modos de Falha do `web_search`

| Sintoma | Causa Provável | Diagnóstico | Solução |
|---------|----------------|-------------|---------|
| `{"data": {"web": []}}` em **toda** query | Backend de search offline | Tente 2-3 queries com termos totalmente diferentes | Use `browser_navigate` para Bing/DuckDuckGo direto |
| `{"data": {"web": []}}` em **uma** query com aspas | Bing interpretou como frase exata e priorizou dicionário | Busque o termo sem aspas | Remova aspas para nomes próprios |
| `{"data": {"web": []}}` em query muito longa/nichada | Query fora do distribution | Reformule para mais simples e broad | Adicione 1-2 termos genéricos (ex: "case study", "implementation") |
| Retorna resultados não relacionados | Query ambígua | Inspecione títulos para drift semântico | Refine com qualificadores |

## Caso Específico: Aspas Duplas em Nomes Próprios

**Pattern identificado:** buscar por `"Reclaim.ai"` (com aspas duplas) fez o Bing interpretar como frase exata e retornar:

- Definições de dicionário da palavra "reclaim"
- Páginas com a string literal "Reclaim" em texto
- Zero resultados sobre a ferramenta Reclaim.ai

**Root cause:** Bing priorizou phrase-match exato sobre relevance. O ponto em "Reclaim.ai" e a capitalização quebraram a busca de dicionário.

**Regra de bolso:**

| Use aspas | NÃO use aspas |
|----------|---------------|
| Frases exatas longas (5+ palavras) | Nomes próprios com pontos (Reclaim.ai, U.S.A.) |
| Títulos conhecidos ("Process Reinvention Ladder") | Termos técnicos com símbolos (C++, .NET) |
| Queries onde sinônimos seriam ruído | Termos com capitalização que o motor não conhece |

**Workaround quando precisar do termo exato:** combine com 1-2 palavras adicionais:
- ❌ `"Reclaim.ai"`
- ✅ `Reclaim.ai case study implementation`
- ✅ `"AI calendar scheduling" Reclaim` (aspas só na frase)

## Workflow de Debugging Quando `web_search` Falha

```python
# 1. Tente 2-3 queries com termos totalmente diferentes (não reformule a mesma)
web_search("AI in healthcare 2025")  # genérico
web_search("enterprise AI productivity 2025")  # ângulo diferente

# 2. Se tudo retorna vazio, é backend offline
# → Switch para browser_navigate direto para Bing
browser_navigate("https://www.bing.com/search?q=...&setlang=en-us")

# 3. Se só uma query falha, é a query
# → Reformule sem aspas, sem pontos, com 1-2 qualificadores
```

## Sinal de User Frustrado: "Debugue sua ferramenta"

Quando o user diz "debugue X" ou "teste Y", significa:
- A primeira tentativa falhou
- O user suspeita da ferramenta, não do pedido
- Quer prova concreta de que o diagnóstico está correto
- **Resposta certa:** rode 2-3 testes rápidos e mostre evidência, depois corrija

Errado: perguntar "qual é o problema que você está tendo?" ou assumir que o backend está quebrado.
Certo: rodar 2-3 queries com formatos diferentes, mostrar a saída, e identificar a causa.

## Quando NÃO Capturar Como Lição de Skill

Não capture como regra durável:
- "Backend está offline" — situação temporária
- "Bing mudou o algoritmo" — atualização específica
- "Minha API key expirou" — setup issue

Capture:
- "Aspas duplas em nome próprio com ponto trava o Bing" — heurística estável
- "Quando 1 query falha, reformule; quando todas falham, é backend" — workflow de debugging
- "User frustrado quer teste concreto, não pergunta de volta" — preferência de comunicação
