#!/usr/bin/env python3
"""Resume ATS Engine — render_html_to_pdf.py

Renderiza HTML (gerado pelo agy) para PDF A4/Letter via WeasyPrint (ARM64-safe,
sem Chromium). Sanitiza Google Fonts e fontes não instaladas → DejaVu, aplica
auto-fix para padrões de layout do agy que o WeasyPrint renderiza mal, e
verifica ATS-parseabilidade do PDF resultante.

Uso:
    render_html_to_pdf.py <input.html> <output.pdf> [--letter]

Saída:
    <output.pdf> + verificação (páginas, texto extraível)
"""
import re
import sys
import subprocess
from pathlib import Path

CHROMIUM_PRINT_FIX = """
/* === FIX Chromium print: 1 página A4 + fidelidade ao navegador === */
@page { size: A4; margin: 8mm 11mm 8mm 11mm; }
@media print {
  /* Fundos fiéis ao HTML (Chromium não imprime background sem print-color-adjust) */
  body { background-color: #F5EFE6 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .page, .letter-sheet { background-color: #FFFFFF !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .metric-chip, [class*="chip"] { background-color: rgba(229, 220, 206, 0.4) !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .header-divider { height: 1px !important; border-top-width: 1px !important; border-bottom-width: 1px !important; }
  .page { padding: 0 !important; }
  body { font-size: 9pt !important; line-height: 1.22 !important; }
  p { margin: 0 0 2pt !important; }
  h1, .candidata-nome { font-size: 17pt !important; margin: 0 0 2pt !important; }
  .contatos-linha { margin: 2pt 0 !important; font-size: 8pt !important; }
  .destaques-secao { margin-top: 6pt !important; padding-top: 6pt !important; }
  .destaque-item { padding: 2pt 0 !important; }
  .metric-chip { font-size: 7pt !important; padding: 1px 4px !important; }
  .assinatura-secao, .letter-footer { margin-top: 2pt !important; padding: 0 !important; }
  .assinatura-nome, .signature-name { font-size: 12pt !important; }
  .assinatura-linha, .signature-line { width: 60px !important; margin-bottom: 2px !important; }
  .editorial-divider { margin: 2pt 0 !important; }
  .destinatario-bloco { margin: 2pt 0 !important; }
  .drop-cap::first-letter, [class*="drop"]::first-letter { font-size: 24pt !important; }
}
"""

# Mapa de fontes: nome no CSS → fallback instalado no sistema (ARM64 container)
SAFE_FONTS = {
    "dejavu sans": "'DejaVu Sans', sans-serif",
    "dejavu serif": "'DejaVu Serif', serif",
    "dejavu sans mono": "'DejaVu Sans Mono', monospace",
    "arial": "Arial, sans-serif",
    "helvetica": "Helvetica, Arial, sans-serif",
    "times": "'Times New Roman', serif",
    "times new roman": "'Times New Roman', serif",
    "courier": "'Courier New', monospace",
    "courier new": "'Courier New', monospace",
    "georgia": "'DejaVu Serif', serif",
    "inter": "'DejaVu Sans', sans-serif",
    "space mono": "'DejaVu Sans Mono', monospace",
    "syncopate": "'DejaVu Sans', sans-serif",
    "cormorant garamond": "'DejaVu Serif', serif",
    "vt323": "'DejaVu Sans Mono', monospace",
    "system-ui": "system-ui, sans-serif",
    "sans-serif": "sans-serif",
    "serif": "serif",
    "monospace": "monospace",
}


def sanitize_fonts(html: str) -> str:
    """Remove Google Fonts e mapeia fontes desconhecidas para DejaVu (instalada)."""
    html = re.sub(r"<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>", "", html, flags=re.I)
    html = re.sub(r"@import\s+url\([^)]*fonts\.(googleapis|gstatic)\.com[^)]*\)\s*;?", "", html, flags=re.I)

    def repl(m):
        parts = [p.strip().strip("\"'") for p in m.group(1).split(",") if p.strip()]
        out, seen = [], set()
        for fam in parts:
            mapped = SAFE_FONTS.get(fam.lower(), "'DejaVu Sans', sans-serif")
            if mapped not in seen:
                seen.add(mapped)
                out.append(mapped)
        return "font-family: " + ", ".join(out)

    return re.sub(r"font-family\s*:\s*([^;}]+)", repl, html, flags=re.I)


AGY_PAGE_FIX = """
/* === AUTO-FIX agy→WeasyPrint: fluxo natural em vez de páginas simuladas === */
@page { size: A4; margin: 0.55in; @bottom-center { content: counter(page) " de " counter(pages); font-family: 'DejaVu Sans', sans-serif; font-size: 9pt; color: #8C9CA6; } }
@media print {
  body { font-size: 10pt !important; padding: 0 !important; margin: 0 !important; display: block !important; }
  .page { width: auto !important; min-height: auto !important; height: auto !important;
          padding: 0 !important; margin: 0 !important; border: none !important;
          box-shadow: none !important; border-radius: 0 !important;
          page-break-after: auto !important; page-break-inside: auto !important;
          display: block !important; }
  .page-content { padding: 0 !important; }
  .page-footer { display: none !important; }
  .report-header { margin: 0 0 7pt !important; padding: 0 !important; }
  .report-title, h1 { font-size: 19pt !important; margin: 0 0 2pt !important; }
  .report-subtitle { font-size: 10.5pt !important; margin: 0 0 4pt !important; }
  .section-title { font-size: 11pt !important; margin: 8pt 0 3pt !important; page-break-after: avoid !important; break-after: avoid !important; }
  .meta-card, .competitor-card, .grid-item { min-height: auto !important; height: auto !important;
          padding: 6pt 10pt !important; margin: 0 0 4pt !important;
          page-break-inside: auto !important; }
  .campaign-grid, .competitors-grid, .team-grid { grid-template-columns: 48% 48% !important; justify-content: space-between !important; gap: 0 !important; margin-top: 4pt !important; }
  .timeline { gap: 6pt !important; margin: 6pt 0 !important; }
  .timeline-item { min-height: auto !important; margin: 0 0 2pt !important; }
  .timeline-year { font-size: 8.5pt !important; }
  p, li, .meta-card-value, .meta-card-label, .grid-value, .grid-label { font-size: 10pt !important; }
  .sources-section { margin: 5pt 0 0 !important; }
  .sources-section li { margin: 0 0 2pt !important; }
  * { box-sizing: border-box !important; }
  .page-content { margin-right: 5pt !important; overflow: hidden !important; }
}
"""

AGY_GRID_FIX = """
/* === AUTO-FIX agy→WeasyPrint: grids 2 colunas (sem mexer em fontes/margens) === */
@media print {
  .main-grid { display: block !important; }
  .column-left, .column-right, .left-column, .right-column { display: block !important; width: 100% !important; float: none !important; flex: none !important; height: auto !important; }
  .letter-body { display: block !important; height: auto !important; }
  .resume-page, .a4-page { height: auto !important; min-height: auto !important; }
  .resume-content { height: auto !important; }
  body { min-height: auto !important; }
  * { box-sizing: border-box !important; }
  .skill-badge { overflow: hidden !important; }
}
"""

AGY_LETTER_FIX = """
/* === AUTO-FIX agy→WeasyPrint: carta 1 página (card com min-height fixo) === */
@page { margin: 8mm 12mm 8mm 12mm; }
@media print {
  body { min-height: auto !important; height: auto !important; width: auto !important; font-size: 8.5pt !important; line-height: 1.25 !important; }
  .letter-card, .a4-page, .letter-sheet { min-height: auto !important; height: auto !important; overflow: visible !important; zoom: 1 !important; display: block !important; }
  .letter-card > div, .letter-content, .letter-body, main, header, .header-main, .header-row, .contact-row, .document-header { display: block !important; }
  .letter-content, .letter-body { font-size: 8.5pt !important; line-height: 1.25 !important; }
  h1, .candidate-name { font-size: 14pt !important; margin: 0 0 1pt !important; }
  header, .document-header, .contact-row, .destinatario-bloco, .data-linha { page-break-inside: auto !important; break-inside: auto !important; }
  p { margin: 0 0 2pt !important; }
  li { margin: 0 0 1pt !important; }
  ul { margin: 1pt 0 2pt !important; padding-left: 9pt !important; }
  .signature-area, .signature-section { margin-top: 6pt !important; page-break-inside: auto !important; }
  [class*="metric"], [class*="chip"], [class*="stat"], [class*="kpi"] { font-size: 7pt !important; margin: 0 1.5pt 0 0 !important; display: inline !important; }
  section, .section { page-break-inside: auto !important; }
  /* Drop cap sem float (WeasyPrint 69 crasha com ::first-letter { float }) */
  .drop-cap::first-letter, [class*="drop"]::first-letter { float: none !important; font-size: 26pt !important; line-height: 0.9 !important; color: #C9A227 !important; padding-right: 2pt !important; }
  /* Compactação direcionada para cartas do agy com .page + cards + destaques */
  .page { padding: 16px 24px !important; gap: 6px !important; }
  .card-item { padding: 3px 0 !important; }
  .cards-linha { margin: 3px 0 !important; gap: 4px !important; }
  .destaques-secao { margin-top: 7px !important; padding-top: 7px !important; }
  .destaque-item { padding: 3px 0 !important; }
  .destaque-metrics { display: inline !important; flex-wrap: wrap !important; gap: 2px !important; }
  .document-header, .destinatario-bloco { margin: 0 !important; padding: 0 !important; }
  .contatos-linha { margin: 2px 0 !important; }
}
"""


def auto_fix_agy(html: str) -> str:
    """Detecta HTML do agy e injeta os CSS fixes apropriados (podem combinar):
    - páginas simuladas (.page min-height:297mm + page-break-after:always) →
      AGY_PAGE_FIX (fluxo natural + fontes/margens).
    - carta de apresentação (.letter-card/.a4-page com min-height/zoom) →
      AGY_LETTER_FIX (1 página).
    - grids 2 colunas (.main-grid com fr) que o WeasyPrint renderiza mal →
      AGY_GRID_FIX (empilha, sem tocar no restante do design).
    Idempotente."""
    if "AUTO-FIX agy" in html:
        return html
    idx = html.rfind("</style>")
    if idx == -1:
        return html
    fixes = []
    if "min-height: 297mm" in html and "page-break-after: always" in html:
        fixes.append(AGY_PAGE_FIX)
    title = re.search(r"<title>([^<]*)</title>", html, re.I)
    is_letter = any(s in html for s in [".letter-card", ".a4-page", ".letter-body", ".signature-section"])
    if title and re.search(r"carta|cover letter", title.group(1), re.I):
        is_letter = True
    if is_letter:
        fixes.append(AGY_LETTER_FIX)
    if any(g in html for g in [".main-grid", ".campaign-grid", ".competitors-grid", ".team-grid"]):
        fixes.append(AGY_GRID_FIX)
    if fixes:
        return html[:idx] + "\n".join(fixes) + html[idx:]
    return html


def sanitize_chromium(html: str) -> str:
    """Para Chromium: SÓ remove Google Fonts (links/@import) — NÃO mapeia
    font-family (o Chromium do host tem fontes do sistema e faz fallback
    natural; mapear para DejaVu infla o layout e quebra a paginação)."""
    html = re.sub(r"<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>", "", html, flags=re.I)
    html = re.sub(r"@import\s+url\([^)]*fonts\.(googleapis|gstatic)\.com[^)]*\)\s*;?", "", html, flags=re.I)
    return html


CHROMIUM_FIDELITY_FIX = """
/* === FIX Chromium print — FIDELIDADE MÁXIMA (mínimo absoluto) === */
/* Regra do usuário: NÃO compactar no print (nada de font-size/margin/line-height
   no @media print). O design deve caber em 1 página NATURALMENTE. Este fix só
   garante que o Chromium imprima cores de fundo (sem print-color-adjust o
   Chromium descarta backgrounds). */
@media print {
  body { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .page, .letter-sheet, .metric-chip, [class*="chip"] { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
}
"""


CHROMIUM_FONTS_DIR = "/opt/data/tmp/fonts_letter"

CHROMIUM_FONT_FACE = """
/* === FONT-FACE embutido (fidelidade tipográfica ao design) === */
@font-face { font-family: "EB Garamond"; src: url("file:///home/ubuntu/fonts/EBGaramond.ttf"); font-weight: 100 900; font-style: normal; }
@font-face { font-family: "EB Garamond"; src: url("file:///home/ubuntu/fonts/EBGaramond-Italic.ttf"); font-weight: 100 900; font-style: italic; }
@font-face { font-family: "Playfair Display"; src: url("file:///home/ubuntu/fonts/PlayfairDisplay.ttf"); font-weight: 100 900; font-style: normal; }
@font-face { font-family: "Playfair Display"; src: url("file:///home/ubuntu/fonts/PlayfairDisplay-Italic.ttf"); font-weight: 100 900; font-style: italic; }
@font-face { font-family: "Cinzel"; src: url("file:///home/ubuntu/fonts/Cinzel.ttf"); font-weight: 100 900; font-style: normal; }
"""


def render_chromium(html_path: Path, out_path: Path):
    """Render HTML → PDF via Chromium headless no HOST (ssh oracle-host).
    Padrão aprendido da IAF newsletter: Chromium renderiza fiel ao navegador
    (drop caps, chips, ornamentos) — o WeasyPrint degrada CSS moderno.
    Requer: ssh oracle-host + chromium-browser (snap).

    FIDELIDADE TIPOGRÁFICA: o snap do Chromium tem fontconfig isolado (não vê
    fontes do usuário nem /usr/share/fonts custom). Solução: injetar @font-face
    com src file:// para /home/ubuntu/fonts/*.ttf (o snap lê /home/ubuntu).
    Fontes: EB Garamond (corpo), Playfair Display (nome/drop cap), Cinzel
    (nome). Pré-requisito: /opt/data/tmp/fonts_letter/ com os .ttf."""
    html = html_path.read_text(encoding="utf-8")
    html = sanitize_chromium(html)
    if "FONT-FACE embutido" not in html:
        idx = html.rfind("</style>")
        if idx != -1:
            html = html[:idx] + CHROMIUM_FONT_FACE + html[idx:]
    # Fix de impressão: por padrão FIDELIDADE MÁXIMA (mínimo — só cores).
    # Com --compact injeta o CHROMIUM_PRINT_FIX (compactação; usuário rejeitou).
    print_fix = CHROMIUM_PRINT_FIX if (sys.argv and "--compact" in sys.argv) else CHROMIUM_FIDELITY_FIX
    if print_fix and "CHROMIUM PRINT FIX" not in html and "CHROMIUM FIDELITY FIX" not in html:
        idx = html.rfind("</style>")
        if idx != -1:
            html = html[:idx] + print_fix + html[idx:]
    ssh_cfg = str(Path.home() / ".ssh" / "config")
    # Garante fontes no host (rápido; idempotente)
    try:
        import glob as _glob
        subprocess.run(["ssh", "-F", ssh_cfg, "oracle-host", "mkdir -p /home/ubuntu/fonts"],
                       check=True, capture_output=True, timeout=30)
        font_files = _glob.glob(str(Path(CHROMIUM_FONTS_DIR) / "*.ttf"))
        if font_files:
            subprocess.run(["scp", "-F", ssh_cfg] + font_files + ["oracle-host:/home/ubuntu/fonts/"],
                           check=True, capture_output=True, timeout=60)
    except Exception as e:  # noqa: BLE001
        print(f"[warn] Não foi possível copiar fontes ({e}) — o PDF pode cair em fallback.")
    work = html_path.with_name(html_path.stem + "_chromium" + html_path.suffix)
    work.write_text(html, encoding="utf-8")
    remote_in = f"/home/ubuntu/{work.name}"
    remote_out = "/home/ubuntu/render_chromium_out.pdf"
    ssh_cfg = str(Path.home() / ".ssh" / "config")
    subprocess.run(["scp", "-F", ssh_cfg, str(work), f"oracle-host:{remote_in}"], check=True)
    cmd = (f"chromium-browser --headless --no-sandbox --disable-gpu --no-pdf-header-footer "
           f"--print-to-pdf={remote_out} 'file://{remote_in}' 2>/dev/null")
    subprocess.run(["ssh", "-F", ssh_cfg, "oracle-host", cmd], check=True)
    subprocess.run(["scp", "-F", ssh_cfg, f"oracle-host:{remote_out}", str(out_path)], check=True)
    return str(out_path)


def main():
    if len(sys.argv) < 3:
        print("Uso: render_html_to_pdf.py <input.html> <output.pdf> [--letter]")
        sys.exit(2)
    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    letter = "--letter" in sys.argv[3:]
    chromium = "--chromium" in sys.argv[3:]

    if not inp.exists():
        print(f"[html] ❌ Arquivo não encontrado: {inp}")
        sys.exit(1)

    if chromium:
        try:
            pdf_path = render_chromium(inp, out)
            print(f"[pdf-chromium] OK: {pdf_path}")
        except Exception as e:  # noqa: BLE001
            print(f"[pdf-chromium] ❌ FALHOU ({e}) — usando fallback WeasyPrint")
            pdf_path = None
        if pdf_path:
            from pypdf import PdfReader
            reader = PdfReader(str(out))
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
            print(f"[verify] PDF: {len(reader.pages)} página(s), {len(text)} chars extraídos")
            if len(reader.pages) > 2:
                print("[verify] ⚠️  Mais de 2 páginas — revise compactação.")
            print("[ats] ✅ VERIFICADO")
            sys.exit(0)
        # fallthrough para WeasyPrint se falhou

    raw = inp.read_text(encoding="utf-8")
    html = sanitize_fonts(raw)
    html = auto_fix_agy(html)

    import weasyprint

    # Força tamanho de página via CSS (a menos que o auto-fix já tenha definido)
    page_css = ("@page { size: A4; margin: 0.75in; }"
                if not letter else
                "@page { size: Letter; margin: 0.75in; }")
    if "AUTO-FIX agy" in html and "AGY_PAGE_FIX" in html:
        pass  # o fix já definiu @page
    elif "<style>" in html:
        html = html.replace("<style>", f"<style>{page_css}", 1)
    else:
        html = html.replace("</head>", f"<style>{page_css}</style></head>", 1)

    weasyprint.HTML(string=html, base_url=str(inp.parent)).write_pdf(str(out))
    print(f"[pdf] OK: {out}")

    from pypdf import PdfReader
    reader = PdfReader(str(out))
    pages = len(reader.pages)
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    ok = len(text.strip()) > 50
    print(f"[verify] PDF: {pages} página(s), {len(text)} chars extraídos")
    if not ok:
        print("[verify] ⚠️  Texto extraível insuficiente — verifique se o HTML não é imagem/texto em SVG.")
        sys.exit(1)
    print("[ats] ✅ VERIFICADO")
    sys.exit(0)


if __name__ == "__main__":
    main()
