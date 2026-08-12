---
name: google-sheets-automation
description: "Polish Google Sheets via API (dropdowns, formulas, KPIs).

Load this skill when you need to polish Google Sheets via API — data validation dropdowns, formulas, KPI sheets, and UX best practices. Complements google-workspace and xlsx."
version: 1.0.0
author: Hermes curator
license: MIT
type: ToolIntegration
timestamp: 2026-08-12T00:00:00Z
metadata:
  hermes:
    tags: [Google, Sheets, Drive, spreadsheet, API]
    related_skills: [google-workspace, xlsx]
---

# Google Sheets Automation (UX/UI estado-da-arte via API)

Cria e formata planilhas Google (checklist, dashboard de progresso, trackers) com padrão
executivo/analista de dados, tudo via Sheets API (`batchUpdate` + `values` endpoints).

## When to Use

- Usuário pede aba/planilha com "formatação agradável", "estado-da-arte", "visual para executivo"
- Pipeline CSV → aba do Google Sheets (ex.: Pi gera CSV → Hermes sobe e formata)
- Checklist, progresso por categoria/sprint, KPIs

## Autenticação e helpers (reutilizar md_to_gdoc.get_token)

```python
import sys, json, time, urllib.request, urllib.error
sys.path.insert(0, "/opt/data/code/workstation/cfp-ia/scripts")
from md_to_gdoc import get_token

def api_request(url, method, payload=None):
    headers = {"Authorization": f"Bearer {get_token()}"}
    data = json.dumps(payload).encode() if payload is not None else None
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:600]
            if e.code == 429:
                time.sleep(12 * (attempt + 1)); continue
            print(f"API ERROR {e.code}: {body}", file=sys.stderr); raise
    raise RuntimeError("rate limit")
```

Batch: aplicar `requests` em lotes de ≤40 com `sleep(1)` entre lotes (anti-429).

## Pitfalls CRÍTICOS (todos vividos em produção)

1. **Locale pt-BR: separador de argumento de fórmula é `;` não `,`** — `=COUNTIF(rng;"CONCLUIDO")`,
   `=COUNTIFS(...,rng;"P0")`, `=SUMIFS(...)`. Com `,` a fórmula dá `#ERROR!` ou vira texto.
2. **Dropdown com múltiplos valores: `ONE_OF_LIST`, NUNCA `ONE_OF_RANGE`** — `ONE_OF_RANGE` exige
   exatamente 1 condition value (400: "requires exactly one ConditionValue, but 5 values were supplied").
3. **URL-encode do nome da aba na URL values**: `values/Checklist pré-MVP!A1:O42` → `urllib.parse.quote('Checklist pré-MVP')`.
4. **`textFormatRuns[].format` — campos de fonte vão DIRETO no `format`** (não aninhados em
   `textFormat`): `{"startIndex": 0, "format": {"link": {"uri": url}, "foregroundColor": {...}}}`.
   Erro: `Unknown name "textFormat" at ...text_format_runs[0].format`.
5. **`fields` no `repeatCell` vai NO NÍVEL do request**, não dentro de `cell`:
   `{"repeatCell": {"range": {...}, "cell": {...}, "fields": "..."}}`. Dentro do cell → 400
   `Unknown name "fields" at ...repeat_cell.cell`.
6. **gradientRule (colorScale)**: usar `type: MIN/MAX/PERCENTILE` — `NUMBER` com `"0.5"` falha
   (400 `Invalid InterpolationPoint.value`). Ex.: midpoint `{"type": "PERCENTILE", "value": "50"}`.
7. **Números como string no CSV → SUM/SUMIFS retornam 0**: converter `esforco_pontos` etc. para
   `int()` antes de escrever (`valueInputOption=RAW` grava texto se vier string).
8. **Idempotência**: para re-rodar sem duplicar banding/regras condicionais, **deletar e recriar**
   as abas no início do script (`deleteSheet` + `addSheet`), depois re-escrever dados.
9. **Smart-chips nativos do Sheets NÃO são criáveis via API** (só via UI com @). Aproximação visual:
   **pill** = fundo claro + bordas SOLID + `textFormatRuns` com link + center alignment.
10. **Fórmulas**: escrever com `valueInputOption=USER_ENTERED` (senão vira texto literal).

## Padrão UX para aba executiva

- Banner dark (`#0f2a4a`) com título + linha de meta
- **KPI cards**: linha de rótulos + linha de valores (fundo azul claro, `fontSize: 16`, bold)
- Tabelas por agrupamento (categoria, subcategoria, responsável, sprint) com COUNTIFS/SUMIFS
- colorScale vermelho→amarelo→verde na coluna % (MIN/MAX/PERCENTILE)
- Checklist: freeze (linha 1 + colunas ID/Categoria), autofiltro, banding, dropdowns com
  validação (Status/Prioridade/Sprint/Responsável/Categoria/Subcategoria), semáforo por status
  (formatação condicional TEXT_EQ), wrap em descrição/critério, larguras por coluna
- Links como pills na coluna de documentos (ver pitfall 9)

## Pipeline CSV → Sheets (padrão validado)

1. **Pi gera o CSV do zero** (pi-cost-max) — usuário exige que Pi NÃO veja trabalho prévio do Hermes
   (sem viés); prompt leva árvore de links do Drive como insumo para Pi escolher links por tarefa
2. Validar CSV (cabeçalho, contagens, status permitidos)
3. Script sobe na aba + formata (padrão acima)
4. Verificar valores CALCULADOS via `valueRenderOption=FORMATTED_VALUE` (fórmulas renderizando)

## Verificação pós-escrita

- Ler `Progresso!A6:B15?valueRenderOption=FORMATTED_VALUE` — conferir que COUNTIF retorna número
  e não `#ERROR!`
- Ler coluna de links com FORMATTED_VALUE — confirmar pills `[Doc] [Planilha]`
- Conferir abas via `?fields=sheets.properties.title` (sem duplicatas)

## Referências

- `references/sheets-api-pitfalls.md` — payloads exatos, erros 400 vistos, checklist de correção
