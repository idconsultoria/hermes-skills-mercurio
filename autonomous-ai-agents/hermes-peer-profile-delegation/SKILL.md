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

1. **Descobrir** antes de lançar:

```bash
hermes profile list
hermes profile show <nome>      # caminho, modelo, gateway rodando, nº de skills, .env
```

2. **Teste de fumaça** — um turno trivial confirma que o perfil responde antes de investir num brief
   longo: `HERMES_PROFILE=<nome> hermes -z "responda apenas: ok" -t ""`.

3. **Escrever o brief em arquivo**, autocontido. O irmão não vê a conversa: contexto do cliente,
   especificação fechada (nomes, formatos, paleta, restrições), o que **não** fazer e o contrato de
   entrega. Salve em `<HERMES_HOME>/work/<peça>/BRIEF-<irmão>.md`.

4. **Criar o diretório de saída antes de lançar** — `mkdir -p <HERMES_HOME>/work/<peça>/<irmão>/`. Se o
   diretório do log não existir, o `tee` falha e o rastro do turno inteiro se perde em silêncio (o
   processo continua rodando, sem log).

5. **Lançar em background**:

```bash
HERMES_PROFILE=<nome> hermes -z "$(cat <HERMES_HOME>/work/<peça>/task-<irmão>.txt)" --yolo
```

   Use `terminal(background=true, notify_on_complete=true)`. Nunca em foreground: o turno dura de
   minutos a dezenas de minutos.

6. **Contrato de entrega explícito no brief**: saída em arquivo, em caminho combinado e formato fixo —
   por exemplo `status.json` com `{url, repo, screenshots, observacoes}` — mais os arquivos de apoio
   (PNGs, builds) na mesma pasta. Instrua: *"só pare quando o `status.json` existir com a URL de
   produção ou com o motivo da falha registrado"*.

7. **Fechar o ciclo você mesmo**: leia o `status.json`, abra a URL, conte páginas, olhe as capturas.
   Resumo de irmão é auto-relato — para efeito externo (deploy, publicação, escrita remota) exija handle
   verificável e verifique antes de dizer ao usuário que funcionou.

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

- `hermes profile show <nome>` antes: gateway rodando e `.env` presente.
- Turno de fumaça respondeu antes do brief longo.
- `status.json` existe no caminho combinado, com os campos pedidos.
- O artefato é real: URL abre, PNG abre, contagem confere.
- Nada do seu arquivo principal foi tocado pelo irmão (`git status` / `ls -la` no diretório).
