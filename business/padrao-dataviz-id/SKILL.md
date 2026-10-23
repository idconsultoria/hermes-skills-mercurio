---
name: padrao-dataviz-id
description: "Use ao construir painel, dashboard ou gráfico da ID."
category: business
type: Reference
timestamp: 2026-10-22T00:00:00Z
---

# Padrão de dado da ID Consultoria

Contrato único para todo artefato que mostra número: painel de cliente, dashboard interno,
relatório, slide. Derivado do padrão fixado no projeto Métricas nas Nuvens (Hefesto, 22/10/2026)
e transportado para a ID inteira.

Fonte de verdade original: `~/metricas-nas-nuvens/DESIGN.md`,
`~/metricas-nas-nuvens/chart-doctrine.md`, `~/metricas-nas-nuvens/product/design/design-system.md`.
Skills de origem do padrão: `data-storytelling`, `data-visualization`, `impeccable`,
`anti-ui-slop`, `userinterface-wiki`, `frontend-design`.

## 1. A regra-mãe

**Tinta que não carrega dado é dívida.** Antes de acrescentar qualquer elemento, responda o que
ele informa. Se a resposta for "organiza", "embeleza" ou "separa", ele não entra.

Meta mensurável, literal do projeto de origem: **"pelo menos 60% da área do gráfico é dado ou
espaço; no máximo 4 elementos de chrome por gráfico"** — equivalente a ≥ 40% de área vazia na tela.

## 2. Remover por padrão

| Removido | Por quê |
|---|---|
| borda e fundo de card de gráfico | não carrega dado |
| `box-shadow`, `backdrop-filter`, gradiente de chrome | ruído |
| gridline, tick, linha de eixo | o rótulo direto já localiza o valor |
| legenda em caixa | rótulo direto na série é mais rápido de ler |
| rótulo repetido no eixo e no ponto | redundância |
| parágrafo dentro do card | método vai para `<details>` |
| ícone decorativo, emoji, ilustração de enfeite | ruído |
| gauge circular, pizza com mais de 4 fatias, eixo duplo sem justificativa | reprovação automática |

**Teste do parágrafo.** Se um card de número precisa de um texto explicativo fixo para ser
entendido, o problema é o rótulo — encurte o rótulo e mova a explicação para o detalhe sob
demanda. Texto fixo repetido em 12 cards é a maior fonte de tinta sem dado em painel de KPI.

## 3. Manter

- a marca de dado (barra, linha, ponto, célula);
- **uma** linha de base, só quando ela compara;
- rótulo direto na série ou no ponto final;
- **uma** anotação — só a que muda a decisão;
- unidade e período, declarados uma vez;
- numeral com `tabular-nums`.

## 4. Título

**Título = conclusão, não métrica.** "Custo furou 8% em The Palms", nunca "Custo por obra".
Se o título não afirma nada, o gráfico não tem pergunta e sai.

Uma linha de apoio com período, unidade e recorte. Nada além dela.

## 5. Seleção de gráfico

| Pergunta | Gráfico | Proibido |
|---|---|---|
| mudança no tempo | linha | pizza |
| comparar categorias | barra (horizontal no mobile) | linha |
| parte de um todo | barra empilhada | donut, pizza > 4 fatias |
| distribuição | histograma, box | barra |
| correlação | dispersão | barra |
| ranking | barra horizontal ordenada | pizza |
| métrica única | número grande | gráfico |

Uma pergunta, um gráfico. Dois gráficos que respondem à mesma pergunta: um sai.

## 6. Composição

- **Sem grade de cards idênticos.** Blocos assimétricos 7/5 ou 8/4; nunca 6/6.
- Separação por **hairline de largura total** ou por espaço — nunca por caixa.
- Espaço base 8 px; 96–120 px entre seções no desktop, 32–40 px no mobile.
- Primeira dobra: **4 números + 1 gráfico** no desktop; **3 números + 1 gráfico** no mobile.
- Cantos: 0 ou 2 px. Nunca 12/16 px.

**Bento grid — como usar sem virar grade de cards.** Bento é permitido como *organização de
área*, não como moldura: blocos de tamanhos diferentes, sem borda, sem fundo, sem sombra,
separados por espaço e hairline. O que reprova é a **repetição de cards idênticos com moldura**.
Um bento com seis caixas iguais de borda cinza é grade de cards com nome novo.

## 7. Estados obrigatórios

Toda tela entrega, além do caminho feliz: **vazio, carregando, erro, parcial, sem permissão,
dado simulado**. Dado fictício é **rotulado na interface e no export**, não só no rodapé.

Estado vazio diz o que aconteceu e o que fazer: "Sem contas vencidas neste mês." Proibido:
"Nenhum dado encontrado", "Ops!", qualquer emoji.

## 8. Acessibilidade

- Contraste ≥ 4,5:1 em texto, ≥ 3:1 em elemento gráfico.
- **Cor nunca é o único canal**: série projetada é tracejada **e** clara; realizado é sólido
  **e** acentuado; estado é ponto **e** texto.
- Alvo de toque 48 × 48 px em ≤ 900 px.
- Foco visível sempre; nada de hover como única via.
- Todo gráfico tem alternativa em tabela.
- `prefers-reduced-motion` e `prefers-contrast: more` respeitados.

## 9. Mobile é o produto

Não é a versão reduzida. Base **16 px** (nunca 14), KPI 48–56 px, gráfico 180–220 px, até 6
categorias, barra horizontal para rótulo longo, zero scroll horizontal em 320/360/390/430 px.

## 10. Marca ID no dado

Fundo branco, navy `#0A1929`, teal `#0E7C8A` / `#14B8A6`, Neulis Neue + Nunito Sans.
**Um acento por tela.** Positivo herda o acento; negativo usa um único vermelho de alerta.
Acento em área nunca maior que 8% da viewport.

## 11. Portão de acabamento

Antes de entregar, verifique no artefato renderizado:

1. existe card de gráfico com borda, fundo ou sombra? reprova;
2. existe gridline, tick ou linha de eixo? reprova;
3. existe legenda em caixa? reprova;
4. existe título métrico no lugar da conclusão? reprova;
5. existe parágrafo fixo dentro de card de número? reprova;
6. dois gráficos na mesma dobra? reprova;
7. número sem unidade ou sem período? reprova;
8. menos de 40% de área vazia? reprova;
9. scroll horizontal em 390 px? reprova;
10. dado simulado sem rótulo visível? reprova.

Medir, não estimar: abrir a página, contar elementos, medir largura de rolagem.
