# PDF Data Extraction — pdftotext Fallback

> When `web_search`, `web_extract`, and browser tools all fail (Firecrawl offline, Google CAPTCHA, DuckDuckGo bot detection), extract project-critical data from local PDFs.

## When to use

- `web_search` returns errors (Firecrawl `'NoneType' object has no attribute 'status_code'`)
- Browser hits CAPTCHA/authwalls (Google, LinkedIn)
- The project already HAS the data in a local PDF (TCC, research paper, client doc)

## Pattern

```python
# execute_code with subprocess to pdftotext
import subprocess

pages = [5, 7, 8, 10, 12, 18, 19]  # 1-indexed
pdf_path = "/path/to/document.pdf"

for p in pages:
    result = subprocess.run(
        ["pdftotext", "-f", str(p), "-l", str(p), pdf_path, "-"],
        capture_output=True, text=True
    )
    text = result.stdout.strip()
    if text:
        print(f"=== PAGE {p} ===")
        print(text[:2500])  # Cap output per page
```

## Prerequisites

```bash
# Fedora
sudo dnf install poppler-utils

# Already available on most Linux distros
which pdftotext  # → /usr/bin/pdftotext
```

## Pitfalls

- **PyMuPDF (`fitz`) may not be installed** — `pdftotext` is more reliably available
- **Large PDFs** — Cap output per page (~2500 chars) to avoid flooding context
- **Scanned PDFs** — `pdftotext` won't extract text from images; use OCR fallback

## Validated

- Desconsultor project, 2026-06-16: Extracted 7 pages from research TCC PDF when all web search tools were down
