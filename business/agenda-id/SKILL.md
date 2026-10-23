---
name: agenda-id
description: "Use ao criar ou ajustar reunião ou lembrete datado da ID.

Carregue esta skill quando um sócio pedir para criar, ajustar ou conferir reunião na agenda da ID — convites, choques de horário, gates de ok para convidados externos e leitura de volta do evento — e também quando pedir um lembrete datado (ex.: me lembra dia 19 de reenviar um aviso), que sai por cron no DM do sócio."
category: business
type: Reference
license: MIT
author: Mercúrio
version: 1.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [agenda, calendar, reunião, google, convite, BRT]
    scopes: [id]
    related_skills: [auxiliar-adm-id, google-workspace]
timestamp: 2026-10-09T19:10:00Z
---

# Agenda da ID (Google Calendar)

Criar, ajustar e conferir reuniões na agenda da ID quando um sócio pede ("cria uma reunião X na
agenda, convida fulano, põe o link na descrição").

## Regras sempre-válidas

1. **A "agenda da ID" é o calendário primário do `admin@idconsultoria.ai`** (token
   `$HERMES_HOME/google_token.json`): `calendarId="primary"` e `admin@idconsultoria.ai` são o
   mesmo calendário — o segundo é aceito e é o que a leitura de volta confirma.
2. **Data e hora não se inventam.** Pedido sem dia/hora → perguntar antes (2–3 opções já
   checadas contra a agenda real). Quando o dia exato for sensível a prazo, confirmar em **fonte
   externa que não venha de cache** e cruzar **duas** delas — p.ex. `curl -s
   'https://timeapi.io/api/Time/current/zone?timeZone=America/Maceio'` e um carimbo de servidor de
   API autenticada (o `modifiedTime` que o Drive devolve). O relógio do contêiner, o cabeçalho de
   contexto **e o header `Date` de uma página pública** já divergiram (o `Date` chega por CDN e pode
   vir com um dia de atraso — datar entrega só por ele erra por 24 h). Exibir em BRT e escrever o
   ISO do evento com offset explícito (`-03:00`).
3. **O gate de ok vale para o CONVITE, não para a linha na agenda.** Criar o evento sem
   convidados (só a casa vê, e dá para apagar) é rotina: crie e reporte. Enviar convite
   (`sendUpdates="all"`) exige mostrar antes (título, dia/hora, e-mails, descrição) e esperar o
   ok — convite disparado não se recolhe. **Mas não repita a pergunta com os mesmos dados:** se
   o pedido do dono já nomeia título, convidados e o conteúdo da descrição, o ok do horário cobre
   o convite (mostrar de novo é burocracia, e ele cobra isso). O que exige mostrar antes é o que
   **você** escolheu: horário oferecido, destinatário que ele não ditou, texto de descrição que
   você redigiu. **Convidado externo sem e-mail na base** (interlocutor
   de órgão/empresa que só apareceu em conversa ou transcrição): crie o evento com o nome dele no
   **título** e sem `attendees`, e diga na resposta que **nenhum convite saiu** e que falta o
   e-mail. Nunca invente endereço de e-mail.
4. **Choque de agenda se reporta**, não se esconde: sobrepor é decisão do dono.
5. **Nada é "feito" sem leitura de volta.** `create` responde só `{status, id, summary, htmlLink}`
   — não prova convite enviado nem descrição íntegra. Retorno **vazio** também não é falha: um
   `create` pode não imprimir nada e ter criado o evento — **ler a janela de volta antes de
   repetir**, porque repetir duplica o compromisso na agenda dos convidados.
6. **Duração e campos ausentes não se inventam, se declaram.** Pedido sem horário final → assuma
   **1h**, escreva o horário final na resposta ("8h30–9h30, assumi 1h") e deixe o dono corrigir em
   uma linha. Campo que só o dono tem (endereço de local presencial) entra como **pergunta**, nunca
   como chute.

## Fluxo

1. `google_api.py calendar list --start <ISO do dia> --end <ISO do dia seguinte>` — **o dia
   inteiro**, nunca só a janela pedida. Evento recorrente curto (a Diária de Vendas, 09:00–09:30)
   some de uma consulta a 09:00–10:00 de outra data e você conclui "livre" errado. Não escreva
   "a agenda está livre": liste o que existe e o que encosta, e diga onde há sobreposição.
2. **Criar já com convite, numa chamada só.** `calendar create` usa `events.insert` **sem
   `sendUpdates`** e a CLI não expõe a flag: o convidado entra como `needsAction` e **nenhum
   e-mail sai**. Vá direto na API — `from google_api import build_service` (importe da pasta
   `scripts/` da skill `google-workspace`) e insira com `sendUpdates="all"`, o que já resolve
   convite e newline real de uma vez:
   ```python
   import sys, json; sys.path.insert(0, f"{HERMES_HOME}/skills/productivity/google-workspace/scripts")
   from google_api import build_service
   svc = build_service("calendar", "v3")
   body = {"summary": "...",
           "description": "linha 1\nlinha 2",          # \n real, não literal
           "start": {"dateTime": "2026-10-23T09:00:00-03:00", "timeZone": "America/Sao_Paulo"},
           "end":   {"dateTime": "2026-10-23T10:00:00-03:00", "timeZone": "America/Sao_Paulo"},
           "attendees": [{"email": "a@x.com"}, {"email": "b@y.com"}]}
   ev = svc.events().insert(calendarId="admin@idconsultoria.ai", body=body, sendUpdates="all").execute()
   ```
   `calendar create` (CLI) só serve para evento **sem** convidados — e aí `--description` ainda
   grava `\n` literal (a barra é comida no caminho shell→API).
3. **Convidado citado pelo nome, e-mail não ditado**: recupere o endereço de um evento anterior
   que o dono já aprovou (`events().get(...)` do mesmo cliente/projeto) ou da base — **nunca**
   monte o endereço a partir do nome, e não troque por um e-mail achado na web.
4. **Verificar**: `events().get()` e conferir summary, `start`/`end`, `location`, `description` e a
   lista de `attendees` (o `responseStatus: needsAction` é o estado inicial normal — o que prova
   convite é o `sendUpdates="all"` na chamada). A CLI expõe apenas `list/create/delete` —
   **não tem `get` nem `patch`**: para ler de volta ou ajustar campo que ela não aceita use
   `scripts/event_get_patch.py` da própria skill, ou o mesmo padrão à mão (`build_service`).
   Evento só entra como "feito" quando a leitura de volta mostra o mesmo que você disse ao dono.

Rodar o `google_api.py` com um python que tenha `googleapiclient` — **descubra, não decore**:
caminho de venv escrito de memória envelhece a cada migração de ambiente (o
`id-nfse-motor/.venv` já foi o certo e hoje pode não existir). Probe antes de usar:

```bash
for P in "$HERMES_HOME/venvs"/*/bin/python "$HERMES_HOME/hermes-agent/venv/bin/python"; do
  "$P" -c "import googleapiclient" 2>/dev/null && { echo "PY=$P"; break; }
done
```

Se nenhum candidato passar, o problema é o ambiente, não o acesso Google — reporte assim em
vez de concluir que o token caiu. Tokens e venvs em detalhe na skill `auxiliar-adm-id` §Geral.

## Avisar o compromisso (aviso ao grupo, e-mail e lembrete na véspera)

Pedido típico de sócio: *"avisa todo mundo, me manda e-mail, me lembra na véspera e põe na
agenda"* — um compromisso, quatro canais. Cada canal tem função própria, e entregar só a agenda
deixa o pedido pela metade:

| Canal | Função |
|---|---|
| **Agenda** | o compromisso em si (dia, hora, local, convidados) |
| **Grupo** | aviso a todos — quem não lê a agenda precisa saber |
| **E-mail** | registro que sobrevive ao chat e chega no celular dele |
| **DM na véspera** | lembrete, quando esquecer custa caro |

- **Grupo da equipe:** `[ID] Núcleo` = `-1004359358267`. Aviso com o helper, que reusa as
  credenciais do gateway: `hermes send --to telegram:-1004359358267 "..."` (registro e pitfalls
  do relay em `id-comunicacao-multiusuario`).
- **Lembrete datado = one-shot de cron, ISO absoluto, `repeat=1`, `deliver` no DM do sócio.**
  Nada de "em 24h": errar o dia do lembrete é o defeito que o lembrete existia para evitar.
  O ISO absoluto é lido em **UTC**, não no fuso do dono — 09:00 BRT = `T12:00:00`; confira
  `schedule.run_at` (volta com `+00:00`) antes de dizer o horário ao dono.
- **Lembrete de texto fixo sai como `no_agent` + script, não em modo agente.** Escreva o texto
  em `$HERMES_HOME/scripts/<nome>.sh` (o stdout é entregue verbatim; sem timestamp na saída) e
  faça `cronjob_manage action=update job_id=<id> script="<nome>.sh" no_agent=true` no job
  criado com `action=create`. Modo agente fica para lembrete que precisa **compor** texto com a
  base: job unpinned pode ser **pulado em silêncio** pelo guarda de drift quando o provider/modelo
  global muda, e o lembrete simplesmente não chega. Mecânica em `hermes-cron-script-dispatch`.
- **A data que o lembrete cita não se inventa.** Se o prazo não está na base, no e-mail nem no
  Drive, o texto sai com "o prazo" genérico e a **pergunta** volta ao dono na mesma resposta
  ("qual é o prazo?") — nunca uma data plausível. O mesmo vale para o canal: se não se sabe se
  o aviso anterior saiu por e-mail ou WhatsApp, o lembrete manda repetir o canal onde a
  contraparte responde.
- **Não dispare teste de lembrete datado:** `action=run` entrega o texto de verdade, com a data
  errada. Prove o conteúdo rodando o script à mão e lendo a saída de volta.
- **Confirme o gravado** em `$HERMES_HOME/cron/jobs.json`: `id`, `no_agent`, `script`,
  `schedule.run_at` e `origin.chat_id` — o `origin` é o que prova para qual DM o
  `deliver="origin"` vai entregar (o `action=list` não o mostra).
- **E-mail de lembrete** sai do `admin@idconsultoria.ai` para o endereço **que o dono ditar**
  (nunca um endereço inferido). O retorno do `send` não prova entrega: conferir depois com
  `gmail search` na caixa de saída.
- **Reportar 1–2 linhas por canal** no fim (o que saiu e onde), não um parágrafo.

## Armadilhas

- **E-mail do convidado: usar LITERALMENTE o que o dono ditou.** Nunca "consertar" grafia nem trocar pelo endereço achado no site/busca do interlocutor (caso real: o dono ditou `sandesassessoria@gmail.com`, foi usado o `sandassessoria@gmail.com` do site da empresa → convite saiu para o endereço errado e convite disparado não se recolhe). Se o ditado divergir do endereço público, **perguntar antes** de convidar; corrigir convidado já convidado = `patch` de `attendees` com `sendUpdates="all"` (o removido recebe cancelamento).
- **`needsAction` não é convite enviado** — é só o estado inicial do convidado no evento.
- **Descrição com link do Drive**: buscar o link no Drive real (ID da pasta), não montar por
  nome — pasta homônima existe em mais de um lugar.
- **Pasta/marco do projeto ≠ pasta comercial**: pegar a pasta que o próprio projeto se declara
  dona (ex.: a que contém o README do contrato), não a pasta de proposta antiga.
- **Evento só entra no roadmap/planilha quando o dono mandar.** Reunião preparatória não autoriza
  preencher célula de cronograma — marcos passam a contar na assinatura, não na agenda.
- **Fuso**: o host roda em UTC; sempre offset explícito, e converter para BRT ao relatar ao dono.
- **Reunião presencial**: preencha `location` como "Presencial — <órgão/empresa>" e peça o endereço
  da sede na mesma resposta; o endereço exato só entra no campo depois de confirmado.
- **Reunião encostada em outra** (uma termina 08:30 e a nova começa 08:30) não é choque técnico,
  mas **se reporta** — emenda sem folga é decisão do dono, não sua.
- **Nome de interlocutor que só existe em transcrição diarizada não é presença confirmada.**
  Cross-check na KB antes de tratar como pessoa; se o dono desconhecer o nome, registre
  `kb_correct` marcando-o como ruído de transcrição (regra detalhada em `reunioes-diarizadas`).
