# Verificação de fidelidade — três gates

Nenhuma edição de leitura é declarada pronta sem os três.

## Gate 1 — bloco a bloco (o que pega corte de verdade)

Contagem de palavras esconde truncamento (o texto perdido sai do denominador). A prova é por bloco:
percorra o **modelo** e confirme que cada trecho aparece no HTML e no EPUB.

```python
import re

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

textos = []
for t in doc['titulos']:
    for c in t['capitulos']:
        for s in c['secoes']:
            for a in s['arts']:
                textos.append(a['caput'])
                for b in a['blocos']:
                    textos.append(b.get('texto', ''))
                    textos += [i['texto'] for i in b.get('incs', [])]
                    if 'inc' in b:
                        textos.append(b['inc']['texto'])

for tx in textos:
    probe = norm(tx)[:70]
    assert probe in norm(html_txt), probe   # html_txt = tags removidas + html.unescape
    assert probe in norm(epub_txt), probe   # epub_txt = mesma coisa nos .xhtml do ZIP
```

Sentido inverso (linha da fonte que não chegou ao modelo): percorra as linhas do OCR, remova o marcador
(`§`, romano, `Art. N.`) com a **mesma regex do parser** e procure os 55 primeiros caracteres no texto do
modelo. O que sobrar deve ser só linha estrutural (título, cabeçalho de página); conteúdo sobrando = perda
no parser.

## Gate 2 — EPUB abre

`zipfile` + `xml.dom.minidom.parseString` em todo `.xhtml/.opf/.ncx`, `mimetype` conferido, contagem de
arquivos. Detalhe em `epub-kindle-manual.md`.

## Gate 3 — visual no aparelho

```bash
chromium-browser --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --hide-scrollbars --window-size=390,2600 --screenshot=$HOME/tmp/shot.png "file://$PWD/arquivo.html"
```

Confirme o binário com `command -v chromium-browser` antes (o caminho muda entre Termux nativo e proot; a skill
`html-to-pdf-chromium` documenta o runtime Playwright). Página muito alta (>30.000 px) estoura o timeout —
capture em faixas em vez de tentar a página inteira.

1. `vision_analyze` na imagem inteira e recortes (`region`) nas faixas de risco: topo (cabeçalho, sumário,
   listas densas), meio (cartões/incisos), fim (anexos, assinatura, nota).
2. Perguntar explicitamente por: texto cortado, sobreposição, cartão vazio, lista quebrada, "muralha de texto"
   (parágrafos colados), botão flutuante cobrindo linha.
3. Corrigir e regerar antes de declarar pronto. Uma rodada de correção é normal — na primeira captura costuma
   aparecer espaçamento apertado e parágrafos sem respiro.

## Checagens baratas

- `h.count('<article')` == número de artigos/itens esperado; pilha de tags balanceada (`html.parser` custom).
- `<ul>` abertos == `</ul>` fechados; `class="badge"`/`class="body"` residual indica conversão mal feita.
- Diferença de tokens numéricos entre as duas passagens de OCR = mapa dos pontos frágeis (datas, prazos, %).
