---
name: bpmn-diagram-renderer
description: "Render BPMN 2.0 XML diagrams to SVG/PNG using bpmn-js + Chromium headless — identical output to Camunda Modeler.

Load this skill when a user asks to render a BPMN diagram, export BPMN to image, or visualize a .bpmn file. Covers setup, HTML template, and batch processing."
trigger: User asks to render a BPMN diagram, export BPMN to image, or visualize a .bpmn file.
related_skills: [html-to-pdf-chromium]
---

# BPMN Diagram Renderer

Renderiza diagramas BPMN 2.0 (arquivos `.bpmn`) em SVG e PNG usando **bpmn-js** — a mesma biblioteca que o Camunda Modeler usa internamente. Output indistinguível do Camunda.

## Por que bpmn-js e não Python

- bpmn-js renderiza pools, lanes, gateways com gutter interno, edge routing com waypoints curvos, message flows tracejados, ícones de eventos — tudo exatamente como o Camunda Modeler.
- Alternativas Python (drawsvg, graphviz) levariam semanas e nunca alcançariam a mesma fidelidade.
- O Chromium headless já está instalado no ambiente (ver `html-to-pdf-chromium`).

## Setup (uma vez por workspace)

### Via setup.sh (Dédalo Squad)

```bash
cd render && bash setup.sh
```

### Manual

```bash
cd /tmp/bpmn-test
npm init -y
PUPPETEER_SKIP_DOWNLOAD=true npm install bpmn-js puppeteer
```

`PUPPETEER_SKIP_DOWNLOAD=true` evita baixar outro Chromium quando já existe um funcional.

## Detecção de Chromium

O script `render_bpmn.js` auto-detecta nesta ordem:
1. `$PUPPETEER_EXECUTABLE_PATH` ou `$CHROMIUM_PATH` (env var)
2. `/tmp/chromium-extracted/usr/lib/chromium/chromium` (Debian extraído, aarch64)
3. Puppeteer built-in (baixado no `npm install`)

Em **aarch64** (Oracle ARM, Raspberry Pi): o built-in do Puppeteer é x86_64 e não funciona. O Debian extraído é obrigatório. O script resolve isso automaticamente na ordem de detecção e injeta `LD_LIBRARY_PATH` via `puppeteer.launch({ env: ... })`:

## Renderizar um BPMN

### 1. Baixar o `.bpmn` do Google Drive (ou ler do disco)

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

creds = service_account.Credentials.from_service_account_file(
    'path/to/service_account.json',
    scopes=['https://www.googleapis.com/auth/drive']
)
drive = build('drive', 'v3', credentials=creds)

request = drive.files().get_media(fileId='<FILE_ID>')
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
    _, done = downloader.next_chunk()

with open('diagram.bpmn', 'w') as f:
    f.write(fh.getvalue().decode('utf-8'))
```

### 2. Script Node.js de renderização

Usar `scripts/render_bpmn.js`.

```javascript
const puppeteer = require('puppeteer');
const fs = require('fs');

const bpmnXML = fs.readFileSync('diagram.bpmn', 'utf8');
const bpmnJS = fs.readFileSync('node_modules/bpmn-js/dist/bpmn-viewer.production.min.js', 'utf8');

const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #fff; }
  #canvas { width: 1200px; height: 800px; }
</style>
</head>
<body>
<div id="canvas"></div>
<script>${bpmnJS}</script>
<script>
  var viewer = new BpmnJS({ container: '#canvas' });
  var xml = ${JSON.stringify(bpmnXML)};
  viewer.importXML(xml).then(function() {
    viewer.get('canvas').zoom('fit-viewport');
    window.__BPMN_READY__ = true;
  }).catch(function(err) {
    document.body.textContent = 'Error: ' + err.message;
  });
</script>
</body>
</html>`;

fs.writeFileSync('diagram.html', html);

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/tmp/chromium-extracted/usr/lib/chromium/chromium',
    args: ['--no-sandbox', '--disable-gpu', '--disable-software-rasterizer'],
    headless: true
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 800, deviceScaleFactor: 2 });
  await page.goto('file://' + __dirname + '/diagram.html', { waitUntil: 'networkidle0', timeout: 30000 });
  await page.waitForFunction('window.__BPMN_READY__ === true', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1000));

  // PNG screenshot
  await page.screenshot({ path: 'diagram.png', fullPage: true });
  console.log('diagram.png salvo');

  // SVG export
  const svg = await page.evaluate(() => {
    const el = document.querySelector('#canvas svg');
    return el ? el.outerHTML : null;
  });
  if (svg) {
    fs.writeFileSync('diagram.svg', svg);
    console.log('diagram.svg salvo (' + svg.length + ' bytes)');
  }

  await browser.close();
})();
```

### 3. Executar

```bash
node render_bpmn.js diagram.bpmn diagram.png
# ou via pipe:
cat diagram.bpmn | node render_bpmn.js - output.png
```

O Chromium e `LD_LIBRARY_PATH` são resolvidos automaticamente pelo script.

## Output

- `diagram.svg` — SVG vetorial (editável, ~15-20KB para diagramas típicos)
- `diagram.png` — Screenshot 2x retina (~70-100KB)

Ambos com fidelidade Camunda: fontes, espaçamento, bordas, conectores, swimlanes — tudo idêntico.

## Pitfalls

- **ES modules (`import ... from 'bpmn-js'`) não funcionam no browser.** Usar SEMPRE o bundle UMD (`bpmn-viewer.production.min.js`) com tag `<script>` inline.
- **`LD_LIBRARY_PATH` ausente** → Chromium aborta com `libopenh264.so.8: cannot open shared object file`. O script `render_bpmn.js` resolve isso automaticamente setando `env.LD_LIBRARY_PATH` no `puppeteer.launch()`.
- **`PUPPETEER_SKIP_DOWNLOAD=true`** é obrigatório no `npm install` para não tentar baixar outro Chromium (o Debian extraído já cobre).
- **Chromium Puppeteer x86_64 em aarch64** — `qemu-x86_64: Could not open '/lib64/ld-linux-x86-64.so.2'`. Usar o Debian extraído, que o script prioriza na detecção.
- **Viewport maior que o diagrama** → usar `canvas.zoom('fit-viewport')` para ajustar automaticamente.
- **BPMN com colaboração (pools)** → bpmn-js lida nativamente; não requer configuração extra.
- **Timeout de 15s** no `waitForFunction` é suficiente para BPMNs de até ~200 elementos. Diagramas maiores podem precisar de 30s.
- **Google Drive `files().list()` sem `trashed=false`** — com `supportsAllDrives=True`, a API retorna arquivos da lixeira junto com os ativos, fazendo o download de 7 áudios deletados além do 1 real. **Sempre adicionar `and trashed=false` na query.**
- **Rate limit Gemini (429) em execução paralela** — o free tier do `gemini-3.1-flash-lite` tem 15 RPM. Rodar 4+ processos BPMN em paralelo estoura o limite. Solução: monkey-patch de exponential backoff em `agemini/modelos/gemini.py` (ver `agemini/backoff.py`) + limitar a 5 concorrentes com `xargs -P 5`.
- **Progresso em batch jobs** — ao rodar 30+ processos, reportar progresso incremental a cada ~2 minutos (contagem de OK/FAIL/pendentes). O usuário cobra ativamente se não houver balanço ("Cadê os balanços?").
- **Paralelismo com `xargs -P`** — rodar sequencial é rejeitado ("Por que não em paralelo?"). Usar `xargs -P 5` (5 concorrentes = seguro com backoff). Não usar `-P` maior que 5 com Gemini free tier (15 RPM). Exemplo: `printf '%s\n' CVT-006 CVT-007 ... | xargs -P 5 -I {} sh -c 'python3 run_one.py "{}" 2>&1 && echo "OK: {}" || echo "FAIL: {}"'`
- **Pular processos já concluídos** — antes de disparar batch, verificar planilha: processos com transcrição preenchida (coluna Q) já estão feitos. Não reexecutar. O `run_one.py` skippa etapas já preenchidas, mas reexecutar gera PNGs novos com IDs diferentes (desperdício).
- **Sheets API HttpError (gravação da planilha)** — a função `atualizar_planilha` pode falhar com `HttpError` (timeout, rede). O backoff agora cobre isso: `retry_call(lambda: ...execute(), max_attempts=3, retry_predicate=lambda e: True)` em `agemini/conectores/google_sheets.py`.
- **Consentimento antes de executar** — o usuário exige consentimento explícito antes de disparar qualquer processo. Não executar `run_one.py` ou batch sem autorização verbal clara.
- **Pipeline caching envenenado (células não-vazias)** — o pipeline (`elaboracao_de_pops_e_diagramas.py`) pula qualquer etapa cuja célula na planilha NÃO está vazia (`if cell == "" or cell is None`). Se uma execução anterior falhou e escreveu placeholder genérico (ex: "preciso que você forneça o conteúdo"), as reexecuções subsequentes pularão silenciosamente Escriba, Popeye e Disgrama — mesmo com transcrição nova e válida. **Antes de reexecutar um processo que falhou, limpar manualmente as colunas R (Questionário), S, T (POPs), U (Raciocínio), V, W (XMLs), X, Z, AA (Camunda), AE, AG (URLs PNG), AK (Status).** Usar `sheets.spreadsheets().values().batchUpdate()` com `valueInputOption: 'RAW'` e valores `[['']]`.
- **Sheets API: limite de 50.000 caracteres por célula** — `HttpError 400: "Your input contains more than the maximum of 50000 characters in a single cell."` NÃO é rate limit (429) nem timeout — é erro de validação. Ocorre com transcrições longas (mentoria, jurídico). **Solução**: truncar valores >49.000 chars com marcador `... [TRUNCADO]` antes de gravar na planilha. O valor completo fica no Google Docs (Drive). Aplicar o truncamento em `google_sheets.py:atualizar_planilha()`.
- **Diagnóstico de falha: verificar coluna por coluna** — quando um processo falha, o erro pode estar em qualquer etapa do pipeline. Verificar cada coluna individualmente (transcrição → questionário → POPs → XMLs → PNGs) para isolar o ponto exato da falha. Não assumir que "o áudio é ruim" sem verificar se a diarização de fato rodou.

## Integração com Dédalo Squad

> **Mapa completo de colunas da planilha:** `references/sergipetec-planilha-colunas.md` — use para diagnóstico e limpeza cirúrgica em retries.

O renderizador está integrado ao pipeline em `dedalo_squad/render/`:

```
render/
  .gitignore          # node_modules/
  package.json        # bpmn-js + puppeteer
  package-lock.json
  render_bpmn.js      # node render_bpmn.js <input.bpmn> [output.png]
  setup.sh            # npm install + detecção de Chromium
```

### Python wrapper

```python
from agemini.conectores.render_bpmn import renderizar_bpmn, renderizar_e_salvar_no_drive

# Renderizar para bytes
png_bytes = renderizar_bpmn(bpmn_xml_string)

# Renderizar + upload para Google Drive (retorna URL compartilhável)
url = renderizar_e_salvar_no_drive(
    bpmn_xml_string,
    pasta_drive_id="1abc...",
    nome_base="Estrategico"  # → Estrategico.png
)
```

### Pipeline automático

Em `elaboracao_de_pops_e_diagramas.py`, após gerar os XMLs BPMN, o pipeline automaticamente:
1. Renderiza PNG via `render_bpmn.js`
2. Faz upload para `Subprodutos/<processo>/4. XMLs/`
3. Preenche as colunas `url_diag_estrategico` e `url_diag_operacional` na planilha

Tudo orquestrado pelo `run_one.py`, que usa exponential backoff (`agemini/backoff.py`) para lidar com rate limits da Gemini.
