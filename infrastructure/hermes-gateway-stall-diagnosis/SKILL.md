---
name: hermes-gateway-stall-diagnosis
description: "Diagnosticar agente travado, gateway reiniciado, casa multi-perfil.

Carregue esta skill quando um agente trava, o gateway reinicia sozinho, turnos ficam presos no lease, ou a casa multi-perfil precisa de config/idioma em lote. Cobre forense de state.db, watchdog, diagnóstico de stall e recuperação de update falho."
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
fica mudo por minutos; ou o gateway cai e volta sozinho (exit 75); ou **todos** os chats do
perfil emudecem de uma vez, em especial logo depois de uma atualização; ou é preciso aplicar
config/idioma em **todos** os perfis de uma casa multiplex (então vá direto a
`references/casa-multi-perfil-ops.md`).

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

**"O agente X está trabalhando agora?" — sonda de três leituras.** Não infira pelo silêncio:

1. `gateway_state.json` → `active_agents` (0 = nenhum turno em curso) e `active_work`; `gateway_state`
   diz se o serviço está `running`/`starting`.
   `state.db` do perfil, em `mode=ro`: última atividade por sessão (ordene pela coluna de tempo que
   existir — rode `PRAGMA table_info(<tabela>)` antes; o nome não é `session_id`). Guarde título e hora.
3. `profiles/<perfil>/logs/agent.log` (tail): último evento carimbado; `Reconnect <plataforma> … next
   retry` ou `no adapter yet` significam **inacessível**, não ocioso.

Responda a hora convertida para BRT e separe os dois veredictos: "não está trabalhando desde HH:MM" e
"está alcançável / fora do ar". Quando o veredicto for fora do ar, o resto da apuração é a seção 5.

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
- **Diagnosticar lease quando o sintoma é o processo.** Um chat esperando lease continua recebendo
  e respondendo outros chats; se *todas* as plataformas do perfil calam juntas, o processo morreu e
  a apuração é outra (seção 5), não lease.
- **Aceitar "voltei a responder" como conserto.** Depois de um restart o perfil reconecta enquanto o
  update segue **falho** (código novo sobre venv velho). Declare o estado real: processo vivo e
  instalação íntegra são duas verificações distintas.
- **Tratar `Failed to load plugin … did not return an extension module` como plugin quebrado.** É
  ABI: módulo compilado de outra versão de CPython dentro do processo. A prova é
  `readlink -f /proc/<pid>/exe` contra os caminhos em `/proc/<pid>/maps`; testar o import no
  ambiente isolado não substitui essa leitura.
- **Ler chave i18n crua (`gateway.status.*`, `cli.*`) como tradução faltando.** É catálogo ausente no
  caminho em que o processo roda (`_locales_dir()` inexistente → `t()` devolve a chave). Compare o
  caminho resolvido com o diretório real antes de mexer em idioma ou em arquivo de tradução.
- **Editar `config.yaml` de perfis com o gateway no ar.** Cada gravação dispara
  `[MULTIPLEX] Re-scanned profile '<p>' after config/.env change (0 adapter(s) connected)` e o adapter
  não volta sozinho. Agrupe todas as mudanças e faça **um** restart, conferindo
  `✓ <plataforma> connected (profile: <p>)` até N/N — procedimento em
  `references/casa-multi-perfil-ops.md`.
- **Rodar o CLI/interpretador da instalação investigada com o ambiente da sessão.** `PYTHONPATH` e
  cwd herdados fazem importar `agent`/`hermes_cli` da instalação **de quem executa** — resultado
  falso (`ModuleNotFoundError` de dependência, `_locales_dir()` da árvore errada). Passe env mínimo,
  `cwd=<geração>/workspace` e `HERMES_HOME` do home alvo.
- **Provar variável de ambiente pelo `/proc` do supervisor.** `/proc/<pid>/environ` é o ambiente do
  **exec**: `export` feito depois pelo script não aparece nele para o supervisor, só nos filhos. Leia
  o environ do PID do gateway.
- **Anunciar regressão de ABI pelo primeiro PID que aparece após um `kill`.** O processo efêmero do
  caminho de parada também responde ao `pgrep`. Confirme `readlink -f /proc/<pid>/exe`, o PPID (deve
  ser o supervisor) e a hora de início antes de dizer que voltou ao interpretador antigo.
- **Confiar no "agora" do contexto da conversa.** Turnos consecutivos da mesma sessão podem estar a
  dias de distância; confirme a hora com `date` e com um header HTTP `Date` antes de dizer "parou há
  N horas".

## 5 · Todos os chats emudecem: update interrompido

`hermes update` é a primeira suspeita quando o silêncio é do perfil inteiro e coincide com uma
atualização. O encadeamento que produz o mutismo tem quatro elos, e cada um deixa assinatura:

1. **O update derruba os serviços do fleet** — o turno em curso morre no meio
   (`[Background process … exited (exit code 143, SIGTERM)]`, `Stream ended with no finish_reason`).
2. **A sincronização de dependências falha** — `update_receipts/*.json` com `"outcome": "failed"` e
   passo `dependency-sync` com `InstallError: venv: uv sync exited 1`. Quando a causa é build de
   extensão nativa faltando header de sistema, a saída é instalar o pacote do sistema e refazer o
   sync — **não** existe "venv irrecuperável".
3. **O gateway morre de novo** — `gateway-exit-diag.log`/`errors.log` com `SystemExit: 2` vindo de
   `resolve_uv() → stop_for_relaunch()`: quando o boot tenta instalar dependência lazy de uma
   plataforma ausente, o updater antigo pede relançamento e derruba o processo que está subindo.
4. **Boot lento e sequencial** — o gateway novo reconecta **perfil por perfil** (~15 s cada), com
   `startup exceeded 300s` e lease de migração do `state.db` sendo honrado. Não é loop: é fila.

Ordem de leitura (barato → decisivo):

1. `logs/update_receipts/latest.json` (e o `post_swap_*.json`) — `outcome`, passo que falhou, `plan.runtimes`.
2. `profiles/<perfil>/logs/update.log` e `~/.hermes/update-*.log` — onde o pull parou.
3. `gateway_state.json` — `gateway_state` (`starting` vs `running`), `code_sha`, `active_agents`.
4. `logs/gateway.log` — conte `✓ <plataforma> connected (profile: <perfil>)`: é o relógio da volta.
5. `logs/gateway-exit-diag.log` — `"tag": "gateway.start"` de hoje (quantos restarts) e o traceback
   imediatamente antes.

**Variante que engana:** o update pode terminar com `outcome: ok` e o fleet seguir mudo porque o
**processo** ficou no interpretador antigo carregando `.so` do ambiente novo — todo plugin de
plataforma falha ao carregar (`initialization of speedups / _audioop did not return an extension
module`) e o `gateway_state` continua `running`. Nesse caso reiniciar o gateway não basta: o script
de supervisão é que precisa resolver o ambiente **selecionado** em `installs/<key>/facts.json`.
Receita completa (prova por `/proc/<pid>/maps`, correção do supervisor, ordem do restart, padrões de
`pgrep` a ajustar) em `references/failed-update-recovery.md`, seção final.

**Segunda variante silenciosa: recurso fora da cópia.** O workspace por geração recebe membros de
pacote, não a árvore inteira — `locales/`, `skills/`, `ui-tui/` ficam de fora. Quando o código
resolve o recurso por `<repo-root>/<dir>`, ele desaparece sem erro: em i18n, `t()` passa a devolver a
própria chave e o usuário vê `gateway.status.session_id` cru nas respostas. A prova é
`_locales_dir().is_dir()` + uma chamada `t()` no interpretador **selecionado**; contorno é exportar
`HERMES_BUNDLED_LOCALES` no supervisor. Detalhe na mesma referência, seção "Dados que ficam fora da
cópia".

Para acompanhar esse estado sem repetir a leitura à mão, rode
`scripts/gateway-update-state-probe.sh [HERMES_HOME]`: saída determinística (`pending`, `attempts`,
interpretador do gateway, libs do venv legado mapeadas, falhas de ABI do boot atual, catálogo i18n
alcançável) — própria para cron em modo monitor, onde só a mudança acorda o agente.

O detalhamento (provar código novo sobre venv velho, patches locais no stash, resíduos e ordem de
restauração) está em `references/failed-update-recovery.md`.

Quando o perfil volta: o adapter sobe com `drop_pending_on_cold_boot: true`, então **as mensagens
enviadas durante a queda foram descartadas** — peça o reenvio explicitamente.

Nunca disparar `hermes update` de dentro de um turno do próprio gateway: o comando mata o processo
que serve o turno (o agente derruba a si mesmo). Delegue a um shell externo ou aceite a interrupção
combinada antes.

## 6 · Acesso e escrita

Ler `state.db`, `logs/`, `gateway_state.json` e `config.yaml` de qualquer perfil faz parte da
apuração. **Escrever** (reiniciar gateway, podar linhas de lease, mexer em config de perfil alheio)
exige ok explícito do dono do perfil, e vale a mesma regra de backup + leitura de volta.

## References

- `references/turn-lease-internals.md` — constantes, caminhos de código, esquema de
  `session_turn_leases`, semântica de renovação/reclaim, tabela de assinaturas de log e receita de
  medição de FDs.
- `references/failed-update-recovery.md` — update interrompido: mapa dos arquivos de recibo, receita
  read-only para provar código novo × venv velho, conferência dos patches locais que ficaram no
  `git stash`, resíduos (lock de update e lease órfão de turno morto) e a ordem de restauração sob ok
  do dono. Inclui a variante "update ok, processo no interpretador errado": gerações de ambiente em
  `installs/<key>/environments/`, correção do launcher/supervisor, ordem do restart sob runit e a
  verificação de volta por perfil; e a variante "recurso fora da cópia" (`locales/` ausente → chaves
  i18n cruas, contorno por `HERMES_BUNDLED_LOCALES`).
- `scripts/gateway-update-state-probe.sh` — foto determinística do estado (marker do update, `attempts`,
  interpretador do gateway, libs do venv legado, falhas de ABI do boot, catálogo i18n) para uso como
  fonte de cron em modo monitor.
- `references/casa-multi-perfil-ops.md` — operar a casa inteira num gateway multiplex: config por
  perfil via CLI, regra do restart único (editar config derruba adapter), ambiente saneado para
  sondar o runtime alvo, limites do `/proc` como evidência e a receita de instalar um idioma em todos
  os perfis com verificação de paridade.
- `scripts/i18n-catalog-parity.py <locales-dir> [lang]` — compara catálogo traduzido com o `en`:
  chaves faltando, chaves sobrando e placeholders divergentes (sai com 1 quando há defeito).
