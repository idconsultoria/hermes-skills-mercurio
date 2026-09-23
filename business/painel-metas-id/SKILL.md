---
name: painel-metas-id
description: "Use when gerar painel de metas ou slide da Phronesis (ID)."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ID, metas, painel, phronesis, slide, symplexis, cron, html]
    scopes: [id]
type: Reference
timestamp: 2026-09-21T00:00:00Z
---

# Acompanhamento de metas da ID — painel e slide da Phronesis

Dois artefatos da mesma fonte: o **painel de metas** (dashboard de acompanhamento) e o
**slide semanal da Phronesis** (reunião de operações). Os dois leem a **mesma planilha** e
o slide importa o motor do painel — número digitado à mão em qualquer um dos dois é erro.

## Quando usar

- Gerar/atualizar o painel de metas da ID.
- Preparar ou revisar o slide da Phronesis (reunião semanal de operações).
- Responder "como estão as metas?" com dado da planilha.
- Mexer nos crons que produzem esses artefatos.

## Fonte de verdade e acesso

- Planilha **[ID] Gestão de Symplexis** (`1qV_L-WMOMDKQwIgLj_l9frokFVO032nsVbM_Qbw8kR0`),
  abas `contratos`, `recebimentos`, `symplexis`.
- Interpretador que tem `googleapiclient`: `/opt/mercurio-data/id-nfse-motor/.venv/bin/python`.
- Token: `$HERMES_HOME/google_token.json` (admin@idconsultoria.ai, escopo Sheets).
- Detalhes de planilha, tokens e vínculo de parcela recebida: skill `gestao-financeira-id`.

## Regra do ciclo (manda em tudo)

**As metas contam somente contratos NOVOS.** O corte fica em `corte_novos_contratos` no
`metas.json` — contrato assinado antes do corte é **carteira herdada**: entra no painel como
caixa real, mas não abate meta. Um gerador que some tudo e mostre progresso de meta com
receita herdada está mentindo sobre o avanço do ciclo.

**Exceção única (fixada em 21/09/2026 pelo sócio):** a meta de **entrada de caixa mensal**
mede o caixa **efetivado no mês, de qualquer natureza** — recorrência ou parcela, de contrato
novo ou da carteira herdada. Caixa é caixa; conquista do ciclo é contrato novo. É a única meta
que a carteira herdada abate — todas as outras (faturamento, nº de contratos) seguem contando
só contrato novo.

Classificação por contrato (função `classificar` do motor):

| Situação do contrato | Balde |
|---|---|
| Assinatura a partir do corte | `novo` (conta para meta) |
| Assinatura antes do corte | `herdado` |
| Sem data de assinatura, mas com movimento financeiro antes do corte | `herdado` (fallback — se já recebeu antes do corte, já estava em execução) |
| Sem data e sem movimento | `indeterminado` — corrigir a **planilha**, não o painel |

Contrato em andamento sem data de assinatura é dívida de dado: o painel avisa e o trabalho é
preencher a data na Symplexis.

## Como rodar

Painel (gera HTML versionado + histórico + resumo no stdout):

```bash
/opt/mercurio-data/id-nfse-motor/.venv/bin/python \
  /opt/mercurio-data/painel-metas/painel_metas.py [--pdf] [--json] [--sem-html] [--hoje AAAA-MM-DD]
```

- `--json --sem-html --sem-historico` = só leitura, para responder "onde estamos".
- `metas.json` é onde a meta muda (alvo, prazo, métrica, metas manuais). Mudar meta é decisão
  do sócio, não do agente.
- Saída: `saida/painel-metas-id-<AAAAMMDD-HHMM>.html` (nunca reaproveita nome), `saida/ultimo.html`
  (symlink), `saida/historico.jsonl` (uma linha por execução, com os baldes novo/herdado).

Slide da Phronesis (importa o motor do painel; ver `references/phronesis-slide.md`):

```bash
/opt/mercurio-data/id-nfse-motor/.venv/bin/python \
  /opt/mercurio-data/phronesis-slide/montar_slide.py [--data AAAA-MM-DD] [--sem-metas]
```

Wrapper para cron: `bash /opt/mercurio-data/scripts/phronesis_slide.sh [AAAA-MM-DD]` — imprime
caminho do deck, contagem de slides e flags de sanidade (`TEM_METAS`, `TEM_GRAFICO`, `TEM_ATAH`).

## Execução sob demanda (slide da Phronesis)

O slide **não é mais um job recorrente**. O cron `phronesis-slide-semanal` (`ee87da776417`)
foi **desativado por decisão do dono** — gerar e entregar o deck é ação **sob demanda**,
executada quando alguém pedir (antes da reunião de operações ou em uma sessão de trabalho).

Fluxo a seguir quando pedirem o slide:

1. Definir a data: por padrão, a **próxima segunda** (é o dia da Phronesis); com `--data` se a
   reunião for em outro dia.
2. Rodar o wrapper (ele imprime caminho do deck + sanidade):
   `bash /opt/mercurio-data/scripts/phronesis_slide.sh [AAAA-MM-DD]`
3. **Conferir o `STATUS` antes de anunciar.** Exigir `STATUS=OK`, `QTD_SLIDES` coerente e
   `TEM_METAS=1`, `TEM_GRAFICO=1`, `TEM_ATAH=1`. Qualquer um zerado = deck incompleto, refazer.
4. Entregar o HTML com `MEDIA:<caminho absoluto>` como **primeira linha** da resposta (sozinha).
5. Se a planilha estiver indisponível, regerar com `--sem-metas` e **dizer no texto que a seção
   de metas ficou de fora** — nunca entregar deck incompleto em silêncio.

Não recriar o cron sem pedido explícito do dono. Se recriar, **pine `--provider` e `--model`**
(job sem pin vira `drift_skip:silent` quando o provider global muda).

## Crons

| Job | Quando | Papel |
|---|---|---|
| `phronesis-slide-semanal` | **desativado** | era a geração semanal do deck; virou execução sob demanda (seção acima) |
| `phronesis-semanal` | terça 11:00 UTC | **depois** da reunião: detecta a Phronesis no Fathom e cria ata/transcrição no Drive |

- **Sempre pine `--provider` e `--model` ao criar cron neste host**
  (`hermes cron edit <job_id> --provider opencode-go --model deepseek-flash`). Job sem pin vira
  `drift_skip:silent` quando o provider global muda: ele para de rodar sem avisar ninguém, e o
  sintoma aparece dias depois como "o ritual não aconteceu".
- Antes de confiar no pin, confira o par na lista de modelos do provider
  (`provider_models_cache.json`) — pin órfão falha na primeira execução.
- Entrega recorrente para os sócios e criação de cron são ações de efeito externo: propor e
  esperar o ok explícito.

## Entrega da ata aos sócios — o rito da Sessão 2 do planejamento

O `phronesis-semanal` existe por causa de uma decisão da 2ª sessão do planejamento estratégico:
**entrega individualizada da ata no privado de cada sócio, com confirmação de leitura** — o
gatilho combinado é a reunião de operações (segunda), logo o rito é semanal. Nasceu do risco nº 1
apontado nas duas sessões, "ignorar oportunidades": o que era decidido na reunião não era
revisitado por ninguém depois.

Meia implementação, hoje:

| Combinado | Estado atual |
|---|---|
| Ata + encaminhamentos no **privado de cada** sócio | o job entrega **um texto idêntico** aos quatro (origin + os 3 sócios); individualizar exige **envio separado por destinatário**, porque o `deliver` do cron manda o mesmo corpo para toda a lista |
| **Confirmação de leitura** ("só pare de mandar quando eu falar li") | não existe mecanismo — nenhuma cobrança repetida até o "li" |

- **Ao explicar o rito, separe combinado × implementado** e diga o que falta: a decisão consta na
  ata como ação "em andamento", e é exatamente essa diferença que o sócio cobra depois.
- Individualizar a entrega é **efeito externo** para os outros três sócios: propor e esperar ok
  explícito antes de mexer no job.
- Lembre que o texto único existe para caber no `deliver`: por isso o corpo leva o bloco
  "encaminhamentos por pessoa" com os quatro sub-blocos, em vez de quatro mensagens.

## Mudar a definição de uma meta — o que move junto

Mudar a régua de uma meta (alvo, métrica, o que conta) é decisão de sócio, mas a **execução da
mudança é do agente** — e ela não vive num arquivo só. Na mesma passada:

1. `metas.json` — `descricao` da meta, `regra_das_metas` e, se for meta manual, o `responsavel`.
   Registre na própria descrição **a data e quem fixou** (a régua tem dono, não é preferência).
2. `painel_metas.py` — o mapeamento em `valores_meta` (a métrica), **o texto do alerta** que fala
   daquela meta, os títulos/parágrafos de regra do HTML e as linhas de `resumo_texto`. Texto que
   ficou para trás vira alerta mentiroso no painel do sócio.
3. Os documentos que citam a régua — o `README.md` e o `AGENTS.md` do projeto SPV declaram a
   mesma regra: **painel e manual não podem contar histórias diferentes**.

**Como provar que a mudança funciona** (não basta o rótulo ter mudado): rode o painel numa data
em que a nova regra produza número diferente da antiga — `--hoje AAAA-MM-DD` num mês com
recebimento da carteira herdada. Uma meta que mede caixa de qualquer natureza sai de R$ 0 para
o valor daquele mês; se o número não mudar, a agregação não foi trocada.

**Teste sem sujar o histórico:** `--out-dir /tmp/<dir>` gera HTML e histórico em diretório
descartável, deixando `saida/` e o `historico.jsonl` oficiais intactos. Lembre que, depois da
mudança, a linha nova no histórico mede coisa diferente da anterior — comparação de série
atravessa a régua e precisa da ressalva.

## Pitfalls

- **Parcela "Recebido" sem data efetuada não entra em nenhum total.** Na Symplexis a data é
  fórmula que resolve pelo ID da transação; marcar só o status deixa a parcela fora do ano.
  Ver o procedimento de vínculo na skill `gestao-financeira-id`.
- **Nada de número inventado.** Todo valor sai de linha da planilha, do `metas.json` ou do
  `historico.jsonl`. Se o dado não existe, diga "não está na planilha" — não estime sem marcar
  a estimativa como tal.
- **Não confunda "mundo real" com "progresso de meta".** Os dois números convivem no painel e
  no slide (carteira herdada é caixa, não conquista do ciclo) — apagar essa distinção destrói a
  utilidade do artefato.
- **Meta manual** (ex.: novos canais de venda) só muda em `metas.json`; o painel não a deduz da
  planilha e marca `a registrar` enquanto ninguém atualizar.
- **NPS sem instrumentação**: a planilha tem a coluna nos symplexis e ela costuma estar vazia —
  o painel denuncia; nunca preencha por inferência.

## Arquivos de apoio

- `references/phronesis-slide.md` — estrutura do deck, identidade extraída do modelo de
  proposta, o que já está pronto e o que depende de processo (funil/CRM).
- `references/render-html-para-pdf.md` — gerar PDF destes HTML e verificar de verdade (o que o
  motor de impressão não suporta e como medir onde o layout estourou).
