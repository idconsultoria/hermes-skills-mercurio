# Especificação: Análise Sistêmica Global (HTML)

> **Arquivo:** `analise-sistemica.html` (raiz da etapa-1-analise)
> **Escopo:** documento ÚNICO com TODOS os nós de todos os setores + conexões cross-setor.
> **Produzido após:** conclusão de TODOS os relatórios de dores + análises sistêmicas setoriais.
> **Gera:** Pi Agent final (MiniMax M3).

## Estrutura do documento

Documento HTML único e autossuficiente contendo TODAS as dores, gargalos, ganhos e oportunidades de todos os setores como nós individuais — não meta-nós de setor. Conexões cross-setor extraídas do `relatorio-integracao.md`.

### 1. Diagrama de Loop Causal Global (D3.js)

**Nós:** Todos os ~80-95 itens (DOR-*, GAR-*, OPO-*) de todos os setores.
- Raio ~17px, cor por natureza: cultural (#6366F1 — indigo substituiu gold), técnica (#66E8F1), organizacional (#4AC6D3)
- Label: código (IBM Plex Mono 9px) + nome curto (Nunito Sans 10px)
- Identificação do setor pelo prefixo do código (ASP-/JUR-/INV-/CVT-)

**Arestas:**
- Intra-setor: herdadas das análises setoriais
- Cross-setor: extraídas do relatório de integração
- **TODAS direcionadas** com arrowheads preenchidos (fill #8B98A8), independente do tipo de relação
- Sólidas: relação causal direta. Tracejadas: mitigação/influência difusa. **Ambos os tipos têm seta cheia.**
- Símbolos +/- posicionados a 78% da distância source→target (próximo à ponta da seta)

### 2. Análise de Ciclos
- Detecção de todos os ciclos (DFS profundidade 5) incluindo ciclos cross-setor
- Nomeação e análise textual de cada ciclo

### 3. Classificação de Nós-Alavanca
- Ranking por participação em ciclos (cross-setor + intra-setor combinados)

## Design Tokens (ID Consultoria)

```css
--bg: #050A0F;
--bg-card: #0B1320;
--line: #1B2A3F;
--text: #E6EDF3;
--text-muted: #8B98A8;
--c-cultural: #C9A227;       /* kintsugi-gold */
--c-tecnica: #66E8F1;        /* electric-teal */
--c-organizacional: #6366F1; /* indigo — distinto do teal */
--font-headline: 'Bricolage Grotesque', sans-serif;
--font-body: 'Nunito Sans', sans-serif;
--font-mono: 'IBM Plex Mono', monospace;
```

## O que NÃO deve ter

- ❌ Meta-nós de setor (SETOR-ASP, SETOR-JUR, etc.) — usar os nós individuais
- ❌ Dois níveis de abstração no mesmo diagrama
- ❌ Gráficos de barras/pizza
- ❌ Arquivos separados de análise de ciclos (tudo no HTML)
- ❌ **Markdown cru no HTML** — use `<strong>`, `<code>`, `<em>` diretamente. Nunca aplique regex de conversão ao HTML final (corrompe o JavaScript).

## Histórico de Atualizações

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-06-19 | Hermes (Gustavo Mello) | Redesenhado para conter TODOS os nós individuais (~82), não meta-nós de setor. Arestas cross-setor extraídas do relatório de integração. |
| 2026-06-19 | Hermes (Gustavo Mello) | Identidade visual ID Consultoria aplicada. Símbolos +/- nas arestas. |
