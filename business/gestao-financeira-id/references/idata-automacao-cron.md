# Automação iData — cron diário e resiliência ao Google Sheets

Detalhe operacional do job que alimenta a planilha de Gestão Financeira a partir do
Banco Inter. Consolidado em 24/08/2026 ao diagnosticar a falha do dia.

## Arquitetura do cron (job `e60e713b0b62`)

- **Agenda:** `0 7 * * *` (diário 07:00), modo **`no_agent`** = o cron roda o script e
  **não chama LLM**.
- **Semântica de entrega (watchdog):**
  - Sucesso (exit 0 + stdout vazio) → **silêncio total** (não incomoda o principal).
  - Falha (exit ≠ 0) → entrega só o erro (`tail -n 25` da execução) + aponta o log.
- **Cadeia de scripts** (em `/opt/data/scripts/`):
  1. `watchdog-idata-diario.sh` — decide mudo vs. grito; reaproveita o runner.
  2. `runner-idata-diario.sh` — autentica no Inter primeiro (exit 2 se cert falhar),
     depois chama o entrypoint. Processa **sempre "ontem"** (`date -d yesterday`).
  3. `entrypoint_ingestão_inter.py` no repo `/opt/data/work/idata`.

## Onde estão os logs (diagnóstico)

- **Cron:** `~/cron/output/e60e713b0b62/<YYYY-MM-DD_HH-MM-SS>.md`
- **Runner:** `/opt/data/work/idata/logs/idata_<stamp>.log`
- Sequência de diagnóstico: ler o `.md` do dia (mostra exit code + tail), depois o log
  apontado ali para o traceback real.

## Resiliência ao Google Sheets (fix 24/08/2026)

**Bug que motivou:** em 2026-08-24 o append em `CCI_saldo!A:F` deu
`HttpError 503 "The service is currently unavailable"` — um **pico transitório** da API
do Google derrubou o dia inteiro do iData (o job ficava vermelho no cron, sem nada gravado
parcialmente — o 503 veio antes de escrever). Autenticação no Inter estivera OK.

**Correção** em `etl/carregadores/google_planilhas.py`:
- Wrapper `_executar_com_retry(operacao)` em volta de `update` e `append`.
- **4 tentativas**, backoff exponencial **1s → 2s → 4s → 8s**.
- Re-tenta **só erros transitórios**: `429` (quota) e `500/502/503/504`.
- Erros permanentes (ex.: `404`, `403`) **falham imediato** — não mascara problema real.
- Padrão `print('[iData] Google <status> — tentativa N/4 …')` no log auxilia diagnóstico.

**Teste local do wrapper** (sem tocar na rede): mock de `HttpError` exige que o objeto
`resp` tenha `.status` **e** `.reason` (o próprio `HttpError.__init__` lê `.reason`).
Cenários validados: 2×503 + sucesso → sucesso na 3ª; 503 persistente → estoura na 4ª;
404 → falha na 1ª.

## Regras de operação

- O dado nunca se perde nessa falha específica (append é atômico — 503 antes de escrever =
  nada gravado). O saldo do dia fica pendente e o cron alimenta na próxima rodada; ou roda o
  runner manualmente para recuperar fora do horário.
- Se um **503 persistente** reaparecer (mesmo com retry), não é backoff que resolve — é a
  API do Google fora do ar; reportar como incidente externo.
- Repo `/opt/data/work/idata` é git local; commits de correção não sobem automaticamente ao
  remote e **precisam de push explícito** (confirmar com o principal — não é rotina).
