# Pesquisa Multi-Fonte para Relatórios HTML

Metodologia provada nesta sessão (Jun 2026) para quando `web_search` retorna vazio.

## Fallback Chain

```
1. web_search(query) → se vazio:
2. web_extract(urls_conhecidas) → URLs oficiais, docs, repos
3. browser_navigate(YouTube) → busca visual, extrai resultados
4. web_extract(Anthropic Blog, GitHub) → artigos específicos
```

## Fontes Prioritárias (por tipo de conteúdo)

| Tipo | Fonte | URL Base |
|------|-------|----------|
| Docs oficiais MCP | modelcontextprotocol.io | `/docs/concepts/architecture`, `/docs/develop/` |
| Especificação | spec.modelcontextprotocol.io | `/specification/` |
| GitHub | github.com/modelcontextprotocol | `/servers`, `/python-sdk`, `/typescript-sdk` |
| Blog Anthropic | anthropic.com/engineering | `/building-effective-agents`, `/writing-tools-for-agents` |
| YouTube | youtube.com/results | `search_query=MCP+design+patterns` |
| Reddit | old.reddit.com/r/modelcontextprotocol | (pode bloquear — tentar old.reddit.com) |
| Índice completo | modelcontextprotocol.io/llms.txt | Mapa de toda documentação |

## Estrutura do HTML para Relatórios Ranqueados

Usar 🅱 Hermes Official Design (escrita direta, sem agy):

- Hero: gradiente azul (#0000FF → #000088) + título serifado + metadados
- Cards ranqueados com: rank badge, tag colorida (docs/video/article/github), título, descrição, metadados (autor, ⏱ tempo, relevância, visualizações)
- left-border colorido por nível (azul=essencial, verde=avançado, ouro=intermediário, etc.)
- Tabela de conteúdos no topo com âncoras
- Roteiro de aprendizado ao final
- Footer minimalista: produto + data

## Entrega

- ZIP via Python `shutil.make_archive()` ou `zipfile.ZipFile`
- Enviar via `send_message(target="telegram")` com o ZIP