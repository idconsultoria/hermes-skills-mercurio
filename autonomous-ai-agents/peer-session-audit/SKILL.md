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

## Regra de acesso (primeiro passo, sempre)

Outro perfil tem skills, plugins, cron e memorias proprios. **Auditar = ler; corrigir o ritual =
escrever.** Nunca `skill_manage` em perfil alheio: a analise pode propor mudanca, a escrita so
acontece com o dono e no perfil dono, ou via `hermes curator adopt <skill>`.

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

## Armadilhas

- **Auditar e ler.** Editar a skill do outro perfil e acao fora da rotina e fora do escopo: diga
  "posso aplicar no <perfil>?" e espere.
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

- `references/audit-checklist.md` - extrativos prontos para extrair transcript cru e contar padroes de
  afunilamento, sem despejar a sessao inteira no contexto.
