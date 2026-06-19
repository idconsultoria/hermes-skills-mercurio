# Template de Relatório de Efetividade de Ferramenta

> **Referência do `process-augmentation-pipeline`**
> Padrão validado no relatório Vulcano do Sergipetec (Junho 2026)

## Quando usar

Quando o usuário pede análise de efetividade de uma ferramenta usada no pipeline (Vulcano, Pi Agent, agy, etc.), gerar um HTML no Hermes Design Guide com a estrutura abaixo.

## Estrutura do Relatório

### 0. Header
- Eyebrow em Space Mono: "Relatório de Efetividade"
- Título em Spectral: "Ferramenta X no Pipeline Y"
- Subtítulo: contexto (projeto, data, etapa)

### 1. KPIs (4 scorecards)
- Métricas chave da execução (ex.: chamadas, engramas, tokens, precisão)
- Deltas com baseline quando disponível (↑/↓)

### 2. Sumário Executivo: A Ferramenta em Si
**OBRIGATÓRIO — foi correção explícita do usuário.** Analisar a robustez INTRÍNSECA da ferramenta, desacoplada do projeto. Eixos:
- Qualidade da indexação / arquitetura interna
- Riqueza do conteúdo indexado
- Eficiência do protocolo de recuperação
- Limites atuais DA FERRAMENTA, não do contexto

Formato: prosa fluida, parágrafos de 4-6 linhas, ênfase em strong para conceitos-chave, code para nomes técnicos. Não usar bullet points — é um texto corrido de alta legibilidade.

### 3. Seções numeradas (1 a N)
Cada seção cobre um critério:
1. Chamadas Realizadas — tabela com query, engramas, tokens, relevância
2. Qualidade das Informações — barras CSS por cluster, tabela de dimensões
3. Eficiência de Tokens — grid de benchmark cards
4. Cobertura do Vault por Domínio — tabela com tags coloridas
5. Impacto Qualitativo — tabela comparativa com deltas
6. Lições e Recomendações — timeline + tabela de ações

### 4. Considerações Finais — Limitações Extrínsecas
**OBRIGATÓRIO — foi correção explícita do usuário.** Separar claramente:
- O que é limitação DA FERRAMENTA (coberto no Sumário Executivo)
- O que é limitação DO PROJETO/CONTEXTO (coberto aqui)

Exemplos de extrínsecas: subutilização por protocolo, cobertura assimétrica do vault, custo de contexto em modelos caros, dependência de prompt bem formulado, ausência de ciclo de feedback.

### 5. Conclusão
- Nota final (X/10) com benchmark quando disponível
- Veredito em prosa
- Recomendação de próximo passo

## Design Tokens (Hermes Official)
- Azul: #0000FF
- Dourado: #E8B830
- Fundo: #F9FAFB
- Cards: #FFF com borda #E8ECF2
- Callouts: #F0F5FF com borda esquerda azul
- Fontes: Spectral (títulos), Space Mono (números, código, labels), Inter (corpo)
- Gráficos: CSS puro (barras horizontais), sem Chart.js

## Responsividade
- Container: max-width 820px
- Mobile < 520px: KPI row 2-col, bench grid 1-col, bar labels reduzidas

## Pitfalls
- ⚠️ Não confundir intrínseco com extrínseco. O Sumário Executivo analisa a ferramenta; as Considerações Finais analisam o uso dela no projeto.
- ⚠️ Não usar bullet points no Sumário Executivo — é prosa fluida.
- ⚠️ Incluir SEMPRE as duas seções (Sumário Executivo + Considerações Finais). O usuário corrigiu a ausência de ambas.
