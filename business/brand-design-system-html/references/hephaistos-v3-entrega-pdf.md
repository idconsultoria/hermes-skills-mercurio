# Entrega HTML+PDF do relatório Hephaistos — WeasyPrint ARM64

**Entrega 26/08/2026:** relatório Hephaistos v3 — HTML 51KB + PDF 25 páginas/155KB — entregue via Telegram como `MEDIA:/tmp/...html` e `MEDIA:/tmp/...pdf`

## Pipeline que funcionou em container ARM64 sem Chromium

1. HTML gerado com identidade ID.TEAL (`#14b8a6` + navy `#0a1929` + Neulis Neue/Nunito Sans) — ver `references/identidade-id-vs-cliente.md`
2. PDF via WeasyPrint (fallback quando Chromium .deb indisponível):
   ```bash
   apt update -qq && apt install -y libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf2.0-0
   pip install weasyprint
   python3 -c "import weasyprint; doc=weasyprint.HTML(filename='/tmp/input.html').render(); doc.write_pdf('/tmp/output.pdf'); print(len(doc.pages))"
   # 25 páginas, 155KB
   ```
3. Cópia para `/tmp` com `chmod 644` + entrega `MEDIA:/tmp/...` (Telegram)

## Pitfall — arquivo >20MB não chega via Telegram

`hephaistos-20260826-estado-fechado.zip` (63MB) deu `Maximum: 20 MB`. Fallback: pedir link Drive (`drive_link`) e baixar via `google_api.py drive download FILE_ID` — validado 26/08.

## Quando usar este padrão

- Relatórios analíticos multi-página da ID (framework, análises) — identidade ID.TEAL, não do cliente
- Container sem Chromium; WeasyPrint suficiente quando glow/gradiente não é crítico (conteúdo > efeito)
