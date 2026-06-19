# Data Report — Prompt Pattern (Hermes Agent Style)

## Quando usar

Relatórios de consultoria multi-sessão: custos, KPIs, comparativos, análises financeiras. Qualquer tarefa que combine **tabelas + gráficos + análise textual** num único HTML.

## Estrutura do Prompt para agy

### 1. Cabeçalho — Regras absolutas

No TOPO do prompt, antes de qualquer dado:

```
Gere um HTML autônomo e autossuficiente (ZERO dependências externas — sem CDN, sem Chart.js, sem Google Fonts, sem fetch).

REGRAS ABSOLUTAS:
- ZERO dependências externas. Nada de CDN, Chart.js, Google Fonts.
- Gráficos em CSS PURO — divs com width percentual, @keyframes slideIn.
- Fontes do sistema APENAS: Georgia serif, Courier New mono, system-ui corpo.
- NENHUM gráfico de pizza/donut/rosca. SÓ barras horizontais.
- Um único arquivo HTML. Zero requisições externas.
```

### 2. Design System — Tokens inline

Sempre embeder os tokens de cor e fontes no prompt, mesmo que o style guide exista em arquivo:

```css
--blue-royal: #0000F2
--white: #FFFFFF
--charcoal: #171717
--paper: #F5F5F7
--amber: #FFBD38
--red: #FF0000
--gray-muted: rgba(0,0,242,0.15)
--gray-light: rgba(0,0,242,0.05)
```

Incluir padrões de componentes: "Tabelas: th border-bottom 2px solid, td border-bottom 1px dashed, hover rows. Tags: border 1px solid blue-royal, padding 4px 8px, letter-spacing. Botão isométrico: box-shadow 4px 4px."

### 3. Dados — Pré-processados

NUNCA passar dados crus esperando que o agy calcule. Pré-calcular:
- Totais, percentuais, rankings
- Séries ordenadas (maior→menor para gráficos)
- Relações explícitas (ex: "40 pesquisas/mês × 150K tokens = 6M tokens")
- Comparativos (com pacotes vs sem pacotes)

### 4. Análises — Curtas e diretas

Texto em bullet points de 1 linha cada. NADA de floreios. Ex:

```
1. Custo total: R$ 2.946,99. Humano 68% / IA 32%.
2. Revisão domina: 82,8% do custo API. Gargalo.
3. Economia com pacotes: R$ 1.924/mês (39,5%).
```

### 5. Estrutura do Relatório

Numerar cada seção em ordem. Ex:

```
1. HERO — fundo azul sólido, título serif bold white, total em monospace grande
2. EXECUTIVE SUMMARY — grid 2×2 de cards KPI
3. DRIVERS DE CUSTO — tabela
...
N. FOOTER — tech footer
```

### 6. Regras Visuais (sempre no final)

```
- SEM gradientes, SEM glassmorphism, SEM neon, SEM emojis
- SEM pizza/donut/rosca
- Tabela de apoio abaixo de CADA gráfico
- Total geral em monospace bold grande
- Fontes do sistema APENAS
- Tabelas: th border-bottom 2px solid, td border-bottom 1px dashed, hover
- Texto CURTO e direto
```

## Exemplo Completo

Ver o prompt usado em `/opt/data/agy-report-v3.md` (sessão 17/06/2026) como template real.
