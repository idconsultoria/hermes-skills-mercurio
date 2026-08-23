---
name: inter-api-id-consultoria
description: "Consultar extrato/saldo da conta Inter da ID."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Banco Inter, API, extrato, saldo, finanças, ID, relatório, CDPJ]
    scopes: [id]
type: ToolIntegration
timestamp: 2026-08-19T13:00:00Z
---

# API do Banco Inter — conta PJ da ID Consultoria (iData)

Consulta o extrato e o saldo da conta corrente PJ da ID no Banco Inter via certificado
CDPJ (escopo `extrato.read`), e gera relatórios personalizados. É o mesmo motor da
automação `idconsultoria/iData` ("Atualizador de extrato").

## Quando usar

- Precisar de consultas ao extrato/saldo da conta Inter da ID (extrato completo, por
  período, detalhes de PIX/pagamento/compra no débito, saldo atual ou por dia).
- Precisar de relatórios financeiros personalizados da conta Inter (fluxo, categorizações,
  resumo por tipo/valor/período) entregues em HTML na identidade da ID.
- Investigar/auditar a automação de comprovantes que alimenta a planilha "[ID] Gestão
  Financeira".

Não usar para: outras contas/bancos, ou escopos além de leitura (`extrato.read`).

## Pré-requisitos (credenciais)

A autenticação exige 4 elementos (o "par" certificado+chave e as credenciais de app):

| Elemento | Onde vive |
|---|---|
| Certificado client | `auth/extrator_de_extrato_inter/Inter API_Certificado.crt` |
| Chave privada | `auth/extrator_de_extrato_inter/Inter API_Chave.key` |
| `client_id` | topo de `etl/extratores/api_inter.py` |
| `client_secret` | topo de `etl/extratores/api_inter.py` |

- Os arquivos estão versionados no repo **`idconsultoria/iData`** (privado). Clone/atualize
  localmente (ex.: `/opt/data/work/idata`) antes de usar a skill.
- Conta corrente PJ: **352969059** (consta no código como `x-conta-corrente`).
- Endpoints (produção, CDPJ partners):
  - token: `https://cdpj.partners.bancointer.com.br/oauth/v2/token` (grant `client_credentials`, scope `extrato.read`)
  - extrato: `.../banking/v2/extrato/completo`
  - saldo: `.../banking/v2/saldo`

> ⚠️ Certificados do Inter valem **1 ano**. Se a autenticação falhar com
> `SSLV3_ALERT_CERTIFICATE_EXPIRED`, o certificado expirou → renovar no Internet Banking PJ
> (Integrar → Nova Integração → Download chave e certificado) e atualizar no repo.

## Setup (uma vez)

```bash
# clonar o motor (se ainda não existir)
TOKEN=$(grep -E "^GITHUB_TOKEN=" /opt/data/.env | head -1 | cut -d= -f2- | tr -d '"')
git clone "https://x-access-token:${TOKEN}@github.com/idconsultoria/iData.git" /opt/data/work/idata
# venv
uv venv /opt/data/work/idata/.venv -q
uv pip install -q -p /opt/data/work/idata/.venv/bin/python -r /opt/data/work/idata/requirements.txt
```

REPO e PY são ajustáveis no script por env var (ver `scripts/inter_api.py`) caso o clone
viva em outro caminho.

## Uso — script `scripts/inter_api.py`

Comandos (read-only por padrão; relatório apenas gera arquivo HTML local):

```bash
PY=/opt/data/work/idata/.venv/bin/python
SC=/opt/data/skills/business/inter-api-id-consultoria/scripts/inter_api.py

# saldo atual
$PY $SC saldo
# saldo por dia em um intervalo
$PY $SC saldo --inicio 2026-06-01 --fim 2026-06-30
# extrato de um período (detalhes PIX/pagamento/compra inclusos)
$PY $SC extrato --inicio 2026-06-01 --fim 2026-06-30
# extrato resumido (data, tipo, titulo, valor)
$PY $SC extrato --inicio 2026-06-01 --fim 2026-06-30 --resumo
# relatório financeiro HTML (identidade ID) de um período
$PY $SC relatorio --inicio 2026-06-01 --fim 2026-06-30 --o /opt/data/work/id-inter-relatorio_v1.html
```

Flags globais: `--repo /caminho/idata`.

## Relatório HTML

O `relatorio` gera um HTML na identidade visual da ID (skill `id-design-guide`):
teal `#14b8a6`, fundo navy `#0a1929` gradient, Neulis Neue + Nunito Sans. Inclui:
resumo (entradas/saídas/saldo inicial e final), distribuição por tipo (barras horizontais,
**nunca** pizza/donut), lista de transações com detalhes, e série de saldo.

## Verificação rápida da autenticação

```bash
$PY $SC saldo   # deve imprimir saldo atual (ex.: disponivel: 75.52)
```
Se falhar, checar: certificado válido (`openssl x509 -in ... -noout -dates`), par
chave/cert casa (`openssl md5` das pubkeys), client_id/secret atuais no `api_inter.py`.

## Pitfalls / observações

- **Escopo é só leitura.** Os endpoints usados não escrevem; o motor de escrita é a
  planilha/Drive da automação, fora desta skill.
- **Saldo por dia** usa `/banking/v2/saldo` com `dataSaldo` (1 chamada/dia). Intervalos
  longos = muitas chamadas; respeitar rate limit (429 → o motor já espera 60s).
- **Paginação**: `obter_extrato` itera páginas de 50 até `ultimaPagina`.
- **Valores**: o extrato devolve `tipoOperacao` C/D; o motor converte para float sinalizado
  (C = +, D = −). Relatório usa o mesmo sinal.
- **Relatório não espelha credenciais**: nunca imprimir client_secret/cert/key em output
  ou chat. Para depurar, mostre só status HTTP e campos de dados.
- A service account do Google (planilha) não é necessária para estas consultas — é outra
  camada (alimentação do Drive/Sheets).

## Relação com o repo

- Motor: `idconsultoria/iData` — `etl/extratores/api_inter.py` (auth/extrato/saldo),
  `etl/transformadores/json_para_pandas.py` (detalhes PIX/pagamento/compra/outros),
  `etl/fluxos/alimentar_planilha_de_gestão_financeira.py` (escrita na planilha).
- Planilha alimentada: "[ID] Gestão Financeira" (ID `1cOMQM2B1ircEdFJ5iiAGiUO7-Mx_qSo51uWDRtAV_gE`),
  abas `CCI_extrato`, `CCI_saldo`, `CCI_detalhes_*`.
