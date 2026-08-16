# Lendo ESTADO de checkboxes em Google Docs (marcado × vazio)

Confirmado empiricamente (2026-08, guia de demandas CFP IA): a Docs REST API **não
expõe** o estado de checkboxes. O JSON de um parágrafo com bullet é **idêntico**
para marcado e não-marcado:

```json
{"bullet": {"listId": "kix.xxx", "textStyle": {"underline": false}}}
// listProperties.nestingLevels[].glyphType = GLYPH_TYPE_UNSPECIFIED em ambos os casos
```

Não há campo `checked`/`state` em lugar nenhum do documento. Qualquer heurística
baseada no JSON da API vai falhar silenciosamente.

## Fluxo que funciona: PDF export → render → vision_analyze

1. **Exportar o doc como PDF autenticado** (via Drive API, token do venv google):

```python
import json, urllib.request, importlib.util
spec = importlib.util.spec_from_file_location("md_to_gdoc", "/opt/data/skills/productivity/google-workspace/scripts/md-to-gdoc.py")
md = importlib.util.module_from_spec(spec); spec.loader.exec_module(md)
tok = md.get_token()
url = f"https://www.googleapis.com/drive/v3/files/{DOC_ID}/export?mimeType=application/pdf"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
pdf = urllib.request.urlopen(req).read()
open("/tmp/guia.pdf", "wb").write(pdf)
```

2. **Renderizar as páginas com PyMuPDF** (já instalado no venv google — `fitz`):

```bash
/opt/data/venvs/google/bin/python -c "
import fitz
doc = fitz.open('/tmp/guia.pdf')
for i in range(min(2, len(doc))):
    doc[i].get_pixmap(dpi=150).save(f'/tmp/guia-p{i+1}.png')
"
```

(`pdftoppm`/`pdftocairo` NÃO existem neste host — usar PyMuPDF do venv google.)

3. **vision_analyze** na imagem, pedindo o estado linha a linha — dar a lista
   esperada de itens e pedir MARCADO/VAZIO por item. Funciona bem para tabelas
   pequenas (7–10 linhas).

## Caveats

- A detecção depende do modelo de visão — confiável, mas não determinístico.
- Se o requisito for 100% determinístico, trocar os checkboxes por texto legível
  pela API (ex.: coluna "SIM/NÃO" preenchida pelo autor) ou pedir ao autor para
  exportar os estados.
- Verificação alternativa de progresso: `modifiedTime` dos arquivos da pasta via
  Drive API (`drive search`/`drive get`) — bom sinal secundário de atividade, mas
  não prova conclusão.
