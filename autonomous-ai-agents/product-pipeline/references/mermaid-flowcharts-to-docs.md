# Flowcharts (mermaid) → imagens no Google Docs

Pipeline validado (CFP IA, 2026-08-11) para substituir blocos ```` ```mermaid ````
em Google Docs por **imagens renderizadas com fundo transparente** (~192 DPI).

## ⚠️ Regra do usuário (crítica)

Arquivos `.md` do repositório continuam contendo **apenas texto** (com o mermaid
dentro). A renderização em imagem acontece **somente no espelhamento para o
Google Docs** — nunca substituir o bloco mermaid no `.md` por referência a imagem.

## Renderização (container ARM64, sem root/sudo)

```bash
# Instalação única (--ignore-scripts: pula download do browser que falha sem unzip)
mkdir -p /opt/data/mmdc && cd /opt/data/mmdc
npm init -y >/dev/null && npm install @mermaid-js/mermaid-cli --no-audit --no-fund --ignore-scripts
```

`/opt/data/mmdc/puppeteer-config.json` — aponta para o Chromium do próprio Hermes
(nunca tocar no browser do host):
```json
{
  "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
  "executablePath": "/opt/hermes/.playwright/chromium_headless_shell-1234/chrome-linux/headless_shell"
}
```

```bash
/opt/data/mmdc/node_modules/.bin/mmdc -i fluxo.mmd -o fluxo.png \
  -b transparent -s 2 -p /opt/data/mmdc/puppeteer-config.json
```

- `-b transparent` → fundo transparente (RGBA, alpha=0) — **usuário prefere
  transparente, NÃO branco**
- `-s 2` → escala 2x ≈ 192 DPI — texto legível mesmo ampliado

## Pitfalls de parsing mermaid

- **Aspas simples E duplas em labels quebram** (`Q['Revisão do consultor
  humano']` → `Parse error ... got 'PS'/'STR'`)
- **Parênteses não balanceados também quebram** (ex.: `CFP (Igor)`)
- **Fix:** remover `" ' ( )` dentro dos labels `[ ]`/`{ }` antes de renderizar
  (o texto perde os parênteses, mas o diagrama renderiza)

## Inserir imagem no Google Docs

`insertInlineImage` exige URI **publicamente acessível** (400 "There was a
problem retrieving the image" caso contrário):

1. **Upload multipart** no Drive: `POST https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id` (boundary + metadata `{name, mimeType:"image/png"}` + bytes)
2. **Tornar público:** `POST /drive/v3/files/{id}/permissions` com `{"role":"reader","type":"anyone"}`
3. **URI para o Docs:** `https://drive.google.com/thumbnail?id={FILE_ID}&sz=w3000`
4. **`insertInlineImage` com `objectSize` calculado para CABER na página:**
   - ler `w,h` do PNG pelo header IHDR (bytes 16-24, `>II`) — sem depender de PIL
   - `max_w=550pt, max_h=700pt`; `scale = min(max_w/(w*0.75), max_h/(h*0.75), 1)`
   - `objectSize = {width: w*0.75*scale, height: h*0.75*scale}` (0.75pt/px em PNG 2x)

## Pageless NÃO existe na API

O modo "sem páginas" do Google Docs **não é exposto pela API** (nem
`updateDocumentStyle`, nem Drive create, nem Apps Script — issue tracker
227875469). Só dá pela UI (File → Page setup → Pageless). Por isso o
dimensionamento proporcional (passo 4) é obrigatório para imagens não cortarem
em modo Pages normal.

## ⚠️ NUNCA `snap remove`/instalar browser no oracle-host

O Chromium snap do host é **infraestrutura compartilhada entre sessões** (IAF
PDF etc.). Acidente real: um agente rodou `sudo snap remove chromium` durante
setup do mmdc → outra sessão perdeu o browser subitamente e reinstalou (o `snap
changes` mostrou Remove 21:13 / Install 21:21 UTC). Para renderização local usar
SEMPRE o `headless_shell` do Hermes — não tocar no host.
