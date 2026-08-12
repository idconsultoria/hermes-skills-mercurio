---
name: google-docs-formatting
description: "Format Google Docs/Sheets via REST API (markdown, chips).

Load this skill when you need to format Google Docs or Sheets through the REST API — markdown conversion (md-to-gdoc), chips and checkboxes, tables, and mermaid rendering to images. Complements google-workspace with pixel-level fidelity notes."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Google, Docs, Sheets, REST, formatting, markdown, chips, checkboxes]
    related_skills: [google-workspace]
type: ToolIntegration
timestamp: 2026-08-11T00:00:00Z
---

# Google Docs/Sheets Formatting (REST API)

Class-level knowledge for **creating and formatting Google Docs/Sheets with
real structure** via the Docs/Sheets REST APIs — NOT plain text. Companion to
the bundled `google-workspace` skill (CLI/OAuth wrapper, `google_api.py`).
Load this skill when a Google Doc/Sheet must look right: headings, bold,
bullets, native tables, clickable checkboxes, smart chips, callouts.

## When to use

- Converting markdown → Google Docs with correct formatting (never
  `docs create --body`: plain text only, loses tables/chips/checkboxes).
- Reading a Google Doc and needing tables/chips/checkboxes preserved
  (`docs get` returns structured text once `_extract_doc_text` is recursive).
- Creating/formatted spreadsheets: multiple tabs, bold headers, currency
  columns, column autofit.
- Adding smart chips (rich links) that link docs, PDFs, and Drive folders.
- Replacing mermaid/code-notation flowcharts with rendered white-background
  images in Docs (see `references/mermaid-rendering.md`).

## Core tooling

- **Converter script:** `scripts/md-to-gdoc.py` (in the bundled
  `google-workspace` skill: `google-workspace/scripts/md-to-gdoc.py`).
  Batch mode (flush every 25 requests) avoids 429 rate limits.
- **Auth/token:** same OAuth as google-workspace (`google_token.json`),
  refresh via google-auth `Credentials`.
- **Reads:** `google_api.py docs get` now returns structure-preserving text:
  `#`/`##` headings, `-` bullets, `- [ ]` checklists, `[Chip Title]` chips,
  tables as `| a | b |` blocks. If a read shows empty tables, check whether
  `_extract_doc_text` is the recursive version (fix in references).

## Key techniques (see references for depth)

1. **Emoji-safe offsets — ALWAYS `u16len`:** the Docs API indexes by UTF-16
   code units; Python `len()` counts codepoints. An emoji (🎯 = surrogate
   pair) is 2 units, not 1. One emoji shifts every later index by 1 → glued
   paragraphs ("TITLEtext"), wrong style ranges (whole doc becomes heading).
   Use `u16len(s) = len(s.encode("utf-16-le")) // 2` in EVERY offset: `cur`
   advancement, `updateTextStyle` ranges, chip positions, font normalization.
2. **Never let a style range include the trailing `\n`:** style bleeding —
   the style propagates to the next paragraph, cascading through the doc.
   Always use `end - 1` on paragraph ranges.
3. **Chips = `insertRichLink`, not a link style:** accepts
   `docs.google.com/(document|spreadsheets|presentation)` and
   `drive.google.com/(file|open|drive/folders)` URLs. Chip shows the linked
   resource's real title + icon (including Drive folder names). `insertRichLink`
   INSERTS beside the placeholder `\uFFFC` — delete the residual
   (`deleteContentRange [idx+1, idx+2]`) to avoid the OBJ character ￼.
4. **Checkboxes = `createParagraphBullets` with `BULLET_CHECKBOX`:** works in
   paragraphs AND table cells. Empty checkbox cells (`[ ]` alone) still need
   the bullet applied — don't skip cells just because text is empty.
5. **Table cells:** fill from back to front (inserting text shifts later cell
   indexes → everything accumulates in the first cell otherwise). Insert text
   at `cell["content"][0]["startIndex"]` (the paragraph inside the cell), not
   `cell["startIndex"]`.
6. **Smart column widths:** proportionally to content length (max chars per
   column), clamped 60–300pt, total ~560pt; one `updateTableColumnProperties`
   per column in a single batch.
7. **Sheets `#ERROR!` trap:** a value like `+4.500,00` is interpreted as a
   formula (leading `+`) → `#ERROR!`. Strip leading `+` (and thousands
   separators) before writing; send numbers as numeric types.

## References

- `references/mermaid-rendering.md` — render mermaid/flowchart notation to
  **transparent-background PNGs** (mermaid-cli + Hermes Chromium headless_shell,
  `-b transparent -s 2` ≈192 DPI) and swap code blocks for images in Docs.
  Includes the quote+parenthesis parse-error fix, image sizing to fit the
  page, and the pageless-via-API limitation. `.md` sources stay text-only;
  rendering happens only when mirroring to Docs. Show the user a sample
  render BEFORE editing documents.
- `references/md-to-gdoc-pitfalls.md` — 20 pitfalls found in practice
  (style bleeding, font/bullet inheritance, `tableCellLocation` doesn't exist,
  `weightedFontFamily` not `fontFamily`, `link.url` vs `richLink.uri`,
  3-tuple segs, empty table cells, checkbox cells, Drive folder chips,
  `u16len` emoji offsets, parallel-writer race).
- `references/sheets-spreadsheet-formatting.md` — create+format spreadsheets
  via REST batchUpdate: rename Sheet1→Resumo, addSheet, autofit columns,
  bold+shaded headers, currency number formats, move to Drive folder.
- `references/sheets-rich-tab-formatting.md` — **state-of-the-art rich tabs**
  (checklists, dashboards, progress summaries): pt-BR `;` formula separator,
  `ONE_OF_LIST` dropdowns, link chips via `textFormatRuns` (flat `link.uri`),
  `repeatCell` fields placement, sheet-name URL-encoding, CSV string→number
  conversion, delete+recreate idempotency, PERCENT format, inline-image
  detection inside `paragraph.elements`, and the formula-driven summary tab
  pattern (COUNTIFS/SUMIFS). Load this before building any polished tab.
- Quando o CONTEÚDO da tabela vem de um agente (ex.: pi-cost-max gera CSV do
  zero), ver o fluxo de delegação em `product-pipeline` →
  `references/pi-delegation-content-formatting.md` (insumo: árvore do Drive no
  prompt; Hermes sobe + formata depois).

## Workflow (markdown → formatted Doc)

1. Write markdown with the supported syntax (see pitfalls reference table).
2. Run: `python <skill>/scripts/md-to-gdoc.py file.md --title "T" --parent FOLDER`
   (create) or `--doc-id ID` (update existing, preserves ID/link).
3. Verify via `docs get` (structure-preserving) — trust the USER's visual
   check over partial API reads; the run structure can look empty when it
   isn't.

## Pitfall: fixing a read that loses tables

The original `_extract_doc_text` in `google_api.py` only iterated
`doc["body"]["content"]` looking for `paragraph` — table elements were
silently dropped (docs looked empty). The fix: recursive walk over
paragraphs + tables → cells → runs, plus `doc["lists"]` map to distinguish
real checklists (`BULLET_CHECKBOX`: nestingLevels without `glyphSymbol`)
from normal bullets (`●`). See `references/md-to-gdoc-pitfalls.md` #21.
