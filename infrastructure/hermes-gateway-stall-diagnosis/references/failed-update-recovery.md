# Update interrompido — recuperação

Aprofundamento da seção 5 do SKILL.md. Tudo aqui é **leitura**; toda escrita (sync, restart, limpeza
de resíduo, `git stash apply`) é ação fora da rotina e espera ok do dono.

## Mapa dos arquivos

| Caminho | O que responde |
|---|---|
| `$HERMES_HOME/logs/update_receipts/latest.json` | desfecho do último sync: `outcome`, `steps[].name/detail`, `feature_list` |
| `$HERMES_HOME/logs/update_receipts/post_swap_*.json` | plano do swap: `pre_pull_sha`, `pre_update_version`, `plan.runtimes`, snapshots irmãos |
| `$HERMES_HOME/update-*.log` (raiz do home) | saída integral do `hermes update`, inclusive o erro de build |
| `profiles/<perfil>/logs/update.log` | mesma coisa, com carimbo do perfil |
| `$HERMES_HOME/logs/gateway-exit-diag.log` | eventos JSON `gateway.start` / `gateway.exit_*` e o traceback que precedeu cada morte |
| `$HERMES_HOME/gateway_state.json` | `gateway_state`, `code_sha`, `served_profiles`, `active_agents` |
| `$HERMES_HOME/logs/gateway.log` | reconexão por perfil e plataforma — use como relógio da volta |

## Assinaturas

| Assinatura | Leitura |
|---|---|
| `exited (exit code 143, SIGTERM)` no turno | o update derrubou o serviço; o turno morreu no meio |
| `InstallError: venv: uv sync exited 1` | dependência não sincronizou — instalação **incompleta** |
| `RequiredDependencyException: … headers … not found` | falta header de biblioteca do sistema para compilar a extensão |
| `SystemExit: 2` com `resolve_uv → stop_for_relaunch` | updater antigo matou o gateway durante o boot |
| `startup exceeded 300s … progress lease` | boot lento esperando migração do `state.db`, não travamento |
| `✓ <plataforma> connected (profile: X)` | aquele perfil voltou — compare a hora com a do incidente |
| `drop_pending_on_cold_boot` | o que chegou durante a queda foi **descartado**, sem retentativa |

## Provar código novo × venv velho

Um update que falha na etapa de dependências deixa o repositório no commit novo e o runtime no
antigo. Prova objetiva, sem escrever nada:

```bash
git -C "$HERMES_HOME/hermes-agent" log -1 --format='%h %ad %s' --date=iso
git -C "$HERMES_HOME/hermes-agent" describe --tags
"$HERMES_HOME/hermes-agent/venv/bin/python" -c "import <dependência_do_erro>; print('ok')"
```

`ModuleNotFoundError` aqui, com o recibo em `failed`, é divergência confirmada. Consequência a
declarar ao operador: todo caminho que importe aquela dependência quebra, e o próximo update falha
no mesmo ponto até o header do sistema existir.

O binário `sqlite3` pode não existir no ambiente — leia os bancos pelo módulo `sqlite3` do Python em
modo `mode=ro`.

## Patches locais: o stash

O update guarda as modificações locais em stash, tenta restaurar, e em conflito **reseta a árvore**.
Depois de qualquer update falho, compare as duas listas:

```bash
git -C "$HERMES_HOME/hermes-agent" stash list
git -C "$HERMES_HOME/hermes-agent" stash show --name-only stash@{0}
git -C "$HERMES_HOME/hermes-agent" diff --stat
```

O que aparece no stash e não aparece no `diff` **não está na árvore** — provedor, gateway e adapter
customizados podem estar inertes mesmo com o processo "no ar". Arquivos não rastreados (plugins
locais, `.bak`) sobrevivem ao reset; os rastreados, não.

## Resíduos que sobram

- `.hermes-update-in-progress.lock` na raiz do home: fica de um update abortado.
- **Lease de turno órfão** em `session_turn_leases`: `holder` com `pid=` de processo já morto. A
  sessão que foi interrompida pode continuar parecendo ocupada depois da volta; diga qual sessão é.

## Ordem de restauração (propor, não executar)

1. Prover o header/biblioteca do sistema que faltou e refazer o sync de dependências.
2. Reaplicar os patches locais do stash, conferindo conflito arquivo por arquivo.
3. Limpar o lock de update e o lease órfão.
4. Reiniciar o gateway uma única vez, no fim, e conferir `connected (profile: …)` de cada perfil.

Alternativa mais segura quando há snapshot pré-update: voltar ao snapshot e atualizar depois, com o
ambiente já preparado. Apresente as duas e deixe a escolha com o dono.

## Update concluído (outcome: ok) e o processo no interpretador errado

O recibo pode dizer `outcome: ok` / `venv_rebuild: ok` e o fleet continuar mudo. A causa é outra:
o **processo** segue no interpretador antigo enquanto o `sys.path` já aponta para o ambiente novo —
módulos compilados de uma versão de CPython dentro de outra não inicializam.

Assinatura (todo o fleet cala, mas `gateway_state` diz `running`):

```
Failed to load plugin 'telegram-platform': initialization of speedups did not return an extension module
tools.mcp_tool … / Reconnect telegram: no adapter yet, next retry in 300s
Failed to load plugin 'discord-platform': initialization of _audioop did not return an extension module
```

`speedups` é do `tornado`; `_audioop` é do `audioop-lts`. Nenhum dos dois é "plugin quebrado": é
ABI divergente.

### Provar em dois comandos

```bash
readlink -f /proc/<pid>/exe                      # qual python roda de fato
for p in $(pgrep -f 'gateway run'); do echo "$p"; done
```

```bash
grep -o "$HERMES_HOME/installs/[^ ]*" /proc/<pid>/maps | sort -u
```

Se o `exe` é `python3.x` **antigo** e o `maps` lista `.so` sob `.../environments/<hash>/venv/lib/python3.y/site-packages`
com **y > x**, está provado. Teste cada ambiente isolado para saber qual está são — o import que
falha no processo pode passar no ambiente novo:

```bash
"$ENV/venv/bin/python" -c "import tornado.speedups, audioop, pillow_heif; print('ok')"
```

### Onde o interpretador é escolhido

O `pm` guarda **gerações** do ambiente em `$HERMES_HOME/installs/<install_key>/environments/<hash>/`
(uma por tentativa de sync, com `venv` + `workspace`); `$HERMES_HOME/installs/<install_key>/facts.json`
→ `packages.venv.environment` nomeia a **selecionada**, e `source-completion-pending` /
`source-completion-attempts` registram se o "tail" (relançar no ambiente novo) terminou. Um launcher
que fixa `hermes-agent/venv/bin/python` ignora tudo isso e reproduz o defeito a cada restart.

Correção no script de supervisão (não no processo):

```bash
OLIMPO_SEL_VENV=$(python3 -c "import json;print(json.load(open('$FACTS'))['packages']['venv']['environment'])")
if [ -n "$OLIMPO_SEL_VENV" ] && [ -x "$OLIMPO_SEL_VENV/bin/hermes" ]; then
  HERMES_BIN="$OLIMPO_SEL_VENV/bin/python"; HERMES_MAIN="$OLIMPO_SEL_VENV/bin/hermes"
fi
```

Ao trocar o caminho do `hermes` no comando, **ajuste todo `pgrep` do script** (`hermes-agent/hermes
gateway run` → `hermes gateway run`): padrão desatualizado não reconhece o processo novo e o
supervisor passa a subir gateway duplicado a cada volta do laço.

**O marker não é limpo por gateway supervisionado.** `prepare_launch` só retoma o tail quando as
dependências estão desatualizadas; um filho sob supervisor deixa a obrigação para o próximo
`hermes update` (senão o tail — e seus builds — rerodaria a cada boot até encher o disco). Logo
`source-completion-pending` presente com `source-completion-attempts` **estável** é estado esperado,
não incidente; attempts crescendo significa update tentando e falhando. Fechar de verdade = rodar
`hermes update` com as dependências já correntes (ação de escrita: exige ok).

### Dados que ficam fora da cópia: `locales/` e o texto cru nas respostas

O workspace por geração é uma cópia de **membros de pacote**, não da árvore inteira: `locales/`,
`skills/`, `ui-tui/`, `apps/`, `tests/` **não** entram. Quem roda do workspace e resolve recurso por
`<repo-root>/<dir>` perde o recurso em silêncio. O caso visível é i18n: `agent/i18n._locales_dir()`
aponta para `<workspace>/locales`, o diretório não existe, `_load_bundled()` devolve `{}` e só
registra `logger.debug`; `t()` cai no último fallback e devolve **a própria chave**. Sintoma na
conversa: `gateway.status.session_id`, `gateway.status.header` e afins crus no lugar do texto.

Prova em dois comandos (use o interpretador do **ambiente selecionado**, não o da fonte):

```bash
"$SEL_VENV/bin/python" -c "import agent.i18n as i; print(i._locales_dir(), i._locales_dir().is_dir())"
"$SEL_VENV/bin/python" -c "from agent.i18n import t; print(repr(t('gateway.status.session_id', session_id='abc')))"
```

Diretório inexistente + retorno igual à chave = catálogo ausente, **não** tradução faltando. Confirme
que os catálogos estão completos antes de acusar cobertura — parseie-os e compare com as chaves
usadas no código; se todas existem, o problema é o caminho, não o arquivo.

Contorno imediato, previsto pelo próprio código (`HERMES_BUNDLED_LOCALES` existe para packaging
selado): exportar no supervisor apontando para os catálogos da árvore-fonte e reiniciar o gateway.

```bash
export HERMES_BUNDLED_LOCALES="$HOME/.hermes/hermes-agent/locales"
```

Correção durável é upstream: o manifesto de membros do `pm` precisa incluir os diretórios de dados
(ou o pacote precisa declará-los como package data), e `_load_bundled` deve **avisar** quando o
diretório não existe, não sussurrar em debug. Sem `display.language` no perfil o texto sai em inglês;
`display.language: pt` só funciona depois que o catálogo está no lugar.

### Reiniciar na ordem certa

1. Backup do script de supervisão.
2. `sv restart <serviço>` quando ele está sob runit (`sv status <serviço>` mostra o PID) — **antes**
   de matar o gateway. As variáveis do script (`HERMES_BIN`) foram avaliadas no boot do supervisor;
   matar só o gateway faz o supervisor antigo ressuscitá-lo no interpretador velho.
3. Parar o gateway (`<env selecionado>/bin/hermes gateway stop --all` ou `kill -TERM <pid>`) e
   esperar o supervisor subir o novo (laço típico de 20 s).

### Verificação (não declarar pronto sem ela)

- `readlink -f /proc/<novo_pid>/exe` → versão nova;
- `grep -c 'hermes-agent/venv' /proc/<novo_pid>/maps` → **0**;
- `did not return an extension module` filtrado **pelo horário depois do restart** → 0 (o log guarda
  as falhas antigas; contar sem filtrar dá falso positivo);
- `✓ <plataforma> connected (profile: X)` para **todos** os perfis — o boot reconecta um a cada
  ~25 s e leva vários minutos; ausência de falha não é sinal de volta.

### Armadilhas

- **Chaves i18n cruas na resposta ("gateway.status.header") = catálogo ausente, não tradução
  faltando.** O ambiente isolado do `pm` é montado por `pm/workspace.py::_copy_core_inputs`, que só
  copia diretórios cujo nome casa com `tool.setuptools.packages.find.include` — diretórios de dados
  resolvidos pelo *repo root* (`locales/`) ficam de fora. Sem eles `agent/i18n._load_bundled`
  devolve `{}` (log em `debug`, invisível) e `t()` cai no último fallback: **a própria chave**.
  Prova em dois comandos: `_locales_dir()` mostra `<generation>/workspace/locales` com
  `is_dir() = False`, e `t('gateway.status.session_id', session_id='x')` devolve a chave.
  Cuidado: rodar o teste com o interpretador do ambiente mas com `PYTHONPATH`/cwd herdados importa
  o `agent` da *outra* instalação — limpe `PYTHONPATH`/`HERMES_HOME` e rode com
  `cwd=<generation>/workspace` para que a leitura seja do processo real.
  Correção em dois níveis: (a) `export HERMES_BUNDLED_LOCALES=<repo>/locales` no supervisor —
  variável prevista por `_locales_dir()` para packaging selado, vale para todos os perfis do
  gateway; (b) durável, copiar os dados: incluir `locales` num `_RUNTIME_DATA_DIRS` em
  `_copy_core_inputs` (a condição de cópia passa a ser `entry.name in _RUNTIME_DATA_DIRS or ...
  package_roots`) e promover o `logger.debug` de catálogo ausente para `logger.warning` quando o
  *diretório* não existe. Copiar `locales/` para o workspace da geração viva resolve o processo
  atual sem re-sync (o stamp do venv não inclui o código-fonte, então o `pm` não reconstrói sozinho).
  Depois do restart, a verificação é `tr '\0' '\n' < /proc/<pid>/environ | grep BUNDLED` e repetir
  o `t()` com o env do processo vivo.
- **Concluir pelo `--version` do ambiente.** `env/venv/bin/python -c "import ..."` provar que o
  ambiente novo é são não diz nada sobre o processo vivo; só `readlink /proc/<pid>/exe` + `maps`
  respondem.
- **Linha de base de extensão ignorada.** `abi3` não é passe livre entre minors — um `abi3.so`
  construído para 3.14 pode não inicializar em 3.13.
- **Laço de monitoração casando a si mesmo.** `pgrep -f '<padrão>'` dentro de `bash -c` casa o
  próprio shell porque o padrão está no seu `cmdline`; confirme com `ps -ef | grep … | grep -v 'bash -c'`
  e confira `readlink /proc/$PID/exe` antes de matar.
- **Resíduo de gerações.** Cada tentativa de sync deixa uma geração em
  `installs/<key>/environments/<hash>/` (62 MB quebradas, 400–450 MB completas). `hermes pm gc`
  **não poda gerações** — na prática devolve `kept 6; removed 0 dependency generations` mesmo com
  seis mortas na pasta; `hermes pm status` mostra o último recibo e `hermes pm environment` lista os
  ambientes nomeados. A poda real é `rm -rf` das gerações **não referenciadas** em `facts.json`
  (conferir antes: `grep -rl <hash> *.json` fora de `environments/`), preservando a selecionada e,
  de preferência, a última completa anterior como rollback. É escrita: proponha, execute com ok e
  verifique depois que o gateway segue vivo e `facts.json` intacto.
- **`hermes pm doctor` com `KeyError: 'sha256'`.** Acontece quando o `uv.lock` foi gerado sem hashes
  (todos os artefatos sem `sha256`), não por geração removida: leia o lock direto
  (`tomllib`, contar `sha256` ausente) antes de suspeitar da limpeza. É defeito do `pm/_identity`,
  não sinal de instalação quebrada — o gateway roda normalmente assim.
- **Procurar chave i18n com `grep` no YAML.** Os catálogos são aninhados (`gateway:` → `status:` →
  `header:`), então `grep 'gateway\.status'` não casa nada e induz a "a chave não existe". Achatе o
  YAML (parse com `hermes_yaml`/`parse_locale_file`) antes de concluir que falta tradução — e note
  que `t()` aplica `str.format` no fallback: uma chave sem `{}` passa intacta e não gera erro.
- **Contar falha de ABI no log inteiro.** O log guarda as falhas do processo morto; filtre pelo
  horário posterior ao restart ou pela janela desde a última linha `Starting Hermes Gateway`.
