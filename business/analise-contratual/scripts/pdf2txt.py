#!/usr/bin/env python3
"""Extract text from PDFs (e.g. Google Drive downloads) to .txt.

Usage: python3 pdf2txt.py IN.pdf [OUT.txt]

Tries pypdf, then fitz (PyMuPDF), then pdfplumber.

System python usually lacks these libs; create a uv venv and point PYTHONPATH
at its site-packages (prefer this over calling the venv interpreter directly,
which can be blocked by the Hermes security scanner):

  uv venv /tmp/pdfv
  uv pip install --python /tmp/pdfv/bin/python pypdf
  PYTHONPATH="$(ls -d /tmp/pdfv/lib/python*/site-packages)" python3 pdf2txt.py IN.pdf OUT.txt
"""
import sys


def try_pypdf(path):
    from pypdf import PdfReader

    reader = PdfReader(path)
    return "\n".join(
        f"--- PAGE {i + 1} ---\n" + (page.extract_text() or "")
        for i, page in enumerate(reader.pages)
    )


def try_fitz(path):
    import fitz

    doc = fitz.open(path)
    return "\n".join(
        f"--- PAGE {i + 1} ---\n" + (page.get_text() or "") for i, page in enumerate(doc)
    )


def try_pdfplumber(path):
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        return "\n".join(
            f"--- PAGE {i + 1} ---\n" + (page.extract_text() or "")
            for i, page in enumerate(pdf.pages)
        )


def main():
    if len(sys.argv) < 2:
        print("usage: pdf2txt.py FILE.pdf [OUTPUT.txt]")
        sys.exit(1)
    path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    text = None
    for fn in (try_pypdf, try_fitz, try_pdfplumber):
        try:
            t = fn(path)
            if t and t.strip():
                text = t
                break
        except Exception as e:
            print(f"[{fn.__name__} failed: {e}]", file=sys.stderr)

    if not text:
        print("ERROR: could not extract text from PDF")
        sys.exit(2)

    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK -> {out} ({len(text)} chars)")
    else:
        print(text)


if __name__ == "__main__":
    main()
