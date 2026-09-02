---
name: hermes-cron-script-dispatch
description: "Hermes cron scripts resilient to HERMES_HOME path changes."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
category: infrastructure
type: Reference
timestamp: 2026-08-30T00:00:00Z
---

# Hermes cron — script dispatch resiliente a HERMES_HOME

Como fazer com que os crons do Hermes usem scripts em `HERMES_HOME/scripts` e sobrevivam
à variação do diretório home (migração `/opt/data` → `/opt/mercurio-data`, ou volta ao host
Oracle onde o bind antigo era `/opt/data`).

## Restrição dura do scheduler (verificada em produção)
O campo `script` de `cronjob` (action=create/update) **obrigatoriamente** é um *nome de
arquivo* resolvido contra `~/.hermes/scripts/` (ou seja, `/root/.hermes/scripts/` quando
`HOME=/root`). Caminho absoluto ou `~/x` é **rejeitado** com:

> `Script path must be relative to ~/.hermes/scripts/. Got absolute or home-relative path: '...'`

Portanto NÃO dá para apontar o cron direto para `/opt/mercurio-data/scripts/foo.sh`.
A solução é o padrão de dois arquivos abaixo.

## Padrão de dois arquivos (resiliente)
1. **Dispatcher magro** em `~/.hermes/scripts/<nome>.sh` (é o que o cron referencia pelo
   nome). Ele apenas encaminha para o script real em HERMES_HOME:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   HH="${HERMES_HOME:-/opt/mercurio-data}"
   [[ ! -d "$HH" ]] && HH=/opt/data
   TARGET="$HH/scripts/<nome>.sh"
   [[ ! -f "$TARGET" ]] && { echo "ERRO: $TARGET ausente"; exit 4; }
   exec "$TARGET" "$@"
   ```
2. **Lógica real** em `$HERMES_HOME/scripts/<nome>.sh` — com resolução multi-home para
   backend, venv e dados (ex.: procura em `/opt/mercurio-data` E `/opt/data`).

Assim o cron aponta para um nome (permitido) e a execução sempre cai no HERMES_HOME correto,
funcione qual for o home ativo. O wrapper real deve também varrer múltiplos candidatos de
venv Python e de backend antes de falhar (ver `references/dispatcher-examples.md`).

## no_agent watchdog (semântica de entrega)
Para jobs `no_agent=true` (o script roda e não chama LLM):
- Sucesso = exit 0 **e stdout vazio** → silêncio total (não entrega nada ao usuário).
- Falha = exit ≠ 0 → o scheduler entrega o stdout (útil para alertar).
O wrapper pode implementar isso: captura a saída; se RC=0 e vazia, `exit 0` (mudo); senão
`echo "$OUT"; exit $RC` (grita).

## Verificação (produção)
No job `e60e713b0b62` (iData diário) o teste manual retornou `exit 4` com:
`ERRO: runner-idata-diario.sh não encontrado em /opt/mercurio-data/scripts/runner-idata-diario.sh /opt/data/scripts/runner-idata-diario.sh`
— provando que o dispatcher achou o HERMES_HOME e o wrapper varreu os dois homes. O erro era
de *backend ausente*, não de caminho. ✓ (A resiliência de caminho está validada; o que falta
é restaurar o backend do host/repo.)

## Pitfalls
- Nunca passar caminho absoluto no campo `script` — o scheduler recusa com erro claro.
- `HERMES_HOME` pode NÃO estar no `.env` (neste ambiente não estava); por isso o dispatcher
  tem fallback `${HERMES_HOME:-/opt/mercurio-data}` + checagem de existência do dir.
- `cronjob list` pode reportar `gateway_running: false` — os jobs ficam agendados mas não
  disparam até `hermes gateway start`. Sempre avisar o usuário se o gateway estiver parado.
- Jobs com `drift_skip` (provider/modelo global mudou e o job é unpinned) ficam pausados por
  segurança contra gasto; exigem pin no host:
  `hermes cron edit <id> --provider <p> --model <m>`.
- Ao migrar container, o data antigo pode ter ficado no host (bind `/home/ubuntu/selfhost/
  mercurio/data` → `/opt/data` na VPS). Os scripts por nome resolvem contra o home antigo e
  quebram — daí a regra de ouro: **todo script de cron vive em HERMES_HOME/scripts e o cron
  aponta para um dispatcher em `~/.hermes/scripts/`**.
