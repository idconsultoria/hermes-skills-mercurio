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

## Monitor gate — notificar SÓ quando o evento acontecer

`--monitor-script` roda o script ANTES do agente a cada tick e compara o **hash exato em bytes**
da saída: igual → agente suprimido (run silencioso `no_change`, sem entrega); diferente → bloco
`MONITOR CHANGE DETECTED` (diff + saída atual) vai no prompt. Primeira execução = baseline.

Regras para o script do monitor:

- **Sem o evento, emita SEMPRE a mesma linha constante** (ex.: `STATUS=NO_REPLY_...`). Nunca
  imprima timestamp, contagem de mensagens, labels/estado de leitura ou qualquer coisa que mude
  sem o evento — isso gera falso positivo e notificação inútil.
- Com o evento, emita linhas estáveis de detalhe (id, remetente, data, assunto), uma por evento,
  ordenado — cada evento novo muda o hash uma vez.
- Defina o evento pelo que importa, não por "qualquer mudança": p.ex. mensagem de entrada
  (fora de rascunho, não enviada pela casa) E posterior à última mensagem enviada pela casa.
- Falha de rede/API: `stderr` + `exit 1` — o gate trata como erro de fonte (nunca como mudança) e
  preserva o hash guardado.
- **Gate + guarda de drift = falha muda.** Num job unpinned cujo `model.default` mudou, o run é
  pulado ANTES do agente e o aviso sai uma vez só. Num job de monitorar-e-avisar isso o silencia
  justamente quando o evento chega. Depois de `cron pause`/`resume` ou de qualquer troca de
  modelo/provider, confirme `model_snapshot`/`provider_snapshot` em `jobs.json` == default atual
  (`hermes-inference-config` → `references/cron-drift-recovery.md`).

No **prompt** do job, a segunda linha de defesa: instrua que, se o bloco do monitor não trouxer
linha do evento, a resposta seja exatamente `[SILENT]` — o scheduler usa `_is_cron_silence_response`
e **não entrega** nada (`[SILENT]`, `SILENT`, `NO_REPLY`, `NO REPLY`, sozinhos na resposta ou na
primeira/última linha). Sem isso, o diff de formato do próprio script (quando você o reescreve)
vira notificação.

## Verificar entrega a um usuário nomeado (@handle)

Quando perguntarem "o cron X enviou para @fulano?", seguir nesta ordem:

1. `cronjob_manage action=list` → localizar o job pelo nome, anotar `deliver`, `last_run_at`, `last_status` e `last_delivery_error`.
2. Mapear o destino por **chat_id, nunca por handle/nome de exibição** — o campo é `telegram:<chat_id>` e o handle pode divergir do cadastro (ver `id-comunicacao-multiusuario` para a tabela sócios ↔ chat_ids). Confirmar o vínculo na Context-KB (`people/<nome>.md` traz o id Telegram).
3. Confirmar o conteúdo entregue: `session_search` pelo nome/job_id, abrir a sessão `cron_<job_id>_<data>` e ler a **última mensagem assistant com texto** — ela é o payload entregue. Não concluir só por `last_status: ok`; extrair dela os artefatos (ids Drive, recording_id, links).
4. Em jobs em MODO AGENTE, distinguir falha do script coletor de falha da entrega: o bloco "Script Error" no prompt indica que o `script` quebrou, mas o agente pode ter concluído por fallback (ex.: API REST direta) — o veredito está na mensagem final, não no bloco de erro.
5. `last_delivery_error: null` significa sem falha registrada pelo scheduler nos canais de `deliver`; citar os destinos verificados e os links entregues.

## Pitfalls
- Nunca mapear destinatário por @handle ou nome de exibição — o Telegram permite nickname divergente e o erro vira falso "não entregue"; casar sempre pelo `telegram:<chat_id>` do campo `deliver`.
- Nunca passar caminho absoluto no campo `script` — o scheduler recusa com erro claro.
- `HERMES_HOME` pode NÃO estar no `.env` (neste ambiente não estava); por isso o dispatcher
  tem fallback `${HERMES_HOME:-/opt/mercurio-data}` + checagem de existência do dir.
- `cronjob list` pode reportar `gateway_running: false` — os jobs ficam agendados mas não
  disparam até `hermes gateway start`. Sempre avisar o usuário se o gateway estiver parado.
- Jobs com `drift_skip` (provider/modelo global mudou e o job é unpinned) ficam pausados por
  segurança contra gasto. Para voltar a herdar o global: `hermes cron edit <id> --model "" --provider ""`
  **NÃO resolve** se o job já está despinado — `update_job` só recalcula `model_snapshot`/
  `provider_snapshot` quando os eixos (`model`/`provider`) de fato mudam. Receita que funciona:
  1) pine no default atual, 2) despine — a segunda chamada recalcula os snapshots e o guarda solta:
  ```bash
  hermes cron edit <id> --model <modelo-atual> --provider <provider-atual>
  hermes cron edit <id> --model "" --provider ""
  ```
  Verificação real é `cron_model_drift_axes(job, current_provider=..., current_model=...)` → `[]`
  (o `hermes cron doctor` continua acusando porque lê o `last_error` histórico, não a config atual).
  Detalhes em `hermes-inference-config` → `references/cron-drift-recovery.md`.
- Ao migrar container, o data antigo pode ter ficado no host (bind `/home/ubuntu/selfhost/
  mercurio/data` → `/opt/data` na VPS). Os scripts por nome resolvem contra o home antigo e
  quebram — daí a regra de ouro: **todo script de cron vive em HERMES_HOME/scripts e o cron
  aponta para um dispatcher em `~/.hermes/scripts/`**.
