# Harness de QA no ambiente Mercúrio (Termux/proot) — CDP próprio

Quando rodar dogfood de site aqui, o browser_exec e o terminal têm limitações que
quebram o fluxo padrão da skill. O caminho que funciona:

## 1. Terminal não devolve stdout

`terminal(...)` e `terminal()` via hermes_tools retornam `output: ''` mesmo em
sucesso. Contorne sempre com `subprocess.run(..., capture_output=True, text=True)`
dentro de `execute_code` — inclusive para git, vercel, pdftoppm, pdfinfo, node.

## 2. browser_exec: sem WebGL, sem clique real, e a aba pode ser roubada

- O Chromium do browser_exec **não tem WebGL** (`getContext('webgl2')` = null em
  canvas novo, mesmo com SwiftShader). Site 3D fica sem cenas.
- Cliques de coordenada não chegam à página (memória: só eventos via `js()`).
- Sessões compartilhadas podem trocar de aba no meio do teste (já apareceu uma
  aba do Facebook no meio de um audit). Use `session=` dedicada.

## 3. Driver CDP próprio (o que resolve)

Subir o Chromium do cache do playwright e falar CDP por websocket:

```python
CHROME = '/data/data/com.termux/files/home/.hermes/.cache/ms-playwright/chromium-1117/chrome-linux/chrome'
# flags: --headless=new --no-sandbox --disable-dev-shm-usage --hide-scrollbars --mute-audio
#        --use-angle=swiftshader --enable-unsafe-swiftshader (não habilita GL aqui, mas não atrapalha)
```

Comandos que funcionam de verdade: `Page.navigate`, `Runtime.evaluate`,
`Page.captureScreenshot`, `Input.dispatchMouseEvent` (**clique real**),
`Emulation.setDeviceMetricsOverride` (desktop/mobile + dpr),
`Browser.setDownloadBehavior` (**testa download de PDF/arquivo**),
`Emulation.setEmulatedMedia` (prefers-reduced-motion), `Log.enable` +
`Runtime.exceptionThrown` (erros de console).

Pitfalls: `Emulation.setTouchEmulationEnabled` é rejeitado no Chromium 125
(`Touch points must be between 1 and 16`) — não chame. Módulos importados ficam
em `sys.modules`: depois de editar o driver, `sys.modules.pop('cdp')` + reload,
senão roda código velho.

## 4. Servir o site local

`python3 -m http.server <porta> --bind 0.0.0.0 --directory <dir>` roda no host e
**o Chromium local alcança 127.0.0.1** (o browser_exec, não — ele é outro
namespace; lá só IP de LAN/Tailscale). O flag `--directory` é obrigatório:
cwd do Popen não foi respeitado.

## 5. Auditar contraste sem enxergar a tela

Injete um script que percorre os nós de texto, compõe o fundo efetivo subindo os
ancestrais (rgba sobre rgba, base = fundo do body) e multiplica a **opacidade de
todos os ancestrais** — sem isso o audit acusa como falha o texto de telas
inativas (`opacity: 0` por design) e elementos `.reveal` ainda não revelados.
Ignore `op < 0.9` (não está visível agora) e compare com 4.5:1 (ou 3:1 para
≥24px / ≥18.66px bold).

## 6. Verificar PDF/print sem abrir o arquivo

`pdfinfo` (páginas) + `pdftoppm -png -r 40` + `PIL` contando pixels escuros por
página: "página vazia" = 0% de tinta. Pega exatamente o caso em que o
`html2pdf().save()` resolve a promise **sem gerar arquivo** (erro engolido no
`catch`). Para provar geração, escute `Page.downloadWillBegin` /
`Browser.setDownloadBehavior` ou instrumente `URL.createObjectURL` e leia o
tamanho do blob.
