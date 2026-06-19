# Awwwards Knowledge Embedding — Worked Example

> Como 100 colecoes de design foram convertidas em 9 engramas de conhecimento no vault do Hephaistos.
> Executado em junho de 2026.

## Source Material

- Documento: `/home/taciobrito/.hermes/awwwards-research/contextual.md`
- Tamanho: 1013 linhas, ~54KB
- Conteudo: 97 colecoes da biblioteca Awwwards Collections
- Categorias: 10 secoes tematicas (cores, animacao, tecnologia, UX, portfolios, industrias, ferramentas, conteudo, eventos)
- Sites referenciados: ~13,000+

## Workflow Executado

### Fase 1: Parse
```python
# Ler contextual.md, extrair cada colecao com regex
# Campos: num, name, section, url, curator, items, followers, description, examples, resources
# Salvar em JSON estruturado
```
Output: `/home/taciobrito/.hermes/awwwards-research/collections-data.json`

### Fase 2: Gerar Engramas em Lote
Script unico que le o JSON e escreve 9 engramas:
- `awwwards-color.md` — 17 colecoes de paleta
- `awwwards-typography.md` — 6 colecoes de tipografia
- `awwwards-animation.md` — 13 colecoes de animacao
- `awwwards-technology.md` — 9 colecoes de tecnologia
- `awwwards-ux.md` — 19 colecoes de UX
- `awwwards-portfolios.md` — 5 colecoes de portfolio
- `awwwards-industries.md` — 13 colecoes de industria
- `awwwards-content.md` — 10 colecoes de storytelling
- `awwwards-tools.md` — 7 colecoes de ferramentas

Cada engrama inclui:
- Collections com links originais
- Ferramentas mencionadas
- Exemplos reais com nomes de sites
- Principios de design extraidos
- Estatisticas (itens, seguidores)

### Fase 3: Indexar
- `awwwards-index.md` — indice dos 9 engramas
- `engramas/index.md` — patch para incluir secao Awwwards

### Fase 4: Indexar e Integrar
- `awwwards-index.md` — indice dos 9 engramas
- `engramas/index.md` — patch para incluir secao Awwwards
- Skill hephaistos — Fase 0 no DESIGN mode para carregar contexto Awwwards

## Licao Aprendida

O usuario corrigiu: "Nao e apenas extrair padroes de design e aprender eles, ter em contexto, as ferramentas, padroes, referencias, tudo."

Isso significa que cada engrama de pesquisa deve conter **conhecimento completo e consultavel**, nao apenas um resumo de padroes. Ferramentas, exemplos reais, links, principios e contexto sao obrigatorios.

**Correcao adicional:** Nao crie um diretorio separado em `projetos/` para melhorias do Hephaistos. O vault do Hephaistos E o projeto. As melhorias vao diretamente para `engramas/`, `_contexto/`, e a skill. O diretorio `projetos/` e para projetos de clientes (jogo-da-solidariedade, sergipetec).

## Como Reutilizar

Para qualquer pesquisa massiva no futuro:
1. Parse para JSON estruturado
2. Script que gera N engramas em lote
3. Cada engrama = 1 categoria com profundidade completa
4. Index atualizado automaticamente
5. Skill atualizada para referenciar os novos engramas
