# Diagnóstico de falha de credencial (401 / "Provider authentication failed")

Checklist para quando o gateway devolve ao usuário *"Provider authentication failed. Check the
configured credentials"* — rótulo genérico que embrulha um `AuthenticationError [HTTP 401]` do
provider. Ordem: classificar → provar fora do gateway → restart limpo → ler o registro → eliminar
chamarizes. Não pule para "a chave está errada".

## 1. Classificar o 401 antes de tocar em qualquer coisa

A linha do log traz o suficiente:

```
WARNING agent.conversation_loop: API call failed (attempt 1/3) error_type=AuthenticationError
  thread=hermes-gateway_0:<id> provider=<p> base_url=<url> model=<m>
   📝 Error: HTTP 401: Missing API key.
   📋 Details: {'type': 'AuthError', 'message': 'Missing API key.'}
```

| Corpo do erro | Significado |
|---|---|
| `{'type':'AuthError','message':'Missing API key.'}` | A requisição saiu **sem** credencial. Não é chave morta. |
| `Model <x> is not supported` | Chegou ao provider: autenticou, mas o modelo não existe naquela rota. |
| `GoUsageLimitError` / `Monthly usage limit reached` | Chave válida, quota da rota estourada. |
| `requires explicit opt in` | Consentimento do modelo Contributor, pendente no workspace do provider. |

Controle que separa "sem chave" de "chave rejeitada": repetir o POST **sem** header
`Authorization` na mesma rota. Se o corpo voltar idêntico ao do erro, nenhuma chave está sendo
entregue — e aí o campo `Details` do log confirma.

Marcador de falha recente, sem garimpar o log: `$HERMES_HOME/sessions/request_dump_<sessão>_<ts>.json`
(o mtime é o momento da falha; o payload exato está dentro). **Turno bem-sucedido não gera linha**
`provider=...` no log — só falha gera; ausência de linha não é ausência de turno.

## 2. Provar a credencial fora do gateway

- **Direto na API** (com a chave): prova só que ela é válida no provider; não passa pelo Hermes.
- **Um processo novo do Hermes**: `hermes -z "responda somente: ok" --provider <p> -m <model>`.
  Se devolve texto, então env → provider → request estão sãos para esse provider/modelo.

Se o comando do Hermes funciona e o gateway falha, o defeito está **no processo/estado do
gateway** — não no valor da chave, no `.env`, nem na config. Diga isso explicitamente ao
operador nessa forma, porque a intuição dele será "a chave está errada".

## 3. Restart limpo — e o que a ausência de efeito prova

Reinicie o gateway do default pelo procedimento seguro (SIGTERM no PID exato, ver SKILL.md) e
peça UM teste ao operador no chat. Erro idêntico no processo novo elimina **memória de processo** —
nada mais. Não conclua "estado em disco": a **sessão viva** também sobrevive ao restart, e é a
causa mais provável quando a chave está comprovadamente boa.

A seguir, teste da sessão **antes** de mexer em credencial: `/new` na conversa afetada, uma
mensagem comum, e `/model` para ver se a sessão nova roda o mesmo modelo/provider. Respondeu com o
mesmo modelo → era estado da sessão; encerre o diagnóstico. Caso real neste ambiente: sessão aberta
01:41 atravessou a troca de chave e um 429, passou a mandar requisição sem chave; `/new` às 10:36
com o mesmo `deepseek-flash`/`opencode-go` voltou a funcionar.

## 4. Ler o registro de credenciais

`$HERMES_HOME/auth.json` → `credential_pool.<provider>.entries[]`. Campos que importam:
`source` (`env:<VAR>`), `secret_fingerprint` (sha256 do valor registrado — tem que bater com a
chave nova depois de uma troca), `base_url`, `last_status`, `request_count` e `failure_reason`
(resíduo).

- `entries` é **lista aninhada** — um dump que faça `.get` direto em cada entry quebra com
  `AttributeError: 'list' object has no attribute 'get'`. Recursa (listas e dicts) e mascare
  qualquer campo que contenha `secret`/`key`.
- `hermes auth reset <provider>` = *"Clear exhaustion status for all credentials for a
  provider"*: mexe em `last_status`, **não** em `failure_reason`. Responder *"Reset status on 0
  credentials"* significa "nada estava marcado como exausto" — não significa "credencial sã".
- O resíduo `failure_reason: rate_limit` sobrevive a restart e a `auth reset`, mas **não tem efeito
  comprovado**: no caso real o registro estava correto (fingerprint novo, `last_status: null`) e a
  requisição saía sem chave por estado da **sessão** (§3). Não intervenha no pool antes do teste de
  sessão nova. Se algum dia se provar necessário, tirar e re-adicionar a entrada
  (`hermes auth remove` / `hermes auth add`) — ação que altera estado: só com ok explícito do operador.

## 5. Chamarizes que já custaram tempo

- `agent.relay_runtime: Hermes Relay runtime initialization failed / No module named 'nemo_relay'`
  é crônico neste ambiente. Antes de tratá-lo como causa, procure o mesmo aviso em turnos
  **anteriores** do log onde a inferência funcionou. Co-ocorrência não é causalidade.
- **Multiplex / escopo de segredo fail-closed** só vale com `gateway.multiplex_profiles` ligado.
  Nenhuma linha "multiplex" no log do gateway = desligado, e com multiplex desligado a leitura de
  credencial vai direto ao `os.environ`. Não use essa pista para explicar um gateway por perfil.
- Um diretório de perfil sem `.env`/`config.yaml` próprio herda `$HERMES_HOME/.env`. Confirme
  **qual arquivo** o processo que falha lê antes de acusar valores.
- `api_key: ''` no `config.yaml` costuma pertencer ao bloco `auxiliary:` (visão e afins), não ao
  provider principal. E um provider embutido (ex.: `opencode-go`) pode **não ter** entrada em
  `providers:` e ainda assim resolver pelo env — ausência de entrada não é o defeito.
- Log de outro perfil é controle barato: as mesmas linhas `provider=<p>` sem nenhum
  `Missing API key` provam que a rota e a chave funcionam na máquina.
- `/proc/<pid>/environ` mostra só o ambiente do **exec** — o `.env` carregado pela aplicação em
  runtime nunca aparece ali. Ausência de `OPENCODE_*` nesse arquivo **não** é evidência de
  credencial faltando.

## 6. Como reportar (operador técnico, dono do host)

- Log **literal**: timestamp + linha exata, valores de segredo mascarados (`sk-xxxxx***`).
- Separe **provado** de **hipótese** em voz alta: *"o log não confirma isso — os horários batem,
  a prova não"*. Não apresente corroboração como causa.
- Leitura pura quando o operador pedir "não mexa em nada, só olhe os logs": só leituras (logs,
  `/proc`, `hermes config get`). Nada de reset, restart ou escrita.
- Pedido de "resposta simples" = responder a pergunta em sim/não + uma linha de porquê, **sem**
  nova investigação nem novas chamadas de ferramenta.
- Teste que depende do operador (mensagem no Telegram): passos **numerados** (o comando a enviar,
  a mensagem a enviar, o que ele reporta de volta) e como cada desfecho será lido — um teste por
  vez, e aguardar o retorno antes do próximo.
- Intervenção que altera estado (limpar entrada do pool, remover/re-adicionar credencial, mudar
  config) só depois de ok explícito.
