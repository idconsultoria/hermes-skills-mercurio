# Mermaid → Imagem no Google Docs (flowcharts renderizados)

Como renderizar blocos ```mermaid``` dos `.md` de produto em **imagens** e inserí-las
nos Google Docs espelhados (o usuário quer: `.md` continuam só texto; a imagem entra
apenas no espelhamento).

## Regra de camadas (decisão do usuário, CFP IA ago/2026)

- **Arquivos `.md`:** NUNCA substituir o bloco mermaid por imagem. Ficam só texto.
- **Google Docs:** o conversor `md-to-gdoc.py` detecta ` ```mermaid ` e insere a
  imagem renderizada no lugar do bloco de código.
- **Fundo:** transparente (`-b transparent`), não branco — o usuário pediu transparente
  e depois rejeitou callouts/branco em seções de checklist.
- **DPI:** usar `-s 2` (~192 DPI) para legibilidade garantida em qualquer zoom.

## Pipeline (validado CFP IA, ago/2026)

1. **Renderizar PNG** com mermaid-cli + headless_shell do Hermes (NÃO usar o Chromium
   snap do host — infraestrutura compartilhada, nunca mexer nele):
   ```bash
   MMDC=/opt/data/mmdc/node_modules/.bin/mmdc
   $MMDC -i fluxo.mmd -o fluxo.png -b transparent -s 2 \
     -p /opt/data/mmdc/puppeteer-config.json
   ```
   `puppeteer-config.json` aponta `executablePath` para
   `/opt/hermes/.playwright/chromium_headless_shell-1234/chrome-linux/headless_shell`
   com args `--no-sandbox --disable-setuid-sandbox --disable-gpu --disable-dev-shm-usage`.
   Instalar o mermaid-cli com `--ignore-scripts` (não baixa browser).

2. **Corrigir labels que quebram o parser mermaid ANTES de renderizar** (`_fix_mermaid`):
   - Aspas simples/duplas dentro de labels → remover (ex.: `'Revisão do consultor humano'`)
   - Parênteses não balanceados dentro de labels → remover (ex.: `(Igor)`)
   - Sintoma: `Parse error on line N` / mmdc exit não-zero.

3. **Upload para o Drive e tornar público** (necessário para `insertInlineImage`):
   multipart `drive/files?uploadType=multipart` com metadados JSON + bytes PNG;
   depois `POST /files/{id}/permissions` `{role: reader, type: anyone}`;
   URI final: `https://drive.google.com/thumbnail?id={ID}&sz=w3000`.

4. **Inserir no Docs** com `insertInlineImage` + `objectSize` calculado para CABER na
   página: ler dimensões do PNG pelo header IHDR (`struct.unpack(">II", head[16:24])`),
   converter px→pt (96dpi base; 2x → 0.75 pt/px), escalar com
   `min(550 / (w*0.75), 700 / (h*0.75), 1.0)`. Máx 550pt largura / 700pt altura.

5. **A imagem ocupa 1 índice** — avançar `cur += 1` após o insert e inserir `\n` depois.

## Pageless NÃO é possível via API

O modo pageless (sem páginas) **não é exposto pela API pública do Google Docs**:
- `updateDocumentStyle` rejeita `layoutType`/`pageSetup` (400 "Unknown name").
- Issue tracker Google [#227875469](https://issuetracker.google.com/issues/227875469) — aberto;
  Apps Script e gws CLI também não suportam.
- Só dá pela UI (File → Page setup → Pageless, ou "Set as default" na conta).
- **Workaround aceitável:** dimensionar imagens para caber na página em modo Pages
  (passo 4 acima) — nenhum flowchart fica cortado.
- NÃO tentar via API de novo; se o usuário pedir, explicar a limitação e oferecer a UI.

## Verificação visual

- `docs get` (google_api.py) mostra as imagens como `🖼️ IMAGEM` na estrutura — mas a
  fidelidade real é visual. Para conferir no browser do Hermes, o servidor Next deve
  rodar no container (porta 3001, `npm start -- -p 3001`) — o browser do Hermes não
  alcança o servidor do host via rede Docker.
- Screenshots via `chromium-browser --headless --screenshot` no host saem **sem CSS**
  (AppArmor bloqueia) — não usar como verificação visual de layout.
