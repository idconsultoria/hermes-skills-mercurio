---
name: coordenacao-perfis-hermes
description: "Use ao delegar tarefa a outro perfil Hermes irmão."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [panteao, perfis, delegacao, orquestracao, gateway, terminos, agentes]
    related_skills: [autonomous-ai-agents, facilitacao-grupo-agentes, peer-session-audit]
type: Orchestrator
timestamp: 2026-10-22T00:00:00Z
---

# Coordenação de perfis Hermes irmãos

## Quando usar

O dono pede que **outro agente da casa** produza uma parte da entrega (“direcione o Terminus para
construir o painel”, “o Júpiter levanta os números”). Aqui o veículo não é um subagente isolado nem um
CLI de código: é outro **perfil Hermes** da mesma instalação, com skills, memórias e workspace
próprios.

Para reunião de vários agentes com turnos em grupo do Telegram, use `facilitacao-grupo-agentes`.
Para delegar código a Claude Code/Codex/OpenCode, use `autonomous-ai-agents`.

## Procedimento

1. **Confirme quem é o irmão.** `hermes profile show <perfil>` devolve caminho, modelo e estado do
gateway. Não delegue a um perfil que você não identificou.
2. **Escreva o brief em arquivo**, autocontido: o filho não sabe nada da conversa. Inclua o contexto
do domínio, a especificação fechada (nomes, siglas, ordem, visual), o que **não** fazer, o caminho
exato dos artefatos e o formato do recibo. Sem brief, o filho inventa.
3. **Crie o diretório de saída antes de lançar.** `mkdir -p <saida>` na mesma sequência, e não
   canalize a execução por `tee` para um caminho que pode não existir: o `tee` falha, o log se perde
   e a tarefa roda às cegas.
4. **Lance um turno one-shot em background:**

   ```bash
   HERMES_PROFILE=<perfil> hermes -z "$(cat brief.md)" --yolo
   ```

   Use `terminal(background=True, notify=True)` com `--yolo`. Construir e publicar leva dezenas de
   minutos; o timeout de foreground trunca a tarefa no meio.

5. **Peça recibo legível por máquina**: um `status.json` na pasta combinada com URL/artefatos,
   caminhos das capturas e observações de falha. Instrua que o arquivo deve existir mesmo em caso de
   erro, com o motivo no campo de observações.
6. **Siga o seu próprio fio de trabalho** enquanto ele roda. Não consulte transcript nem fique
   esperando: o resultado volta por notificação.
7. **Verifique o recibo você mesmo.** O resumo do irmão é auto-relato, não prova: abra o
   `status.json`, confira que as capturas existem e que a URL responde antes de dizer ao dono que
   está pronto. Se ele não gravou o recibo, relate o que existe de fato.
8. **Para saber o que o irmão leu, consulte a sessão dele.** O banco `state.db` do HERMES_HOME tem
   as tabelas `sessions` e `messages`: filtre por `profile_name`, ordene por `last_activity_at` e
   procure os caminhos nos `tool_calls` de `read_file`. Serve para responder "ele está trabalhando com
   os documentos de referência?" com evidência, em vez de repetir o que ele disse. Se a resposta dele
   vier vazia ou duvidosa, **vá à fonte original** (os arquivos) e só então reporte — nunca repasse a
   um sócio um resumo de irmão que você não conferiu.

## Pitfalls

1. **Brief longo não vai dentro do `-z`.** O comando leva um **bilhete curto** que manda ler o
   arquivo: escreva `task.txt` com 5 a 10 linhas apontando o caminho do brief, e chame
   `hermes -z "$(cat task.txt)"`. Brief inteiro inline (com markdown, aspas e quebras) faz o turno
   morrer logo depois da primeira ferramenta e o log fica com uma linha só — parece que o irmão
   "começou e travou". O brief completo continua em arquivo, para ele ler com `read_file`.
2. **Pergunta a irmão também termina cedo.** Em modo pergunta, o turno pode encerrar após a primeira
   ferramenta sem responder nada. Peça explicitamente "não pare depois da primeira ferramenta; só
   encerre com a resposta completa na última mensagem" e redirecione a saída para um log
   (`> resposta.log 2>&1`); leia o log depois, não a notificação de conclusão.
2. **Sem pasta criada, sem log.** Caminho inexistente no `tee` mata o log e você fica sem saber se o
   filho terminou, falhou ou fez outra coisa.
3. **Não entregue o trabalho do irmão como concluído antes de inspecionar o artefato.** Recibo sem
   arquivo correspondente no disco é promessa.
4. **Dependência externa não segura a sua entrega.** Se a peça principal fica pronta antes do irmão,
   entregue a peça e enriqueça depois com link e capturas; o dono prefere prévia hoje a pacote
   completo amanhã.
5. **Combine os nomes antes.** Se a peça principal e a demonstração usam os mesmos rótulos e siglas,
   a especificação tem de ir no brief do irmão, palavra por palavra; divergência de nomenclatura
   entre peça e demo aparece na primeira leitura.
