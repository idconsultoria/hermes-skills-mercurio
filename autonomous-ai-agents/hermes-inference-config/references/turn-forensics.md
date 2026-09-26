# Forense de turno de gateway: "parou sem entregar o artefato"

Use quando o usuário disser que um pedido disparado no grupo/DM "está rodando faz 30 minutos",
"parou de responder" ou "prometeu e não entregou". A pergunta nunca é "está lento?" — é **em qual
dos três estados o turno está**: rodando de verdade, **terminado sem fazer**, ou **morto no meio
de uma ferramenta**. Responder sem distinguir os três é chutar.

Todo o procedimento é **leitura pura**. Nenhum restart, reset ou edição sem ok explícito.

## 1. Triagem de 60s — os limites do turno estão no log

Duas linhas delimitam o turno. Busque-as pelo `session_key` (`agent:<perfil>:<plataforma>:<chat>`):

```bash
P=/opt/mercurio-data/profiles/<perfil>
grep -E "inbound message|response ready" $P/logs/gateway.log | tail -12
```

| Evidência | Estado do turno |
|---|---|
| `response ready: ... session=<key> time=NNNs` **depois** do `inbound` | **TERMINOU.** `time=` é a duração real. Um `time=771.6s` com 30 min de silêncio significa que ela respondeu — e o que ela respondeu foi uma promessa. |
| `Suppressing normal final send ... (streamed=True ... content_delivered=True)` logo acima | O conteúdo **chegou** ao chat. O silêncio posterior é de outra natureza. |
| Só `inbound`, sem `response ready` | Ainda rodando **ou** morreu. Vá ao passo 2. |

Para saber **por que** parou, `agent.log` do mesmo perfil:

```bash
grep -F "<session_id>" $P/logs/agent.log | tail -30
```

- `Turn ended: reason=text_response(finish_reason=stop)` → **o modelo escolheu parar**. Não é
  travamento: é uma decisão. O conteúdo da última mensagem `assistant` diz o que ele jurou fazer.
- `reason=...` outro valor (`max_iterations`, erro de tool) muda o diagnóstico — leia a linha
  inteira, ela traz `api_calls=N/MAX`.
- `API call #N ... latency=NNs` mostra onde o tempo foi. `cache=99%` = contexto servido do cache.

## 2. Estado real no banco (o spy que separa "parou" de "entregando")

`state.db` é SQLite com WAL — **abra em read-only** para não disputar o lock com o gateway vivo:

```bash
cd /opt/mercurio-data/profiles/<perfil>
python3 -c "
import sqlite3
c=sqlite3.connect('file:state.db?mode=ro', uri=True)
for t in ('session_turn_leases','async_delegations','delivery_obligations'):
    cur=c.execute(f'select * from {t}')
    cols=[d[0] for d in cur.description]
    print(t, '->', [dict(zip(cols,r)) for r in cur.fetchall()][:5])
"
```

| Tabela | O que a linha residual prova |
|---|---|
| `session_turn_leases` **vazia** | Ninguém segura turno agora. Turno parado. |
| `session_turn_leases` com linha | O turno ainda está vivo — o holder pode até ser **outro** turno. |
| `async_delegations` com `state` fora de `completed`/`error` | Subagente em voo: o turno **está** produzindo, em background. |
| `async_delegations` com `delivery_state` ≠ `delivered` | O subagente **terminou** e o resumo não foi entregue — silêncio real, com trabalho já feito. |
| `delivery_obligations` com `state` ≠ `delivered` | A mensagem final nunca chegou ao chat. Esta é a causa legítima de "não responde no grupo". |
| `gateway_heartbeats` vazia | Nada: perfis multiplexados gravam heartbeat só no backend que os serve. Ausência **não** é prova de gateway fora. |

`conversation_generations` (contador por `session_key`) serve para provar que a sessão **rotacionou** —
se o número subiu, o trabalho do pedido anterior está em outra geração da sessão.

## 3. O artefato decide a pergunta

Afirmação de progresso ("está gerando o PDF") se prova ou se descarta por **mtime**, não por discurso:

```bash
find <workspace-do-perfil> -mmin -40 -type f -printf '%TH:%TM %10s %p\n' | sort -r | head -30
```

- **Nenhum arquivo novo** depois do `inbound` → o turno trackeou a existência do artefato mas
  nunca o escreveu. É a prova decisiva de "terminou na promessa".
- Arquivo existe → o trabalho está feito ou em curso; volte ao passo 2 para saber por que não
  chegou ao chat.
- Não ache no workspace só: um `find` amplo em `/tmp` e no `cache/` do perfil fecha o caso quando o
  agente escreveu fora da árvore óbvia.

## 4. Gateway multiplexado — o log certo é o do outro perfil

Num gateway com `multiplex_profiles`, cada perfil tem **seu próprio** `state.db`, `logs/` e
`sessions/`. Ler o `default` para investigar o turno de outro perfil só produz chronologia
inexistente. Cheque também se o perfil tem `.env`/`config.yaml` próprios (herda do default se não).

## 5. Chamarizes — coisas que parecem causa e não são

- **Ruído de rede do Telegram** (`ConnectTimeout`, "Sticky path ... failed", "transport recovered
  via <ip>") no `gateway.log`: é transporte de entrega, **independente** do turno. Só
  `response ready` / `Turn ended` decidem o estado. Não cite ruído de rede como causa de turno parado.
- **`agent.deadline: 'terminal.wait:LocalEnvironment' timed out`** = **uma** chamada de ferramenta
  abandonada. O turno costuma seguir depois dela.
- **503 do provider** é chamada retentada; ela explica **latência**, nunca um artefato faltando.
- **`MarkdownV2 edit failed, falling back to plain text`** = degradação do *preview*; a mensagem
  saiu. `Button-based approval send timed out — treating as possibly-delivered` = o prompt pode
  estar **armado esperando um toque humano**, não travado.
- **Reprodução de alternation de mensagens** (`Repaired N message-alternation violations`,
  `Re-anchored current_turn_user_idx`) é rotina de integridade do transcript, não erro do turno.

## 6. Como reportar (o formato que o dono aceita)

Três linhas, nessa ordem, e nenhuma além disso:

1. **Veredito em uma frase** — "não está em andamento, acabou" / "está rodando, mas não há
   artefato ainda" / "morreu em `<ferramenta>`".
2. **Evidência com origem** — `logs/gateway.log: response ready ... time=771.6s`,
   `state.db.session_turn_leases vazia`, `workspace sem arquivo novo`. Cite arquivo:linha.
3. **Causa acumulada** — só se a evidência sustentar; separe o que é **provado** do que é
   **inferido** ("a API deu 503 e o comando estourou 180s: isso explica a lentidão, não o artefato").

Feche com **o próximo passo concreto e reversível** (retomar a mesma sessão, `/retry`, ou executar
você mesmo) e peça o ok. Se o pedido for "você faz aí", execute — mas só com leitura do
`state.db` e dos logs, sem tocar no perfil do outro agente.
