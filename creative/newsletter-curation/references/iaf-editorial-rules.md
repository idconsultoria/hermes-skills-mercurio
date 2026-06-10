# IAF — Manhã Aumentada: Regras Editoriais Completas

## Escopo

Este documento registra as regras específicas da newsletter "IAF — Manhã Aumentada",
uma publicação diária (08:00 UTC) sobre IA generativa aplicada, em português brasileiro.

## Pipeline de Produção (6 Crons Encadeados)

```
04:00 ── #1 Notícias Gerais          → web_search (termos amplos de IA)
04:15 ── #2 Hacker News              → web_extract (frontpage + newest)
04:30 ── #3 Reddit (10 subreddits)   → reddit_rss_parser.py (hot + top/day)
04:45 ── #4 X + discussões           → web_search (termos de tendências)
07:30 ── #5 Newsletters especializadas → web_extract (therundown + superhuman)
07:50 ── #6 Síntese + PDF            → ranqueamento → HTML → PDF → entrega
```

### Regras dos Coletores (Crons 1–5)

- Cada arquivo de saída em `/opt/data/cron/output/iaf_*.md` DEVE ter links em TODAS as entradas.
- O prompt do delegate_task DEVE incluir: *"CRITICAL: Every entry MUST include its clickable source URL."*
- Verificar após coleta: `grep -c 'https\?://' arquivo.md` — se 0, a coleta falhou.
- Arquivos existentes:
  - iaf_noticias_gerais.md — 15+ links
  - iaf_hackernews.md — 88+ links
  - iaf_reddit.md — 70+ links
  - iaf_social.md — 27+ links
  - iaf_especializados.md — 17+ links

### Regras da Síntese (Cron #6)

1. **Ranqueamento** → Toda notícia/discussão é ranqueada antes de ir pra newsletter.
2. **Tipo** → Cada item é classificado como "notícia" ou "discussão".
3. **Distribuição**:
   - Top 3 (qualquer tipo) → Análise
   - Notícias restantes → Radar
   - Discussões restantes (top 2 expandidas) → Pulso
   - Sem repetir Análise no Pulso
4. **Deduplicação** → Ler HTMLs dos últimos 14 dias em `/opt/data/cron/history/` para evitar repetição.
5. **Aplicação Prática** → 1 item, última seção, tutorial extenso com "O que você ganha".
6. **Links** → Toda entrada tem link, sem exceção.

## Renderização PDF

O HTML final (v3.html) usa CSS moderno (gradientes, webkit, box-shadow) que o weasyprint
não renderiza bem. Para gerar PDF:

1. Fazer uma cópia do HTML (`/tmp/iaf_v3_pdf.html`)
2. Substituir:
   - `background: linear-gradient(...) + -webkit-background-clip: text` → `color: var(--accent-hover)`
   - `@page { size: A4; margin: 0; }` → `@page { size: A4; margin: 1.2cm 1.5cm; }`
   - Remover `border-radius`, `box-shadow`, `overflow: hidden` do `.page`
   - Remover `display: flex; justify-content: center; padding: 40px 20px;` do body
   - Remover `@keyframes`
3. Renderizar: `uv run python3 -c "from weasyprint import HTML; HTML('/tmp/iaf_v3_pdf.html').write_pdf('/tmp/iaf.pdf')"`
4. Remover hover effects (não têm efeito em PDF)
5. NUNCA modificar o HTML fonte (v3.html) — só a cópia de renderização

## Mensagem do WhatsApp

Formato exato:

```
*IAF — Manhã Aumentada* · [DATA]

[Gancho editorial — 1-2 frases resumindo o hot take]

• [bullet 1]
• [bullet 2]
• [bullet 3]

🎯 [spoiler da aplicação prática]
```

Sem assinatura, sem links, sem metadata adicional.

## Histórico

Os HTMLs publicados são salvos em `/opt/data/cron/history/iaf_YYYY-MM-DD.html`
para alimentar a deduplicação de 14 dias e para referência futura.
