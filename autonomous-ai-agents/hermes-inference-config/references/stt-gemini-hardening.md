# STT Gemini — endurecer o provider `command` e propagar para todos os perfis

Receita verificada em produção (22/09/2026): o sintoma era a mensagem
`[voice message could not be transcribed automatically]` chegando no chat, com o áudio salvo em
`cache/audio/`. Causa: **modelo fixo** (`gemini-flash-lite-latest`) devolvendo `503 UNAVAILABLE`
— e o STT não passa por `fallback_providers`, então não havia fallback nenhum.

## Por que a config precisa de cadeia de resolução de caminho

O provider `command` roda com `shell=True` num env **sanitizado** (`hermes_subprocess_env`,
`inherit_credentials=False`): a `GOOGLE_API_KEY` normalmente NÃO chega no subprocesso. Duas
consequências:

1. o script tem de resolver a chave sozinho nos `.env` candidatos; e
2. o caminho do script na config não pode ser um HERMES_HOME fixo se o home migra
   (`/opt/data` ⇄ `/opt/mercurio-data`, host Oracle, perfis).

Solução: **um ponto de entrada único** no `command` — a linha `for c in ...` que testa candidatos
em ordem e faz `exec`. Ela funciona mesmo sem o dispatcher instalado.

## Arquivos (fonte da verdade)

| Papel | Caminho |
|---|---|
| Cadeia de modelos + retry + chunking | `<HERMES_HOME>/scripts/gemini-stt.py` (canônico) |
| Dispatcher manual/agente | `/usr/local/bin/gemini-stt` (shell; resolve o canônico por HERMES_HOME) |
| Config | `stt.providers.gemini.command` (linha acima) + `timeout: 300` + `env_passthrough` |
| Pantheon fora do proot | `~/.hermes/.hermes/scripts/gemini-stt.py` — **o mesmo arquivo serve os 8 perfis** |

O script é stdlib-only (roda no python do venv ou no python3 do Termux), não imprime transcrição
no stdout (só stderr resumido) e **não escreve o arquivo de saída quando falha** — o Hermes então
avisa o usuário em vez de inventar texto.

## Ordem da cadeia de modelos

`gemini-2.5-flash` → `gemini-flash-lite-latest` → `gemini-flash-latest` → `gemini-2.0-flash`.

- `gemini-2.5-flash` primeiro: melhor transcrição pt-BR e foi o que transcreveu quando o lite
  estava em 503.
- **Não inclua `gemini-2.5-pro`**: `404 ... no longer available to new users`.
- Sobrescrever sem editar código: `GEMINI_STT_MODELS=a,b,c` ou `--models a,b` (útil para testar
  o fallback com um nome inexistente na frente).

## Controles por ambiente

| Var | Default | Uso |
|---|---|---|
| `GEMINI_STT_MODELS` | lista acima | ordem de tentativa |
| `GEMINI_STT_ATTEMPTS` | 2 | tentativas por modelo |
| `GEMINI_STT_TIMEOUT` | 120 s | timeout por requisição |
| `GEMINI_STT_BUDGET` | 260 s | orçamento total (< `timeout` do provider) |
| `GEMINI_STT_INLINE_MAX` | 15 MiB | acima disso: resize/chunk com ffmpeg |
| `GEMINI_STT_CHUNK_S` | 600 s | tamanho do pedaço |

Retentável: `408/409/425/429/5xx`, timeout/rede, resposta vazia. Não retentável: `400/401/403/404`
(passa para o próximo modelo em vez de insistir).

## Deploy: proot (Mercúrio + perfis)

```bash
# 1. script canônico
cp gemini-stt.py "$HERMES_HOME/scripts/gemini-stt.py"

# 2. dispatcher
install -m 755 gemini-stt /usr/local/bin/gemini-stt   # sh, resolve HERMES_HOME e afins

# 3. config por perfil (HERMES_HOME aponta o perfil; repita para cada um)
export HERMES_HOME=/opt/mercurio-data/profiles/<nome>
hermes config set stt.enabled true
hermes config set stt.provider gemini --force          # SEM --force o CLI recusa a chave
hermes config set stt.providers.gemini.type command --force
hermes config set stt.providers.gemini.command "$CMD" --force
hermes config set stt.providers.gemini.language pt-BR --force
hermes config set stt.providers.gemini.timeout 300 --force
hermes config set stt.providers.gemini.env_passthrough '["GOOGLE_API_KEY","GEMINI_API_KEY"]' --force
```

**`hermes config set` reescreve o arquivo e APAGA comentários.** Faça backup
(`cp -p config.yaml config.yaml.bak-pre-stt-<ts>`) antes e confira o bloco depois.

## Deploy: pantheon fora do proot (Termux por SSH)

Todos os perfis do host apontam para o MESMO arquivo `~/.hermes/.hermes/scripts/gemini-stt.py` —
trocar esse arquivo conserta default + apolo + ares + atena + caissa + hefesto + themis + zeus.

```bash
KEY=~/.ssh/id_ed25519
SSH="ssh -p 8022 -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null localhost"
$SSH 'cat > "$HOME/.hermes/.hermes/scripts/gemini-stt.py.new"' < gemini-stt.py
$SSH 'cd "$HOME/.hermes/.hermes/scripts" && cp -p gemini-stt.py gemini-stt.py.bak-$(date +%Y%m%d-%H%M%S) \
      && mv gemini-stt.py.new gemini-stt.py && chmod 600 gemini-stt.py'
```

Não há `/tmp` em sessão ssh no Termux — use `mktemp -d "$HOME/.tmp/..."`.
Nó remoto (VPS/Oracle), que não está no alcance local, continua com o caminho antigo: aponte a
config dele para a mesma linha `for c in ...` quando houver acesso.

## Verificação (o que conta como prova)

1. **Direto:** `/usr/local/bin/gemini-stt --input <audio.ogg> --output /tmp/t.txt --language pt-BR`
   → `ok: N caracteres` e o texto no arquivo.
2. **Caminho NATIVO (o que importa):** com o python do Hermes,
   `HERMES_HOME=<home> python -c "import sys; sys.path.insert(0,'/usr/local/lib/hermes-agent');
   from tools.transcription_tools import transcribe_audio; print(transcribe_audio('<audio>'))"`
   → `{'success': True, 'transcript': ...}`. Repita por perfil (o `HERMES_HOME` certo).
3. **Env limpo:** `env -i HOME=/root PATH=... /usr/local/bin/gemini-stt ...` prova que a chave sai
   do `.env` (não do env do gateway) e que o caminho não depende de `HERMES_HOME`.
4. **Fallback:** `--models gemini-zzz-bogus,gemini-2.5-flash` → erro no primeiro, texto no segundo.
5. **Falha honesta:** `--models bogus-a,bogus-b` → `rc=1` e **nenhum** arquivo de saída.

## Pitfalls (todos mordidos)

- **`-c copy` no muxer `segment` com ogg NÃO corta certo:** os pedaços saem com duração crescente
  e conteúdo sobreposto (`8s, 16s, 17.5s` num arquivo de 17.5s) e a transcrição final repete trecho.
  Use re-encode + `-reset_timestamps 1` — os pedaços saem `8, 8, 1.6`.
- **Validar saída de ffmpeg por caminho de arquivo quebra o `segment`:** o template `part_%03d.ogg`
  nunca existe como arquivo; valide por `rc` e liste os `part_*` produzidos.
- **Provider sem `stt.provider` cai no backend local** — o Hermes tenta instalar `faster-whisper`
  no venv na hora e falha com erro de permissão, devolvendo `No STT provider available`. Sempre
  confirme `provider: gemini` no perfil.
- **`stt.provider` exige `--force`** no `hermes config set` (o CLI não lista a chave).
- Nome de provider `gemini` **não** é builtin (`local`, `local_command`, `groq`, `openai`,
  `mistral`, `xai`, `elevenlabs`, `deepinfra`) — se fosse, o `command` seria ignorado.
- Timeout acima de 300 s não adianta: o timeout do provider é *idle* e o script corta por
  orçamento (`GEMINI_STT_BUDGET`) antes.
- O gateway re-lê a config pela **assinatura do arquivo** — não precisa reiniciar para o STT novo
  valer (diferente de `model.default`, que exige restart).
