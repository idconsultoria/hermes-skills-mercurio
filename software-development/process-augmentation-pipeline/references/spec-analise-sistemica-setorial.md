# Especificação: Análise Sistêmica Setorial (HTML)

> **Arquivo alvo:** `setor-{nome}/analise-sistemica.html`
> **Gera:** Pi Agent (MiniMax M3), no mesmo prompt que produz `relatorio-dores.md` do setor.

## Estrutura do documento

Documento HTML único e autossuficiente (CSS inline, D3.js via CDN, dados como JSON inline no `<script>`).

### 1. Navbar fixa
- Fundo semi-transparente com backdrop-filter blur (`rgba(5,10,15,0.92)`)
- Links internos para: Diagrama, Ciclos, Classificação
- Brand: "<Organização> · Análise Sistêmica"
- Fonte: Nunito Sans (body)
- Cor dos links: #66E8F1 (electric-teal) no hover

### 2. Cabeçalho
- Título: "🔬 Análise Sistêmica — Setor {Nome}" em Bricolage Grotesque
- Subtítulo: quantidade de processos + resumo quantitativo (N dores, M gargalos)
- Legenda de cores com identificação visual:
  - ● Cultural (kintsugi-gold #C9A227) · ● Técnica (electric-teal #66E8F1) · ● Organizacional (teal-ciano #4AC6D3)

### 3. Diagrama de Loop Causal (D3.js)
- **Container:** altura 85vh (60vh mobile), fundo #050A0F, borda sutil #1B2A3F
- **Tecnologia:** D3.js v7 via CDN, force-directed layout
- **Nós:** 
  - Raio 17-20px, cor por natureza:
    - Cultural: fill #C9A227, stroke #F0D060
    - Técnica: fill #66E8F1, stroke #A5F3FC
    - Organizacional: fill #4AC6D3, stroke #99F6E4
  - Label: código (DOR-ASP-01) acima em IBM Plex Mono 9px, nome curto (2-3 linhas max) abaixo em Nunito Sans 10px
  - Clique → painel lateral com descrição completa
- **Arestas:**
  - **TODAS direcionadas** com arrowheads (marcador SVG triangular preenchido, fill #8B98A8). Setas CHEIAS (não vazadas), idênticas para reforço positivo e negativo.
  - Sólidas para relações causais diretas, tracejadas (`stroke-dasharray: 5,5`) para relações de mitigação (ganhos → dores). Ambos os tipos têm seta.
  - **Símbolos +/-:** label posicionado a **78% da distância** source→target (próximo à ponta da seta), não no ponto médio. Fonte IBM Plex Mono 10px, fundo semi-transparente rgba(11,19,32,0.85). `+` para reforço (aresta sólida), `−` para balanceamento (aresta tracejada).
- **Interação:** zoom (scroll), drag de nós, clique para detalhes
- **Legenda:** overlay no canto inferior esquerdo, fundo rgba(11,19,32,0.9), borda #1B2A3F

### 4. Painel de Detalhes (ao clicar no nó)
- Overlay no canto superior direito, 340px largura, fundo rgba(11,19,32,0.95)
- Mostra: título (Nunito Sans 14px), código (IBM Plex Mono 11px), classificação (badge colorido), descrição completa, processos afetados
- Botão ✕ para fechar

### 5. Análise de Ciclos
- Título em Bricolage Grotesque, borda inferior sutil
- Parágrafo introdutório com total de ciclos detectados
- Para cada ciclo (máximo 15):
  - **Nome do ciclo** (descritivo, baseado nos nós participantes) em electric-teal
  - **Percurso:** sequência de nós no formato `DOR-ASP-01 → DOR-ASP-06 → ... → DOR-ASP-01` em IBM Plex Mono
  - **Funcionamento:** análise textual de 2-4 frases explicando:
    - Tipo de ciclo (reforço/vicioso/virtuoso)
    - Mecanismo de autoalimentação
    - Ponto de intervenção sugerido para quebrá-lo

### 6. Classificação de Nós (Ranking de Alavancas)
- Tabela: Nó (IBM Plex Mono) | Descrição (Nunito Sans) | Natureza (badge) | Ciclos (número)
- Ordenada por quantidade de ciclos decrescente
- Cabeçalho da tabela: uppercase, 11px, cor #8B98A8

### 7. Conclusão
- Síntese de 2-3 parágrafos com os principais achados
- Destaque para as alavancas principais
- Recomendação de foco para a etapa de brainstorming

## Design Tokens (ID Consultoria)

```css
--bg-color: #050A0F;
--bg-card: #0B1320;
--bg-card-hover: #122035;
--line: #1B2A3F;
--text: #E6EDF3;
--text-muted: #8B98A8;
--deep-teal: #003B46;
--electric-teal: #66E8F1;
--teal-ciano: #4AC6D3;
--kintsugi-gold: #C9A227;
--deep-indigo: #1B2A6B;

/* Classificação de nós — cores com alto contraste entre si */
--c-cultural: #C9A227;        /* kintsugi-gold — dourado */
--c-tecnica: #66E8F1;         /* electric-teal — ciano brilhante */
--c-organizacional: #6366F1;  /* indigo — azul-violeta, distinto do teal */

/* Backgrounds de badge */
--c-cultural-bg: rgba(201, 162, 39, 0.12);
--c-tecnica-bg: rgba(102, 232, 241, 0.12);
--c-organizacional-bg: rgba(99, 102, 241, 0.15);

/* Tipografia */
--font-headline: 'Bricolage Grotesque', sans-serif;
--font-body: 'Nunito Sans', sans-serif;
--font-mono: 'IBM Plex Mono', monospace;
```

> ⚠️ **Contraste entre classificações:** As três cores foram escolhidas para serem mutuamente distinguíveis mesmo em telas de baixa qualidade. Dourado (cultural) vs ciano (técnica) vs azul-violeta (organizacional). NÃO usar teal-ciano (#4AC6D3) para organizacional — é muito próximo do electric-teal (#66E8F1) e torna os nós indistinguíveis.

## Algoritmo de Detecção de Ciclos

- DFS com profundidade máxima 5
- Ciclos de 2+ nós
- Deduplicação por conjunto ordenado de nós
- Ordenação por tamanho do ciclo

## Símbolos +/- nas Arestas

Cada aresta deve ser classificada como:
- **`+` (reforço):** o nó origem e o nó destino variam na MESMA direção. Se a dor A aumenta, a dor B também aumenta. Arestas de mitigação (ganhos → dores) são sempre `−`.
- **`−` (balanceamento):** o nó origem e o nó destino variam em direções OPOSTAS. Se o ganho A aumenta, a dor B diminui.

O label deve ser renderizado como um elemento `<text>` sobre um `<rect>` de fundo semi-transparente, posicionado no ponto médio da aresta, atualizado a cada tick da simulação.

## Requisitos Técnicos

- HTML válido, standalone (sem dependências de build)
- D3.js carregado via CDN (`https://d3js.org/d3.v7.min.js`)
- Fontes carregadas via Google Fonts CDN: `Bricolage+Grotesque`, `Nunito+Sans`, `IBM+Plex+Mono`
- Dados dos nós e arestas como JSON inline no `<script>`
- Responsivo: @media (max-width: 768px) ajusta container e painel
- Sem frameworks CSS — CSS puro com custom properties

## O que NÃO deve ter

- ❌ Gráficos de barras/pizza (não é dashboard, é análise causal)
- ❌ Tabelas abaixo do diagrama repetindo dados já visíveis nos nós
- ❌ Branding ou logos (a marca do cliente não é ID Consultoria)
- ❌ Múltiplos arquivos separados (diagrama + análise + ciclos em UM documento)
- ❌ Gerar o HTML separadamente do relatório de dores — o Pi Agent deve produzir AMBOS no mesmo prompt para consistência dos nós
- ❌ Cores fora da paleta ID Consultoria (sem azul royal, sem verde genérico, sem vermelho #FF0000)
- ❌ **Markdown cru (`**`, `` ` ``, `*`) no HTML** — o navegador não renderiza markdown. Use tags HTML diretamente (`<strong>`, `<code>`, `<em>`) nas descrições de ciclos e nós. A conversão deve ser feita ANTES da inserção no HTML, nunca como regex pós-geração (risco de corromper o JavaScript do D3).
- ❌ **Regex global no HTML final** para converter markdown — os caracteres `*` e `` ` `` aparecem no código D3.js e serão corrompidos. Aplique a conversão apenas nas strings de texto antes de concatená-las ao template HTML.

## Histórico de Atualizações

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-06-19 | Hermes (Gustavo Mello) | Identidade visual ID Consultoria aplicada: paleta gold/teal/indigo, fontes Bricolage+Nunito+IBM Plex. Adicionados símbolos +/- nas arestas com labels posicionados no ponto médio. |
| 2026-06-19 | Hermes (Gustavo Mello) | Responsabilidade transferida para Pi Agent (MiniMax M3) — mesmo prompt que relatorio-dores.md. |
| 2026-06-19 | Hermes (Gustavo Mello) | Criação. Extraído do padrão observado na execução real do pipeline Sergipetec. |
