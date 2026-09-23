---
name: stack2-mesh-failback
description: "Use ao mexer no failover/failback da Stack 2 (mesh)."
category: infrastructure
type: Runbook
version: "1.0.0"
timestamp: 2026-09-18T00:00:00Z
metadata:
  hermes:
    tags: [mesh, failover, failback, litestream, minio, termux, oracle, stack2]
    related_skills:
      - infra-mesh-distribuida
      - hermes-cron-script-dispatch
---

# Stack 2 (Hermes + Mercúrio) — failover/failback sem loop e sem perda

## Quando usar

Qualquer intervenção no supervisor de HA da Stack 2 (`/opt/mesh/stack2_supervisor.py` na
Oracle), no switch `~/mesh/STACK2_ACTIVE` (Redmagic) ou na replicação litestream → S3
(MinIO). Sintoma clássico: "supervisor em loop tentando concluir o failback".

## Arquitetura em uma linha

Oracle = árbitro único (systemd `stack2-supervisor`, estados NORMAL → FAILOVER →
FAILBACK). Redmagic = PRIMARY normal; a Oracle roda o SURVIVAL (`hermes_migration`) +
replicador litestream só durante FAILOVER. S3/MinIO (`100.104.121.28:9000`, bucket
`litestream`) é a fonte de verdade dos `state.db` entre os nós. `run_forever.sh` (runit,
loop 20 s) é o supervisor do nó Redmagic.

## Regras que evitaram produção quebrada

1. **Timeout de cópia tem que ser proporcional ao tamanho do arquivo.**
   Teto fixo (`scp ... timeout=300`) + `state.db` de 2,49 GiB num link de ~4 MB/s =
   `subprocess.TimeoutExpired` não tratado → processo morre → `Restart=always`
   reergue → ciclo infinito de failback (28 reinícios, ~38 ciclos, 3h44 sem concluir).
   Piso de 1,5 MB/s + folga de 120 s, teto de 2 h. **Nunca deixar exceção de subprocess
   subir até o módulo de um supervisor com Restart=always.**
2. **Nunca rebaixar dado no handoff.** Antes de sobrescrever um `state.db`, comparar
   watermark (`select count(*), max(rowid) from messages`) no destino e abortar se o
   destino estiver à frente. Num failback após failover longo, o nó que serviu mais
   tempo tem mais história — o snapshot é o mais VELHO. Sem essa guarda o failback
   apaga horas de sessões.
3. **Quiescência só quando há o que transferir.** Sobrescrever DB aberto por gateway
   vivo deixa WAL/SHM sujos e corrompe. Fazer fence (`rm ~/mesh/STACK2_ACTIVE`) +
   `gw_down.sh` (só `hermes gateway stop --all`, regra sagrada) antes do envio — e
   **não** quiescer quando o probe conclui que nada mudou (senão o failback vira
   downtime de 10 min por nada).
4. **Lista de perfis NUNCA fixa.** Todo laço (replicação, adopt, restore, listagem S3)
   descobre por glob/consulta: `_list_s3_replicas()` via `mc ls`, `profiles/*/state.db`,
   `served_profiles` do multiplex. Perfis criados depois da HA ficam sem réplica → o
   failover restaura vazio/velho.
5. **Config do litestream: gerar onde o arquivo vive.** O `/etc/litestream.yml` do
   Redmagic está no `/etc` do **proot**, não no do Termux. Comparar md5 no `/etc` do
   Termux dá "vazio == vazio" → "config não mudou" → o litestream fica preso na config
   do dia do setup (4 dbs) enquanto os perfis crescem para 11.
6. **`proot-distro` não roda dentro de proot.** Scripts que fazem
   `proot-distro login ubuntu -- ...` só funcionam no Termux (é o caso do supervisor,
   que entra por SSH). Testar sempre pelo caminho SSH (`sudo ssh termux-redmagic ...`),
   nunca de dentro do proot.
7. **Multiplex: perfil servido pelo gateway default não precisa de processo próprio.**
   `gateway_state.json` do default tem `served_profiles` (ex.: `[default, jupiter]`).
   Lançar gateway separado aborta com double-bind de bot e gasta um proot login por
   ciclo. Perfis servidos contam como UP na saúde.
8. **Perfil real = `config.yaml` + `state.db`.** Em `data/profiles/` convivem cópias
   legadas de subpastas do próprio Hermes (`logs`, `cron`, `hooks`, `sessions`,
   `skills`, `memories`, `audio_cache`, `image_cache`, `pairing`) que têm `state.db`
   vazio (0,2 MiB). Filtrar por `config.yaml` evita "hermes -p logs gateway start".
9. **Saúde: script em disco, não base64/quoting aninhado por SSH.** O detalhe antigo
   (base64 no supervisor) só enxergava os perfis do dia do setup ("3/3") e lia o
   Mercúrio por comando com aspas aninhadas que quebrava → alerta "Mercurio:DOWN" com
   11 gateways no ar. Usar `~/scripts/gateway_health.sh` (e `mercurio-gateway-status`,
   `mercurio-profiles-to-launch`, `stack2-litestream-refresh` no proot).
10. **`ssh` aninhado come o stdin do script (`bash -s`).** Rodar script remoto que
    chama outro ssh: usar `ssh -n` ou redirecionar `< /dev/null` no interno, senão o
    script é truncado no meio.
11. **`pkill -f`/`pgrep -f` casa o próprio shell** (a cmdline contém o padrão). Usar
    bracket (`[l]itestream`) ou `ps | grep "[r]un_forever.sh"` — já rendeu kill no
    próprio terminal.
12. **Guarda de papel no script só vale se a chamada acontecer no momento certo.**
    O `stack2-rcopy-reverse` (devolve arquivos de trabalho do survival ao Redmagic)
    exigia `role=PRIMARY=redmagic`, mas era chamado de dentro do delta-sync, quando o
    role ainda era `oracle->redmagic draining` → SKIP em 100% das execuções (29/08,
    30/08, 18/09): nada voltava. Chamar DEPOIS de `set_role("redmagic")` e antes do
    fence-off; falha ali não deve abortar o failback (os `state.db` já foram).
13. **Devolução de arquivos em modo `safe` (`--update`, sem `--delete`).** Se o
    Redmagic voltou a servir sozinho (net_guard) enquanto a Oracle ainda achava que
    estava em failover, o Redmagic tem arquivo MAIS NOVO que o mirror — `--delete`
    apagaria trabalho recente. Mesmo critério de "nunca rebaixar" aplicado aos DBs.
    Usar `dryrun` antes quando o escopo/exclusões mudarem; medir com `--stats`
    (`total size` × `sent` mostra se a varredura está fazendo trabalho inútil).
14. **Excluir árvores vendorizadas do sync de arquivos (nos DOIS sentidos).**
    `hermes-agent/`, `node/`, `node_modules/`, `.cargo/`, `.npm/`, `lsp/`, `venvs/`,
    `tmp/`, `whatsapp/media/` e backups de sessão antigos inflam a varredura sem trazer
    informação nova: o mirror do survival estava com 333 k arquivos / 16 GB e a rodada
    horária levava ~2m49s caminhando só isso (medido: caiu para ~30 s / 84 k arquivos com
    as exclusões). Manter o que o failover usa: `skills/`, `scripts/`, `cron/`, `casos/`,
    `work/`, `deliverables/`, `context-kb/`, configs/`.env`, `memories/` e a sessão VIVA do
    WhatsApp (`whatsapp/session`, `history*`, `self_chat_ids.json`). Com `--delete` +
    `--exclude`, o que saiu do escopo fica PRESERVADO no destino (não é apagado).
    Log com `-v` de rsync em árvore grande vira ~1 GB: usar `--stats` (resumo) + rodízio.
    Em caminho com `--delete`, sempre `--max-delete=<N>` como trava contra varredura total
    se a origem vier vazia/inalcançável.

## Procedimento (failback travado)

1. Ler `/var/log/stack2-supervisor.log`, `journalctl -u stack2-supervisor`, contador de
   reinícios e o `Restart=always`. Achar a linha de crash (arquivo + timeout).
2. Medir o payload: tamanho do `state.db` (local e remoto) e a taxa real do link
   (`/proc/net/dev` na interface tailscale, amostrado). Fazer a conta tempo × timeout.
3. Comparar watermarks dos dois lados — decide se o failback pode transferir ou só
   registrar (nunca rebaixar).
4. Corrigir o código com backup datado (`stack2_supervisor.py.bak-<ts>`), `py_compile`,
   `systemctl restart`, e acompanhar UM ciclo completo até `phase=NORMAL`.
5. Só depois cuidar de cobertura (replicação de todos os perfis) — assim o loop para de
   gerar ruído durante a intervenção.

## Higiene de `state.db` (causa de fundo)

`state.db` do perfil default já chegou a **2,49 GiB** (`messages` 647 MiB em 234 k
linhas + dois FTS5 espelhando conteúdo: `messages_fts_*` ~538 MiB e
`messages_fts_trigram_*` ~1,3 GiB). `VACUUM` não resolve (freelist ~0): é dado real.
Um DB desse tamanho em nó móvel que sincroniza por 4G é a causa de fundo do handoff
caro. Decidir com o dono: purgar sessões antigas por corte de data, ou desativar/rotar
um dos índices FTS — nunca apagar histórico por conta própria.

## Verificação pós-intervenção (checklist)

- `phase=NORMAL`, `NRestarts=0`, `stack2_role=PRIMARY=redmagic`, `dash_target` no nó ativo.
- `mc ls m/litestream/ | wc -l` == número de perfis (Hermes + Mercúrio).
- `tail /var/log/litestream.log` sem `read header: EOF` e com `wal segment written` de
  TODOS os dbs (inclusive os novos).
- Geração nova por replica: `mc ls m/litestream/<replica>/generations/` com id recente.
- `gateway_health.sh` batendo com a realidade (nativos + multiplex do Mercúrio).
- Dashboard público `:9119` respondendo (segue `dash_target`).
- Um único `run_forever.sh` rodando (`runsv` repõe; não pode sobrar órfão).
- `stack2-rcopy-reverse safe` terminando com `done ... rc=0/0` (e NUNCA com `SKIP`)
  quando o role é `PRIMARY=redmagic`.
