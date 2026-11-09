---
name: cobranca-clientes-id
description: "Use ao cobrar cliente inadimplente da ID (escalada)."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ID, cobrança, inadimplência, financeiro, dunning, email, escalada]
    scopes: [id]
type: Orchestrator
timestamp: 2026-11-04T00:00:00Z
---

# Cobrança de clientes da ID — escalada com texto aprovado

Política do dono para **toda cobrança de cliente da ID** (qualquer contrato, qualquer parcela):
parcela vencida, reenvio de aviso, escalada para outro interlocutor, lembrete de prazo prometido
e revisão de um cron de cobrança já existente. Antes desta política o cron enviava sozinho por dia
útil; agora **só envia o que tem texto aprovado**, e a escalada é um plano — não um gatilho
automático.

Os scripts e o motor de envio vivem em `$HERMES_HOME/scripts/` e `work/cobranca-<cliente>/`; o
detalhe operacional (config, estado, log, releitura de envio) está em
`references/fluxo-operacional.md`. Leitura da thread: `scripts/ler_thread_gmail.py`.

## Regra zero — texto aprovado antes do envio

Nenhum e-mail de cobrança sai sem **texto aprovado pelo dono**. Duas formas:

1. **Template aprovado** — vale para os próximos envios **enquanto o texto não mudar**.
2. **Texto do caso** — aprovado por DM para aquele envio.

Silêncio não é aprovação. Sem ok, **não envia**: a cobrança atrasa, nunca improvisa.

**Destinatário novo (cc, gestor, sócio) exige aprovação nova**, mesmo com template aprovado:
a aprovação cobre o texto **e** a lista de gente. O registro (texto, hash, data, quem aprovou,
destinatários cobertos) vai em `work/cobranca-<cliente>/aprovacoes.json`.

**Fila D-1:** o cron prepara o próximo passo **um dia útil antes** e manda o texto inteiro no DM
do sócio responsável; sem ok até a hora do envio, não envia e reinsere no dia seguinte.

## Escalada por níveis

| nível | quem | quando |
|---|---|---|
| N1 | financeiro do cliente (`financeiro@…` + coordenador financeiro em cc) | padrão |
| N2 | gestor direto / dono do cliente | N1 sem resposta ou promessa não cumprida |
| N3 | representante legal · suspensão de entrega | **só com autorização explícita do dono** |

Intervalo padrão entre níveis: **2 dias úteis**. A escalada troca o interlocutor e o argumento
(prazo não cumprido, continuidade dos projetos) — **não** troca o tom.

## Os dois ramos

**A — sem prazo novo.** Cobra no nível atual na data marcada; sem resposta em 2 dias úteis,
sobe um nível.

**B — prazo novo dado pelo cliente.** Lembrete **no dia do prazo**, com valor, NFS-e de
referência, chave Pix e a nota reanexada se preciso. Não pagou → cobra em **D+1** e reinicia a
escalada no N1.

## Procedimento por ciclo

1. **Ler a thread antes de qualquer coisa:** `scripts/ler_thread_gmail.py <thread_id> [--de nome]`
   mostra quem respondeu, quando e o corpo. Sem isso não se sabe em que nível a cobrança está.
2. **Conferir o extrato** com janela a partir do vencimento (nunca janela fixa). `ERRO` de
   leitura = **não cobra**; reporta a falha.
3. **Checar `estado.json`** — um e-mail por dia útil, mesmo com o cron rodando duas vezes.
4. **Classificar o caso:** houve promessa? com data? vencida? → ramo A ou B, nível atual.
5. **Preparar o texto** (template aprovado ou texto novo) e mandar para aprovação em D-1.
6. **Enviar só aprovado**, na thread da NFS-e (`threadId` explícito, assunto original sem
   sufixo), e **reler** a mensagem enviada (label `SENT`, thread ganhou +1).
7. **Registrar** texto, destinatários, data, mensagem-id e o estado do nível.

## Pitfalls

- **Nível já consumido.** Se o destinatário do N2 já foi escalado e respondeu sem data, o
  próximo passo é a **segunda** escalada cobrando a previsão que **ele** prometeu — repetir a
  primeira queima o nível e soa automático.
- **Nome ditado não é destinatário.** Nome de contato vindo de áudio/transcrição chega
  corrompido (variantes de um mesmo dono). Tire o endereço dos **headers da thread** ou da base
  (`kb_search`); se o nome não existir em nenhum dos dois, **pergunte** antes de criar
  destinatário.
- **Promessa sem data não é prazo.** "Em breve o financeiro informa a previsão" não move o caso
  para o ramo B nem suspende a cobrança: registre e siga o ramo A no nível seguinte.
- **Template aprovado não valida número.** Valor, vencimento e nº da NFS-e saem da configuração;
  número digitado à mão no corpo é o defeito que o cliente cobra de volta.
- **Cadência mora em dois lugares.** A expressão cron e a regra por dia da semana no JSON
  precisam mudar juntas; senão o job executa o plano antigo com a aparência de novo.
- **Silêncio é resultado.** Dia sem novidade não gera mensagem; falha de leitura e envio feito
  geram uma linha. Não transformar "nada aconteceu" em relatório.

## Antes de implementar

Quando o dono pede para "transformar em rotina mais robusta", ele quer **primeiro** o
entendimento confirmado do caso concreto + o rascunho da política em até 10 bullets. Só depois
do ok explícito se escrevem scripts e se reprograma cron.
