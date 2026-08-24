---
name: gestao-financeira-id
description: "Operar planilhas/Google da ID e fazer backfill de extrato."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ID, finanças, planilha, Google, Sheets, Drive, Symplexis, backfill, token]
    scopes: [id]
type: Reference
timestamp: 2026-08-19T14:00:00Z
---

# Gestão financeira da ID — planilhas, acessos Google e backfill

Como operar e auditar o mundo de dados financeiros da ID Consultoria: as duas planilhas
mestras, o mapa de **tokens Google** (qual arquivo cobre Sheets/Drive — fonte comum de erro),
e o método de **backfill** da planilha de extrato. A consulta em si à API do Banco Inter
fica na skill irmã `inter-api-id-consultoria`.

## Quando usar

- Auditar/atualizar a planilha de **Gestão Financeira** ou a de **Symplexis** (engagements).
- Ler/escrever Google Sheets ou Drive da ID e precisar do **token certo**.
- Fazer **backfill** do extrato/saldo (a automação só alimenta "ontem"; atrasos exigem isso).
- Investigar de onde vêm os dados (conexões IMPORTRANGE entre as planilhas).

## Planilhas e conexão

| Planilha | ID | Papel |
|---|---|---|
| **[ID] Gestão Financeira** | `1cOMQM2B1ircEdFJ5iiAGiUO7-Mx_qSo51uWDRtAV_gE` | painel de controle financeiro (23 abas): extrato/saldo Inter + classificação + relatórios |
| **[ID] Gestão de Symplexis** | `1qV_L-WMOMDKQwIgLj_l9frokFVO032nsVbM_Qbw8kR0` | planilha-mestra dos **engagements** ("symplexi" = entrega): 13 abas (clientes, contratos, symplexis, recebimentos, sankeys, __projetos, _transações) |

**Conexão bidirecional via IMPORTRANGE:**
- Gestão Financeira importa da Symplexis: `_projetos` (`__projetos!A:Z`) e `_recebimentos` (`recebimentos!A:Z`).
- Symplexis re-importa da Gestão: aba `_transações` (`transações!A:AB`). Overlap verificado = 100%.

**Fluxo do ciclo:**
`Automação iData (Banco Inter) → CCI_* da Gestão Financeira → aba transações (classificação)
→ _transações da Symplexis` ; projetos/recebimentos vão da Symplexis → Gestão Financeira.

## Camadas da Gestão Financeira (23 abas)
1. **Cadastro**: `parâmetros`, `contas`, `_projetos`, `_recebimentos`
2. **Dados brutos API**: `CCI_extrato`, `CCI_saldo`, `CCI_detalhes_PIX/PAGAMENTO/COMPRA_DEBITO/OUTROS`, `extrato_para_verificação`
3. **Gestão/classificação**: `transações`, `pagamentos`, `recebimentos`, `pagamentos_e_recebimentos`, `Sheet14`
4. **Relatórios**: `Lucro bruto por projeto`, `FL por projeto`, `margem_bruta_por_projeto`, `DRE`, `sankey_tabelas`, `Proventos`, `projeção_de_caixa`

Quando a Symplexis está desatualizada, a fonte de verdade dos engagements novos é o Drive
`ID → 4. Operação → 4.2. Symplexis/` (subpastas 4.2.x por cliente). Emails de contrato/NF de
parcela em `admin@idconsultoria.ai` reconstroem recebimentos recentes.

## Acessos Google — mapa de TOKENS (CRÍTICO)

Cada token cobre apenas os escopos com que foi autorizado. **Verifique os `scopes` do token
antes de chamar a API** — usar o errado dá `invalid_scope`/`403`.

| Arquivo token | Conta | Escopos |
|---|---|---|
| `google_token.json` | admin@idconsultoria.ai | **só Gmail** (read/send/modify) — NÃO acessa Sheets/Drive |
| `google_token.admin_idconsultoria.json` | admin@idconsultoria.ai | Gmail + **Drive + documentos** (lê planilha OK) |
| `google_token.gustavo_idteal.json` | gustavo.idteal@gmail.com | só Gmail |
| `google_token.backup_gustavomelloenciv.json` | gustavomelloenciv@gmail.com | full (Drive + spreadsheets + docs + gmail) |

- Para Sheets/Drive da ID use **`google_token.admin_idconsultoria.json`** (ou o backup) e o
  venv `/opt/data/venvs/google/bin/python`. **NÃO** usar `google_token.json` para Sheets.
- A service account do repo iData (`service_account.json`, escopo drive) lê a Gestão
  Financeira (compartilhada), mas **não** a Symplexis (404) — a Symplexis exige token admin.
- Toda entrega visual ao principal ID sai em **HTML** na identidade da ID (skill `id-design-guide`).

## Backfill da planilha (método validado 19/08/2026)

O `entrypoint_ingestão_inter.py` alimenta só **"ontem"**. Para cobrir atrasos:

```python
from etl.fluxos.alimentar_planilha_de_gestão_financeira import (
    alimentar_planilha_com_transações_do_período, registrar_saldo_do_período)
# para cada bloco mensal (ini, fim) na janela em atraso:
alimentar_planilha_com_transações_do_período(str(ini), str(fim))   # extrato + detalhes + pastas de anexos (Drive)
registrar_saldo_do_período(str(ini), str(fim))                     # saldo diário
```

- **Rate limit:** `obter_saldo` por dia dispara 429 no Inter → o motor espera 60s sozinho.
  Backfill de ~4 meses de saldo leva vários minutos → rodar em background
  (`terminal(background=True)` + `notify_on_complete`).
- **Verificação pós-backfill:** ler `CCI_saldo` (alvo = "ontem", gap 0) e datas máximas de cada
  aba `CCI_*`. Data de extrato para antes se não houve movimentação (não é buraco).
- **Idempotência:** após backfill, o cron segue de "ontem" sem duplicar.

## Ler FÓRMULAS (IMPORTRANGE / links)

`values().get` retorna valores **renderizados**, não fórmulas. Para detectar `IMPORTRANGE`,
use `valueRenderOption="FORMULA"` e varra **todas as colunas** (algumas abas têm 200+).

## Pitfalls
- **Google Sheets retorna 503 transitório no `append`/`update`** — um único 503 derruba o dia
  inteiro do cron iData se a chamada `.execute()` não tem retry. O `google_planilhas.py` do repo
  iData precisa de retry + exponential backoff em 429/5xx (500/502/503/504); erros permanentes
  (404, auth) devem falhar imediato. Corrigido no commit `9249e87` (wrapping `_executar_com_retry`
  em `update` e `append`). Diagnóstico rápido: `HttpError 503 ... The service is currently
  unavailable` = indisponibilidade transitória do Google, NÃO problema de cert/token/config.
- Não usar `google_token.json` (Gmail-only) para Sheets/Drive — foi o erro que custou passos na
  primeira tentativa de acessar a Symplexis.
- A skill irmã `inter-api-id-consultoria` cobre a API do Banco Inter em si (consultas/relatórios);
  esta cobre o ecossistema de planilhas e acesso.
