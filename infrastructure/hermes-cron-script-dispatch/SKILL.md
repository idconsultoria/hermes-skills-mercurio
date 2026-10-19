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
à variação do diretório home (migração `/opt/data` → `/data/data/com.termux/files/home/capitolium`, ou volta ao host
Oracle onde o bind antigo era `/opt/data`).

## Restrição dura do scheduler (verificada em produção)
O campo `script` de `cronjob` (action=create/update) **obrigatoriamente** é um *nome de
arquivo* resolvido contra `~/.hermes/scripts/` (ou seja, `/root/.hermes/scripts/` quando
`HOME=/root`). Caminho absoluto ou `~/x` é **rejeitado** com:

> `Script path must be relative to ~/.hermes/scripts/. Got absolute or home-relative path: '...'`

Portanto NÃO dá para apontar o cron direto para `/data/data/com.termux/files/home/capitolium/scripts/foo.sh`.
A solução é o padrão de dois arquivos abaixo.

**Atualização (15/10/2026, build em produção no Mercúrio):** nesta versão o nome do script é
resolvido contra `HERMES_HOME/scripts/` (aqui `/data/data/com.termux/files/home/capitolium/scripts/`). Colocar o
arquivo só em `~/.hermes/.hermes/scripts/` e criar o job por nome falha com:

> `Script file not found: /data/data/com.termux/files/home/capitolium/scripts/foo.sh. Create it in /data/data/com.termux/files/home/capitolium/scripts/ first.`

Regra prática: **coloque o script (ou um launcher `.sh` que descobre o python e executa o
`.py` vizinho) em `$HERMES_HOME/scripts/`**, e mantenha um dispatcher em `~/.hermes/scripts/`
só como fallback de builds antigos. Antes de agendar, rode o caminho real à mão:
`bash $HERMES_HOME/scripts/<nome>.sh --dry-run`.

## Padrão de dois arquivos (resiliente)
1. **Dispatcher magro** em `~/.hermes/scripts/<nome>.sh` (é o que o cron referencia pelo
   nome). Ele apenas encaminha para o script real em HERMES_HOME:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   HH="${HERMES_HOME:-/data/data/com.termux/files/home/capitolium}"
   [[ ! -d "$HH" ]] && HH=/opt/data
   TARGET="$HH/scripts/<nome>.sh"
   [[ ! -f "$TARGET" ]] && { echo "ERRO: $TARGET ausente"; exit 4; }
   exec "$TARGET" "$@"
   ```
2. **Lógica real** em `$HERMES_HOME/scripts/<nome>.sh` — com resolução multi-home para
   backend, venv e dados (ex.: procura em `/data/data/com.termux/files/home/capitolium` E `/opt/data`).

Assim o cron aponta para um nome (permitido) e a execução sempre cai no HERMES_HOME correto,
funcione qual for o home ativo. O wrapper real deve também varrer múltiplos candidatos de
venv Python e de backend antes de falhar (ver `references/dispatcher-examples.md`).

## no_agent watchdog (semântica de entrega)
Para jobs `no_agent=true` (o script roda e não chama LLM):
- Sucesso = exit 0 **e stdout vazio** → silêncio total (não entrega nada ao usuário).
- Falha = exit ≠ 0 → o scheduler entrega o stdout (útil para alertar).
O wrapper pode implementar isso: captura a saída; se RC=0 e vazia, `exit 0` (mudo); senão
`echo "$OUT"; exit $RC` (grita).

**O silêncio tem de ser merecido — nunca conquistado por defeito do script.** O watchdog
transforma qualquer `exit 0` mudo em silêncio permanente, então um script que engole erro
de parsing e sai limpo some justamente quando falhou. Regra: todo caminho de erro real
precisa sair com `exit != 0` e diagnóstico; sucesso só é `exit 0` depois de uma leitura de
verdade. Sinais de que o silêncio está mascarando defeito: comparação/casamento que
nunca encontra nada, lista que volta vazia, contagem zero em campo que deveria ter itens.
Ao criar um watchdog novo, exercite-o com um caso que **deve** casar e outro que **deve**
falhar — silêncio validado só no caso mudo não prova nada.

## Lembrete datado one-shot: script puro, não agente

Para um lembrete cuja função é chegar no dia certo (pedido do tipo "me lembra dia 19 de
reenviar X"), o job é `no_agent=true` com o texto já pronto no script — o stdout é entregue
verbatim:

1. Escreva `$HERMES_HOME/scripts/<nome>.sh` imprimindo **só o texto do lembrete**
   (`cat <<'TXT'`) — modelo pronto em `templates/lembrete-datado-one-shot.sh` (`chmod +x`
   depois de copiar). Sem timestamp nem "gerado em": a saída é uma mensagem humana, e a data já
   está escrita no corpo.
2. `action=create` com `schedule="<AAAA-MM-DD>T<HH>:00:00"`, `repeat=1`, `deliver="origin"`;
   depois `action=update` com `script="<nome>.sh"` + `no_agent=true`.
3. Leia de volta `$HERMES_HOME/cron/jobs.json` (ver Pitfalls) antes de responder ao dono.

Por que não modo agente: job unpinned é **pulado em silêncio** pelo guarda de drift quando o
provider/modelo global muda (`drift_skip`), e ainda depende de provedor no ar — num lembrete de
uma data só isso é o risco inteiro da tarefa entregue a quem não devia carregá-lo. Modo agente
fica para lembrete que precisa **compor** texto com a base.

**ISO absoluto é interpretado em UTC**, independente do fuso do dono: 09:00 BRT = `12:00:00`, e
"23h de quinta" num job de véspera aparece como `02:00:00` do dia seguinte. Confirme
`schedule.run_at` antes de afirmar o horário.

**Não dispare teste de um lembrete que carrega data.** `action=run` entrega o texto de verdade
na hora e o dono recebe um lembrete com a data errada. Prove o conteúdo rodando o script à mão;
o caminho de entrega já está provado pelos jobs `no_agent` que rodam todo dia.

## Verificação (produção)
No job `e60e713b0b62` (iData diário) o teste manual retornou `exit 4` com:
`ERRO: runner-idata-diario.sh não encontrado em /data/data/com.termux/files/home/capitolium/scripts/runner-idata-diario.sh /data/data/com.termux/files/home/capitolium/scripts/runner-idata-diario.sh`
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

## "Sempre ative o agente" ≠ "gaste tokens" — quem economiza é o gate

P有时 o principal pede para tirar o `no_agent` achando que o modo sem LLM economiza token.
Ao contrário: o que zera o custo no dia sem evento é o **gate de mudança** — com saida
estável, o agente nem é chamado. Então a resposta certa **não** é reduzir o escopo da
tarefa (isso seria entregar menos), e sim manter a tarefa inteira e o gate.

## `None` como sentinela + `is not None` = armadilha

Funcao que devolve `None` para "não casou" e `True`/`False` para o resto, testada com
`is not None`, deixa `False` passar como se fosse sucesso. Em casamento financeiro isso é
a diferenca entre registrar uma parcela errada e nao registrar nada. Devolva **booleano** e
teste por verdade.

## O gate hasheia a saída SEM o `\n` final — não compare `stdout` cru

O arquivo `cron/output/<job_id>/monitor_last_output.txt` guarda a saída com o **newline
final removido** (26 bytes para `SYMPLEXIS_NADA_A_REGISTRAR`). Se você conferir o estado
do gate calculando `sha256(subprocess.stdout)`, dá **hash diferente com conteúdo
idêntico** e você conclui, errado, que o agente vai acordar todo dia.

- Hash do gate = `sha256(saida.rstrip("\n"))` — o `monitor_last_output.txt` é a fonte da
  verdade do que foi realmente gravado.
- **Prova do comportamento, não do detalhe interno:** dispare o job duas vezes seguidas e
  veja o segundo tick. Se o gate funciona, o segundo run sai `no_change` (sem run de
  agente, `API calls: 0`). Confirmar por execução real evita usar a forma do hash como
  proxy — detalhe de implementação muda entre versões.
- Se o `\n` for removido e o conteúdo for o mesmo, o run é suprimido: `last_run_at` avança,
  `last_status: ok`, mas **sem** arquivo novo em `cron/output/<job_id>/` e sem entrega.

## Falha SEMPRE notificar num job com `monitor` — a inversão do exit code

Com `monitor` (gate de mudança), a semântica do exit code é **invertida** em relação ao
watchdog `no_agent`:

| Situação | `no_agent` | `monitor` |
|---|---|---|
| sucesso mudo | exit 0 + stdout vazio | stdout **igual** ao anterior → run suprimido |
| **falha** | exit ≠ 0 → entrega o erro | **exit ≠ 0 → hash preservado + run suprimido** =Somega-se |

Ou seja: num job com `monitor`, `exit ≠ 0` é a forma de **engolir** a notificação. Se o
principal exige saber de toda falha, a falha tem de virar **linha de stdout com exit 0**:

```
SYMPLEXIS_FALHA motivo=token Google ausente: /caminho/google_token.json
```

Assim o hash muda, o gate vê “mudança”, o agente acorda e reporta — e continua sendo uma
linha estável quando o problema é o mesmo (não vira chuva de notificação a cada tick).
Contraste: no passo de **registro** (executado pelo agente já acordado), a falha DEVE ser
`exit ≠ 0` — ali o ruído é o comportamento correto.

Nunca misture os dois mundos no mesmo script sem pensar: saída estável é para o **gate**;
`raise SystemExit` no meio do fluxo do coletor engole o erro em vez de reportá-lo —
use exceção própria (`SymplexisErro`) e converta em linha.

## Verificar entrega a um usuário nomeado (@handle)

Quando perguntarem "o cron X enviou para @fulano?", seguir nesta ordem:

1. `cronjob_manage action=list` → localizar o job pelo nome, anotar `deliver`, `last_run_at`, `last_status` e `last_delivery_error`.
2. Mapear o destino por **chat_id, nunca por handle/nome de exibição** — o campo é `telegram:<chat_id>` e o handle pode divergir do cadastro (ver `id-comunicacao-multiusuario` para a tabela sócios ↔ chat_ids). Confirmar o vínculo na Context-KB (`people/<nome>.md` traz o id Telegram).
3. Confirmar o conteúdo entregue: `session_search` pelo nome/job_id, abrir a sessão `cron_<job_id>_<data>` e ler a **última mensagem assistant com texto** — ela é o payload entregue. Não concluir só por `last_status: ok`; extrair dela os artefatos (ids Drive, recording_id, links).
4. Em jobs em MODO AGENTE, distinguir falha do script coletor de falha da entrega: o bloco "Script Error" no prompt indica que o `script` quebrou, mas o agente pode ter concluído por fallback (ex.: API REST direta) — o veredito está na mensagem final, não no bloco de erro.
5. `last_delivery_error: null` significa sem falha registrada pelo scheduler nos canais de `deliver`; citar os destinos verificados e os links entregues.

## Diagnosticar um cron que "falhou" — o veredito está no arquivo de output

`cronjob_manage action=list` mostra `last_status`/`last_error` do **agendamento e da entrega**,
não da coleta. Job que coletou errado mas redactou o relatório de falha aparece como `ok`.
Nunca conclua "funcionou" (nem "quebrou") por esse campo.

Ordem da evidência:
1. `cron/output/<job_id>/<data>_<hh-mm-ss>.md` — transcript real. Leia `## Run Context` (o
   diff/bloco do monitor = o que o script devolveu) e `## Response` (o que foi entregue).
2. `## Mode: no_change (agent run suppressed)` = gate funcionou, nada foi entregue.
   `## Mode: no_agent (script)` = quem decidiu foi o script, não o agente.
3. O motivo vindo do coletor (`X_FALHA motivo=…` no bloco do monitor) é o dado, não o
   comentário do agente — mesmo com `last_status: ok` no `list`.

Distinga sempre **"o cron falhou"** de **"o cron reportou uma falha"**: num job com monitor a
segunda é o comportamento correto, e é o que o principal pediu.

## Script de cron que depende da rede: retry e credencial renovada em disco

Um job que lê planilha/Gmail/API depende de (a) resolver nome e (b) token válido. Com token
expirado, **cada disparo faz uma chamada de rede só para renovar** — exatamente a janela em
que o DNS cai. Duas correções matam a classe da falha, não o episódio:

- **Retry com backoff** no ponto de rede: 3 tentativas, 2s/5s/15s. Sem isso, uma queda de 30s
  de DNS custa o dia inteiro de conferência.
- **Gravar a credencial renovada em disco** após o refresh bem-sucedido. Sem isso o arquivo
  fica expirado para sempre e a exposição vira uma chamada de rede por disparo, em vez de
  uma por dia.

Em cron não há ninguém para aprovar timeout nem retry: o script tem de se defender sozinho.

Para provar que a falha é transitória e não de credencial: N resoluções seguidas + N refreshs
seguidos. N/N ok com erro de resolução no meio **fecha o diagnóstico**. Use
`scripts/probe-rede-token.sh`.

Depois de uma coleta que falhou, **rode de novo com a janela alargada** (`SYMX_JANELA=4` para a
Symplexis, cujo padrão é 2) e veja se aparece registro que ficou sem tratar. Sem essa rodada
você só sabe que "deu erro" — não se algo se perdeu.

## "O job irmão passou" NÃO é prova de que a rede está de pé

Antes de culpar o script, confira se o job que passou depende do **mesmo** recurso. Job que
autentica por certificado no banco e não toca Sheets passa mesmo com o Google fora do ar —
foi assim que o iData (07:00 UTC) sobreviveu ao dia em que a conferência de parcelas (07:25,
via `googleapiclient`) caiu. "A rede funciona porque o outro rodou" é inferência inválida.

Resolvendo DNS: se `/etc/resolv.conf` aponta para `100.64.0.0/10`, é MagicDNS de malha
(Tailscale) e pode falhar transitório. Num erro de resolução, o primeiro dado é **quem é o
resolver** — e se vários jobs caíram no mesmo minuto, é o resolver, não cada script.

## Pitfalls
- `no_agent` + `exit 0` + stdout **não vazio** = stdout é ENTREGUE verbatim ao destino; só
  `exit 0` **com stdout vazio** é silêncio. Use isso para um job script-only que envia
  mensagens por conta própria (Bot API/curl) e imprime uma confirmação curta
  (`Fulano: entregue (msg 123)`) — o principal recebe o recibo sem pagar chamada de LLM.
- Job script-only que **envia mensagem** só se prova enviando: dê ao script um modo
  `--test` que manda apenas para o principal com prefixo `[teste]` e rode à mão antes de
  agendar. Para validar auth+chat sem sujar a caixa dos outros, use `sendChatAction`
  (`action=typing`) nos chat_ids de destino — não cria mensagem e prova o caminho.
- Nunca mapear destinatário por @handle ou nome de exibição — o Telegram permite nickname divergente e o erro vira falso "não entregue"; casar sempre pelo `telegram:<chat_id>` do campo `deliver`.
- Nunca passar caminho absoluto no campo `script` — o scheduler recusa com erro claro.
- `cronjob_manage action=create` **não persiste** `model`/`provider`: o job nasce com
  `"model": null` mesmo com os campos passados, e `action=update` os recusa com
  `No updates provided`. Para pinear inferência, use a CLI
  (`hermes cron edit <id> --model <m> --provider <p>`); se a tarefa não precisa de LLM, resolva
  pelo `no_agent` em vez de brigar com o pin.
- **Formato do `cron/jobs.json`**: cada job tem `id` (o `job_id` só existe no retorno das
  tools) e `origin` = `{platform, chat_id, chat_name, thread_id, user_id}` capturado na criação.
  `origin` é o único campo que prova para onde um `deliver="origin"` entrega — `action=list`
  não o mostra. Case por `id` (ou `name`) no arquivo, não por substring do JSON inteiro.
- **Saída de script se confirma por arquivo**: rode
  `bash script.sh > /tmp/x.out 2>&1; echo rc=$?` e **leia o arquivo**. `exit 0` com stdout vazio
  é o caso mudo do watchdog — silêncio legítimo e script que não imprimiu nada são
  indistinguíveis sem ler o conteúdo.
- `HERMES_HOME` pode NÃO estar no `.env` (neste ambiente não estava); por isso o dispatcher
  tem fallback `${HERMES_HOME:-/data/data/com.termux/files/home/capitolium}` + checagem de existência do dir.
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
