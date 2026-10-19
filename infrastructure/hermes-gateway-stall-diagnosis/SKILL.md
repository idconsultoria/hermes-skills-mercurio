---
name: hermes-gateway-stall-diagnosis
description: "Use quando um agente Hermes trava ou o gateway reinicia."
category: infrastructure
type: Reference
timestamp: 2026-10-14T00:00:00Z
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [gateway, lease, turno, watchdog, state.db, forense, travamento]
    related_skills: [hermes-session-forensics, telegram-group-bot-diagnosis, messaging-platforms]
---

# Sessão travada, 'waiting for the other Hermes process', gateway reiniciou sozinho

Carregar quando: aparece o aviso de espera de lease de turno (`⏳ Still waiting for the other
Hermes process on this session (Ns)...`); o turno é recusado com `the user must resend`; o agente
fica mudo por minutos; ou o gateway cai e volta sozinho (exit 75).

Um turno longo (ou travado) segura o **lease da sessão**; toda mensagem nova naquele chat esbarra
nele. A apuração é **leitura** — a única escrita possível (restart) cai o multiplex inteiro.

## 1 · Os dois leases, e o que cada mensagem significa

| Sintoma | Mecanismo | Espera |
|---|---|---|
| `Another Hermes process is using this session…` → `Still waiting… (Ns)…` | lease **durável** no `state.db` do perfil (`session_turn_leases`) | até ~1800 s, avisando a cada 15 s; TTL de 300 s **renovado** pelo dono |
| `turn lease wait timed out after 5s … failing closed` + `'the user must resend'` | lease **asyncio em memória** do gateway (por session_id resolvido) | 5 s e desiste — é desenho, não bug |

Consequência prática: enquanto o turno dono está **lento mas vivo**, o lease nunca expira
(renovação), então esperar não resolve. Um turno recusado em 5 s **precisa da mensagem reenviada** —
diga isso ao operador.

## 2 · Ordem de apuração (do barato ao decisivo)

1. **Quem segura o que** — `state.db` do perfil, read-only:
   ```sql
   SELECT conversation_id, holder, acquired_at, expires_at FROM session_turn_leases;
   ```
   `holder` traz `pid=…:turn=…:platform=…`. **PID diferente do gateway atual prova processo**
   (irmão morto/vivo); o mesmo PID com gerações diferentes é o **próprio** gateway serializando
   dois turnos da mesma sessão. `expires_at` no futuro = alguém está renovando agora.
2. **Histórico de vida do gateway** — `$HERMES_HOME/logs/gateway-exit-diag.log`:
   `gateway.start` / `gateway.exit_clean` / `gateway.exit_nonzero` / `gateway.previous_unclean_exit`.
   Um `gateway.start` sem `exit_clean` anterior = morte suja. Confira qual PID serve o perfil em
   `gateway_state.json` (`writer_pid` por plataforma) e `gateway.pid`.
3. **Por que morreu** — `$HERMES_HOME/logs/errors.log`:
   - `gateway.shutdown_watchdog: … missed 3 consecutive liveness probes … exiting with code 75` →
     o event loop parou de responder e o supervisor reiniciou.
   - `Wedged-turn stack dump (task=…)` → stack exato do thread preso (diz se esperava lease, se
     estava no caminho de escrita do `state.db` ou numa chamada de modelo).
   - `Agent idle for Ns (timeout 1800s) … last_activity=initializing | iteration=0 | tool=none` →
     o turno **não estava trabalhando**: estava preso na admissão. O watchdog mata *esse* turno,
     que é o que esperava — não o dono do lease.
4. **O que o perfil viu** — `$HERMES_HOME/profiles/<perfil>/logs/gateway.log`: contenção
   (`turn lease contention … gen N waiting behind … gen M`), `Rejecting turn … the user must
   resend`, `/stop`, `Cancelled task … did not exit within 5s; unblocking dispatch`, e
   `Pruned N stale active session lease(s)` (faxina no boot).
5. **Contexto que explica o lease preso** — `profiles/<perfil>/logs/agent.log`: tamanho do turno
   (`API call #N`, tokens de entrada), duração das tools, `session turn lease wait aborted by
   interrupt`. Turno de 50+ chamadas, contexto de ~200 k tokens e tools de minutos explica uma hora
   de lease.
6. **Antes de culpar recurso, meça** — `ls /proc/<pid>/fd | wc -l`, um `os.fstat` cronometrado
   sobre esses FDs, `hermes doctor` e o `gateway_state.json`. Só afirme estouro de FD/pool com
   número.
7. **Atribua o PID à instalação** antes de falar em "outro processo":
   `tr '\0' '\n' < /proc/<pid>/environ | grep HERMES_HOME`. Duas instalações Hermes com
   `HERMES_HOME` distintos (ex.: a rama com `profiles/` vs `~/.hermes`) coexistem na mesma máquina
   e **não** compartilham lease.

## 3 · Como responder

- **Veredito na primeira frase**, e desfaça o engano mais provável: "outro processo" pode ser o
  **mesmo** processo (turno anterior) — só vira literal quando existe um PID irmão vivo ou
  recém-reiniciado segurando a linha.
- **Explique por imagem + encadeamento, não por lista de logs** (pedido explícito do Gustavo para
  explicações didáticas): uma analogia concreta (ex.: caderno da conversa + bastão de revezamento =
  sessão + lease), religando cada termo técnico à imagem; depois **o que aconteceu, em ordem
  numerada**; depois o que foi verificado no estado atual; e só no fim as opções de conserto.
  "Sem perder profundidade" = mantém mecanismo, causa raiz e evidência e simplifica apenas o
  vocabulário.
- **Separe o desenho do defeito.** Recusa em 5 s com "reenvie" é comportamento projetado; o defeito
  costuma estar no tempo da espera e no que o watchdog mata.
- **Feche com opções e gate**: nunca reiniciar o gateway por conta própria (derruba todas as
  plataformas e perfis por ~30 s). Ofereça as opções e espere o ok.

## 4 · Armadilhas

- **Concluir "dois processos" pelo texto do aviso.** O texto é genérico; só o `holder` com PID
  declarado (ou um PID presente em `/proc`) prova processo distinto.
- **Esquecer que o lease é durável.** Reiniciar o gateway **não** libera a linha no `state.db`; ela
  sobrevive até `expires_at` (ou até o reclaim). No restart, a faxina de rotas órfãs aparece no log
  (`Pruned N stale active session lease(s)`) — não confundir com o lease de turno.
- **Culpar PID morto que não é reconhecido.** O reclaim de lease expirado/morto acontece no
  `try_acquire`; sob proot/namespace remapeado o PID antigo pode não ser lido como morto e a linha
  fica até o TTL vencer. Verifique `expires_at` em vez de supor.
- **Ler o watchdog de inatividade como "agente travado no trabalho".** `last_activity=initializing |
  iteration=0 | tool=none` significa turno preso **antes** de começar — o oposto de um turno pesado
  em execução.
- **Buscar causa de entrega quando a causa é serialização.** Entrega/allowlist/gatilho é outra
  classe (`telegram-group-bot-diagnosis`); aqui a mensagem **chegou** e foi serializada.
- **Achar que o sintoma é exclusivo de Telegram.** O lease é por sessão resolvida — qualquer
  plataforma (DM, grupo, CLI) reproduz.

## 5 · Acesso e escrita

Ler `state.db`, `logs/`, `gateway_state.json` e `config.yaml` de qualquer perfil faz parte da
apuração. **Escrever** (reiniciar gateway, podar linhas de lease, mexer em config de perfil alheio)
exige ok explícito do dono do perfil, e vale a mesma regra de backup + leitura de volta.

## References

- `references/turn-lease-internals.md` — constantes, caminhos de código, esquema de
  `session_turn_leases`, semântica de renovação/reclaim, tabela de assinaturas de log e receita de
  medição de FDs.
