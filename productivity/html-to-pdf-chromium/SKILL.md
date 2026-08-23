---
name: html-to-pdf-chromium
description: "Convert HTML to PDF via Chromium headless — ARM64 fallback to WeasyPrint.

Load this skill when generating PDF from HTML with browser-quality rendering, or when weasyprint output lacks CSS features like -webkit-background-clip or gradients. Covers Chromium headless installation via Debian .deb extraction without root or Playwright, PDF generation with full CSS support, WeasyPrint for ARM64 systems, and common rendering fixes."
trigger: User asks to generate PDF from HTML with browser-quality rendering, or when weasyprint output lacks CSS features like -webkit-background-clip or gradients.
related_skills: [html-report-hermes, iaf-newsletter-pipeline]
type: Template
timestamp: 2026-07-16T22:30:00Z
---

# HTML → PDF com Chromium Headless

## ⚠️ ARM64 — Leia Antes do Setup

**Chromium para ARM64 é frequentemente indisponível.** Antes de investir tempo no setup abaixo, saiba:

- **Debian `.deb` são rotacionados rapidamente.** `apt-get download chromium` frequentemente retorna 404 — a versão listada no cache do `apt-cache` já foi removida do repositório. Não há garantia de disponibilidade.
- **Google Chrome for Testing NÃO publica `linux-arm64`.** A API `known-good-versions-with-downloads.json` lista apenas `linux64` (x86_64). Não há build ARM64 para Linux.
- **Puppeteer/Playwright `install chromium`** no ARM64 tipicamente baixa diretórios vazios (`linux_arm-*/` sem binários) ou instala binários x86_64 que falham com `Exec format error`.

**✅ Fallback: WeasyPrint.** Instale com `uv pip install weasyprint` e gere PDF com:

```bash
uv run python3 -c "
import weasyprint
doc = weasyprint.HTML(filename='/tmp/input.html')
doc.write_pdf('/tmp/output.pdf')
"
```

**Preparação para WeasyPrint:** remova `<link href="fonts.googleapis.com">` do HTML e substitua `font-family` por fontes de sistema (`'DejaVu Sans'`, `'DejaVu Serif'`, `'DejaVu Sans Mono'`).

**Tradeoffs WeasyPrint vs Chromium:**

| Aspecto | Chromium | WeasyPrint |
|---------|----------|------------|
| Gradientes CSS, glow | ✅ | ❌ Perdidos |
| `-webkit-background-clip: text` | ✅ | ❌ Ignorado |
| Tamanho típico PDF | 500-700 KB | 100-150 KB |
| Disponibilidade ARM64 | ❌ Binários frequentemente offline | ✅ Sempre funciona |

## Pré-requisitos (Chromium — tente, mas use o fallback se falhar)

Chromium headless compilado para o Debian 13 (trixie) arm64, extraído dos pacotes `.deb` oficiais. Não precisa de root, nem de Playwright, nem de Puppeteer.
## Setup (se os .deb estiverem disponíveis — tente, mas use WeasyPrint se falhar)

```bash
# 1. Baixar os pacotes .deb
cd /tmp
apt-get download chromium chromium-common
# ⚠️ Se falhar com 404: os pacotes foram removidos do repositório.
# Use o fallback WeasyPrint. Não perca tempo caçando versões alternativas.

# 2. Extrair para uma pasta local
mkdir -p /tmp/chromium-extracted
dpkg -x chromium_*.deb /tmp/chromium-extracted/
dpkg -x chromium-common_*.deb /tmp/chromium-extracted/

# 3. Baixar e extrair bibliotecas dependentes
apt-get download libdouble-conversion3 libharfbuzz-subset0 libminizip1t64 libopenh264-8 libicu76 libxnvctrl0
for pkg in libdouble-conversion3_*.deb libharfbuzz-subset0_*.deb libminizip1t64_*.deb libopenh264-8_*.deb libicu76_*.deb libxnvctrl0_*.deb; do
  dpkg -x "$pkg" /tmp/chromium-extracted/
done

# 4. Consolidar todas as .so num único diretório
cp -r /tmp/chromium-extracted/usr/lib/aarch64-linux-gnu/*.so* /tmp/chromium-extracted/usr/lib/chromium/

# 5. Verificar se não faltam libs
ldd /tmp/chromium-extracted/usr/lib/chromium/chromium 2>&1 | grep "not found"
```

> **Arquivo crítico:** `icudtl.dat` (11 MB) está no pacote `chromium-common`. Sem ele o Chromium aborta com `Invalid file descriptor to ICU data received`.

## Gerar PDF

```bash
CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
INPUT=/caminho/para/arquivo.html
OUTPUT=/caminho/para/resultado.pdf

LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium \
  $CHROMIUM \
  --headless --no-sandbox --disable-gpu \
  --disable-software-rasterizer \
  --no-pdf-header-footer \
  --print-to-pdf="$OUTPUT" \
  "file://$INPUT"
```

Flags:
- `--headless`: modo sem cabeça
- `--no-sandbox`: necessário sem root
- `--disable-gpu`: sem aceleração gráfica (servidor)
- `--disable-software-rasterizer`: evita travamentos em HTML com CSS complexo
- `--no-pdf-header-footer`: remove cabeçalho/rodapé padrão do Chromium (data, URL, numeração)
- `--print-to-pdf=`: path de saída
- `file://$INPUT`: path de entrada (obrigatório `file://`)

### Se o Chromium travar (exit 124 — timeout)

HTMLs com CSS complexo (grids, animações, @media queries) ou Google Fonts podem travar o Chromium headless. Soluções testadas:

1. **Remover Google Fonts** — a tag `<link href="https://fonts.googleapis.com/...">` causa hang. Remova antes de gerar PDF e use fallback system fonts.
2. **Base64 grande → arquivo externo** — se o HTML tem logo embutido como base64 (>500KB), substitua por `src="logo.png"` (crie symlink). Base64 inline gigante faz Chromium travar.
3. **Timeout de 90s** — usar `timeout 90` (não 60) para HTMLs estilizados.
4. **Flags extras** — adicionar `--disable-dev-shm-usage` e `--deterministic-mode` se ainda travar.

### Crash SIGTRAP/`core dump` no `--print-to-pdf` (mas `--version`/`--screenshot` funcionam)

Sintoma: `--print-to-pdf` imprime `timeout: the monitored command dumped core` / `exit=133` (SIGTRAP), ainda que `--version` OK e `--screenshot` gere imagem. Em containers ARM64/Debian trixie (chromium extraído de .deb), a causa é o pipeline de compositor do print. **Receita que destrava** (validada em produção 08/2026):

```bash
CHR=/caminho/chromium; export HOME=/tmp/home; export LD_LIBRARY_PATH=<dir-libs-chromium>
$CHR --headless=new --no-sandbox --disable-gpu --no-zygote --disable-dev-shm-usage \
     --use-angle=swiftshader --user-data-dir=/tmp/cd \
     --no-pdf-header-footer \
     --print-to-pdf=/tmp/out.pdf "file:///path/input.html"
```

Combinação crítica: **`--headless=new` + `--no-zygote` + `--use-angle=swiftshader`** + HOME gravável + varrer `/dev/shm`-de-64MB com `--disable-dev-shm-usage`. Sem `--no-zygote`/`--use-angle=swiftshader` o renderer aborta com SIGTRAP mesmo com as libs de sistema (libnss3/libgtk/libgbm) presentes. Também ter `--no-sandbox` (sem root) e um `--user-data-dir` gravável distinto por execução.

## Verificação

```bash
ls -lh "$OUTPUT"
```

## Pitfalls

- **Debian `.deb` 404 — pacote removido do repositório.** `apt-cache show chromium` lista versões, mas `apt-get download` retorna 404. Isso acontece porque os pacotes são rotacionados rapidamente no repositório Debian. **Não insista.** Use o fallback WeasyPrint documentado no topo desta skill.
- **Chrome for Testing sem `linux-arm64`.** Se tentar baixar via `@puppeteer/browsers`, vai receber diretório vazio. O Google não publica builds ARM64 para Linux.
- **libXNVCtrl.so.0 not found:** Chromium precisa da lib `libxnvctrl0` (NVIDIA control). Já incluída no `apt-get download` do setup, mas se estiver reutilizando uma extração antiga, baixe e extraia separadamente. Verifique todas as faltas com `ldd /caminho/chromium 2>&1 | grep "not found"`.
- **DBus errors:** `Failed to connect to the bus` — normais em servidor sem desktop, ignorar
- **glibc mismatch:** builds oficiais do Google exigem glibc >= 2.42. Usar SEMPRE o pacote Debian (compilado pro glibc 2.41 da máquina)
- **URL de entrada:** Chromium headless requer prefixo `file://` com path absoluto
- **Timeout:** HTMLs grandes podem demorar; timeout de 60s é seguro
- **Gradiente vaza 1px acima do texto no `<h1>`:** Chromium às vezes renderiza uma linha fina com a cor do gradiente acima de headings que usam `background-clip: text; -webkit-text-fill-color: transparent` diretamente no `<h1>`. **Solução:** aplicar o gradiente num `<span>` dentro do `<h1>`, não no próprio `<h1>`:
```html
<h1 class="title"><span>Título com Gradiente</span></h1>
```
```css
.title { margin: 0; padding: 0; } /* h1 sem gradient */
.title span {
  background: linear-gradient(90deg, #fff, #0da69e);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```
Isso funciona porque o `<span>` ocupa apenas o espaço do texto renderizado, sem o box-model extra do `<h1>` que o Chromium usa como área do gradiente mesmo com `background-clip: text`.

- **MEDIA delivery from cron:** Para entregar o PDF via cron auto-delivery, a linha `MEDIA:/path/to/file.pdf` deve ser a **primeira linha** da resposta do agente, sem nada antes. O sistema de auto-entrega do cron processa essa tag e anexa o arquivo. Não funciona se houver texto antes ou se a tag estiver no meio do conteúdo.
- **Print styles não podem converter para grayscale:** Se o HTML tiver `@media print` que converte cores para preto-e-branco (agy costuma fazer isso para "high contrast"), o PDF sai monocromático. A correção: substituir as regras grayscale por `-webkit-print-color-adjust: exact !important` + `print-color-adjust: exact !important` no `*` universal, e manter os CSS custom properties com as cores reais da marca.
- **Logo não renderiza no PDF:** O Chromium headless precisa encontrar o arquivo de logo via path relativo ao HTML. Crie um symlink no mesmo diretório do HTML apontando pro logo real: `ln -sf /caminho/real/logo.png /caminho/do/html/logo.png`
- **Screenshots com Chromium:** `--screenshot=/path.png --window-size=W,H` para capturar screenshot headless. Útil para debug visual em servidores sem display.

## Casos de uso relacionados

- **Renderização BPMN 2.0 → PNG:** Mesmo Chromium + bpmn-js (motor do Camunda Modeler) para converter diagramas BPMN XML em imagens. Setup e wrapper Python em [`references/bpmn-rendering.md`](references/bpmn-rendering.md).
