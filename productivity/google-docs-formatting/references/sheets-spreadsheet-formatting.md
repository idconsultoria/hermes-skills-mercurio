# Spreadsheet creation + formatting via Sheets REST API

Pattern for creating a formatted Google Spreadsheet (multi-tab, styled) when
the `google_api.py` wrapper only offers `sheets create/get/update/append`
(no `addSheet`, no move-to-folder, no formatting). Use the REST API directly
with the same OAuth token as google-workspace.

## Sequence

1. **Create** — POST `https://sheets.googleapis.com/v4/spreadsheets`
   `{"properties": {"title": ...}}` → `spreadsheetId`.
2. **Move to Drive folder** — PATCH
   `https://www.googleapis.com/drive/v3/files/{id}?addParents={folder}&removeParents={old}&fields=id`
   (get `parents` first with `?fields=parents`).
3. **Tabs** — one `batchUpdate` with `updateSheetProperties` (rename the
   auto-created `Sheet1` → e.g. "Resumo", `fields: "title"`) plus one
   `addSheet` per extra tab (`{"properties": {"title": ...}}`).
4. **Fill** — PUT
   `https://sheets.googleapis.com/v4/spreadsheets/{id}/values/{Tab}!A1?valueInputOption=USER_ENTERED`
   with `{"values": [[...]]}`. (POST append to append below existing.)
5. **Format** — one `batchUpdate` with:
   - `autoResizeDimensions` per tab (`dimensions: {sheetId, dimension:
     "COLUMNS", startIndex: 0, endIndex: N}`)
   - `repeatCell` header row: `textFormat.bold: true` +
     `backgroundColor` light gray, `fields: "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"`
   - `repeatCell` currency columns:
     `numberFormat: {type: "CURRENCY", pattern: "R$ #,##0.00"}`
   - `repeatCell` bold on TOTAL row
   - Batches must target `sheetId` (numeric) per tab — `repeatCell` without
     `sheetId` hits the active tab only.

## #ERROR! trap (critical)

Sheets interprets a cell value starting with `+` as a FORMULA →
`+4.500,00` renders `#ERROR!`. When converting Brazilian-formatted values
(`+4.500,00`, `-1.000,00`, `R$ 2.450`):
- strip leading `+` and `R$`
- strip thousands separators (`.`)
- swap decimal comma → dot
- attempt `float()`; on failure keep the original string
- send numbers as numeric types (JSON float), not strings

## Money display

With `USER_ENTERED`, a float `4500.0` + currency format shows as
`R$ 4.500,00`. Negative floats show `-R$ 1.000,00`. Keep the raw numbers in
the API (formatting is presentation only) so the sheet stays sortable and
computable — do not write pre-formatted strings back into value cells.

## Verified example

3 per-case spreadsheets (Resumo/Extrato/Fatura/Contratos [+ Investimentos])
built from HTML artifact tables: 13–16 format requests each, applied in
batches of 50, all returned OK. Column autofit + bold/shaded headers +
currency on money columns + bold TOTAL row.
