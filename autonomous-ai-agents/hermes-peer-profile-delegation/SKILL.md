---
name: hermes-peer-profile-delegation
description: "Use para dirigir outro perfil Hermes do mesmo gateway."
category: autonomous-ai-agents
type: Orchestrator
timestamp: 2026-10-22T00:00:00Z
---

# Dirigir um perfil Hermes irmão

## Quando usar

Uma entrega tem duas partes independentes e uma delas cabe a outro perfil da casa (ex.: você faz o
documento e o irmão constrói o painel/app que o acompanha). Perfis do Capitólio vivem em
`<HERMES_HOME>/profiles/<nome>/` e rodam no mesmo gateway.

**Não confundir com:**

- `delegate_task` — subagente isolado, sem skills/memória/credenciais próprias, morre com o turno.
- `pi-agent-coordination` / CLIs externos — agentes de código sem identidade na casa.
- `facilitacao-grupo-agentes` — reunião de bots em grupo do Telegram, com turnos e menções.

Aqui o irmão tem skills, memória, SOUL e credenciais próprias, executa no filesystem real e assina o
trabalho.

## Procedimento

0. **Use SEMPRE o binário da própria casa, nunca o `hermes` do PATH.**

```bash
HERMES_BIN="$HERMES_HOME/hermes-agent/venv/bin/hermes"
```

   O `hermes` do PATH resolve para `/usr/bin/hermes`, que aponta para a instalação do **Olimpo**
   (`~/.hermes/hermes-agent`). Rodar esse binário com `HERMES_HOME` do Capitólio faz o CLI novo
   classificar o gateway da casa (versão mais antiga) como dono incompatível de runtime e **pará-lo
   do mesmo jeito que `hermes gateway stop`** — o `run_forever` ressuscita em ~40 s, o turno é
   retomado, o comando se repete e vira laço de restart (breaker dispara após 3 boots encadeados).
   Sintoma no log: `Received SIGTERM as a planned gateway stop` sem nenhum `gateway stop` digitado.

1. **Descobrir** antes de lançar:

```bash
"$HERMES_BIN" profile list
"$HERMES_BIN" profile show <nome>      # caminho, modelo, gateway rodando, nº de skills, .env
```

2. **Teste de fumaça** — um turno trivial confirma que o perfil responde antes de investir num brief
   longo: `HERMES_PROFILE=<nome> "$HERMES_BIN" -z "responda apenas: ok" -t ""`.

3. **Escrever o brief em arquivo**, autocontido. O irmão não vê a conversa: contexto do cliente,
   especificação fechada (nomes, formatos, paleta, restrições), o que **não** fazer e o contrato de
   entrega. Salve em `<HERMES_HOME>/work/<peça>/BRIEF-<irmão>.md`.

4. **Criar o diretório de saída antes de lançar** — `mkdir -p <HERMES_HOME>/work/<peça>/<irmão>/`. Se o
   diretório do log não existir, o `tee` falha e o rastro do turno inteiro se perde em silêncio (o
   processo continua rodando, sem log).

5. **Lançar em background passando um ponteiro, nunca o brief inteiro.** O arquivo `task-<irmão>.txt`
   tem de ser curto (10-20 linhas): o pedido em uma frase, o caminho do brief e o do contrato de
   entrega. Brief de vários KB colado dentro de `-z` mata a execução — o irmão lê o primeiro arquivo,
   não emite mais nenhuma ferramenta e encerra com sucesso falso; o mesmo brief apontado por caminho
   roda até o fim. O ponteiro também obriga o irmão a abrir o brief, em vez de resumi-lo de memória do
   prompt.

```bash
HERMES_PROFILE=<nome> "$HERMES_BIN" -z "$(cat <HERMES_HOME>/work/<peça>/task-<irmão>.txt)" --yolo > <dir>/run.log 2>&1
```

   Use `terminal(background=true, notify_on_complete=true)`. Nunca em foreground: o turno dura de
   minutos a dezenas de minutos. `run.log` de 0 byte **não** significa que morreu: o buffer do processo
   só descarrega no fim.

6. **Contrato de entrega explícito no brief**: saída em arquivo, em caminho combinado e formato fixo —
   por exemplo `status.json` com `{url, repo, screenshots, observacoes}` — mais os arquivos de apoio
   (PNGs, builds) na mesma pasta. Instrua: *"só pare quando o `status.json` existir com a URL de
   produção ou com o motivo da falha registrado"*.

7. **Fechar o ciclo você mesmo**: leia o `status.json`, abra a URL, conte páginas, olhe as capturas.
   Resumo de irmão é auto-relato — para efeito externo (deploy, publicação, escrita remota) exija handle
   verificável e verifique antes de dizer ao usuário que funcionou.

8. **Ler o turno do irmão no `state.db` quando a pergunta é "ele está fazendo o que pedi?".** O log
   pode estar vazio e o relatório final só chega no fim; a prova do que ele leu e fez está gravada em
   `<HERMES_HOME>/state.db`. Abra em somente-leitura para não travar o gateway:

```python
import sqlite3
c = sqlite3.connect('file:state.db?mode=ro', uri=True)
c.execute("SELECT id, profile_name, title, message_count, tool_call_count FROM sessions ORDER BY last_activity_at DESC LIMIT 5")
# depois, por sessão: mensagens de ferramenta trazem `tool_name` e `tool_calls` (JSON) — dá para
# confirmar quais caminhos ele abriu de fato e quantas chamadas fez.
```

   Serve para dois diagnósticos: (a) o irmão leu os documentos de referência que importam, ou está
   improvisando? (b) o turno parou depois da primeira ferramenta (sinal de brief colado inline) ou
   está avançando? Coluna `last_activity_at` de 10 minutos atrás com `tool_call_count` parado é turno
   morto — relance com o brief em arquivo.

## Regras

- **Fronteira de arquivo, não de etapa.** Se a peça principal é sua, o irmão escreve só na pasta dele e
  fica explicitamente proibido de editar o seu arquivo. Paralelismo por arquivo não colide; por etapa
  cria espera e conflito.
- **Brief imperativo e sem confirmação.** O irmão não pode perguntar: escreva *"não peça confirmação,
  execute de ponta a ponta"*. Cada rodada de dúvida queima o turno inteiro.
- **Brief com o desenho fechado.** Nomes de indicadores, siglas, paleta, formatos e o que é proibido
  (emoji, gráfico de pizza, dado real de cliente) vão escritos no brief. Irmão com liberdade criativa
  entrega fora do padrão da casa e você refaz.
- **Credencial não entra no brief.** Escreva o necessário para a tarefa; o irmão usa o `.env` dele.
- **Se o irmão falhar**, o `status.json` deve existir mesmo assim, com `url` vazia e o motivo em
  `observacoes`, mantendo as capturas locais — preserva a parte boa para você aproveitar.

## Verificação

- `"$HERMES_BIN" profile show <nome>` antes: gateway rodando e `.env` presente.
- O comando de lançamento usou `"$HERMES_BIN"`, nunca o `hermes` do PATH (ver passo 0).
- Turno de fumaça respondeu antes do brief longo.
- `status.json` existe no caminho combinado, com os campos pedidos.
- Arquivo do `task-<irmão>.txt` é curto e aponta para o brief; o brief, não o prompt, carrega a
  especificação.
- O que o irmão fez foi conferido em `state.db` (`tool_call_count` crescente, arquivos de referência
  abertos) quando a entrega demorou ou o log ficou em branco.
- O artefato é real: URL abre, PNG abre, contagem confere.
- Nada do seu arquivo principal foi tocado pelo irmão (`git status` / `ls -la` no diretório).
