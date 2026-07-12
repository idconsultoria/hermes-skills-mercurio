# WhatsApp Companion Message — IAF Manhã Aumentada

## Exact Format

Delivered inside ```text block in Cron #3 response.

```text
📰 *IAF — Manhã Aumentada* · [DATA]
🌐 https://iaf-newsletter.vercel.app/[SLUG_DATA]

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
2. 🌐 Link da newsletter SEMPRE na segunda linha, logo após o título, no formato `🌐 https://iaf-newsletter.vercel.app/[SLUG_DATA]`
3. First sentence of editorial in **bold** + period, everything after in normal text (no bold)
4. 🔥 *Destaques do dia* — italic, with fire emoji, followed by bullets
5. 3 bullets = top 3 overall ranking scores (mix of news and discussions)
   - Selection by score, NOT by category. A discussion with score 8.5 beats a news with 8.0.
6. 🎯 *Aplicação prática de hoje* as header line, description on next line in normal text
7. Zero sign-offs, no "—" metadata, no extra text
8. Zero anglicisms in the body

### Regra de editorial no WhatsApp (3 frases máx)

O parágrafo do editorial na mensagem de WhatsApp deve ter **no máximo 3 frases**. Nem muito extensas (evitar frases com mais de 30 palavras) nem muito curtas (evitar frases de menos de 6 palavras). O ideal é 2 frases curtas e diretas, ou 3 quando houver necessidade de conectivo narrativo. A primeira frase SEMPRE em negrito. O objetivo é dar contexto e gancho para o leitor abrir o PDF — não reproduzir o editorial inteiro.

## Delivery Mechanism

A mensagem é enviada ao grupo WhatsApp via bridge API HTTP:

- **Endpoint:** `POST http://127.0.0.1:3000/send`
- **Payload:** JSON com `chatId` e `message`
- **Chat ID do grupo:** `120363419131378682@g.us` (IA que Funciona)
- **Ferramenta:** Python `urllib.request` (jq NÃO está disponível neste sistema — não tente usar `jq` para construir o JSON)

```python
import json, urllib.request
with open('/tmp/iaf_whatsapp_{SLUG}.txt') as f:
    msg = f.read()
payload = json.dumps({'chatId': '120363419131378682@g.us', 'message': msg}).encode()
req = urllib.request.Request('http://127.0.0.1:3000/send', data=payload, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=10)
# Verificar: resp.status == 200, JSON retorna {'success': true, 'messageId': '...'}
```

## Example

```text
📰 *IAF — Manhã Aumentada* · 06/06/2026
🌐 https://iaf-newsletter.vercel.app/06062026

*O S&P 500 barrou OpenAI, Anthropic e SpaceX.* As três maiores empresas de IA do mundo não atendem o critério mais básico de um índice de ações: dar lucro.

🔥 *Destaques do dia*
• S&P 500 barra OpenAI, Anthropic e SpaceX — recusou waivers de rentabilidade. OpenAI perderia mais de US$ 8 bilhões em compras passivas de fundos de índice
• Gemma 4 QAT — Google lança checkpoints com treinamento consciente de quantização. Modelo E2B cabe em 1GB de RAM. Suporte nativo a llama.cpp, Ollama, MLX e vLLM
• Tutores de IA vencem faculdade de direito — juízes anônimos escolheram respostas do Gemini e NotebookLM em 75% das vezes. Apenas um professor empatou com os modelos

🎯 *Aplicação prática de hoje*
Automatize sua busca de emprego com a extensão Claude para Chrome — busca vagas, compara com seu currículo e candidata-se automaticamente em 4 passos
```
