# md-to-gdoc.py — Pitfalls (found in practice, 2026-08)

All pitfalls below were hit and fixed while converting markdown → Google Docs
for a real project (CFP IA). They apply to ANY Docs REST batchUpdate work.

## Index/offset rules

1. **Style bleeding via `\n`:** applying `updateTextStyle`/`updateParagraphStyle`
   to a range that INCLUDES the trailing `\n` propagates the style to the NEXT
   paragraph — and in cascade through the whole doc. Symptom: whole doc in mono
   font, or every paragraph becomes a heading. Always use `end - 1` on
   paragraph ranges. Same for `createParagraphBullets` and `add_code`.
2. **Emoji offsets — use `u16len()`:** Docs API indexes by UTF-16 code units;
   Python `len()` counts codepoints. 🎯 (U+1F3AF) is a surrogate pair = 2 code
   units, not 1. One emoji shifts all subsequent indexes by 1 → paragraphs
   glued ("TITLEtext"), wrong style ranges. Use `u16len(s) =
   len(s.encode("utf-16-le")) // 2` for EVERY offset: `cur` advancement,
   updateTextStyle ranges, chip positions, font normalization, header bold.
3. **`endOfSegmentLocation` normalizes indexes:** inserting text at
   `endOfSegmentLocation` lands at an unpredictable index. Use
   `location.index = current_end() - 1` (inside the trailing empty paragraph)
   and track `cur` locally. Inserted text starts exactly at `cur`.

## Font / style

4. **Font inheritance on insert:** a paragraph created after a code block is
   born with the mono font inherited. Normalize every paragraph to Arial
   (`_normalize_font`) BEFORE applying bold/code inline — otherwise the mono
   contaminates everything downstream.
5. **`fontFamily` doesn't exist in `updateTextStyle`:** the field is
   `weightedFontFamily: {fontFamily: "..."}`. `fontFamily` direct → 400.
6. **Bullet inheritance cascade:** a paragraph created after a list inherits
   the bullet. `clear_bullet()` must target the CURRENT empty paragraph at
   `[cur, cur+1]` — NOT `[cur-1, cur]` (that deletes the previous item's
   bullet; symptom: only the last item of a list keeps its bullet).

## Chips (rich links)

7. **`insertRichLink` INSERTS, doesn't replace:** inserting a chip at the
   reserved `\uFFFC` index leaves the `\uFFFC` residual at `idx+1` (shift +1,
   gluing the next block). Always follow with
   `deleteContentRange [idx+1, idx+2]`, processing chips BACK TO FRONT so
   deletes don't invalidate earlier chips' indexes.
8. **Field names are inverted between APIs:** `updateTextStyle.textStyle.link`
   uses `url`; `insertRichLink.richLinkProperties` uses `uri`. Mixing them →
   400 "Unknown name".
9. **Chips inside TABLE cells:** the cell loop must handle `richlink` segs —
   otherwise `\uFFFC` shows as the OBJ character ￼. Same insert+delete pattern,
   `offset += 1` (not `u16len(label)`).
10. **Drive folder chips:** `insertRichLink` accepts
    `drive.google.com/drive/folders/<id>`; the chip shows the folder name with
    a folder icon. Include `drive/folders` in the link-detection regex (with
    `docs.google.com/(document|spreadsheets|presentation)` and
    `drive.google.com/(file|open)`).

## Tables

11. **`tableCellLocation` doesn't exist in `insertText`:** no such field in
    `insertText.location`. To fill a cell, insert at the paragraph INSIDE the
    cell: `cell["content"][0]["startIndex"]` — not `cell["startIndex"]`
    (that's the cell marker).
12. **Empty table cells → 400:** `insertText` with `text: ""` is rejected
    ("must specify text to insert"). Skip empty cells (`if not plain:
    continue`) UNLESS the cell is a checkbox (see #13).
13. **Checkbox cells:** a cell `[ ]` (empty, no text) still needs
    `BULLET_CHECKBOX` applied with a range of at least 1. The
    `if not plain: continue` guard must come AFTER checkbox detection; the
    bullet range uses `max(u16len(plain), 1)`.
14. **Fill cells back-to-front:** inserting text in a cell shifts the indexes
    of LATER cells. Fill from the highest index to the lowest, otherwise all
    content accumulates in the first cell.
15. **`segs` are 3-tuples now:** after adding chips/links, every loop over
    segments must unpack `tipo, txt = seg[0], seg[1]` (3rd is url). The old
    `for tipo, txt in segs` → `ValueError: too many values to unpack`.
16. **`emit_segs` must return start:** callers use the return as
    `startIndex` of style ranges; missing `return start` → `start=None` →
    400 "must contain a start and end index".

## Callouts / checklists

17. **Callout with internal heading:** `> ### Título` is NOT parsed as a
    heading (stays literal `###`). Inside callouts use `> **Bold title**` —
    the callout already has a shaded background; bold is enough.
18. **Checkboxes in markdown:** `- [ ] item` → `BULLET_CHECKBOX`. In reads,
    distinguish real checklists from normal bullets via the `doc["lists"]`
    map: checkbox list = nestingLevels WITHOUT `glyphSymbol` (glyphType
    UNSPECIFIED); normal bullet = `glyphSymbol '●'`.

## Operations

19. **429 rate limits:** batch requests (flush every ~25) + exponential retry
    (15s × attempt). Large docs (~700 ops) finish in 2–4 min with a few 429s.
    Never run two converter processes on the SAME doc in parallel — the last
    one to finish wins (indeterminate result if they finish together).
20. **Verify visually, not by API read:** the Docs run structure can LOOK
    empty when it isn't (depends on how `tableRows` is walked). Trust the
    user's visual inspection over partial API reads.

## Read-side fix (docs get losing tables)

Original `_extract_doc_text` in `google_api.py` iterated
`doc["body"]["content"]` looking for `paragraph` — `table` elements were
silently dropped, making documents appear empty. Fix: recursive walk over
paragraphs + tables → cells → runs, emitting headings (`#`), bullets (`-`),
checklists (`- [ ]`), chips (`[Title]`), and tables as `| a | b |` blocks.
