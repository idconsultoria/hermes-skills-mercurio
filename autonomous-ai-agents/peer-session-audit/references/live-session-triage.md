# Triage de sessao em andamento + causa real de runtime delegado

Recurso de `peer-session-audit`. Duas situacoes: a sessao **ainda roda** e o dono quer um veredito
agora; e o agente esta esperando um **runtime externo** (OpenDesign, Codex, Claude Code, qualquer
servico com fila) cujo status resumido nomeia o sintoma, nao a causa.

## 1. As tres medidas que decidem o veredito

Selecione a sessao por `chat_id` + `ended_at IS NULL`. O `session_id` ordena por criacao, nao por
atividade: uma sessao antiga pode ser a ativa.

```bash
P=/opt/mercurio-data/profiles/<perfil>/state.db
sqlite3 "$P" "SELECT id, chat_type, display_name, datetime(started_at,'unixepoch'),
                     datetime(COALESCE(ended_at,0),'unixepoch'), end_reason, message_count,
                     tool_call_count FROM sessions ORDER BY started_at DESC LIMIT 12;"
```

**a) O turno avanca?** `max(timestamp)` de `messages` vs `now`, medido mais de uma vez, com
intervalos de minutos. Um `sleep 400` seguido de nova mensagem e progresso; um `sleep 400` sem
retorno algum e o agente esperando por algo que nao vem.

**b) Houve entrega?** Duas contagens:

```bash
sqlite3 "$P" "SELECT count(*) FROM delivery_obligations WHERE chat_id='<chat>';"
sqlite3 "$P" "SELECT count(*) FROM messages WHERE session_id='<sid>' AND role='assistant'
               AND content IS NOT NULL AND content!=''
               AND (tool_calls IS NULL OR tool_calls IN ('','[]'));"
```

Zero com turno longo e **defeito de report**, independente do trabalho interno. Some `group_concat`
de `tool_name` por sessao para ver o mix: `terminal(sleep N)` repetido contra poucas tool calls
substantivas e o loop de espera.

**c) Duracao do turno:**

```bash
sqlite3 "$P" "SELECT acquired_at, expires_at FROM session_turn_leases WHERE conversation_id='<sid>';"
```

`expires_at - now` e o prazo de vida do lease; `now - acquired_at` a idade do turno.

## 2. Subtindo do sintoma do agente para a causa do runtime

O status que o agente le ("timeout", "empty_output", "stalled") descreve **como o run morreu**, nao
**por que**. Antes de culpar container, host ou provedor, leia o event log do proprio runtime.
O caminho depende de onde o runtime roda; SSH direto quando ele esta em outro no:

```bash
# leitura generica dos eventos de um run
docker exec <container> python3 -c "
import json
for l in open('/app/.od/runs/<runId>/events.jsonl'):
    e=json.loads(l); d=e.get('data') or {}
    print(e.get('id'), e.get('event'), d.get('type',''), json.dumps(d,ensure_ascii=False)[:300])
"
```

O que procurar, em ordem:

1. **A sequencia de tool calls** (`tool_use`/`tool_result`). Muitas `read` e zero `write` antes da
   morte = o agente nunca chegou a produzir; um arquivo grande por ler e a causa, nao a engine.
2. **Tokens por passo** (evento `usage`): `input`, `output`, `thought`, `cached_read`.
3. **O evento `error` cru** — traz o detalhe que o resumo esconde: tempo de silencio ate o kill,
   se stdout chegou, tamanho do maior tool result.
4. **Infra** (`docker inspect` health, `OOMKilled`, `RestartCount`, `docker stats`, disco). Container
   `healthy` convive com run que falha: o run pode morrer com o servico inteiro sao.

## 3. Assinatura thought/output: o diagnostico que separa modelo de provedor

A tabela de tokens por run e o que fecha o diagnostico. O padrao que importa:

| `output` | `thought` | leitura |
|---|---|---|
| alto | qualquer | o modelo produziu; falha, se houver, e de execucao |
| ~centenas | alto (dezenas de milhares) | **loop de planejamento**: queimou raciocinio e nao escreveu nada |
| zero | alto | resposta vazia do provedor apos pensar |
| zero | zero | travou antes do primeiro token |

O caso do meio e o que se repete quando o escopo do run e grande demais (um HTML de 20k+ caracteres
com contexto herdado de varias execucoes). **Prescricao: reduzir o escopo do run, nao repetir.** O
mesmo trabalho em unidade por unidade, com entrada de poucos milhares de tokens, fecha com
`output` alto e `thought` curto — e o mesmo modelo, o mesmo provedor, a mesma maquina.

Ou seja: `empty_output` com `thought` alto e `output` ~0 nao e "provedor instavel". Repetir o run
identico reproduz a falha; repetir com escopo menor nao.

## 4. Quando o status e ambiguo

`bottleneckPhase: queued` com `queueDurationMs` alto e `agentExecutionDurationMs` baixo e o retrato
normal de fila — a espera e real e o tempo de relogio diz pouco. So desconfie do relogio quando ele
passa do razoavel **e** o `bottleneckPhase` aponta outra fase. Verifique sempre os dois juntos: fila
real e loop de planejamento produzem a mesma aparencia de "demora" para quem so olha o relogio.

## 5. Config que remove a classe de falha

- **Whitelist de um so modelo** no `opencode.json` do runtime nao deixa o daemon cair para um
  alternativo quando o modelo trava; `failureAction: retry` fica sem para onde ir. Verificar
  `model`, `small_model` e `provider.whitelist` juntos — eles precisam concordar.
- **O watchdog de silencio** (tipicamente 600 s) nao distingue "pensando" de "travado". Um run
  bom pode passar 113 s ate o primeiro evento de modelo; um run morto emite nada por 600 s. Os
  dois recebem o mesmo rotulo, entao o rotulo sozinho nunca basta para o veredito.
