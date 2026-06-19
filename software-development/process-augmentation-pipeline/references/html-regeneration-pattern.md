# Padrão: Regeneração de HTMLs de Análise Sistêmica pelo Hermes

> Quando o Hermes precisa regenerar os HTMLs de análise sistêmica (ex.: aplicar identidade visual corrigida, adicionar símbolos +/- nas arestas, ajustar cores após mudança de spec).

## Quando usar

- A identidade visual dos HTMLs gerados por Pi Agent não está conforme a spec ID Consultoria
- Foram adicionados novos requisitos visuais (símbolos +/- nas arestas, fontes ID, etc.)
- O usuário pediu ajustes em TODOS os HTMLs de uma vez
- A spec de referência foi atualizada e os HTMLs existentes precisam ser regenerados

## Método

Usar um script Python único que:

1. Define os dados (nós + arestas) hardcoded — extraídos dos `relatorio-dores.md`
2. Roda detecção de ciclos via DFS com profundidade máxima 5
3. Gera HTML com template contendo:
   - Google Fonts CDN: Bricolage Grotesque, Nunito Sans, IBM Plex Mono
   - D3.js v7 via CDN
   - CSS custom properties com tokens ID Consultoria
   - Force-directed layout com edge labels +/- a 78% source→target (próximo à seta)
   - Painel lateral com descrições em 2 parágrafos
   - Análise de ciclos com mecanismo + consequência (2 parágrafos)
   - Ranking de alavancas
4. Salva em `setor-{nome}/analise-sistemica.html`

## Design tokens obrigatórios

```css
--c-cultural: #C9A227;       /* kintsugi-gold — fator humano */
--c-tecnica: #66E8F1;        /* electric-teal — ferramentas/sistemas */
--c-organizacional: #6366F1; /* indigo — papéis/políticas */
```

> ⚠️ **NUNCA usar #4AC6D3 (teal-ciano) para organizacional.** É indistinguível do electric-teal (#66E8F1) e torna os nós técnicos e organizacionais visualmente idênticos em telas de baixa qualidade. A tríade correta é ouro/ciano/índigo.

## Arestas e setas (regras obrigatórias)

### Arrowheads
- **TODAS as arestas** (sólidas e tracejadas) devem ter arrowhead — NUNCA usar `null` para `marker-end`
- Marcador SVG triangular preenchido, fill #8B98A8
- Comando D3.js correto: `.attr("marker-end", "url(#arrow)")` para TODAS as arestas

### Linhas tracejadas (reforço negativo / mitigação)
- **Mesma opacidade** das linhas sólidas: `stroke-opacity: 0.55`
- Largura: `1.5px` (vs `1.8px` das sólidas)
- Tracejado: `stroke-dasharray: 6,4`
- CSS: `.link.dashed { stroke-dasharray:6,4; stroke-opacity:0.55 }`
- JS: `.attr("stroke-width", d => d.dashed ? 1.5 : 1.8)`

### Edge labels +/−
- Posicionar a **78%** da distância source→target (próximo à ponta da seta), NÃO no ponto médio
- Fórmula: `translate(${d.source.x*0.22 + d.target.x*0.78}, ${d.source.y*0.22 + d.target.y*0.78})`
- Label: `+` para aresta sólida (reforço), `−` para tracejada (balanceamento/mitigação)
- Fonte: IBM Plex Mono 10px, fill var(--text-muted), fundo semi-transparente rgba(11,19,32,0.85)

## Descrições (regra de profundidade)

### Ciclos: 2 parágrafos (mecanismo + consequência)
- **Parágrafo 1 — Mecanismo:** descrever a cadeia causal específica usando os labels reais dos nós, explicar o tipo de ciclo (vicioso/virtuoso/misto) e a direção do reforço.
- **Parágrafo 2 — Consequência:** impacto prático na organização, ponto de intervenção recomendado e justificativa (ex.: "intervir em X porque é de natureza organizacional e quebra o ciclo nos dois sentidos").

### Nós (painel de clique): 2 parágrafos
- **Parágrafo 1:** descrição do problema/oportunidade com contexto real da organização.
- **Parágrafo 2:** evidência literal da fonte (transcrição), natureza (Cultural/Técnica/Organizacional) e processos afetados.

## Markdown → HTML (conversão obrigatória)

Textos de análise de ciclos e descrições de nós usam formatação que **DEVE ser convertida para tags HTML** antes de ser inserida no documento:

| Markdown | HTML |
|----------|------|
| `**texto**` | `<strong>texto</strong>` |
| `*texto*` | `<em>texto</em>` |
| `` `código` `` | `<code>código</code>` |

O navegador não renderiza markdown cru — `**Mecanismo:**` aparece literalmente como texto se não for convertido.

⚠️ **CRÍTICO: A conversão deve ser feita nas strings Python ANTES de concatená-las ao template HTML.** Nunca aplicar regex de substituição ao arquivo HTML completo — os caracteres `*` e `` ` `` aparecem no código JavaScript do D3.js e serão corrompidos, quebrando a renderização do grafo. O gerador canônico está em `references/generator-template.py`.

## Verificação pós-geração

```bash
for f in etapa-1-analise/setor-*/analise-sistemica.html etapa-1-analise/analise-sistemica.html; do
  python3 -c "
with open('$f') as fh:
    c = fh.read()
    assert '#C9A227' in c, 'falta gold ID'
    assert '#66E8F1' in c, 'falta electric-teal'
    assert '#6366F1' in c, 'falta indigo (organizacional)'
    assert '#4AC6D3' not in c, 'teal-ciano proibido para organizacional'
    assert 'edge-label' in c, 'faltam edge labels'
    assert 'Bricolage' in c, 'falta fonte Bricolage'
    assert 'marker-end' in c, 'faltam arrowheads'
    assert 'dashed?null' not in c, 'aresta tracejada sem seta (null marker)'
    assert 'stroke-opacity:0.55' in c, 'dashed com opacidade errada'
    assert 'd.source.x*0.22' in c, 'label não está a 78%'
    print('OK:', '$f'.split('/')[-1])
  "
done
```

## Pitfall

⚠️ **Regex no HTML final CORROMPE o JavaScript do D3.** Os caracteres `*` e `` ` `` são usados no código de força do grafo (ex.: `d3.forceManyBody().strength(-300)`, `` `translate(...)` ``). Aplicar `.replace()` global para converter markdown em HTML quebra a sintaxe do script e os nós desaparecem do diagrama. **Sempre** converta a formatação ANTES de inserir no template, usando f-strings Python com tags HTML diretas. O padrão correto está em `references/generator-template.py`.

⚠️ **Este padrão é para regeneração pelo Hermes, não para o Pi Agent.** O Pi Agent gera os HTMLs diretamente a partir da spec `references/spec-analise-sistemica-setorial.md`. O Hermes usa este padrão e o `generator-template.py` apenas quando precisa corrigir/regenerar HTMLs já existentes sem re-disparar Pi Agents.

## Histórico de Atualizações

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-06-19 | Hermes (Gustavo Mello) | Correções da execução real: cor organizacional #6366F1 (não #4AC6D3), labels a 78%, todas as arestas com seta, linhas tracejadas com mesma opacidade, markdown→HTML obrigatório, 2 parágrafos em descrições. |
| 2026-06-19 | Hermes (Gustavo Mello) | Criação. Extraído da regeneração dos HTMLs do Sergipetec. |
