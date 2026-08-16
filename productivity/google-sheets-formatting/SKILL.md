---
name: google-sheets-formatting
description: "Formatar Google Sheets via API — batchUpdate pitfalls validados.

Carregue esta skill ao criar/popular/formatar planilha Google via Sheets API (googleapiclient, gws, batchUpdate): múltiplas abas, fórmulas vivas, banding, charts e numberFormat. Cobre erros reais (No grid with id, sobreposição de addBanding, BOTTOM_AXIS, valores que não formatam como moeda/%). Complementa google-workspace com lições de formatação validadas em execução real."
version: 1.0.0
author: Hermes
license: MIT
type: ToolIntegration
timestamp: 2026-08-15T09:15:00Z
metadata:
  hermes:
    tags: [google-sheets, sheets-api, formatting, automation, batchupdate]
    category: productivity
    related_skills: [google-workspace, valuation-consultivo]
---

# Google Sheets — Formatação e Construção via API (pitfalls validados)

## When to Use

- Criar/popular/formatar uma planilha Google via Sheets API (`googleapiclient`, `gws`, scripts com batchUpdate) — múltiplas abas, fórmulas vivas, banding, charts e numberFormat.
- Quando um script de Sheets falhar com `No grid with id`, sobreposição de `addBanding`, `Bar charts ... BOTTOM_AXIS`, ou valores que não formatam como moeda/%.
- Complementa `google-workspace` (bundled) — esta skill carrega os pitfalls de formatação validados em execução real.

Guia de armadilhas reais encontradas ao criar e formatar uma planilha Google via Sheets API (`googleapiclient`, batchUpdate). Complementa a skill `google-workspace` (bundled) com as lições de FORMATAÇÃO que ela não documenta. **Validado em 15/08/2026** (planilha de valuation com 9 abas, rNPV + cap table, ~150 requests).

## Setup (resumo)

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file("/opt/data/google_token.json",
    ["https://www.googleapis.com/auth/spreadsheets"])
if creds.expired and creds.refresh_token: creds.refresh(Request())
svc = build("sheets", "v4", credentials=creds)
```

Criar com todas as abas de uma vez: `spreadsheets().create(body={"properties":{"title":T},"sheets":[{"properties":{"title":a}} for a in ABAS]})`. **Buscar os sheetIds reais** com `spreadsheets().get(fields="sheets.properties(sheetId,title)")` — o Google atribui IDs NÃO sequenciais; usar `ABAS.index()` como sheetId dá erro `No grid with id: N`.

## Pitfalls (todos reproduzidos nesta sessão)

### 1. Índices de range são 0-based (o bug nº 1)
`startRowIndex`/`endRowIndex`/`startColumnIndex`/`endColumnIndex` são **0-based** e `end*` é exclusivo. Erro clássico: pensar 1-based e deslocar tudo +1 linha → formatos aplicados nas células erradas (ex: `r` exibido como "R$ 0", burn como "3200000,0%"). **Sempre conferir cada range contra a planilha 1-based: linha 1 = índice 0; range [r0, r1) cobre linhas r0+1..r1.**

### 2. `addBanding` falha se já existe banding no range
`Invalid ... Não é possível adicionar cores de fundo alternadas a um intervalo que já tenha cores de fundo alternadas`. Se o script roda 2x (ou já formatou antes): buscar `sheets(bandedRanges(bandedRangeId))` e emitir `deleteBanding` para cada ID ANTES de re-adicionar. O batchUpdate é **atômico** — se um request falha, NADA é aplicado (e o `values.clear` anterior já rodou, deixando a aba vazia).

### 3. Gráfico BAR só aceita `targetAxis BOTTOM_AXIS`
`Bar charts series may only target the BOTTOM_AXIS`. Não usar `targetAxis: LEFT_AXIS` em séries de bar chart — omitir o campo.

### 4. Números gravados como string não formatam
Em `updateCells`/`values.batchUpdate`, número Python vira `{"userEnteredValue":{"stringValue":"5000000"}}` se você fizer `str(v)` — a célula fica TEXTO e ignora `numberFormat` de moeda. **Usar `numberValue` para int/float, `formulaValue` para strings que começam com `=`, `stringValue` só para texto.**

### 5. `endColumnIndex` = comprimento MÁXIMO das linhas
Em `updateCells` com várias linhas de larguras diferentes (ex: uma linha de 1 coluna e outra de 4), usar `len(values[0])` dá `Attempting to write column: 1, beyond the last requested column of: 0`. Usar `max(len(r) for r in values)`.

### 6. Fórmulas com separador decimal
No locale BR do Google Sheets, fórmula com `*1.3` pode dar `#ERROR!` em célula que a fórmula `*1,3` aceita. Ao injetar fórmulas via API com decimais, preferir vírgula (`*1,3`).

### 7. `header()` de helper pinta SEMPRE a linha 0
Se o helper "header" hard-coda `startRowIndex:0`, chamá-lo 2x numa mesma aba (ex: duas tabelas) sobrescreve o título/hero da linha 0. Fazer `header_at(sheet, r, ncols)` parametrizado por linha.

### 8. Section titles via `updateCells` com `fields:"userEnteredValue"` sobrescrevem valor mas preservam formato antigo
Após `clear`, sem problema. Mas se a célula já tinha formato (ex: de uma execução anterior), o texto novo herda o formato antigo — reaplicar formato depois, ou clear antes.

## Convenções de cor (padrão Hermes Official / financeiro)

- Headers: fundo `#1A73E8`, texto branco bold 11pt, centralizado
- Inputs/premissas-chave: fundo dourado `#FFD959` (r, ticket, pré-money, rNPV, post-money)
- Zebra: `#F5F8FE` (branco alternado)
- Confiança: ALTA verde `#E6F4EA` / MÉDIA âmbar `#FFF0E0` / BAIXA vermelha `#FCE8E6`
- Números: moeda `R$ #,##0` (nunca sem formatação), `%` 0.0%, múltiplo `0.0"x"`
- `td.num` (valores financeiros): `text-align:right`
- **Nunca pizza/donut** (preferência do usuário) — barras horizontais ou tabelas
- Congelar header: `updateSheetProperties gridProperties frozenRowCount`

## Verificação

- Conferir valores formatados com `sheets().values().get()` (retorna FORMATTED_VALUE por default) — "R$ 0" ou "3200000,0%" = range errado (pitfall 1) ou número gravado como string (pitfall 4)
- Acessibilidade/DOM não prova renderização visual: em HTML use browser; em Sheets, conferir cells + numberFormat via API
