---
name: cobranca-cliente-aprovacao
version: 1.0.0
description: "Use ao cobrar cliente inadimplente: escalada aprovada."
type: Orchestrator
timestamp: 2026-11-04T21:00:00Z
---

# Cobrança de cliente — escalada com aprovação

Política fixada pelo dono em 04/11/2026 depois do caso Solution Master. Substitui a cobrança
diária automática que enviava texto sem revisão.

## Regra zero

**Nenhum e-mail de cobrança sai sem aprovação registrada do texto exato** (assunto +
destinatários + corpo). Aprovar um template não aprova um texto renderizado diferente: a
aprovação é por hash do texto final. Sem aprovação, o envio não acontece — e o silêncio
não é opção: o job avisa que faltou aprovação.

## Tom do texto (registro do dono, 04/11/2026)

**Neutro e direto.** Sem "prezado", sem parágrafo explicando a relação ou o valor do
serviço, sem discurso de parceria. Estrutura: fato verificável (parcela, NFS-e, valor,
vencimento, dias úteis em aberto) → o que o cliente disse e não cumpriu, em uma frase →
**um pedido objetivo** (data do pagamento ou comprovante) → dados de pagamento → assinatura.
O argumento "o que a parcela sustenta" existe em `config.descricao_entrega` e fica
**guardado para o nível 3**, quando o dono autorizar: não entra na cobrança de rotina.

## Antes de escrever o texto (não pule)

1. **Extrato primeiro.** O pagamento pode ter caído. Cobrança enviada a quem já pagou é
   dano de relação, não erro técnico. Falha de leitura do extrato = **não cobra**, avisa.
2. **Leia o contexto do cliente:** a thread da cobrança/NFS-e **e** os últimos e-mails do
   domínio do cliente (qualquer assunto, ~30 dias). Quem respondeu, quando, o que prometeu.
   - Promessa com data vira `prazo_prometido`; promessa sem data ("em breve", "vamos
     informar uma previsão") **não** é prazo — e o texto deve cobrar exatamente isso.
   - Data já vencida citada em e-mail antigo não é prazo novo.
3. O texto referencia a última resposta real do cliente (data + quem), nunca uma promessa
   inventada. Se não houver resposta, o texto não menciona resposta.

## Escalada (níveis)

| Nível | Quem | Papel |
|---|---|---|
| 1 | financeiro + coordenador financeiro | cobrança objetiva |
| 2 | gestor direto / dono | escalada: prazo não cumprido e previsão não informada |
| 3 | representante legal | **só com autorização explícita do dono** |

Intervalo padrão entre níveis: **2 dias úteis** (`politica.dias_uteis_entre_niveis`).

**Ramo A — sem prazo novo:** cobra no nível atual na data marcada; sem resposta em 2 dias
úteis, sobe um nível.

**Ramo B — prazo novo declarado:** lembrete **no dia do prazo**, com valor, Pix, NFS-e de
referência e oferta de reenviar a nota. Não pagou → cobra em **D+1** e reinicia no nível 1.

## Fila de aprovação (D-1)

O rascunho é preparado com **1 dia útil de antecedência** e apresentado ao dono com o texto
inteiro. Aprovação é explícita ("aprovado"). Se a aprovação não chegar, **não envia**.
Incluir destinatário novo (cc, sócio, gestor) é **nova aprovação**.

Se o contexto mudar depois do rascunho (prazo novo, resposta, pagamento), o rascunho antigo
fica **obsoleto** e é refeito — o envio reconfere o plano na hora e recusa o texto velho.

## Como operar

Tudo vive em `$HERMES_HOME/work/cobranca-<cliente>/` (config, estado, fila, aprovacoes, log)
e o motor é `$HERMES_HOME/scripts/cobranca_fluxo.py` + wrapper `cobranca_fluxo.sh`.
Wrapper: extrato → `pago` se caiu → `enviar` (só aprovados vencidos) → `preparar` (D-1).

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

Copie `work/cobranca-sm/` para `work/cobranca-<sigla>/` e ajuste `config.json`:
`cliente`, `dominios_cliente`, parcela/contrato/valor/vencimento/NFS-e, `thread_id` (thread da
nota ou da última cobrança), `niveis` (to/cc/tratamento de cada nível), `descricao_entrega`
(o que a parcela sustenta — argumento da escalada) e `politica`. Zere `estado.json`
(`enviados`, `pago`, `cobranca_atual`) e a `fila/`. Rode `COBRANCA_CLIENTE=<sigla> ... status`.

## Armadilhas (custaram erro de verdade)

- **Saudação e datas pelo horário do ENVIO, não do rascunho.** Rascunho escrito à noite para
  envio às 9h: "Bom dia" e a data do dia do envio. `"até hoje"` com a data de ontem é erro
  na cara do cliente.
- **Thread forçada:** envie com `threadId` explícito e `In-Reply-To`/`References`; lembrete
  em fio novo fica fora da conversa da nota, onde o financeiro olha. Depois releia a
  mensagem e confirme `SENT` **e** a thread.
- **Não confunda promessa com prazo.** "Vou falar com a diretoria / em breve informamos" não
  é data; tratá-la como prazo descumprido queima o argumento.
- **Não escale quem já escalou.** Antes de subir de nível, cheque o histórico: se o nível 2
  já recebeu e respondeu, a próxima mensagem a ele cobra a promessa dele, não repete a
  primeira.
- **Uma cobrança por dia no máximo**, e nunca no mesmo dia de pagamento recém-detectado.
- **Fail-closed:** hash divergente, falta de aprovação, extrato ilegível, plano mudado → não
  envia e avisa. Nunca "resolver" contornando a trava.
- Fins de semana e feriados: o cálculo de dias úteis só considera seg–sex; feriado nacional
  precisa de ajuste manual na data marcada.
- Regra da casa: nada de emoji no texto ao cliente; assinatura fixa em `config.assinatura`.
