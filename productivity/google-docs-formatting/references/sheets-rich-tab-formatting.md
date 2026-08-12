# Sheets — Rich Tab Formatting (state-of-the-art via REST batchUpdate)

Session-proven pitfalls for building **state-of-the-art spreadsheets tabs** (checklists,
dashboards, progress summaries) via the Sheets REST API (`batchUpdate` + `values.update`).
Companion to `sheets-spreadsheet-formatting.md` (basic create+format) — this one is the
advanced/rich-tab layer. All learned 2026-08-12 building a "checklist pré-MVP" tab with
89 tasks, link chips, dropdowns, semáforo colors, and a formula-driven summary tab.

## 1. pt-BR locale: formula argument separator is `;` — NOT `,`

Google Sheets in pt-BR locale interprets `,` as the **decimal separator**, so `;` is the
argument separator. `=SUM(1,2)` becomes text `"1,2"`; `=COUNTIF(A:A,"X")` → `#ERROR!`.

- Write ALL formulas with `;`: `=COUNTIF('Checklist pré-MVP'!G2:G500;"CONCLUIDO")`,
  `=COUNTIFS(Sheet!B2:B500;"cat";Sheet!G2:G500;"CONCLUIDO")`,
  `=SUMIFS(Sheet!I2:I500;Sheet!B2:B500;"cat";Sheet!G2:G500;"CONCLUIDO")`.
- Sheet names with spaces/accents need single quotes: `'Checklist pré-MVP'!A2:A500`.
- **Sanity probe before batch:** write `=1+1` (expect 2) and `=SUM(1;2)` (expect 3) via
  `valueInputOption=USER_ENTERED` and read back FORMATTED_VALUE. If `=SUM(1,2)` renders
  as text `1,2`, locale is pt-BR → use `;`.

## 2. Dropdowns: `ONE_OF_LIST`, not `ONE_OF_RANGE`

`ConditionType.ONE_OF_RANGE` requires EXACTLY ONE condition value (it references a range).
For a fixed list of options use `ONE_OF_LIST` with N values:

```json
{"setDataValidation": {"range": {"sheetId": N, "startRowIndex": 1, "endRowIndex": R,
  "startColumnIndex": 6, "endColumnIndex": 7},
  "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
    {"userEnteredValue": "CONCLUIDO"}, {"userEnteredValue": "EM_ANDAMENTO"}]},
    "showCustomUi": true, "strict": true}}}
```

## 3. Link chips (rich text links) — `textFormatRuns`, format is FLAT

To make per-link chips in one cell (e.g. `[Doc] [Planilha] [Arquivo]` each clickable):

- Use `updateCells` with `textFormatRuns` (plural) on the CellData.
- Inside each run, `format` takes **`link.uri` and `foregroundColor` DIRECTLY** — there is no
  `textFormat` sub-object, and it's `uri`, not `url`:
  `{"startIndex": 0, "format": {"link": {"uri": "https://..."}, "foregroundColor": {...}}}`
- `startIndex` is the char offset in the cell's string; runs inherit until the next run.
- Fields string: `"fields": "userEnteredValue,textFormatRuns"`.

## 4. `repeatCell` — `fields` goes at repeatCell level, not inside `cell`

`{"repeatCell": {"range": {...}, "cell": {"userEnteredFormat": {...}}, "fields": "..."}}`.
Putting `fields` inside `cell` → `Unknown name "fields" at ... repeat_cell.cell` (400).

## 5. Sheet-name URL-encoding in values.update

`values.update` range URLs with accented/space sheet names MUST be percent-encoded:
`urllib.parse.quote('Checklist pré-MVP')` inside the URL. Raw space → `InvalidURL: URL
can't contain control characters`.

## 6. CSV → Sheets: numeric columns arrive as strings

`values.update` with `valueInputOption=RAW` writes `"5"` as a text cell → `SUM` returns 0,
`SUMIFS` fails. Convert numeric columns (`esforco_pontos`, values, dates as needed) to
`int`/`float` in Python BEFORE building the payload:
```python
if h == "esforco_pontos" and v.strip().isdigit():
    v = int(v.strip())
```

## 7. Idempotency: delete + recreate tabs to avoid duplicated banding/rules

Re-running a formatting script against existing tabs duplicates `addBanding` and
`addConditionalFormatRule`. Make the script idempotent by **deleting then recreating** the
tabs at the start (`deleteSheet` by sheetId, `addSheet`, re-fetch sheetId map) before
writing values/formatting.

## 8. Percent display

Fraction results (0–1) from division read as `0,2134831461` by default. Apply
`numberFormat: {"type": "PERCENT", "pattern": "0.0%"}` via `repeatCell` over the % columns
for readability (`21,3%`).

## 8b. colorScale gradient: use MIN/PERCENTILE/MAX, NOT NUMBER

`gradientRule` interpolation points with `type: "NUMBER", value: "0.5"` → 400
`Invalid InterpolationPoint.value` (pt-BR locale rejects the decimal point). Use:
- minpoint: `{"color": {...}, "type": "MIN"}`
- midpoint: `{"color": {...}, "type": "PERCENTILE", "value": "50"}`
- maxpoint: `{"color": {...}, "type": "MAX"}`

Red→yellow→green for % columns: min red `#db2121`, mid amber `#fab90a`, max green `#21a053`.

## 9. Detecting inline images in a Google Doc (verification)

`inlineObjectElement` lives **INSIDE `paragraph.elements`** — NOT as a top-level
`body.content` element. Iterating top-level elements and checking `"inlineObjectElement" in
el` returns 0 even when images exist. Correct count:
```python
for el in content:
    for run in el.get("paragraph", {}).get("elements", []):
        if "inlineObjectElement" in run:
            images += 1
```
The response root also carries `inlineObjects` (id → props map) as a cross-check. When the
user says an image is present but your read says 0, this is almost always the bug.

## 10. Formula-driven summary tab pattern

Build the summary tab with live formulas (COUNTIFS/SUMIFS against the checklist tab) instead
of precomputed numbers, so status changes ripple automatically. Sections: VISÃO GERAL
(COUNTA total, COUNTIF por status, SUM pts, SUMIF pts concluídos), POR CATEGORIA,
POR SUBCATEGORIA, POR SPRINT — each a table of `COUNTIFS`/`SUMIFS` rows keyed on the
category/subcategory/sprint column. Write with `valueInputOption=USER_ENTERED` so `=` is
parsed as formula.

## Recommended build order for a rich checklist tab

1. Delete+recreate tabs (idempotency, §7).
2. `values.update` RAW with numeric conversions (§6).
3. batchUpdate: freeze header row + ID columns, setBasicFilter, header dark fill,
   addBanding, dropdowns (§2), conditional format rules (semáforo by status, colors by
   priority), column widths, wrap on long-text columns, vertical centering.
4. `updateCells` link chips (§3).
5. Build summary tab with formulas (§10), then % formatting (§8).
