# agy Print-Mode Review — invocação correta para reviews longos

> Validado em 14/08/2026 (projeto Zera/CFP IA, Onda 1 e Onda 2). Este arquivo substitui o
> comportamento antigo (`echo "n" | agy` / SSH simples) para **reviews longos de código**
> (onda inteira, múltiplos lotes). Para reviews curtos de design, o fluxo multi-turno do
> `design-review-loop.md` continua valendo — mas as flags abaixo também funcionam.

## Problema

Com `echo "n" | agy -p "..."` ou `ssh oracle-host 'cd ... && agy -p "..."'`, o agy
**aborta após o primeiro passo** em reviews longos:

- Saída típica: só `"I will start by listing the contents of the project directory..."` e sai (exit 0).
- Nada é escrito no `feedbacks.md` (arquivo fica com timestamp antigo).
- Causa: modo print sem `--dangerously-skip-permissions` trava/pede permissão no meio e o stdin
  fechado (EOF) mata o processo.

## Invocação correta (comprovada)

```bash
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
  /home/ubuntu/.local/bin/agy -p "$(cat prompts/agy-review-ondaN.md)" \
  --dangerously-skip-permissions --print-timeout 15m \
  > /tmp/agy-ondaN.log 2>&1; echo "EXIT: $?"; wc -c /tmp/agy-ondaN.log'
```

- `--dangerously-skip-permissions` — auto-aprova tool permissions (sem ele o agy para pedindo ok).
- `--print-timeout 15m` — 5m padrão é pouco para análise longa.
- Redirecionar para log; `wc -c` dá tamanho real (com o aborto antigo ficava ~135 bytes;
  com a invocação correta: 13–16KB para revisão de onda inteira).
- O log final contém o resumo e o veredito (`ACORDO: ... FINALIZADA`).

## Depois da revisão — sync de volta

O agy roda no **host Oracle** sobre o shared volume, mas:

1. **O host não tem credenciais GitHub** — `git push` falha com `could not read Username`.
   Não commitar no host. O agy escreve `feedbacks.md` **direto no shared volume**, então o
   container já vê a mudança (mesmo arquivo, volume montado). Só fazer `git add/commit/push`
   a partir do container Hermes.
2. **Ownership do `.git` muda** — o agy roda `sudo chown ubuntu` no `.git` do host; como é
   volume compartilhado, o container perde escrita (`index.lock: Permission denied`).
   Corrigir no host antes do próximo commit:
   ```bash
   ssh oracle-host 'sudo chown -R 10000:10000 /home/ubuntu/selfhost/shared/code/workstation/PROJETO/.git'
   ```
3. Se precisar trazer o patch sem volume (ex.: volume dessincronizado), usar
   `git format-patch -1 <sha> --stdout` no host → `git apply` no container — mas o
   `feedbacks.md` costuma dar conflito de contexto se o container estiver em commit
   diferente; preferir copiar o arquivo via volume.

## Pitfalls

| Sintoma | Causa | Fix |
|---|---|---|
| Log com ~135 bytes, agy sai no 1º passo | stdin fechado + permissão | `--dangerously-skip-permissions` |
| `fatal: could not read Username for https://github.com` no host | host sem credenciais | commit/push só no container |
| `index.lock: Permission denied` no container | agy chownou `.git` como ubuntu | `sudo chown -R 10000:10000 .git` no host |
| `git fetch` no host: `cannot open .git/FETCH_HEAD: Permission denied` | mesmo chown | idem acima |

## Nota: Pi best/cost em background

- `pi` em lotes grandes (Onda 1–4): rodar com `terminal(background=true)` + `notify_on_complete=true`.
  Foreground com timeout 600s estoura (Pi v4-flash leva 10–28 min por lote).
- Progresso: auditar JSONL com `pi-session-audit` (classify_progress) — não esperar stdout.
- Correções de feedback do agy: retomar a **MESMA sessão** do Pi que executou (`pi --session <path>`),
  nunca sessão nova (requisito do usuário).
