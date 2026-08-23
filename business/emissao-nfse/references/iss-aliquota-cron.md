# Captura mensal da alíquota de ISS (cron)

Como a alíquota do ISS (`pAliq`) é obtida automaticamente todo mês para alimentar o motor
NFS-e. A fonte é o email mensal da contabilidade da ID.

## Fonte
- **Remetente:** `Setor Fiscal <setorfiscal@angeladantas.com.br>` (contabilidade da ID).
- **Assunto:** `ALÍQUOTA DE ISS MM.YYYY` (ex.: `ALÍQUOTA DE ISS 08.2026`), enviado até o dia 5.
- **Conta:** `gustavo.idteal@gmail.com` (2ª conta Google da ID — token dedicado
  `google_token.gustavo_idteal.json`; `admin@idconsultoria.ai` é o primário `google_token.json`).
- **Corpo (exemplo):** "A alíquota de ISS a ser utilizada no mês de agosto é 2,0100%."

## Storage (facilmente recuperável pelo motor)
- **`/opt/data/id-nfse-motor/dados/aliquota_iss.json`** (schema):
  ```json
  {
    "aliquota_iss": 2.01,
    "competencia": "08/2026",
    "mes": "agosto",
    "fonte_email": {"from": "...", "subject": "...", "date": "...", "message_id": "..."},
    "atualizado_em": "ISO 8601"
  }
  ```
- Human-readable em `dados/aliquota_iss.txt`. O motor lê `aliquota_iss` para o campo `pAliq`.

## Cron
- Nome `Alíquota ISS mensal (ID)` · job `3dfe43219f1b` · schedule `0 10 5 * *` (dia 5, 10h BRT).
- Wrapper em `/opt/data/scripts/buscar_aliquota_iss.sh` → chama o venv do Google:
  `/opt/data/venvs/google/bin/python /opt/data/id-nfse-motor/scripts/buscar_aliquota_iss.py`.

## Script — decisões implementadas
- **Query Gmail:** `from:setorfiscal subject:"ALÍQUOTA DE ISS"` (maxResults=5; usa o email mais
  recente).
- **Regex alíquota:** `(\d{1,3}[,.]\d{2,4})\s*%` sobre o corpo em texto puro (o email usa
  `*agosto*` com marcador — `\w+` após "mês de" falha por causa do `*`, use `mês de[^\w]*(\w+)`).
- **Competência:** do assunto `(\d{2})\.(\d{4})` → `MM/YYYY`.
- **Idempotência:** se `competencia` já está no JSON → `SEM_MES_NOVO`, sai sem sobrescrever.

## Fallback de agente (job é de AGENTE, não no_agent)
O cron é um **job de LLM** (enabled_toolsets=terminal,file) cujo stdout do script é injetado
como contexto. O agente decide:
1. stdout `ALÍQUOTA ISS ... capturada` → script já gravou; só confirma.
2. stdout `SEM_MES_NOVO` → responde que o mês já está armazenado.
3. stdout `ERRO_EXTRACAO` → o corpo bruto está após `RAW_EMAIL_BAIXO:`; o agente lê e grava
   `aliquota_iss.json` manualmente via write_file.
4. stdout `ERRO ...` (sem email/acesso) → 1 diagnóstico (verifica o token) e reporta motivo.

## Verificação/local de teste
- Rodar o wrapper direto emite `SEM_MES_NOVO: competência X já capturada (aliq ...)` quando o
  mês já está no JSON — é o sinal esperado de que a extração está funcionando (não é erro).
