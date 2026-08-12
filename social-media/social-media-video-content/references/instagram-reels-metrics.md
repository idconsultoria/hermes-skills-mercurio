# Instagram Reels — extração de métricas (print + URL pública)

Técnica validada em 11/ago/2026 (projeto alô Sergipe). Dois caminhos complementares:
o print diz o que o overlay mostra; a URL pública confirma e completa (data + legenda integral).

## Caminho A — Print/screenshot (vision_analyze)

O overlay lateral de um Reels mostra: **likes (coração), comments (balão), shares
(seta curva), direct (avião de papel), saves (marcador)** — todos com contadores
abaixo dos ícones. Também: @handle + "e outras N pessoas" (= post colaborativo),
legenda truncada, às vezes música.

**⚠️ Views/plays NUNCA aparecem no overlay de Reels em print.** Não inventar.
A contagem de visualizações só existe no painel profissional do criador
(Professional Dashboard) ou via API Graph autenticada com permissão do dono.

Dicas de leitura:
- Zoom (vision_analyze com `region`) na coluna de ícones para confirmar números
  exatos — o primeiro scan costuma misturar direct/shares/saves.
- Imagem típica de print é 610x1356 px (não 1080x1920) — calcular crops dentro
  dos limites reais da imagem, senão o clamp zera a região.

## Caminho B — URL pública (curl)

O Instagram bloqueia scraping completo (web_extract devolve só título "Instagram",
sem conteúdo), mas o HTML da página de um Reels **inclui a meta description
pública com likes, comments, data e legenda completa**:

```bash
curl -sL --max-time 25 -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) \
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" \
  "https://www.instagram.com/reel/<SHORTCODE>/" -o /tmp/reel.html
```

Depois extraia (o HTML é uma linha gigante — usar Python ou grep com contexto amplo):

```python
import re
html = open('/tmp/reel.html', encoding='utf-8', errors='replace').read()
m = re.search(r'<meta name="description" content="([^"]*)"', html)
```

Formato verificado da meta:
```
2,121 likes, 33 comments - alo_sergipe on November 23, 2025: "LEGENDA COMPLETA"
```

- Likes/comments em formato "2,121" (vírgula = milhar); batem exatamente com o print
- Data completa por extenso (ex.: "November 23, 2025")
- Legenda **completa**, com entidades HTML (`&#x1f929;` = emoji, `&#xe7;` = ç) — decodificar
  com `html.unescape()` (Python stdlib)
- Autor/handle + owner user id também disponível via `<meta name="instapp:owner_user_id">`
- `?igsh=` é tracking de compartilhamento — pode ser removido para a URL canônica

**O que a meta NÃO traz:** views, shares, saves, música. Para isso: dashboard do criador.

## Regra de honestidade

Nunca preencher views com estimativa ou "deve ter". Se o usuário pedir views:
dizer claramente que o print não mostra e a URL pública não expõe — e oferecer
a alternativa real (dashboard profissional / API Graph autenticada).
