# JSON Payload com Newlines no curl -d

## O Problema

Quando a mensagem WhatsApp contém quebras de linha (`\n`), o shell expande as strings antes de enviá-las. Se você usa `curl -d '{"message":"linha1\nlinha2"}'` no terminal, o shell interpreta o `\n` como escape, quebrando o JSON:

```
SyntaxError: Bad control character in string literal in JSON at position N
```

## Solução: Escrever o Payload em Arquivo

Sempre escreva o JSON completo em um arquivo primeiro, depois use `-d @arquivo`:

```bash
# 1. Criar o JSON (com quebras de linha literais \n)
cat > /tmp/payload.json << 'JSONEOF'
{
  "chatId": "120363XXXXX@g.us",
  "message": "Linha 1\n\nLinha 2\n\nLinha 3"
}
JSONEOF

# 2. Enviar com -d @arquivo
curl -s -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d @/tmp/payload.json
```

## Verificação Rápida

Antes de enviar, valide o JSON:

```bash
python3 -m json.tool /tmp/payload.json > /dev/null && echo "JSON válido" || echo "JSON inválido"
```

## Por que -d @arquivo Funciona

O `-d @arquivo` envia o conteúdo binário do arquivo sem interpretação do shell. O `\n` dentro das aspas duplas do JSON é preservado como escape sequence JSON (newline), que é exatamente o que o bridge espera.

## Alternativa: write_file + curl

O Hermes `write_file` escreve JSON válido sempre (lint automático). Use-o para criar o payload, depois faça o curl em sequência.
