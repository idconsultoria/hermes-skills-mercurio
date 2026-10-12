---
name: telegram-group-bot-diagnosis
description: "Use quando um bot do Telegram não responde em grupo.

Carregue esta skill quando mencionarem o bot num grupo e ele não responder — apuração read-only em três causas (mensagem não chegou, gatilho recusou, allowlist barrou) via Bot API, SQLite e logs."
category: infrastructure
type: Reference
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [telegram, gateway, multiplex, grupos, acionamento, forense, bot-api]
    related_skills: [messaging-platforms, peer-session-audit]
timestamp: 2026-10-09T18:00:00Z
---

# Bot do Hermes não respondeu num grupo do Telegram

Usar quando a queixa é "mencionei o bot no grupo e ele não respondeu". Três causas têm o mesmo
sintoma e precisam ser separadas: **(1) a mensagem não chegou** ao processo do perfil,
**(2) chegou e o gatilho recusou**, **(3) chegou, passou o gatilho e caiu no allowlist de usuário**.
A apuração inteira é **leitura** — não mexer em config de perfil alheio (ver §5).

## 1 · Fatos do Telegram que decidem o diagnóstico

- **Bot não recebe mensagem de outro bot** — política da plataforma, independe de privacidade.
  Postou um agente? Não há o que depurar do lado do destinatário.
- **Bot não vê histórico anterior a entrar no grupo.** Mensagem anterior à entrada não gera
  update nem erro de entrega em lugar nenhum.
- `can_read_all_group_messages: true` (privacy desligada) só garante que ele veria o *chatter*
  não mencionado; não muda os dois itens acima.
- **Grupo básico (`-54xxxxxxx`) e supergrupo (`-100xxxxxxxxxx`) são chats diferentes.** Recriar
  ou migrar o grupo deixa `group_allowed_chats` e `channel_prompts` apontando para o chat morto:
  o bot nunca age nem observa no grupo novo, e não há erro em log nenhum.
- **Webhook ativo: nunca chamar `getUpdates` no mesmo bot** (409 Conflict, e a tentativa
  derruba a entrega real).

## 2 · Ordem de apuração (do mais barato ao decisivo)

1. **Bot API, read-only** (token do `.env` do perfil): `getMe` (username real — rename deixa a
   config velha), `getWebhookInfo` (`pending_update_count: 0` e ausência de `last_error_*` =
   Telegram sem falha de entrega), `getChatMember(chat_id, bot_id)` (`member`/`administrator`
   = está no grupo; `left`/`kicked` ou `400 Bad Request` = não está / não enxerga o chat).
2. **Fotos do perfil no SQLite** (`state.db`, read-only): sessões por `chat_id` — *nenhuma*
   sessão com o chat do grupo significa que nenhuma mensagem de grupo foi processada, nunca;
   `messages WHERE observed=1` mostra o que foi só guardado como contexto.
3. **Logs**: `inbound message:` (chegou e foi acionado) e
   `Blocked unauthorized user <id> in chat <id>` (chegou, passou o gatilho, caiu no allowlist).
   **Recusa de gatilho não loga nada** — silêncio total não distingue "não chegou" de
   "gatilho recusou". Por isso o passo 4.
4. **Prova decisiva**: rodar a própria lógica do Hermes com a config real do perfil
   (`_should_process_message`) e ver se o gatilho passaria. `True` = a culpa **não** é de
   config/gating: a mensagem não chegou (entrega/membro do grupo). `False` = a chave errada
   está na config. Receita executável em `references/trigger-harness.md`.
5. **Grupos homônimos**: cruzar o ID que aparece em `channel_directory.json`, no `gateway.log`
   (`inbound message: ... chat=-...`) e no `config.yaml` do perfil.
6. **Teste válido exige humano.** Pedir ao dono/sócio que mencione o bot no grupo. Postar pelo
   próprio agente não serve (bot não vê bot).

## 3 · Como responder

Veredito na primeira frase, separando o que é entrega do que é config; depois a evidência que
fecha cada hipótese; e **um** próximo passo pedido ao dono (o teste humano, ou o ok para corrigir
`group_allowed_chats`/`channel_prompts` do perfil). Sem narração de comando, sem lista de
"verifiquei X, Y, Z".

Ao relatar achado colateral do mesmo caso (por exemplo, allowlist de usuário bloqueando um sócio
no grupo), diga em uma linha e ofereça corrigir — é a mesma classe de problema e o dono decide.

## 4 · Armadilhas

- **Ler a config do perfil e concluir sem rodar o gatilho.** A gramática do acionamento
  (`allowed_chats` versus `group_allowed_chats`, `exclusive_bot_mentions`,
  `observe_unmentioned_group_messages`) não se deduz de memória: `group_allowed_chats`
  **concede** autorização por chat, não é hard gate. Rode o harness.
- **Confundir silêncio de log com ausência de mensagem.** Ver §2.3.
- **Concluir "foi bug" a partir de `needsAction`.** Convidado/estado em `needsAction` apenas diz
  que a entidade existe, não que o Telegram/humano processou.
- **Grupo homônimo passa batido** porque o nome é idêntico — compare sempre IDs, nunca títulos.
- **Menu de comandos de grupo** (`set_my_commands`) registrar OK e o webhook responder não provam
  entrega de mensagem: são caminhos diferentes.

## 5 · Acesso e escrita em perfil alheio

Ler `config.yaml`, `.env`, logs e `state.db` de outro perfil faz parte da apuração. **Mudar**
`group_allowed_chats`, `channel_prompts`, allowlist de usuários ou `.env` é escrita: só com ok
explícito do dono, no perfil dono.

Depois de editar, **não confunda "re-escaneado" com "aplicado"**:

- **Allowlist de usuário** (`TELEGRAM_ALLOWED_USERS` no `.env`) vale já na próxima mensagem — é
  resolvida por turno, do `.env` do perfil (confirmar montando o escopo:
  `build_profile_secret_scope(Path(home)).get("TELEGRAM_ALLOWED_USERS")`).
- **Chaves de adapter** (`group_allowed_chats`, `channel_prompts`, `require_mention`, …) **não**
  valem: o re-scan de 30s só constrói plataforma que *não* está live
  (`_start_one_profile_adapters` faz `continue` em plataforma já presente em `_profile_adapters`,
  "never a second poller on the same bot") — e por isso o log fecha com `(0 adapter(s) connected)`.
  O adapter conectado segue com a config antiga até reconectar; na prática, só no **restart do
  gateway**. Dizer isso ao dono em vez de declarar a correção pronta, e oferecer o restart (o
  multiplex inteiro cai por ~30s — é decisão dele). Restart: `SIGUSR1` no PID do gateway, ou os
  verbos do control socket em `HERMES_HOME/gateway.sock` (`identify`/`status`/`rescan-profiles`/
  `pause-for-update`) — nenhum deles recria plataforma live.

Backup do arquivo antes de editar (`config.yaml.bak-<assunto>-<ts>`), e conferir por leitura de
volta (YAML parseado, prompts idênticos, `.env` relido).

## References

- `references/trigger-harness.md` — tabela das chaves de acionamento e o harness que roda
  `_should_process_message` com a config real do perfil.
