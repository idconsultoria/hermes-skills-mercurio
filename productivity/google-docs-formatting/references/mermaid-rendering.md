# Mermaid → PNG (substituir flowcharts em notação por imagens nos Docs)

Usuário exige: fluxogramas escritos como ` ```mermaid ```` (ou notação de
código) viram **imagens renderizadas com fundo TRANSPARENTE** nos Google Docs.
**Os `.md` do repo ficam como estão (só texto)** — a renderização em imagem
acontece APENAS ao subir o espelho no Google Docs (o `md-to-gdoc.py` detecta
blocos ` ```mermaid ```` e insere imagem no lugar do código). **Sempre mostrar
um exemplo renderizado ao usuário e aguardar aprovação ANTES de editar os
documentos.**

## Renderizador validado (2026-08-11)

NÃO tente mermaid.ink (API mudou — 400 "Unknown diagram error" até para
diagramas simples) nem kroki.io para flowcharts grandes (500). Use o
mermaid-cli local com o Chromium do Hermes:

1. **Instalar mermaid-cli com `--ignore-scripts`** (pula o download do browser,
   que falha em ARM64 sem unzip/root):
   ```bash
   mkdir -p /opt/data/mmdc && cd /opt/data/mmdc
   npm init -y >/dev/null 2>&1
   npm install @mermaid-js/mermaid-cli --no-audit --no-fund --ignore-scripts
   ```
2. **Chromium headless do Hermes** — o ÚNICO Chromium ARM funcional no ambiente:
   `/opt/hermes/.playwright/chromium_headless_shell-1234/chrome-linux/headless_shell`
   - ⚠️ O chrome do cache puppeteer
     (`~/.cache/puppeteer/chrome/linux-131.0.6778.204/...`) é x64 → `Exec format
     error` em ARM. O Chromium do host é snap com AppArmor que bloqueia o
     puppeteer. Usar SEMPRE o headless_shell do Hermes.
   - ⚠️ **NUNCA rodar `snap remove chromium` nem instalar browser no host** —
     o Chromium snap do host é INFRA COMPARTILHADA entre sessões/skills (IAF
     PDF etc.); remover derruba outras sessões no meio do trabalho.
   - Warnings de dbus/vaapi no headless_shell: ignorar (renderiza ok).
3. **Puppeteer config** `/opt/data/mmdc/puppeteer-config.json`:
   ```json
   {
     "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
     "executablePath": "/opt/hermes/.playwright/chromium_headless_shell-1234/chrome-linux/headless_shell"
   }
   ```
4. **Renderizar** — fundo TRANSPARENTE (`-b transparent`, RGBA confirmado por
   pixel alpha=0) + escala 2x (`-s 2`, ~192 DPI efetivo — legível ampliado):
   ```bash
   cd /opt/data/mmdc
   node_modules/.bin/mmdc -i /tmp/fluxo.mmd -o /tmp/fluxo.png \
     -b transparent -s 2 -p puppeteer-config.json
   ```
   Verificar o PNG com `vision_analyze` (legibilidade + transparência) antes
   de entregar — fluxograma grande em 2x sai com ~440KB.

## Pitfall crítico: aspas E parênteses quebram o parser

`Parse error on line N ... Expecting 'SQE', 'DOUBLECIRCLEEND', ... got 'PS'`
ou `got 'STR'`

Dois caracteres quebram labels mermaid:
- **Aspas simples/duplas DENTRO do label** — `Q[Selo 'Revisão...']` ❌
- **Parênteses no label** — `Q[... CFP (Igor) ...]` ❌ (parse error mesmo com
  o label já em aspas duplas externas)

Fix mais robusto: remover `" ' ( )` das linhas que contêm labels `[...]`/`{...}`
(cada caractere removido, não trocar por aspas duplas — envolver em aspas
duplas quando o label JÁ tem aspas internas CAUSA novo parse error). Rodar o
mmdc, ler a linha do parse error, corrigir e re-renderizar.

## Inserção no Google Docs (dimensionar para CABER)

O `insertInlineImage` exige imagem **publicamente acessível** (400
"There was a problem retrieving the image" se não for). Pipeline validado:

1. Upload do PNG para o Drive (multipart upload Drive API).
2. Tornar público: `permissions` com `{"role": "reader", "type": "anyone"}`.
3. URI: `https://drive.google.com/thumbnail?id=FILE_ID&sz=w3000`.
4. `objectSize` calculado para caber: ler dimensões do PNG (header IHDR),
   converter px→pt (2x de 96dpi = 0.75pt/px), escala = min(550pt/largura,
   700pt/altura, 1.0) — largura máx ~550pt, altura máx ~700pt, proporcional.

## Pageless NÃO é possível via API

Modo pageless (sem páginas) **não é exposto** na Documents API nem no Apps
Script (issue tracker 227875469 aberto). Tentativas que retornam 400:
`documentStyle.layoutType`, `documentStyle.pageSetup.layoutType`. Só dá pela
UI (File → Page setup → Pageless) ou "Set as default". Para "caber sem
cortes" em modo Pages, dimensionar a imagem proporcionalmente (passo acima).

## Aplicação nos documentos (REGRA DO USUÁRIO — .md ficam SÓ texto)

> ⚠️ Correção explícita do usuário (CFP IA, ago/2026): **os arquivos `.md`
> continuam contendo apenas textos.** A inclusão do diagrama renderizado é
> APENAS ao subir o espelho no Google Docs. NÃO substituir blocos mermaid nos
> `.md` por `![...]`/imagem — se já foi feito, reverter com git checkout.

1. **`.md` do repo:** manter o bloco ` ```mermaid ```` como está (texto puro).
2. **`md-to-gdoc.py`** (conversor md→Docs): parsear ` ```mermaid ```` como
   bloco próprio, renderizar PNG transparente (`-b transparent -s 2`) para tmp,
   upload público + `insertInlineImage` no índice atual + `insertText("\n")`.
   Se o render falhar, **fallback = inserir o código como texto** (nunca
   perder conteúdo).
3. **Fundo TRANSPARENTE** (`-b transparent`, RGBA alpha 0) — NÃO usar `-b
   white` (o usuário corrigiu: pediu transparente). Escala 2x (`-s 2`) para
   ~192 DPI legível.
4. Tema: mermaid padrão (colorido) por padrão; customizar cores para o design
   system minimal neutro somente se o usuário pedir.
5. **Sempre mostrar um exemplo renderizado ao usuário e aguardar aprovação
   ANTES de editar os documentos.**
