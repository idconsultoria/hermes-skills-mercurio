---
name: peer-session-audit
description: "Auditar sessão ruim de um agente par: conversa real, defeitos, postmortem.

Load this skill when a partner reports misbehavior by another profile's agent and the owner requests an investigation of the real session."
category: autonomous-ai-agents
type: Reference
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [session-audit, multi-profile, quality, postmortem]
    related_skills: [hermes-inference-config]
timestamp: 2026-09-24T00:00:00Z
---

# Auditoria de sessao de um agente par

Investigar "por que o agente X se comportou mal" lendo a conversa real do perfil do agente, nao o
relato de segunda mao. Usado quando um socio relata desvio de um agente de outro perfil e o dono
pede apuracao.

## Quando usar

- "A [agente] deu uma devaneada", "mandou a cadeia de pensamento", "que problema ele pontuou".
- Qualquer pedido de auditar conversa entre um agente e uma pessoa, em outro perfil.
- "A sessao dela ta progredindo bem?" / "isso ta demorando demais" — quando a sessao **ainda esta
  rodando** e o dono quer um veredito antes de ela terminar. Ver a secao de sessao em andamento.

## Regra de acesso (primeiro passo, sempre)

Outro perfil tem skills, plugins, cron e memorias proprios. **Auditar = ler; corrigir o ritual =
escrever.** Nunca `skill_manage` em perfil alheio: a analise pode propor mudanca, a escrita so
acontece com o dono e no perfil dono, ou via `hermes curator adopt <skill>`.

## Sessao em andamento: auditar e uma serie temporal, nao um transcript

`session_search` devolve um retrato estatico. Quando a sessao esta viva, o defeito esta no
**comportamento acumulado** (loop de espera, retrabalho, zero entrega) e nao em nenhuma mensagem
isolada. Entao audite direto o SQLite do perfil e tire **varias fotografias** do mesmo intervalo:

```bash
sqlite3 /opt/mercurio-data/profiles/<perfil>/state.db "
SELECT id, source, chat_type, display_name,
       datetime(started_at,'unixepoch'), datetime(COALESCE(ended_at,0),'unixepoch'),
       end_reason, message_count, tool_call_count
FROM sessions ORDER BY started_at DESC LIMIT 12;"
```

Tres medidas decidem o veredito de uma sessao viva:

1. **Turno esta avancando?** Compare `max(timestamp)` da tabela `messages` com `now`, varias vezes.
   Silencio de minutos com um `sleep 400` no meio e o achado; nao e "trabalhando".
2. **Houve entrega?** Conte `delivery_obligations` do chat e as mensagens de `assistant` com texto
   **sem** `tool_calls`. Um turno longo com zero entrega e um defeito de report, independente do
   que a agente fez de bom.
3. **Qual o turno ha quanto tempo?** `session_turn_leases.expires_at - now` da o prazo de vida do
   turno; `now - acquired_at` a idade. Um turno de horas sem entrega e achado por si so.

O `session_id` ordena por criacao, nao por atividade: uma sessao antiga pode ser a ativa.
Selecione por `chat_id` + `ended_at IS NULL`, nunca pelo primeiro `LIMIT`.

Quando o agente aguarda um **runtime delegado** (OpenDesign, Codex, Claude Code, qualquer
servico com fila), o status resumido que o agente le ("timeout", "empty_output") nomeia o
sintoma, nao a causa. **Suba um nivel e le o event log do proprio runtime** antes de culpar
infraestrutura ou modelo. Ver `references/live-session-triage.md`.

## Procedimento

1. **Ler a sessao real, nao o relato.** `session_search(query=..., profile=<perfil-do-agente>)` para
   localizar; `session_search(session_id=..., around_message_id=...)` para percorrer. Scroll por
   ancora, nao pela pagina inicial: as falhas ficam no meio da sessao.
2. **Extrair as mensagens cruas.** Mensagens do agente e da pessoa, em ordem, com texto integral:
   os defeitos de geracao aparecem literalmente no corpo da mensagem (metacomentario, caps nao
   pedido, caractere de outro idioma, run-on). O resumo do dono acima e indicio, nao prova.
3. **Converter horario para BRT.** `datetime.fromtimestamp(ts, tz=utc).astimezone(utc-3)` da a hora
   local e revela o padrao: perguntas em sequencia, silencio longo, rajadas de texto.
4. **Classificar cada defeito separadamente**, porque tem causas diferentes:
   - **Vazamento de rascunho** - texto de planejamento entregue como resposta. Ver
     `hermes-inference-config` ("Rascunho interno entregue como conteudo"): nao e flag de reasoning.
   - **Deformacao de saida** - caps, verbo em forma inexistente, palavra colada, caractere estranho
     numa linha. E geracao de texto corrompida, nao escolha de tom.
   - **Afunilamento** - a pessoa da fragmento curto, o agente vira afirmacao e devolve pergunta mais
     estreita, repetidamente. Conte os ciclos: 4 fragmentos -> 4 follow-ups e padrao de empurrar,
     nao de ouvir.
   - **Narrativa fabricada** - o agente persegue um slot do roteiro (case com metrica, momento
     decisivo) que a pessoa nunca ofereceu.
   - **Loop de espera** - o agente repete `sleep`/poll em vez de produzir. Conte as chamadas de
     espera e compare com as chamadas substantivas: muitas `terminal(sleep N)` e poucas tool calls
     uteis significam que a pessoa espera ha horas por um avanco que nao vem. A contagem e o
     argumento, porque "a engine estava ocupada" nao e visivel no transcript.
   - **Defeito de report, nao de execucao** - o trabalho ate que deu certo, mas nada chegou a
     pessoa (zero `delivery_obligations`, ou a unica mensagem foi "interrompido"). Grave como
     defeito separado: a correcao nao esta no caminho feliz, esta no corte.
5. **Separar o que foi consertado do que nao foi.** Se o agente ja patchou a skill, verificar se o
   patch **remove a armadilha** ou so acrescenta um aviso para o modelo vencer a propria tabela. Regra
   nova que convive com a pergunta que a produziu e remendo, nao correcao.
6. **Procurar o sinal que o owner deu.** Pergunta do tipo "como isso vai tracar meu perfil?" ou "voce
   esta devaneando" e o sujeito detectando o desvio antes do agente. Esse e o achado mais valioso do
   postmortem: a pergunta dele era a certa.
7. **Verificar se a conversa se recuperou.** O pos-reset e a prova de que o rito corrigido funciona;
   citar o turno que voltou ao caminho certo evita diagnostico pessimista.

## Formato do relatorio (para o Gustavo, DM)

Abre com o **veredito em uma frase** - a causa raiz, nao a lista. Depois, por defeito: gravidade,
evidencia literal (curta), mecanismo. Fecha com o que ja foi feito, o que o remendo nao resolve, e
**uma pergunta de proximo passo**. Sem "posso fazer mais?", sem resumo do que foi lido.

Reportar so evidencia da sessao; se a causa provavel for modelo/config, o veredito aponta a classe de
skill que a trata, sem prescrever alteracao em outro perfil sem o ok.

### Quando o dono pede resposta agora, responda agora

Se o dono manda "preciso de uma resposta, ta demorando demais" ou "me responda sem tool call", a
coleta **acabou**: entregue o veredito com o que ja esta na mao, o que ainda falta e o que esta em
curso. Perfurar mais evidencia antes de responder e o proprio defeito sendo apurado. Marque o que
ainda nao se sabe como pendencia, em vez de deixar o dono esperando a proxima rodada de leitura.

O mesmo vale para o meio do turno: se a leitura de 20 minutos nao mudou o veredito, o
relatorio sai com "ainda verificando X" e o dono decide se espera.

## Armadilhas

- **Auditar e ler.** Editar a skill do outro perfil e acao fora da rotina e fora do escopo: diga
  "posso aplicar no <perfil>?" e espere. A skill da propria agente auditada costuma ser a **fonte do
  defeito**: se ela ensina "espere, fila se espera" e a engine esta falhando por escopo, o remendo
  dela e a armadilha, nao a solucao. Proponha a correcao; a escrita e com o dono.
- **Culpar a infraestrutura antes do event log.** Container `healthy` nao prova que o run
  generate a arte; o run pode falhar com o container inteiro sao. Cheque o log de eventos do
  runtime, nao o `docker ps`.
- **Relato do dono x transcript.** O dono percebe o sintoma; so o transcript nomeia o defeito e da a
  ordem de gravidade.
- **Contar os ciclos de pergunta.** A contagem (fragmentos -> follow-ups) e o argumento mais forte
  contra "ela so estava ouvindo".
- **Nao chamar bug o que e ritual.** Defeito de geracao (caps, metacomentario) e do modelo; pergunta
  de roteiro que forca case e da skill. O postmortem separa, porque a correcao cai em lugares
  diferentes.
- **Numero de sessao nao e duracao.** O `session_id` e timestamp de criacao, nao hora do fato;
  sempre converter o timestamp da mensagem.

## References

- `references/live-session-triage.md` - como auditar uma sessao **em andamento**: as medidas do
  SQLite que decidem o veredito, e como subir do status do agente para o event log do runtime
  delegado para achar a causa real (tabela de assinatura thought/output).
