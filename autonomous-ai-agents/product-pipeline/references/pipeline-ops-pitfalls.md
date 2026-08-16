# Pipeline Ops — Pitfalls de orquestração multi-agente (host + container)

> Validade: 14/08/2026 (projeto Zera/CFP-IA, ondas 1–5). Compila as correções de workflow que o
> usuário explicitou ou que emergiram na execução das ondas. Leia antes de orquestrar Pi+agy num
> repo com shared volume.

## Shared volume: NUNCA `git reset --hard` (regra do usuário)

O shared volume é o MESMO diretório montado no host (`/home/ubuntu/selfhost/shared/...`) e no
container (`/opt/data/...`) — mudanças de um lado aparecem no outro. **Proibido rodar
`git reset --hard origin/main` no host "para sincronizar"** (usuário bloqueou em 14/08/2026):
- Desnecessário: o volume já reflete o estado do container (commits aparecem no host sozinhos).
- Perigoso: destrói trabalho não commitado de outros processos (ex.: o agy editando
  `feedbacks.md` ou um designer gerando assets) — `git status` do host é a fonte de verdade
  para saber se há mudanças pendentes.
- Padrão correto para rodar o agy no host: conferir `git log --oneline -1` (já está no commit
  certo) e simplesmente executar o prompt — sem tocar em nada do git do host.

## Permissão quebrada após agy rodar no host (pitfall recorrente)

O agy (Antigravity) roda no host como `ubuntu` e faz `chown -R ubuntu` em `.git` (e às vezes nas
pastas de app) → o container (hermes, UID 10000) perde escrita → `git add`/`write_file` falham com
`Permission denied` / `index.lock`. Correção (via host):
```bash
ssh oracle-host 'sudo chown -R 10000:10000 /home/ubuntu/selfhost/shared/code/workstation/<repo>/.git'
# se pastas de app também ficaram 1001: sudo chown -R 10000:10000 <repo>  (ou só frontend scripts .github)
```
Depois do chown, `git status`/`git add`/`write_file` voltam a funcionar no container. Se o Pi cost
parou com "permissão de arquivo" (pacote em staging/), corrigir o chown e aplicar o pacote
manualmente (copiar arquivos + npm install + marcar code-tasks) em vez de re-disparar o lote.

## Pi preso em loop: quando pegar o controle (regra do usuário)

Regra explícita do usuário (14/08/2026): *"Investigue se ele consegue resolver sozinho o problema.
Se não, pegue o controle, resolva, e depois passe de volta para ele."*

**Como classificar progresso vs loop** (auditar o JSONL da sessão):
- **Progresso:** ENTRIES cresce, timestamps avançam, comandos diferentes entre si, texto novo.
- **Loop:** comando bash idêntico repetido (ex.: mesmo `timeout 100 python ...`), JSONL estável por
  vários minutos, uptime da sessão >> esperado sem saída nova.
- Pausas legítimas existem (pytest/suíte completa: o JSONL não cresce até o resultado entrar) —
  não confundir; cruzar com `ps aux` do comando (se ainda roda, é pausa; se o comando acabou e o
  Pi não seguiu, é loop).

**Protocolo de intervenção:**
1. Kill do job em background (`process kill`).
2. Diagnosticar a causa real (ler o script/erro; reproduzir manualmente com timeout curto).
3. Corrigir (bug mecânico = 🟢 direto; decisão de design = 🔴 reportar).
4. Validar a correção com execução real.
5. Re-disparar o lote ou aplicar o pacote manualmente; devolver o controle ao fluxo.

## Pitfall: `proc.stdout.read()` em subprocess long-lived (deadlock)

Em scripts Python que sobem um servidor/subprocess e o healthcheck falha, **nunca usar
`proc.stdout.read()`** para imprimir o log — o subprocess continua vivo, o pipe nunca fecha e a
leitura bloqueia para sempre (foi o loop do load test em 14/08). Usar `readline()` best-effort +
`proc.terminate()` + `proc.wait(timeout=5)` antes de relançar.

## Pitfall: load test em SQLite = 1 VU só

Load tests com funil de escrita (register/login/consents/onboarding) contra SQLite travam com >1 VU
(lock single-writer serializa tudo; timeout estoura). Não é limitação do produto — é do driver de
teste. Carga real (50-100 VUs) exige PostgreSQL (ou staging real). Registrar baseline com 1 VU e
documentar a limitação.

## Padrão de validação de CI/CD (GitHub Actions)

- Falhas de CI nem sempre são o que parecem: "Lint falhou" no email pode ser teste de integração PG.
  Baixar o log do job real (`/actions/runs/<id>/jobs` → logs) antes de agir.
- **Postgres é estrito onde SQLite tolera:** `server_default=text("0")` numa coluna Boolean quebra
  o `alembic upgrade head` em PG com `DatatypeMismatchError` (SQLite aceita `0`/`1`). Usar
  `text("false")`/`text("true")` em Boolean. Testes locais em SQLite NÃO pegam isso — o CI é o gate.
- Ao estender a cadeia de migrations (0005→0007), atualizar TODAS as asserções de head/cadeia
  (testes SQLite E integração PG); o Pi cost costuma esquecer o de PG.
- CI verde após push → não deve chegar mais email de falha; conferir `actions/runs` para confirmar.
