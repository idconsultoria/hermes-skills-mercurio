---
name: html-to-social-image
description: "Render HTML to social-media-optimized PNG images using Chromium headless screenshots.

Load this skill when creating images for Instagram, Twitter, Open Graph, or any social media platform. Covers Instagram stories/posts/reels, Twitter/OG cards, and any HTML-to-PNG export using Chromium headless via .deb extraction."
type: Media
timestamp: 2026-07-26T05:05:12Z
trigger: User asks to create an image for Instagram, Twitter, Open Graph, or any social media platform — or asks to export HTML as PNG.
related_skills: [html-to-pdf-chromium, html-report-hermes]
---

# HTML → Social Media Image (PNG)

Cria imagens para redes sociais renderizando HTML com Chromium headless e exportando como PNG em alta resolução. Cobre Instagram (stories, posts, reels), Twitter/Open Graph cards, e qualquer formato que precise de HTML estilizado virado imagem.

## Pré-requisitos

Chromium headless extraído dos pacotes `.deb` do Debian. Setup completo em [`html-to-pdf-chromium`](../productivity/html-to-pdf-chromium/SKILL.md) — use exatamente o mesmo procedimento. Resumo rápido:

```bash
cd /tmp
apt-get download chromium chromium-common
apt-get download libdouble-conversion3 libharfbuzz-subset0 libminizip1t64 libopenh264-8 libxnvctrl0
mkdir -p /tmp/chromium-extracted
dpkg -x chromium_*.deb /tmp/chromium-extracted/
dpkg -x chromium-common_*.deb /tmp/chromium-extracted/
for pkg in lib*.deb; do dpkg -x "$pkg" /tmp/chromium-extracted/; done
cp -r /tmp/chromium-extracted/usr/lib/aarch64-linux-gnu/*.so* /tmp/chromium-extracted/usr/lib/chromium/
# Verificar:
LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium ldd /tmp/chromium-extracted/usr/lib/chromium/chromium 2>&1 | grep "not found"
# ^ Se vazio, pronto.
```

> Se o `apt-get download chromium` falhar com 404, os pacotes foram rotacionados. Tente novamente em outro momento ou use o fallback WeasyPrint (só gera PDF, não PNG). Na prática, o pacote Debian 13 (trixie) ARM64 esteve disponível em julho/2026 com Chromium 150.

## Workflow

### 1. Criar o HTML

Dimensione o `<body>` exatamente no tamanho do viewport alvo. Use CSS inline ou `<style>` no `<head>` — sem build step.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1920px;  /* Instagram story */
    overflow: hidden;
    font-family: 'Inter', sans-serif;
  }
</style>
</head>
<body>
  <!-- Conteúdo aqui -->
</body>
</html>
```

**Regras de ouro do HTML para screenshot:**
- **Google Fonts funcionam.** Ao contrário do modo PDF, o modo screenshot do Chromium NÃO trava com `@import url('https://fonts.googleapis.com/...')`. Use à vontade.
- **Gradientes e `-webkit-background-clip: text` funcionam.** Chromium headless renderiza CSS moderno completo no modo screenshot.
- **Sem `@media print`.** Screenshot usa renderização de tela, não de impressão. Nada de `print-color-adjust`.
- **Background no body ou num wrapper.** O Chromium captura o que estiver visível no viewport. Se o background estiver no `html` em vez do `body`, pode sumir.

### 2. Renderizar como PNG

```bash
CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium \
  timeout 90 \
  $CHROMIUM \
  --headless --no-sandbox --disable-gpu \
  --disable-software-rasterizer \
  --disable-dev-shm-usage \
  --screenshot=/path/to/output.png \
  --window-size=1080,1920 \
  --force-device-scale-factor=2 \
  "file:///path/to/input.html"
```

Flags críticas:
- `--window-size=W,H` — define o viewport (use as dimensões da plataforma alvo)
- `--force-device-scale-factor=2` — dobra a resolução real (1080→2160). Essencial para redes sociais que comprimem imagens. Use 1 só para debug rápido.
- `--disable-dev-shm-usage` — evita crashes em containers com `/dev/shm` limitado
- `timeout 90` — safety net; HTMLs complexos com muitos gradientes podem demorar

### 3. Verificar

```bash
python3 -c "
import struct
with open('/path/to/output.png', 'rb') as f:
    f.read(16)
    w = struct.unpack('>I', f.read(4))[0]
    h = struct.unpack('>I', f.read(4))[0]
    print(f'{w}x{h} (ratio {w/h:.3f})')
"
```

Com `--force-device-scale-factor=2` e `--window-size=1080,1920`, o PNG terá 2160×3840.

## Dimensões por Plataforma

| Plataforma / Formato | window-size | scale-factor | Proporção |
|---------------------|-------------|--------------|-----------|
| Instagram Story / Reels | 1080,1920 | 2 | 9:16 |
| Instagram Post (quadrado) | 1080,1080 | 2 | 1:1 |
| Instagram Post (retrato) | 1080,1350 | 2 | 4:5 |
| Open Graph / Twitter Card | 1200,630 | 2 | 1.91:1 |
| Twitter Post | 1600,900 | 2 | 16:9 |
| LinkedIn Post | 1200,627 | 2 | 1.91:1 |

## Pitfalls

- **DBus errors (`Failed to connect to the bus`):** Normais em servidor headless. Ignorar — não afetam o output.
- **`libXNVCtrl.so.0 not found`:** Baixar `apt-get download libxnvctrl0` e extrair. Já incluso no setup acima.
- **HTML com `@media print` converte cores para grayscale no PDF, mas screenshot ignora.** Se estiver reusando HTML feito para PDF, remova as regras de `@media print`.
- **Background não aparece:** Coloque `background` no `body` ou num div wrapper com `width: 100%; height: 100%`. O `html` às vezes não preenche o viewport no Chromium headless.
- **Gradiente vaza 1px acima do texto:** Aplique `background-clip: text` num `<span>` dentro do heading, não no próprio `<h1>`/`<h2>`. Ver detalhes em `html-to-pdf-chromium`.
- **Screenshot sai 1× mesmo com scale-factor:** Confirme que `--force-device-scale-factor=2` está ANTES do `file://` na linha de comando.

## Entrega para o Usuário

Inclua `MEDIA:/path/to/output.png` na resposta. No Telegram, imagens PNG aparecem como fotos nativas.
