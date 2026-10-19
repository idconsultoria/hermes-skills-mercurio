# Lease de turno — internos que decidem o diagnóstico

## Módulos e constantes

- `agent/turn_facade_lease.py` — **lease durável** (cross-process), em `SessionDB`:
  - emite `⏳ Another Hermes process is using this session; waiting…` (primeiro aviso, <1 s) e
    `⏳ Still waiting for the other Hermes process on this session (Ns)...`;
  - `LEASE_TTL_SECONDS = 300` (validade), `LEASE_WAIT_SECONDS = 1800` (paciência);
  - `holder = f"pid={os.getpid()}:turn={relay_turn_id}:platform={platform}"`;
  - `refresh_tick()` renova sob posse — é por isso que o lease **não** expira enquanto o turno dono
    estiver lento mas vivo; se a renovação falha, o PRÓPRIO turno é interrompido
    (`Lost session turn lease while turn is active`).
- `gateway/turn_lease.py` — **lease asyncio em memória**, por `session_id` resolvido, "process-local,
  single-event-loop by design": `DEFAULT_LEASE_WAIT = 5.0` (fallback; a ponte é a env
  `HERMES_TURN_LEASE_TIMEOUT`). Timeout → `TurnLeaseTimeoutError` → **fail closed**: o turno não roda
  sem serialização (`refusing to run this turn UNSERIALIZED`). `rebind()` re-aliás o lease quando a
  sessão rotaciona (compressão) no meio do turno.
- `hermes_state_compression.py` — `acquire_session_turn_lease()` dona do laço de espera:
  `try_acquire_session_turn_lease()` (com `patience_s≈0.5`) → se falha, `on_wait(elapsed)` a cada
  ~15 s → repete. `try_acquire` roda o walk da linhagem + INSERT + reclaim dentro **de uma única
  transação de escrita**, via `_execute_write()`.
- Chave do lease = **raiz da linhagem** da conversa (`_session_turn_lease_key_on_conn`), não o id da
  sessão corrente: sessão rotacionada continua sob a mesma linha.

## Esquema

```sql
CREATE TABLE session_turn_leases (
    conversation_id TEXT PRIMARY KEY,   -- raiz da linhagem
    holder          TEXT NOT NULL,      -- pid=…:turn=…:platform=…
    acquired_at     REAL NOT NULL,
    expires_at      REAL NOT NULL       -- acquired/renovação + TTL
);
```

Reclaim (dentro do `try_acquire`): `expires_at <= now` **ou** o PID do holder considerado morto
**local** (`_compression_lock_holder_process_is_dead`). Em ambiente com PID remapeado
(proot/namespace) a segunda condição pode não disparar — a linha vive até o TTL.

## Onde a espera pode realmente travar

`_execute_write()` chama `_try_wal_checkpoint()` antes de escrever; o checkpoint faz
`hermes_state_lockguard.hold()`, que varre `/proc/self/fd` + `/dev/fd` e dá `os.fstat` em cada

```
descritor para achar os que apontam para `state.db`/`-shm`. Um stack preso em
acquire_session_turn_lease → _execute_write → _try_wal_checkpoint → lockguard → _own_fds_for →
os.fstat  significa: a espera não é do lease em si, é do CAMINHO DE ESCRITA do state.db.
```

Antes de chamar isso de estouro de recurso, meça:

```python
import os, time
pid = "<pid do gateway>"
d = f"/proc/{pid}/fd"
names = [n for n in os.listdir(d) if n.isdigit()]
t0 = time.time()
for n in names:
    try: os.fstat(int(n))
    except OSError: pass
print(len(names), "fds em", round(time.time()-t0, 2), "s")
```

Centenas de FDs = varredura de dezenas de ms: não é a causa. Milhares, ou dezenas de ms por FD em
I/O lento (armazenamento de telefone / proot), aí sim.

## Assinaturas de log → significado

| Linha | Leitura |
|---|---|
| `turn lease contention on session <id>: … gen N waiting behind … gen M, held Ns` | dois turnos da MESMA sessão no MESMO processo (o aviso cita o mapeamento de chaves) |
| `turn lease wait timed out after 5s … waiter gen N; holder gen M` | lease asyncio; turno recusado, usuário precisa reenviar |
| `Skipping stale agent promotion … generation N is no longer current` | `session_reset` invalidou a geração; o turno antigo não promove mais |
| `Cancelled task for <sessão> did not exit within 5s; unblocking dispatch` | `/stop` cancelou a tarefa, o dispatch seguiu e o lease **não** foi devolvido |
| `Agent idle for Ns (timeout 1800s) … last_activity=initializing \| iteration=0 \| tool=none` | turno preso na admissão; o watchdog mata o WAITER, não o dono |
| `Wedged-turn stack dump (task=…)` | stack por thread do turno preso |
| `session turn lease wait aborted by interrupt` | a espera terminou por interrupção, não por posse |
| `Gateway event loop missed 3 consecutive liveness probes; … exiting with code 75` | morte suja do gateway; supervisor reinicia |
| `Pruned N stale active session lease(s)` | faxina de rotas órfãs no boot (não é o lease de turno) |

## Coexistência de instalações

Cada `HERMES_HOME` tem seus próprios `profiles/`, `state.db` por perfil e `logs/`. Dois gateways de
instalações diferentes servindo bots distintos não competem por lease; o **mesmo** `HERMES_HOME` com
dois processos (irmão antigo ainda vivo após restart) compete. Atribua sempre o PID à instalação por
`/proc/<pid>/environ` antes de afirmar qual é o caso.
