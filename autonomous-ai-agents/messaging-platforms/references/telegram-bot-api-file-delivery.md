# Telegram Bot API — File Delivery from TUI

## Quando usar

A entrega padrão via `MEDIA:` no response funciona para mensagens do gateway (Telegram/WhatsApp). Mas quando você está na **TUI** (terminal UI), `MEDIA:` entrega localmente — não roteia para o Telegram. Use a Bot API diretamente via curl.

## Pré-requisitos

- `TELEGRAM_BOT_TOKEN` definido em `/opt/data/.env`
- `TELEGRAM_HOME_CHANNEL` (chat ID) definido em `/opt/data/.env`
- curl instalado

## Enviar arquivo (documento)

```bash
source /opt/data/.env && curl -s -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument" \
  -F chat_id="${TELEGRAM_HOME_CHANNEL}" \
  -F document=@/path/to/file.ext \
  -F caption="Optional caption"
```

**⚠️ HTML é descartado silenciosamente pelo Telegram.** O `sendDocument` retorna 200 OK com um `file_id`, mas o arquivo .html nunca chega ao destinatário. **Sempre zipar arquivos .html antes de enviar:**

```python
import zipfile, os
zip_path = '/tmp/archive.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write('file.html', 'file.html')
```

## Enviar texto (mensagem simples)

```bash
source /opt/data/.env && curl -s -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_HOME_CHANNEL}" \
  -d text="Sua mensagem aqui" \
  -d parse_mode="HTML"
```

## Formas de obter o token (evitando redação do terminal)

O terminal Hermes redaciona valores que parecem tokens/keys na saída. O token não aparece no output, mas o shell exporta a variável corretamente:

```bash
# ✅ Funciona — source exporta, curl usa pela env var
source /opt/data/.env && curl ... -F document=@file.zip

# ❌ Não funciona — o terminal redaciona o valor na saída
echo "$TELEGRAM_BOT_TOKEN"

# ✅ Para debugging sem expor o token:
curl -s -o /dev/null -w "%{http_code}" \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

## Verificar entrega

O retorno `{"ok":true}` com `message_id` e `chat` confirma entrega. Extraia o `message_id` para referência.

## Pitfalls

⚠️ **`.html` files são descartados.** Telegram aceita o upload (200 OK, devolve file_id) mas o arquivo .html nunca aparece no chat. Sempre zipar.

⚠️ **`source /opt/data/.env` pode emitir erros** de outras variáveis (e.g., `ghp_xxx: command not found`). Ignore — o comando curl ainda funciona porque as variáveis foram exportadas antes do erro. Para evitar, filtre: `source <(grep -E '^TELEGRAM_' /opt/data/.env)`.

⚠️ **Rate limits.** Telegram limita a ~30 mensagens/segundo por chat. Uma entrega de arquivo conta como 1 mensagem. Para envio em massa, use `sleep 1` entre chamadas.

⚠️ **Parse mode HTML requer escaping.** Se usar `parse_mode="HTML"` no sendMessage, escape `<`, `>`, `&` no texto. Use `parse_mode="MarkdownV2"` como alternativa (escaping mais previsível).
