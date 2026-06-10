# WhatsApp Companion Message — IAF Manhã Aumentada

## Exact Format

Delivered inside ```text block in Cron #3 response.

```text
📰 *IAF — Manhã Aumentada* · [DATA]

*[PRIMEIRA FRASE DO EDITORIAL EM NEGRITO]* [resto do parágrafo editorial em texto normal, sem negrito]

🔥 *Destaques do dia*
• [top 1 do ranking] — [descrição curta]
• [top 2 do ranking] — [descrição curta]
• [top 3 do ranking] — [descrição curta]

🎯 *Aplicação prática de hoje*
[descrição em 1 linha, texto normal, sem negrito]
```

## Rules

1. 📰 emoji before the title
2. First sentence of editorial in **bold** + period, everything after in normal text (no bold)
3. 🔥 *Destaques do dia* — italic, with fire emoji, followed by bullets
4. 3 bullets = top 3 overall ranking scores (mix of news and discussions)
   - Selection by score, NOT by category. A discussion with score 8.5 beats a news with 8.0.
5. 🎯 *Aplicação prática de hoje* as header line, description on next line in normal text
6. Zero sign-offs, no "—" metadata, no extra text
7. Zero anglicisms in the body

## Example

```text
📰 *IAF — Manhã Aumentada* · 06/06/2026

*O S&P 500 barrou OpenAI, Anthropic e SpaceX.* As três maiores empresas de IA do mundo não atendem o critério mais básico de um índice de ações: dar lucro.

🔥 *Destaques do dia*
• S&P 500 barra OpenAI, Anthropic e SpaceX — recusou waivers de rentabilidade. OpenAI perderia mais de US$ 8 bilhões em compras passivas de fundos de índice
• Gemma 4 QAT — Google lança checkpoints com treinamento consciente de quantização. Modelo E2B cabe em 1GB de RAM. Suporte nativo a llama.cpp, Ollama, MLX e vLLM
• Tutores de IA vencem faculdade de direito — juízes anônimos escolheram respostas do Gemini e NotebookLM em 75% das vezes. Apenas um professor empatou com os modelos

🎯 *Aplicação prática de hoje*
Automatize sua busca de emprego com a extensão Claude para Chrome — busca vagas, compara com seu currículo e candidata-se automaticamente em 4 passos
```
