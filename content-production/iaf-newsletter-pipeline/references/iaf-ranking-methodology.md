# Ranking Methodology — IAF Manhã Aumentada

## Cross-Edition Dedup

Before ranking, ensure no item repeats content from a previous published edition.

### How to dedup (demonstrado na prática)

1. **Ler a edição publicada mais recente** de `/opt/data/cron/history/` (ex: `iaf_2026-06-05.html`)
   - Ignorar arquivos com `*tarde*`, `*second-edition*`, `*v5*`, `*light*` no nome — são rascunhos não publicados
2. **Extrair o índice de tópicos** da edição: editorial + deep dives (Análise) + radar + comunidade + aplicação prática
3. **Para cada item pré-selecionado**, comparar:
   - Título do item vs. títulos/tópicos do índice
   - Tópico central do item vs. tópicos cobertos
   - Se o MESMO tópico (ex: "Anthropic RSI report" ou "ChatGPT Dreaming memory") já apareceu → **descartar**
4. **Puxar substituto** do pool completo (não só dos pré-selecionados). Pegar o próximo mais interessante que NÃO esteja no índice
5. **Repetir** até ter 20 itens rigorosamente inéditos
6. **🔍 LOG obrigatório da dedup** — documente no raciocínio:
   - Quantos itens descartados (e quais títulos específicos)
   - Quantos itens de reposição puxados
   - "20 itens rigorosamente inéditos ✓" ou "0 duplicatas encontradas"
   
   ⚠️ Sem este log, a dedup não é auditável. Pular o log = não ter feito.

### Regras
- Dedup é contra a edição publicada mais recente APENAS (não contra rascunhos/vespertinas)
- Um mesmo tópico não pode aparecer em dias consecutivos — mesmo com ângulo diferente
- Itens que estavam no "Pulso da Comunidade" contam como publicados (bloqueiam reuso em Editorial/Análise)

## Pre-Selection (before ranking)

Do NOT rank all items. First:
1. Skim all collected items (50-200+)
2. Select only 10-15 most interesting
3. Only those pass to ranking

Selection criteria: relevance to AI professional, novelty, discussion potential, practical applicability.

## Scoring Criteria (1-10 each)

### Impact
How much does this move the needle for the reader's industry?
- 1-3: Marginal, niche interest
- 4-6: Relevant to a segment of readers
- 7-8: Broad industry relevance
- 9-10: Game-changing, industry-defining

### Utility
Can the reader act on this today?
- 1-3: Pure speculation, no action
- 4-6: Strategic awareness, indirect application
- 7-8: Tactical, implementable this week
- 9-10: Step-by-step tutorial, immediately actionable

### Intrigue
Is this novel, surprising, or thought-provoking?
- 1-3: Expected, been covered
- 4-6: Moderately interesting
- 7-8: Surprising or contrarian
- 9-10: Jaw-dropping, share-worthy

## Average = (Impact + Utility + Intrigue) / 3

## Section Assignment by Score

| Score Range | Section | Treatment |
|-------------|---------|-----------|
| Top 1-3 | Radar (Deep Dive) | 2-4 paragraph analysis + link |
| Top 1-3 discussions | Pulso da Comunidade | 2-4 paragraph analysis + link |
| Remaining | Demais notícias / Pulso | Compact 1-2 lines + link |
| Highest utility item | Aplicação Prática | Step-by-step tutorial |

## Selection Rules

- Editorial/hot take: item with highest emotional impact among top 5
- Radar: top 2-3 news items (expanded)
- Pulso da Comunidade: top 2-3 discussions (expanded)
- Aplicação Prática: 1 item, most applicable (can overlap with any section)
- No topic should appear twice across sections
- WhatsApp bullets = top 3 overall scores (news OR discussion)
