---
name: hermes-inference-config
description: "Configure Hermes model/provider/fallback; route crons.

Load this skill when selecting or switching a Hermes model/provider, setting fallback chains, or routing crons. Covers hermes config set/get, provider definition, pin-vs-inherit for crons, and reading model errors from logs."
version: 1.0.0
author: Mercúrio
license: MIT
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [hermes, model, provider, fallback, cron, config, opencode]
    related_skills: [hermes-agent, messaging-platforms]
category: autonomous-ai-agents
type: Reference
timestamp: 2026-08-26T00:00:00Z
---

# Hermes Inference Config (models, providers, fallback chains, cron routing)

How to control which model/provider Hermes uses — the default, the ordered fallback
chain, and how cron jobs ride (or don't ride) that ladder. Also how to read model
failures out of the logs. Companion to the bundled `hermes-agent` skill (which is
off-limits to edit); this is the operational deep-dive for the class.

## When to use

- "Configurar modelo/provider", "muda o default", "cadeia de fallback"
- "O cron não usa a mesma cadeia", "cron usa modelo fixo"
- "Está dando 403 no modelo", "fallback não funcionou", "modelo não aceita imagem"

## Model & provider key reads

Read **one key at a time** — `hermes config get model providers fallback_providers`
fails with `unrecognized arguments`.

```bash
hermes config get model                  # default, provider, aliases
hermes config get providers              # defined provider entries
hermes config get fallback_providers     # ordered fallback chain
```

Set:

```bash
hermes config set model.default <model>
hermes config set model.provider <provider>
hermes config set fallback_providers '[{"base_url":"...","model":"...","provider":"..."}, ...]'
```

`HERMES_HOME=/opt/mercurio-data` — always set it so config edits land on the right
profile, not the default home.

## Defining a provider entry

`providers.<name>` blocks map a friendly name to a backend route + the provider that
owns the credential (the `.env` var key). Example:

```yaml
providers:
  opencode-free:
    api_mode: chat_completions
    base_url: https://opencode.ai/zen/v1
    model: muse-spark-1.2-contributor-free
    provider: opencode-zen      # backend that owns the cred (OPENCODE_ZEN_API_KEY)
```

Set field-by-field: `hermes config set providers.<name>.api_mode chat_completions`,
`.base_url`, `.model`, `.provider`. If no `.env` key covers a provider in the chain,
the **resolve fails** and the chain can't try it.

## Fallback chain mechanics

`fallback_providers` is an ordered list of `{base_url, model, provider}`. On primary
failure the scheduler walks it in order (only for `AuthError`/missing-cred and transient
network/DNS during resolve — not for a mid-stream model drop, which the agent loop
handles separately via the same global chain). Keep `model`+`provider` atomic per entry
— never swap just the provider while keeping a paid primary model.

## STT (áudio / nota de voz) — provider `command` e fallback por lista de modelos

Transcrição **não** passa por `fallback_providers`: o STT é um **provider `command`**
declarado em `stt.providers.<nome>` (aqui `gemini`, apontando para um script que lê o áudio e
escreve a transcrição). Quando ele falha, a cadeia global não cobre nada — o fallback tem de
existir **dentro do script**.

Leia a config antes de mexer: `grep -A12 '^stt:' $HERMES_HOME/config.yaml`.

Sintoma de falha no canal: a mensagem do usuário chega como
`[voice message could not be transcribed automatically; the audio is available at: ...]`.
**Isso não é impedimento** — o áudio está em disco e o script do provider roda à mão:

```bash
python3 $HERMES_HOME/scripts/gemini-stt.py --input <audio.ogg> --output /tmp/stt.txt --language pt-BR
```

**Regra: modelo de transcrição fixo é ponto único de falha.** `503 UNAVAILABLE` ("currently
experiencing high demand") e timeout são intermitentes e normais nesses modelos — itere por uma
lista (`gemini-2.5-flash` → `gemini-flash-lite-latest` → `gemini-flash-latest` → `gemini-2.0-flash`),
algumas tentativas por modelo com sleep curto; na prática o primeiro fallback transcreve mesmo com
o modelo configurado em 503. Só relate falha depois de esgotar a lista, e nunca devolva transcrição
que a API não retornou. (`gemini-2.5-pro` NÃO serve: 404 "no longer available to new users".)

**Em produção a cadeia vive DENTRO do script do provider**, não na config: o script canônico
`<HERMES_HOME>/scripts/gemini-stt.py` já itera a lista, faz retry em erro retentável, divide áudio
longo com ffmpeg e resolve a chave nos `.env` do nó. A config aponta para um ponto de entrada único
(cadeia de resolução de caminho no próprio `command`) e passa `env_passthrough` — receita completa,
deploy nos perfis e pitfalls verificados em `references/stt-gemini-hardening.md`.

Config de referência (mesma em todos os perfis; só `enabled`/`provider` variam):

```yaml
stt:
  enabled: true
  provider: gemini
  providers:
    gemini:
      type: command
      command: for c in /usr/local/bin/gemini-stt "${HERMES_HOME:-/opt/mercurio-data}"/scripts/gemini-stt.py /opt/mercurio-data/scripts/gemini-stt.py /opt/data/scripts/gemini-stt.py /opt/data/.hermes/scripts/gemini-stt.py; do [ -f "$c" ] || continue; case "$c" in *.py) exec python3 "$c" --input {input_path} --output {output_path} --language {language} ;; *) exec "$c" --input {input_path} --output {output_path} --language {language} ;; esac; done; echo "STT nenhum script gemini-stt encontrado" >&2; exit 127
      language: pt-BR
      timeout: 300
      env_passthrough: [GOOGLE_API_KEY, GEMINI_API_KEY]
```

Receita avulsa (fora do Hermes): `scripts/transcrever_audio_com_fallback.py` (áudio → texto, com a
lista de modelos e o `--out`).

## CRITICAL — cron jobs follow the chain only when UNPINNED

The trap. A cron job that carries explicit `model`/`provider` fields is **PINNED**: it
uses exactly that model and does **NOT** walk `fallback_providers`. Pin it to a model
that's no longer in the chain and it quietly runs off the ladder — if that model fails,
the job dies instead of falling back.

- **Make a cron inherit the global default + chain:**
  `hermes cron edit <id> --model "" --provider ""` (empty string clears the pin)
- **Force a cron onto a fixed reliable model:** `hermes cron edit <id> --model X --provider Y`

### Drift-guard (why unpin doesn't silently fail-closed)

`hermes config set model.default ...` warns:
`1 enabled unpinned cron job has stored model_snapshot values that differ...`. That's
the **model-drift guard** (#44585 spend-safety). An unpinned job with a creation-time
snapshot that no longer matches the default **fails closed** (skips run, loud alert) to
stop a global switch from silently sending a paid model.

- Unpinning **recalculates** `model_snapshot`/`provider_snapshot` to the new default →
  `snapshot == default`, guard no longer blocks. This is why unpin is safe here.
- A `no_agent` cron (script-only, `no_agent: true`) never touches inference — unaffected.
- **Fail-closed is LOUD once, then silent.** The alert is emitted on the first skipped run; the
  job keeps being skipped afterwards with no further noise. For an **alerting** job (monitor,
  watcher, "avise-me quando X chegar"), that inverts its purpose: it goes mute exactly when the
  event it exists to catch arrives. Re-check alignment after any `model.default`/provider change
  **and** after every `cron pause`/`resume` — pausing and resuming does not refresh a stale
  snapshot. Recipe + verification: `hermes-cron-script-dispatch` (monitor gate) and
  `references/cron-drift-recovery.md` here.

### Decision table

| Need | Action |
|------|--------|
| Cron rides the same ladder as interactive sessions | unpin: `--model "" --provider ""` |
| Cron must always use a specific reliable model | pin: `--model X --provider Y` |
| Confirm current pin state | read `jobs.json` under `$HERMES_HOME/cron/` (fields `model`, `provider`, `model_snapshot`, `provider_snapshot`) |

## Rascunho interno entregue como conteúdo — não é flag de reasoning

Sintoma: a pessoa lê, na mensagem final, o planejamento do modelo em vez da resposta — metacomentário
(\"Wait I must avoid…\", \"não devo alucinar\", \"deixa eu verificar\"), caracteres de outro idioma, ou a
mesma frase reescrita em caixa alta sem querer. No Telegram isso chega como texto corrompido, e o
usuário lê como erro de tom ou bug de produto.

**Não é o canal de reasoning vazando.** `show_reasoning: false`, `verbose: false` e
`reasoning_effort` governam o canal de reasoning; não seguram texto que o modelo escreve dentro do
próprio corpo da mensagem final. Antes de caçar flag, leia a mensagem exata na conversa: se o
metacomentário está no corpo entregue, a hipótese \"config de reasoning\" está morta.

Procedimento: (1) localizar a mensagem e ler o texto bruto; (2) confirmar o estado real das flags no
perfil (`hermes config get model`, ou o `config.yaml` do perfil); (3) concluir que a correção é no
modelo/route ou no script que governa aquela resposta — não na config de reasoning. Registrar como
pitfall de qualidade do modelo no perfil evita que o próximo diagnóstico gaste tempo procurando flag.

Achado associado: o mesmo defeito aparecendo em conversa diferente (DM e grupo) numa janela curta
indica falha do modelo naquele momento, não evento isolado do interlocutor. Quando coincide com
troca recente de modelo/route, olhar o histórico de trocas antes de atribuir ao interlocutor.

## Diagnosing model errors from logs

Logs at `$HERMES_HOME/logs/errors.log` and `agent.log`.

| Log line | Meaning / action |
|----------|------------------|
| `HTTP 403 ... requires explicit opt in` | Data-collection model (e.g. Muse Spark Contributor) needs a **one-time opt-in** at the provider's workspace URL. Provider-side consent, not a Hermes bug. After opt-in, use the model normally. |
| `HTTP 401` com `{'type':'AuthError','message':'Missing API key.'}` | A requisição saiu **sem** credencial — não é chave morta (chave inválida tem outra mensagem). Controle: POST sem header `Authorization` devolve exatamente esse corpo. Prove o caminho em processo novo: `hermes -z "ok" --provider <p> -m <modelo>` — se responder texto, o defeito é o processo antigo do gateway → reinicie. |
| `HTTP 401: Model <x> is not supported` | O modelo não existe no endpoint resolvido. Ex.: `deepseek-flash` só existe na rota Go; resolvido para `opencode-zen` dá esse 401. Nome de modelo é por endpoint, não global. |
| `Fallback to <X> failed: provider not configured` | A named provider in `fallback_providers` has no matching `providers.<name>` entry / no env key. Add it or fix the key. |
| `Model only supports text input; received unsupported content type 'image_url'` | That model has no vision. Images route through the auxiliary model (`auxiliary.vision`), not the main one. |
| `Stream ended with no finish_reason while a tool call's arguments were still incomplete` | Mid-tool-call stream drop by the model. Retry; do not treat as output-length truncation. |
| `Streaming failed before delivery: Connection error` / `Server disconnected` | Transient transport drop. Retry / let the fallback chain catch it. |

## After changing model / provider

Gateway needs a restart for config changes to apply to new sessions:
`/restart` (in gateway session) or `hermes gateway restart`. A model switch made via
OpenCode Go / session override applies to that session immediately; the config `default`
persists across restarts until changed.

## Host Hermes (Termux, FORA do proot) — chaves e perfis

O host Android roda a instalação "de fora" (`HERMES_HOME=$HOME/.hermes`), separada da
rama prootada. Alcance sem sair da sessão:

```bash
ssh -p 8022 -i /data/data/com.termux/files/home/.ssh/id_ed25519 \
  -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null localhost 'bash -s' < script.sh
```

- Perfis = `~/.hermes` (default) + `~/.hermes/profiles/<nome>/`. **Cada perfil tem `.env`
  próprio**; `profiles/default/` sem `.env`/`config.yaml` → **herda `~/.hermes/.env`**.
- Gateways são supervisionados por `~/scripts/run_forever.sh` (loop de respawn por perfil):
  matar o PID do gateway basta — ele volta com o `.env` recarregado.
- Backup antes de editar (`cp -p .env .env.bak-<motivo>-<ts>`), escrever atômico e
  **preservar modo 600** (o `.env` é `-rw-------`).
- Trocar chave = por **nome de variável** (`OPENCODE_GO_API_KEY=`, `OPENCODE_ZEN_API_KEY=`),
  com regex `^(#\s*)?(VAR=)\S*` para pegar também a **cópia comentada** do template —
  deixar a comentada com a chave velha é armadilha para quem descomentar depois.

### Provar que a chave vale (o `/models` NÃO prova)

`GET /zen/*/v1/models` é **público** — devolve 200 até com chave inválida. Use um POST
mínimo, sem gastar quase nada:

```bash
curl -s -o out.json -w '%{http_code}' -H "Authorization: Bearer $KEY" \
  -H 'Content-Type: application/json' -H "x-opencode-session: verify-$(date +%s)" \
  -d '{"model":"<modelo>","max_tokens":1,"messages":[{"role":"user","content":"ping"}]}' \
  https://opencode.ai/zen/go/v1/chat/completions
```

Leitura: **401 AuthError** = chave morta · **400 MissingSessionID** = autenticou e faltou o
header de sessão (Hermes manda) · **429 GoUsageLimitError** = chave válida com quota do mês
estourada · **200** = valendo. Sem `x-opencode-session` a rota "Console Go" nunca fecha 200.

Pitfall do Termux por SSH: **não existe `/tmp`** em sessão ssh → `curl -o /tmp/...` falha
silenciosamente e mascara o resultado. Use `mktemp -d "$HOME/.tmp/..."`.

## Rotação de chave de API (.env) — restart é obrigatório

Trocar o valor no `.env` **não** propaga para o gateway em execução: a credencial já foi
resolvida dentro do processo. Sem restart, a chave nova "não funciona" — o sintoma mais
comum é `401 Missing API key.`, com a chave boa e válida no arquivo.

Ordem de verificação (do mais barato ao definitivo):

1. `hermes auth status <provider>` / `auth list` → fonte ativa `env:<VAR>`.
2. **Fingerprint**: ler `$HERMES_HOME/auth.json` →
   `credential_pool.<provider>.entries[0].secret_fingerprint` deve ser o `sha256:` do valor
   novo — prova que o registro pegou a troca. Atenção ao resíduo `failure_reason: rate_limit`:
   `hermes auth reset <provider>` limpa **só status de exaustão** — responder *"Reset status on 0
   credentials"* quer dizer que nada estava marcado como exausto (quota não era o problema naquele
   instante), **não** que a entrada está sã. Esse campo residual sobrevive ao reset e ao restart, e
   é o suspeito nº 1 quando a requisição sai sem chave.
3. **Caminho real ponta-a-ponta** num processo novo (aceita provider explícito):
   `hermes -z "responda somente: ok" --provider <provider> -m <modelo>` — devolver texto = env → provider → request sano.
4. Só depois confie no chat; o teste final é uma mensagem sua na conversa.

### NUNCA rode `hermes gateway stop` (sem `--all`) no perfil default do host

`_matches_current_profile` (`hermes_cli/gateway.py`) decide o alvo pelo **argv**: no perfil
default, todo gateway cujo cmdline não tenha `--profile` **nem** `HERMES_HOME=` conta como
"deste perfil". O gateway da rama prootada sobe como `hermes gateway run --replace` (sem
`--profile`; `HERMES_HOME` só no environ, nunca no argv) → **entra no alvo e é derrubado
junto**. Foi assim que um `/restart` no default matou o gateway do Mercúrio.

Restart seguro do gateway do default: **SIGTERM no PID exato** (nunca `pkill`, nunca
`--all`) e deixar o `run_forever.sh` respawnar com o env correto. Confirme por
`/proc/<pid>/environ` (`HERMES_HOME=`) e por `logs/gateway_default.log` na linha
`[Telegram] Connected to Telegram (polling mode)`. O boot é lento (migrações do state.db +
DNS-over-HTTPS): ~90 s do SIGTERM até o Telegram reconectar.

Controle natural que confirma o mecanismo: no mesmo PRoot, um gateway com `--profile X` (X ≠
default) **sobrevive** ao restart do host — o `--profile` é o único marcador que o matcher
respeita. Se um gateway seu caiu e outro não, compare os argv antes de culpar a máquina.

## 401 "Missing API key" com credencial válida = identidade ANÔNIMA, não chave morta

Sintoma: relay (ex.: OpenCode Zen **Go**) responde `HTTP 401 {'type': 'AuthError', 'message':
'Missing API key.'}` para um provider cuja chave existe e está correta no `.env`/pool.
Não trate como chave inválida nem como "session state": a chave **não foi anexada**.

Como provar em 3 leituras (host, read-only):
1. `~/.hermes/sessions/request_dump_*.json` (dump só existe para erro 4xx não-retryable):
   `request.headers.Authorization`. Valor mascarado pelo dump como `pref8...suf4`. Se o valor
   mascarado for `opencode...less`, é o literal `opencode-zen-free-keyless`
   (`hermes_cli/models.py`: `OPENCODE_ZEN_FREE_KEYLESS_PLACEHOLDER`) — a identidade anônima
   do tier gratuito, enviada com `Authorization` **vazio** (guards em `agent/agent_init.py`
   e `agent/auxiliary_client.py`). Compare com dumps antigos da MESMA rota: se aparecer
   `Bearer sk-...` (chave real), a mudança é de **estado**, não de config.
2. `~/.hermes/auth.json` → `credential_pool.<provider>[0]`: `failure_reason` (ex.:
   `rate_limit`) e `secret_fingerprint`. Marca de esgotamento presente = credencial tratada
   como indisponível. `hermes auth reset <provider>` zera contadores de cota e devolve
   "0 credentials reset" — **não** limpa esse campo.
3. `logs/gateway_default.log`: linha `API call failed ... provider=<p> base_url=<u>
   model=<m>` + a mensagem do relay. Sequência típica de cota Go: 429 "Monthly usage limit
   reached. Resets in N days" e, daí em diante, 401 `Missing API key` na mesma rota.

Regra de ouro: nessa família de erro a variável é o **par modelo/rota** (modelo capado ou
não servido de forma anônima), não a sessão de chat. Reiniciar gateway ou dar `/new` não
conserta: o runtime é reconstruído, resolve a mesma credencial marcada e volta a sair
anônimo — todo request novo daquela rota falha igual.

Sintoma de restart sujo (fica no log): `Another gateway instance (PID N) started during our
startup. Exiting to avoid double-running` → startup travado esperando lease de
`state_db_data_migrations` → `Previous gateway life (pid=N) exited UNCLEANLY`. O processo
que sobrevive pode atender com credencial não injetada: reinicie limpo antes de investigar a chave.

### Restart que não muda o sintoma: suspeite do STORE DE SESSÃO, não do disco

Erro idêntico no processo recém-subido elimina memória de processo — **não** prova estado em
disco. O que sobrevive ao restart inclui a **sessão viva**: uma sessão que atravessou troca de
chave e/ou 429 pode seguir mandando requisição sem header enquanto o registro de credencial está
impecável. (Aprendido na marra: acusei `failure_reason` do pool e a limpeza não era necessária —
a sessão era a variável.)

Discriminador de 1 minuto, antes de qualquer intervenção em credencial: `/new` na conversa afetada
+ mensagem comum + `/model` para confirmar que a sessão nova roda **o mesmo** modelo/provider que
falhava. Respondeu o mesmo modelo = era estado da sessão; a credencial estava sã o tempo todo.

Só depois disso considere o registro — checklist em `references/credential-failure-diagnosis.md`.

### Como reportar diagnóstico de credencial

Log literal com timestamp e segredos mascarados; **provado** separado de **hipótese**; leitura pura
(sem alterar nada) quando o operador pedir "só olhe os logs"; resposta direta sim/não quando ele
pedir simples; e, para teste que ele faz no Telegram, passos numerados + como cada desfecho será
lido, um teste por vez, aguardando o retorno. Intervenção que altera estado só com ok explícito.

## Forense de turno: "parou sem entregar o artefato"

Um pedido que "está há 30 minutos sem responder" quase nunca está rodando: o `response ready` no
`gateway.log` mostra que o turno **terminou** e o que faltou foi o artefato. Antes de dizer que está
em andamento, leia `references/turn-forensics.md` — limites do turno em `gateway.log`/`agent.log`,
estado real em `state.db` (`session_turn_leases`, `async_delegations`, `delivery_obligations`),
prova do artefato por mtime, e a lista de chamarizes (ruído de rede do Telegram, 503 retentado,
deadline de uma ferramenta) que não são causa.

## References

- `references/turn-forensics.md` — diagnosticar turno de gateway parado/terminado-sem-entregar:
  logs, `state.db` em read-only, prova por mtime, chamarizes, formato do relatório.
- `references/credential-failure-diagnosis.md` — checklist de eliminação de `401`/"Provider
  authentication failed": classificar o 401, provar a credencial fora do gateway, ler `auth.json`,
  chamarizes que custam tempo e como reportar.
- `references/opencode-provider-setup.md` — OpenCode Zen/Go provider routes, `.env`
  keys, and the opt-in flow for Contributor models.
- `scripts/transcrever_audio_com_fallback.py` — transcreve um áudio (nota de voz que chegou sem
  transcrição) via Gemini iterando pela lista de modelos.
