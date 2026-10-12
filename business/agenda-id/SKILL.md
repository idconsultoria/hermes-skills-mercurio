---
name: agenda-id
description: "Use ao criar ou ajustar reunião na agenda da ID.

Carregue esta skill quando um sócio pedir para criar, ajustar ou conferir reunião na agenda da ID — convites, choques de horário, gates de ok para convidados externos e leitura de volta do evento."
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
   `$HERMES_HOME/google_token.json`): usar `--calendar primary` / `calendarId="primary"`.
2. **Data e hora não se inventam.** Pedido sem dia/hora → perguntar antes (2–3 opções já
   checadas contra a agenda real). Antes de agendar algo sensível a prazo, confirmar a data em
   **fonte externa** (header `Date` de um `HEAD https://...`) — o relógio do contêiner e o
   cabeçalho de contexto já divergiram; exibir em BRT e escrever o ISO do evento com offset
   explícito (`-03:00`).
3. **O gate de ok vale para o CONVITE, não para a linha na agenda.** Criar o evento sem
   convidados (só a casa vê, e dá para apagar) é rotina: crie e reporte. Enviar convite
   (`sendUpdates="all"`) exige mostrar antes (título, dia/hora, e-mails, descrição) e esperar o
   ok — convite disparado não se recolhe. **Convidado externo sem e-mail na base** (interlocutor
   de órgão/empresa que só apareceu em conversa ou transcrição): crie o evento com o nome dele no
   **título** e sem `attendees`, e diga na resposta que **nenhum convite saiu** e que falta o
   e-mail. Nunca invente endereço de e-mail.
4. **Choque de agenda se reporta**, não se esconde: sobrepor é decisão do dono.
5. **Nada é "feito" sem leitura de volta.** `create` responde só `{status, id, summary, htmlLink}`
   — não prova convite enviado nem descrição íntegra.
6. **Duração e campos ausentes não se inventam, se declaram.** Pedido sem horário final → assuma
   **1h**, escreva o horário final na resposta ("8h30–9h30, assumi 1h") e deixe o dono corrigir em
   uma linha. Campo que só o dono tem (endereço de local presencial) entra como **pergunta**, nunca
   como chute.

## Fluxo

1. `google_api.py calendar list --start <ISO> --end <ISO>` — ver o que já existe na janela e
   reportar choque.
2. Criar:
   ```bash
   $GAPI calendar create --summary "..." \
     --start 2026-10-09T14:00:00-03:00 --end 2026-10-09T15:00:00-03:00 \
     --attendees "a@x.com,b@y.com" --description "..."
   ```
3. **Convidado NÃO recebe convite por padrão.** O `create` usa `events.insert` **sem
   `sendUpdates`** e a CLI não expõe a flag: os convidados entram como `needsAction` e **nenhum
   e-mail sai**. Refazer logo depois com
   `events().patch(calendarId="primary", eventId=..., body={...}, sendUpdates="all")`,
   repetindo summary/start/end/description/attendees.
4. **Descrição com quebra de linha não sobrevive ao CLI.** `--description "l1\nl2"` grava o `\n`
   **literal** (a barra é comida no caminho shell→API). Setar a descrição no patch da API, com
   newline real.
5. **Verificar**: `events().get()` e conferir summary, `start`/`end`, `location`, `description` e a
   lista de `attendees`. Só então responder ao sócio. A CLI expõe apenas `list/create/delete` —
   **não tem `get` nem `patch`**: para ler de volta ou ajustar campo que ela não aceita (location,
   descrição com newline real), use `scripts/event_get_patch.py` da própria skill, ou o mesmo
   padrão à mão: `sys.path.insert` na pasta `scripts/` da skill `google-workspace`,
   `from google_api import get_credentials`, depois `build("calendar","v3",credentials=...)`.
   Evento só entra como "feito" quando a leitura de volta mostra o mesmo que você disse ao dono.

Rodar o `google_api.py` com o python do venv que tem `googleapiclient`
(`$HERMES_HOME/id-nfse-motor/.venv/bin/python`, detalhado em `auxiliar-adm-id`).

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
