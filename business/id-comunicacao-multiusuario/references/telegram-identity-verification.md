# Verificar identidade de contato Telegram via Bot API (getChat)

Validado 25/08/2026. Objetivo: confirmar quem está atrás de um `chat_id` **sem
interferir no gateway** (que faz long-polling).

## Por que `getChat` é seguro
- É um endpoint de **leitura pura** — **não** consome/confirma updates, portanto não
  rouba mensagens do gateway que está em long-polling. Usar `getUpdates` aqui seria
  arriscado (consumiria o update da mensagem corrente).
- O token do bot fica em `/opt/data/.env` (regex `[0-9]{8,10}:[A-Za-z0-9_-]{30,}`).
  **Nunca imprimir o token** no output — filtrar a saída para só nome/username/type.
- Em alguns containers o CLI `hermes` não está no PATH; o token também não fica na
  `config.yaml` (só em `.env`). Não perder tempo procurando em config.

## Receita (stdlib, sem deps)

```python
import re, json, urllib.request

tok = None
for line in open('/opt/data/.env', encoding='utf-8'):
    m = re.search(r'([0-9]{8,10}:[A-Za-z0-9_-]{30,})', line)
    if m:
        tok = m.group(1)
        break
if not tok:
    print("NO_TOKEN"); raise SystemExit(0)

def gc(cid):
    with urllib.request.urlopen(
        f"https://api.telegram.org/bot{tok}/getChat?chat_id={cid}", timeout=12) as fp:
        return json.loads(fp.read().decode()).get('result', {})

for cid in ["6171996969"]:
    i = gc(cid)
    print(f"id={cid} first={i.get('first_name')} username={i.get('username')} type={i.get('type')}")
```

## Observações
- Para private chat, `type == "private"` e vem `first_name`/`last_name`/`username`.
- Se o id **não** for um chat que o bot conhece como private, `getChat` pode retornar
  `result` vazio ou erro — o id pode ser de grupo ou digitado errado. Confirmar com o
  usuário em vez de assumir.
- O `foreground command` com heredoc dispara auto-approval (smart approval) — normal.

## Exemplo real (validado 25/08/2026)
| chat_id | first | username | type | Quem |
|---|---|---|---|---|
| 6171996969 | Gustavo | None | private | Gustavo (sócio) |
| 8600141184 | Cleverton | None | private | Cleverton (Kel) |
| 8888381551 | (vazio) | None | None | id não-resolvido — **confirmar** (memória diz Maxwell) |
| 609921578 | N0ztr | n0ztr | private | Tácio Brito (handle @n0ztr) |
