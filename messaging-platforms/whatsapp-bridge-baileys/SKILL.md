---
name: whatsapp-bridge-baileys
description: "Send messages, discover group IDs, and manage media via a local WhatsApp Baileys bridge.\n\nLoad this skill when you need to interact with WhatsApp programmatically. Covers the local Node.js HTTP bridge on port 3000 using @whiskeysockets/baileys — sending text and media messages, editing sent messages, discovering group IDs from sender-key files, self-chat mode behavior, and common pitfalls including silent delivery failures and emoji issues. Always verify group names before sending to avoid wrong-group-ID errors."
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

## Self-Chat Mode

Em self-chat mode:
- Mensagens enviadas para grupos aparecem como vindas do **próprio número do usuário**
- A bridge não processa mensagens recebidas de outros membros (eventos `ignored` com reason `self_chat_mode_rejects_non_self`)
- O prefixo padrão `⚕ *Hermes Agent*\n────────────\n` é adicionado automaticamente a mensagens de texto enviadas
- Envio via `sock.sendMessage()` da baileys funciona normalmente — retorno `success` do endpoint ≠ garantia de entrega visível

## Boas Práticas

1. Sempre verificar o nome do grupo via `GET /chat/:id` ANTES de enviar — IDs de grupos não são óbvios e confundir grupos causa ruído
2. Preferir `send-media` com `mediaType: "document"` para arquivos HTML — WhatsApp renderiza como documento baixável
3. Manter o ID salvo em memória com descrição clara do grupo
4. Se a mensagem de texto não aparecer, tentar enviar como mídia (documento) que tem caminho de entrega diferente na baileys

## Contatos Salvos

Group IDs are opaque — always verify name before sending. Contact JIDs follow the format `number@s.whatsapp.net` and group JIDs follow `group_id@g.us`. Use `GET /chat/:id` to resolve names.

## Pitfalls

⚠️ **ID errado de grupo é o erro mais comum.** Sempre confirme o nome ANTES de enviar. Um grupo pode ser ativo nos logs mas não ser o grupo alvo.

⚠️ **`curl /send` retorna `success: true` mesmo se a mensagem não chegar.** O `sendMessage` da baileys confirma o recebimento pelo servidor do WhatsApp, mas self-chat mode pode silenciar a entrega em grupos. Verificar visualmente.

⚠️ **sender-key files têm nomes não óbvios.** O mesmo grupo pode ter múltiplos sender-key files (um por participante). Usar `sed` para extrair o group JID e `sort -u` para deduplicar.

⚠️ **Mensagens com emoji podem falhar silenciosamente** em certos clients WhatsApp. Preferir texto sem emoji ou usar apenas caracteres ASCII.

⚠️ **Cron job com `send_message` + `deliver` errado causa duplicação.** Quando um cron job usa `send_message()` para entregar no grupo E o cron está configurado com `deliver: "whatsapp:grupo"`, a resposta final do agente (incluindo confirmação) também vai pro grupo — gerando duplicata. **Correção:** no cron, usar `deliver: "origin"` (volta pro chat do usuário), e a mensagem pro grupo enviada exclusivamente via `send_message()`. A resposta final do agente deve ser uma confirmação enxuta ("✅ Lembrete enviado.") sem IDs técnicos ou o conteúdo da mensagem.
