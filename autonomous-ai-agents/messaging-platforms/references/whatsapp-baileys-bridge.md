---
name: whatsapp-bridge-baileys
description: "Send messages, discover group IDs, manage media via local WhatsApp Baileys bridge. Load this skill when you need to interact with WhatsApp programmatically. Covers the local Node.js HTTP bridge on port 3000 using @whiskeysockets/baileys — sending text and media messages, editing sent messages, discovering group IDs from sender-key files, self-chat mode behavior, and common pitfalls including silent delivery failures and emoji issues."
metadata:
  hermes:
    tags: [whatsapp, baileys, bridge, messaging, nodejs]
    related_skills: [messaging-platforms]
---

# WhatsApp Bridge (Baileys)

Bridge roda como processo Node.js em `/opt/hermes/scripts/whatsapp-bridge/bridge.js`. Expõe API HTTP na porta 3000.

## Configuração

```
bridge --port 3000 --session /opt/data/whatsapp/session --mode self-chat
```

Logs do bridge: `/opt/data/whatsapp/bridge.log`

## Endpoints

### GET /health — Status da conexão
```bash
curl -s http://localhost:3000/health
```

### GET /chat/:id — Metadados do chat/grupo
```bash
curl -s http://localhost:3000/chat/120363170662612284@g.us
# → { "name": "ID [Núcleo]", "isGroup": true, "participants": [...] }
```

### POST /send — Enviar mensagem de texto
```bash
curl -s -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363XXXXX@g.us","message":"Texto da mensagem"}'
# → { "success": true, "messageId": "3EB0...", "messageIds": [...] }
```

### POST /send-media — Enviar arquivo/mídia nativamente
```bash
curl -s -X POST http://localhost:3000/send-media \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363XXXXX@g.us","filePath":"/caminho/arquivo.html","caption":"Descrição","mediaType":"document","fileName":"nome_amigavel.html"}'
```

### POST /edit — Editar mensagem já enviada
```bash
curl -s -X POST http://localhost:3000/edit \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363XXXXX@g.us","messageId":"3EB0...","message":"Novo texto"}'
```

## Descobrir IDs de Grupos

O bridge mantém session keys no diretório `/opt/data/whatsapp/session/`. Cada grupo tem sender-key files.

### Listar todos os grupos e seus nomes
```bash
for gid in $(ls /opt/data/whatsapp/session/sender-key-*.json | \
  sed 's/.*sender-key-//' | sed 's/--.*//' | sort -u | \
  grep -v "broadcast\|memory\|newsletter\|status"); do
  curl -s http://localhost:3000/chat/$gid | \
    python3 -c "import sys,json; d=json.load(sys.stdin); \
    print(d.get('name','NO_NAME')+' | '+str(d.get('isGroup','?'))+' | $gid')"
done
```

### Encontrar grupo por nome
```bash
for gid in $(ls /opt/data/whatsapp/session/sender-key-*.json | \
  sed 's/.*sender-key-//' | sed 's/--.*//' | sort -u | \
  grep -v "broadcast\|memory\|newsletter\|status"); do
  name=$(curl -s http://localhost:3000/chat/$gid | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('name',''))")
  if echo "$name" | grep -qi "Núcleo\|termo de busca"; then
    echo "ENCONTRADO: $name → $gid"
  fi
done
```

## Descobrir Contatos Individuais (WhatsApp Numbers)

O bridge em self-chat mode **não registra mensagens enviadas para terceiros** (fromMe + !isSelfChat → skip silencioso na linha 310 do bridge.js). Para descobrir números de contatos:

### Método 1: lid-mapping files

O Baileys armazena mapeamentos entre LIDs (Linked Identity Device) e números reais:

```bash
# Encontrar mapeamento reverso de um LID
cat /opt/data/whatsapp/session/lid-mapping-<LID>_reverse.json
# → "557991441720" (número sem formato)

# Listar todos os mappings disponíveis
ls /opt/data/whatsapp/session/lid-mapping-*_reverse.json 2>/dev/null
```

### Método 2: participantAlt no bridge.log

O bridge.log contém o campo `participantAlt` em mensagens de grupo, que revela o número real do participante:

```bash
# Extrair números reais de participantes de grupos
grep -oP '"participantAlt":"[^"]+' /opt/data/whatsapp/bridge.log | sort -u
# → "participantAlt":"557981046907@s.whatsapp.net"
# → "participantAlt":"557991061860@s.whatsapp.net"
```

O LID está no campo `participant`:
```bash
grep -oP '"participant":"[^"]+' /opt/data/whatsapp/bridge.log | sort -u
# → "participant":"9891309699237@lid"
```

Cruzando os dois campos, você mapeia LID → número real.

### Método 3: Google Contacts API

Com o escopo `contacts.readonly` ativo no token do Google Workspace:

```bash
GAPI contacts list --max 500
```

Útil para encontrar contatos por nome (ex: "Tácio") e obter o número de telefone. O número então precisa ser convertido para JID format (`numero@s.whatsapp.net`) — em caso de dúvida sobre o dígito 9, testar com e sem.

### Método 4: user fornece o número

Pedir diretamente ao usuário é sempre a opção mais rápida. Validar com uma mensagem de teste antes de salvar na skill.

## Self-Chat Mode

Em self-chat mode:
- Mensagens enviadas para grupos aparecem como vindas do **próprio número do usuário**
- A bridge não processa mensagens recebidas de outros membros (eventos `ignored` com reason `self_chat_mode_rejects_non_self`)
- O prefixo padrão `⚕ *Hermes Agent*\n────────────\n` é adicionado automaticamente a mensagens de texto enviadas
- Envio via `sock.sendMessage()` da baileys funciona normalmente — retorno `success` do endpoint ≠ garantia de entrega visível

### Outgoing Messages to Third Parties (fromMe + !isGroup)

**São silenciosamente ignorados — NÃO aparecem no bridge.log.** O código da bridge (linha 310) faz `if (!isSelfChat) continue;` — se o destinatário não é o próprio número do usuário, a mensagem é descartada sem log. Isso significa:
- Mensagens-teste como "abangas" / "katastopoulos" enviadas para contatos ou grupos NÃO geram entrada no log
- Para encontrar números de contatos, use **Google People/Contacts API** (escopo `contacts.readonly`) ou peça diretamente ao usuário
- Para confirmar que um grupo existe, use `GET /chat/:id` com o JID candidato (extraído de sender-key files, não do log)

## Boas Práticas

1. Sempre verificar o nome do grupo via `GET /chat/:id` ANTES de enviar — IDs de grupos não são óbvios e confundir grupos causa ruído
2. Preferir `send-media` com `mediaType: "document"` para arquivos HTML — WhatsApp renderiza como documento baixável
3. Manter o ID salvo em memória com descrição clara do grupo
4. Se a mensagem de texto não aparecer, tentar enviar como mídia (documento) que tem caminho de entrega diferente na baileys

## Contatos Salvos

⚠️ **Skill consolidation can delete these.** The skills-repo-curator evolve phase strips verified JIDs from skills. Save in three places: this skill, messaging-platforms umbrella (Contact Reference section), and memory.

| Grupo | JID | Notas |
|-------|-----|-------|
| ID [Núcleo] | `120363170662612284@g.us` | Grupo interno da ID Consultoria |
| IA que Funciona | `120363419131378682@g.us` | Comunidade IAF |
| Tácio Brito | `557991441720@s.whatsapp.net` | Sócio ID Consultoria |

**Verification command:**
```bash
curl -s http://localhost:3000/chat/JID | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','NO_NAME'))"
```

Group IDs are opaque — always verify name before sending. Contact JIDs follow the format `number@s.whatsapp.net` and group JIDs follow `group_id@g.us`. Use `GET /chat/:id` to resolve names.

## Pitfalls

⚠️ **ID errado de grupo é o erro mais comum.** Sempre confirme o nome ANTES de enviar. Um grupo pode ser ativo nos logs mas não ser o grupo alvo.

⚠️ **`curl /send` retorna `success: true` mesmo se a mensagem não chegar.** O `sendMessage` da baileys confirma o recebimento pelo servidor do WhatsApp, mas self-chat mode pode silenciar a entrega em grupos. Verificar visualmente.

⚠️ **sender-key files têm nomes não óbvios.** O mesmo grupo pode ter múltiplos sender-key files (um por participante). Usar `sed` para extrair o group JID e `sort -u` para deduplicar.

⚠️ **Mensagens com emoji podem falhar silenciosamente** em certos clients WhatsApp. Preferir texto sem emoji ou usar apenas caracteres ASCII.

⚠️ **✅ como bullet visual de task dá impressão de "concluído".** Ao listar tarefas/pendências, NÃO use `✅` como marcador — o checkmark visual faz parecer que está tudo entregue, independente do status textual. Use bullet neutro (`•`, `▸`, `—`) e coloque o status explicitamente na linha abaixo com emoji semântico. Exemplo correto:

  ✅ Pazion — Reunião técnica
     *Status:* ✅ Entregue

  ✅ Da Hortinha — Treinamento/Contratação
     *Status:* 🔄 Em progresso

  ✅ Café com IA — Briefing + contatar cafeterias
     *Status:* ⏳ Não iniciado

  Use `✅` APENAS como bullet se todas as tarefas da lista estiverem CONCLUÍDAS. Para listas de pendências com status mistos, use `•` ou `▸` como bullet.

  Paleta de status:
  - `✅` Entregue / Concluído
  - `🔄` Em progresso
  - `⏳` Não iniciado / Pendente
  - `⛔` Bloqueado

  Agrupe por responsável com separadores visuais (━━ NOME ━━) e inclua link do documento original quando referenciar atas/documentos.

⚠️ **Cron job com `send_message` + `deliver` errado causa duplicação.** Quando um cron job usa `send_message()` para entregar no grupo E o cron está configurado com `deliver: "whatsapp:grupo"`, a resposta final do agente (incluindo confirmação) também vai pro grupo — gerando duplicata. **Correção:** no cron, usar `deliver: "origin"` (volta pro chat do usuário), e a mensagem pro grupo enviada exclusivamente via `send_message()`. A resposta final do agente deve ser uma confirmação enxuta ("✅ Lembrete enviado.") sem IDs técnicos ou o conteúdo da mensagem.

⚠️ **Skill consolidation can delete verified group JIDs.** The skills-repo-curator evolve phase may strip the Contatos Salvos table from this skill. Happened 15/06/2026. If you find this section empty, restore from memory or re-verify via `GET /chat/:id` for each known sender-key group JID. Always save in three places: this skill, messaging-platforms umbrella, and memory.
