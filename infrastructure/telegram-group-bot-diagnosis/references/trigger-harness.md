# Harness do gatilho + chaves de acionamento

## Chaves (bloco `telegram:` do `config.yaml` do perfil; o mesmo bloco pode estar duplicado em
`platforms.telegram.extra`)

| Chave (yaml / env) | Efeito |
|---|---|
| `allowed_chats` / `TELEGRAM_ALLOWED_CHATS` | Grupos onde o bot responde. **Não-vazio = hard gate**: fora da lista só passa com `guest_mode` + menção explícita |
| `group_allowed_chats` | Concessão de autorização **por chat** (não é hard gate) e escopo onde a observação acontece: `group_allowed_chats ∩ allowed_chats` |
| `require_mention` | Em grupo, só acorda com menção, `/cmd@bot` ou reply ao bot |
| `free_response_chats` / `free_response_topics` | Chats/tópicos onde responde sem menção |
| `exclusive_bot_mentions` | Mensagem que menciona explicitamente **outro** bot não acorda este |
| `observe_unmentioned_group_messages` | Guarda a conversa do grupo como contexto **sem** acionar o agente |
| `allow_bots` / `bots_require_mention` | Outro bot precisa @mencionar; quote-reply de bot não basta |
| `mention_patterns` | Padrões extra de acionamento |
| `channel_prompts` | Prompt por chat — chaveado por ID, envelhece junto com o chat |

Semântica implementada em `_should_process_message`
(`plugins/platforms/telegram/adapter.py`) e documentada por teste em
`tests/gateway/test_telegram_group_gating.py` — os nomes dos testes são a especificação; leia-os
antes de teorizar.

Menção digitada à mão **não** é o caso que falha: o handle do próprio bot é aceito mesmo sem
entidade `mention` (o fallback de texto opta explicitamente pelo handle próprio).

## Harness — rodar o gatilho com a config real

Boilerplate copiado de `_make_adapter` em `tests/gateway/test_telegram_group_gating.py` (é a
fonte que se mantém atualizada):

```python
import asyncio, yaml
from types import SimpleNamespace
from unittest.mock import AsyncMock
from gateway.config import Platform, PlatformConfig
from plugins.platforms.telegram.adapter import TelegramAdapter

cfg = yaml.safe_load(open("/data/data/com.termux/files/home/capitolium/profiles/<perfil>/config.yaml"))
extra = dict(cfg.get("telegram") or {})

a = object.__new__(TelegramAdapter)
a.platform = Platform.TELEGRAM
a.config = PlatformConfig(enabled=True, token="***", extra=extra)
a._bot = SimpleNamespace(id=<bot_id>, username="<handle>")
a._message_handler = AsyncMock()
a._pending_text_batches = {}; a._pending_text_batch_tasks = {}
a._text_batch_delay_seconds = 0.01; a._text_batch_split_delay_seconds = 0.01
a._mention_patterns = a._compile_mention_patterns()
a._forum_lock = asyncio.Lock(); a._forum_command_registered = set()
a._active_sessions = {}; a._pending_messages = {}

HANDLE = "@<handle>"
def msg(text, chat_id, entities=None, from_user=<id>):
    return SimpleNamespace(
        message_id=1, text=text, caption=None,
        entities=entities if entities is not None else [
            SimpleNamespace(type="mention", offset=0, length=len(HANDLE))],
        caption_entities=[], message_thread_id=None, is_topic_message=False,
        chat=SimpleNamespace(id=chat_id, type="supergroup", title="Grupo", is_forum=False),
        from_user=SimpleNamespace(id=from_user, full_name="Quem", first_name="Quem"),
        reply_to_message=None, date=None)

m = msg(f"{HANDLE} oi", <chat_id>)
print(a._should_process_message(m), a._should_observe_unmentioned_group_message(m))
```

Execução: `cwd`/`PYTHONPATH` = `/usr/local/lib/hermes-agent`, python do venv do próprio Hermes
(`/usr/local/lib/hermes-agent/venv/bin/python`). Rodar também com `entities=[]` — texto puro bomba
para o mesmo resultado e confirma que o problema não é o formato da menção.

Leitura: **`False`** = config/gating explicam a mudez. **`True`** = o gatilho teria acordado o
agente; a mensagem não chegou ao processo (entrega/membro do grupo) — e aí valem os fatos da §1
do SKILL.md.

## Varrer os bots do gateway multiplex

Cada perfil tem token próprio em `/data/data/com.termux/files/home/capitolium/profiles/<perfil>/.env` (o perfil raiz usa
`/data/data/com.termux/files/home/capitolium/.env`). `getMe` + `getChatMember` de cada token responde **quais** bots estão
no grupo — o que descarta na hora o cenário "quem postou foi outro agente".
