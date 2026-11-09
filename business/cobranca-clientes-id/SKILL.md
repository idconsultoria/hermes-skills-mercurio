---
name: cobranca-clientes-id
description: "Use ao cobrar cliente inadimplente da ID (escalada).

Carregue esta skill quando houver parcela vencida, reenvio de aviso, escalada para outro interlocutor ou lembrete de prazo prometido de cliente da ID. Política do dono: nenhum e-mail sai sem texto aprovado (por hash); extrato primeiro; escalada N1→N3 em 2 dias úteis; tom neutro e direto; fila D-1 no DM do sócio. Inclui o motor `cobranca_fluxo.py` e o passo a passo de onboarding de novo cliente."
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

## Tom do texto (registro do dono, 04/11/2026)

**Neutro e direto.** Sem "prezado", sem parágrafo explicando a relação ou o valor do serviço,
sem discurso de parceria. Estrutura: **fato verificável** (parcela, NFS-e, valor, vencimento,
dias úteis em aberto) → **o que o cliente disse e não cumpriu**, em uma frase → **um pedido
objetivo** (data do pagamento ou comprovante) → dados de pagamento → assinatura.

O argumento "o que a parcela sustenta" existe em `config.descricao_entrega` e fica **guardado
para o nível 3**, quando o dono autorizar: não entra na cobrança de rotina.

## Antes de escrever o texto (não pule)

1. **Extrato primeiro.** O pagamento pode ter caído. Cobrança enviada a quem já pagou é dano
   de relação, não erro técnico. Falha de leitura do extrato = **não cobra**, avisa.
2. **Leia o contexto do cliente:** a thread da cobrança/NFS-e **e** os últimos e-mails do
   domínio do cliente (qualquer assunto, ~30 dias). Quem respondeu, quando, o que prometeu.
   - Promessa com data vira `prazo_prometido`; promessa sem data ("em breve", "vamos informar
     uma previsão") **não** é prazo — e o texto deve cobrar exatamente isso.
   - Data já vencida citada em e-mail antigo não é prazo novo.
3. O texto referencia a **última resposta real** do cliente (data + quem), nunca uma promessa
   inventada. Se não houver resposta, o texto não menciona resposta.
4. Se o contexto mudar depois do rascunho (prazo novo, resposta, pagamento), o rascunho antigo
   fica **obsoleto** e é refeito — o envio reconfere o plano na hora e recusa o texto velho.

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

## Como operar (motor)

Tudo vive em `$HERMES_HOME/work/cobranca-<cliente>/` (config, estado, fila, aprovações, log) e
o motor é `$HERMES_HOME/scripts/cobranca_fluxo.py` + wrapper `cobranca_fluxo.sh` — sucede o
`cobranca_sm_diaria.sh` descrito em `references/fluxo-operacional.md`. Wrapper:
extrato → `pago` se caiu → `enviar` (só aprovados vencidos) → `preparar` (D-1).

```bash
P=$HERMES_HOME/venvs/google/bin/python; F=$HERMES_HOME/scripts/cobranca_fluxo.py
$P $F status                 # extrato + thread + plano do dia (diagnóstico)
$P $F preparar [--forcar]    # gera/atualiza rascunho D-1
$P $F listar                 # fila e status (PENDENTE/APROVADO/ENVIADO)
$P $F aprovar --id <id> --nota "aprovado no DM"
$P $F enviar [--dry-run]     # envia o que está vencido E aprovado
$P $F prazo --data AAAA-MM-DD --evidencia "..."   # registra prazo declarado
$P $F pago --detalhe "..."   # encerra a cobrança
```

Cron: dias úteis 09:05, script `cobranca_fluxo.sh`, entrega no DM do dono. O agente do cron
**apresenta** o rascunho e **relata** envio/falha; ele nunca aprova nem envia por conta própria.

## Novo cliente

Copie `work/cobranca-sm/` para `work/cobranca-<sigla>/` e ajuste `config.json`: `cliente`,
`dominios_cliente`, parcela/contrato/valor/vencimento/NFS-e, `thread_id` (thread da nota ou da
última cobrança), `niveis` (to/cc/tratamento de cada nível), `descricao_entrega` (o que a
parcela sustenta — argumento da escalada) e `politica`. Zere `estado.json` (`enviados`, `pago`,
`cobranca_atual`) e a `fila/`. Rode `COBRANCA_CLIENTE=<sigla> ... status`.

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

- **Saudação e datas pelo horário do ENVIO, não do rascunho.** Rascunho escrito à noite para
  envio às 9h: "Bom dia" e a data do dia do envio. `"até hoje"` com a data de ontem é erro na
  cara do cliente.
- **Thread forçada:** envie com `threadId` explícito e `In-Reply-To`/`References`; lembrete em
  fio novo fica fora da conversa da nota, onde o financeiro olha. Depois releia a mensagem e
  confirme `SENT` **e** a thread.
- **Fail-closed:** hash divergente, falta de aprovação, extrato ilegível, plano mudado → não
  envia e avisa. Nunca "resolver" contornando a trava.
- **Uma cobrança por dia no máximo**, e nunca no mesmo dia de pagamento recém-detectado.
- **Feriado não é dia útil:** o cálculo só considera seg–sex; feriado nacional precisa de ajuste
  manual na data marcada.
- **Regra da casa:** nada de emoji no texto ao cliente; assinatura fixa em `config.assinatura`.

## Antes de implementar

Quando o dono pede para "transformar em rotina mais robusta", ele quer **primeiro** o
entendimento confirmado do caso concreto + o rascunho da política em até 10 bullets. Só depois
do ok explícito se escrevem scripts e se reprograma cron.
