#!/usr/bin/env bash
# Modelo de LEMBRETE DATADO one-shot para cron no_agent.
# O stdout deste script é entregue verbatim no destino (deliver) do job.
#
# Copie para $HERMES_HOME/scripts/<nome>.sh, troque o texto e agende:
#   cronjob_manage action=create schedule="AAAA-MM-DDTHH:00:00" repeat=1 deliver="origin"
#   cronjob_manage action=update job_id=<id> script="<nome>.sh" no_agent=true
# O ISO do schedule é lido em UTC (09:00 BRT = T12:00:00).
#
# Regras: só o texto do lembrete na saída (sem data de geração, sem log, sem caminho);
# a data citada é a do dia em que o job dispara; nada de rede, token ou modelo.
# Não use exit != 0 para "avisar": falha só é legítima se for falha de verdade.
set -euo pipefail

cat <<'TXT'
❯ <Nome>, lembrete de hoje (<dia da semana>, <DD/MM/AAAA>).

<A ação de hoje em uma frase — o essencial na primeira linha.>

<Contexto mínimo que a pessoa precisa para agir: projeto/contrato, contato responsável
(com e-mail se houver) e o canal onde repetir o aviso — sem inventar prazo nem data.>
TXT
