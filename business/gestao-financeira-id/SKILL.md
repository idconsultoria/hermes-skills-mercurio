---
name: gestao-financeira-id
description: "Operar planilhas/Google da ID, classificar receita e fazer backfill de extrato."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ID, finanças, planilha, Google, Sheets, Drive, Symplexis, backfill, token]
    scopes: [id]
type: Reference
timestamp: 2026-08-19T14:00:00Z
---

# Gestão financeira da ID — planilhas, acessos Google e backfill

Como operar e auditar o mundo de dados financeiros da ID Consultoria: as duas planilhas
mestras, o mapa de **tokens Google** (qual arquivo cobre Sheets/Drive — fonte comum de erro),
e o método de **backfill** da planilha de extrato. A consulta em si à API do Banco Inter
fica na skill irmã `inter-api-id-consultoria`.

## Quando usar

- Auditar/atualizar a planilha de **Gestão Financeira** ou a de **Symplexis** (engagements).
- Ler/escrever Google Sheets ou Drive da ID e precisar do **token certo**.
- Fazer **backfill** do extrato/saldo (a automação só alimenta "ontem"; atrasos exigem isso).
- Investigar de onde vêm os dados (conexões IMPORTRANGE entre as planilhas).

## Planilhas e conexão

| Planilha | ID | Papel |
|---|---|---|
| **[ID] Gestão Financeira** | `1cOMQM2B1ircEdFJ5iiAGiUO7-Mx_qSo51uWDRtAV_gE` | painel de controle financeiro (23 abas): extrato/saldo Inter + classificação + relatórios |
| **[ID] Gestão de Symplexis** | `1qV_L-WMOMDKQwIgLj_l9frokFVO032nsVbM_Qbw8kR0` | planilha-mestra dos **engagements** ("symplexi" = entrega): 13 abas (clientes, contratos, symplexis, recebimentos, sankeys, __projetos, _transações) |

**Conexão bidirecional via IMPORTRANGE:**
- Gestão Financeira importa da Symplexis: `_projetos` (`__projetos!A:Z`) e `_recebimentos` (`recebimentos!A:Z`).
- Symplexis re-importa da Gestão: aba `_transações` (`transações!A:AB`). Overlap verificado = 100%.

**Fluxo do ciclo:**
`Automação iData (Banco Inter) → CCI_* da Gestão Financeira → aba transações (classificação)
→ _transações da Symplexis` ; projetos/recebimentos vão da Symplexis → Gestão Financeira.

## Camadas da Gestão Financeira (23 abas)
1. **Cadastro**: `parâmetros`, `contas`, `_projetos`, `_recebimentos`
2. **Dados brutos API**: `CCI_extrato`, `CCI_saldo`, `CCI_detalhes_PIX/PAGAMENTO/COMPRA_DEBITO/OUTROS`, `extrato_para_verificação`
3. **Gestão/classificação**: `transações`, `pagamentos`, `recebimentos`, `pagamentos_e_recebimentos`, `Sheet14`
4. **Relatórios**: `Lucro bruto por projeto`, `FL por projeto`, `margem_bruta_por_projeto`, `DRE`, `sankey_tabelas`, `Proventos`, `projeção_de_caixa`

Quando a Symplexis está desatualizada, a fonte de verdade dos engagements novos é o Drive
`ID → 4. Operação → 4.2. Symplexis/` (subpastas 4.2.x por cliente). Emails de contrato/NF de
parcela em `admin@idconsultoria.ai` reconstroem recebimentos recentes.

## Leitura read-only — conferir ANTES de escrever

`scripts/id_sheets.py` lista abas e faz dump/filtro de qualquer planilha da ID usando o token
admin e o venv que já tem `googleapiclient`. É o caminho mais rápido para responder *"a
entidade X existe na planilha?"* antes de tocar em qualquer célula:

```bash
PY=$HERMES_HOME/id-nfse-motor/.venv/bin/python
S=$HERMES_HOME/skills/business/gestao-financeira-id/scripts/id_sheets.py
$PY $S abas  <SPREADSHEET_ID>
$PY $S find  <SPREADSHEET_ID> "recebimentos" "assistentes"   # procura termo (sem acento/caixa) e imprime linhas
$PY $S dump  <SPREADSHEET_ID> "transações" FORMULA          # render: FORMATTED_VALUE (default) | FORMULA | UNFORMATTED_VALUE
```

- **Redirecione o dump para um arquivo do `work/` e analise em Python** quando a aba passa de
  ~100 linhas (a `transações` tem 820+). Ler dump gigante no chat é caro e não escala; `grep`
  por coluna, `collections.Counter` para achar os valores válidos de uma coluna.
- O índice de coluna é **absoluto desde A** — o cabeçalho só ajuda se você contar a partir da
  coluna A, nunca a partir de um range recortado (`E1:M`).

## Lançar faturamento — a pré-condição é o projeto existir

Antes de lançar receita, confirme que **o projeto/contrato existe**: catálogo em `__projetos`
(Symplexis) e lista validada na coluna `projetos` da aba `parâmetros` (Gestão Financeira).
Sem isso a receita não tem para onde ir — `recebimentos` resolve cliente/contrato por VLOOKUP
e o relatório por projeto não enxerga o que não está no catálogo.

- **Padrão ausente = avisar, não executar.** Criar contrato/projeto novo é decisão do dono
  (fora da rotina): relate o que existe, o que falta e as opções, e só escreva depois do ok
  explícito. Criar contrato "para não deixar o crédito solto" contamina catálogo, painel de
  metas e DRE.
- **Produto educacional (Jornada de IA / turmas de curso) não tem casa na Symplexis.** Venda de
  vaga a pessoa física não é contrato de cliente: entra como **transferência de outra conta da
  própria ID** (Nubank → Inter) e o que a venda é de fato vem só na `descricaoPix`. Não force o
  modelo de contrato/parcela para representá-la sem decidir isso com o dono.
- **Transferência entre contas da mesma titular não é faturamento.** Se o pagador do PIX é o
  **próprio CNPJ da ID** (`cpfCnpjPagador` = CNPJ da ID, `nomeEmpresaPagador` = `NU PAGAMENTOS - IP`),
  a perna do Inter é movimentação interna: classificar essa linha como `Receita / Faturamento`
  registra a transferência, não a venda — a planilha não acompanha a conta de origem, e a
  receita passa a ser contada onde não nasceu. Leve a decisão ao dono antes de classificar.
- **Não deduza o que o crédito é comparando com preço de tabela.** Preço praticado, desconto
  negociado, sinal e pagamento parcial produzem valores fora da tabela: pergunte o que o valor
  representa em vez de inferir.

Colunas de `transações`, vocabulário de status e os valores válidos de classificação estão em
`references/classificacao-de-receita.md`.

## Acessos Google — mapa de TOKENS (CRÍTICO)

Cada token cobre apenas os escopos com que foi autorizado. **Verifique os `scopes` do token
antes de chamar a API** — usar o errado dá `invalid_scope`/`403`.

| Arquivo token | Conta | Escopos |
|---|---|---|
| `google_token.json` | admin@idconsultoria.ai | token admin **atual** das demandas da ID — ao ser restaurado vinha com Gmail + Drive + Sheets + Docs + Calendar |
| `google_token.admin_idconsultoria.json` | admin@idconsultoria.ai | Gmail + **Drive + documentos** (lê planilha OK) |
| `google_token.gustavo_idteal.json` | gustavo.idteal@gmail.com | só Gmail |
| `google_token.backup_gustavomelloenciv.json` | gustavomelloenciv@gmail.com | full (Drive + spreadsheets + docs + gmail) |

- Para Sheets/Drive da ID use **`$HERMES_HOME/google_token.json`** (admin@idconsultoria.ai) e o interpretador **`$HERMES_HOME/id-nfse-motor/.venv/bin/python`** — é o venv deste host com `googleapiclient`/`google-auth` instalados. **Leia `d.get("scopes")` do arquivo antes de chamar a API**: usar escopo a menos dá `invalid_scope` no refresh, e conta sem escopo dá 403 — carregue sempre com `Credentials.from_authorized_user_info(d, d.get("scopes"))`.
- A service account do repo iData (`service_account.json`, escopo drive) lê a Gestão
  Financeira (compartilhada), mas **não** a Symplexis (404) — a Symplexis exige token admin.
- Toda entrega visual ao principal ID sai em **HTML** na identidade da ID (skill `id-design-guide`).

## Marcar parcela como recebida na Symplexis (vínculo por transação)

Na aba `recebimentos`, **a coluna `Data efetuada` é fórmula**, não campo de digitação:
`=IF(ISBLANK(Hn);;VLOOKUP(Hn; '_transações'!$C$2:$D; 2; 0))` — ela resolve a data pelo
**ID da transação** lançado em `iD.Transação` (coluna H). Para registrar um recebimento:

1. Ache a transação real no extrato (`CCI_extrato` da Gestão Financeira) casando **valor +
data**; guarde o `iDtransação` **completo** (base64 longo — copiar truncado quebra o VLOOKUP).
2. Escreva na linha da parcela: `Status` = `Recebido` e `iD.Transação` = o ID da transação.
3. Se a linha **não** tiver a fórmula em `Data efetuada` (linhas antigas costumam não ter),
   copie a fórmula de uma linha irmã do mesmo bloco e troque a referência de linha — o
   separador é `;` (locale pt-BR), não `,`.
4. Registre a origem em `Observações`: quem informou, quando, e a data da transação.
5. Confira relendo com `values().get` (valor renderizado): a data efetuada deve aparecer.

Nunca escreva nas colunas de fórmula (`A`, `G`, `J`, `K`, `L` em `recebimentos`) — só
`Status`, `iD.Transação` e `Observações` são dados. Sem o vínculo, uma parcela marcada como
recebida continua **sem data** e não entra em nenhum total por ano/mês.

Status possíveis em `recebimentos`: `Recebido` (confirmado por gente), `confirmado por IA`
(vinculado pela automação, muitas vezes sem data resolvida) e `Por receber` (em aberto).

## Todas as contas: Inter + Nubank (fonte de dados e modelagem da DRE)

A Gestão Financeira enxerga **só a conta Inter** (`contas` cadastra uma conta; a aba `transações`
tem 33 colunas e nenhum movimento de cartão). A outra conta da ID é **Nubank** — corrente
(conta 9900030663) + cartão de crédito — e a movimentação dela está no Drive:

| O que | Onde |
|---|---|
| Raiz | `ID → … → **ID.TEAL - Nubank - Corrente e Crédito**` (`1NxII6mIc31muKjJPlSwBH-ekEqUjVw9y`), subpastas por mês (jun/2024 → set/2026) |
| Extrato da conta | `Extrato/` de cada mês — **CSV + OFX + PDF** |
| Fatura do cartão | `Fatura/` — `Nubank_AAAA-MM-22.pdf` (ago/2024 → set/2026) |

- **Parseie o CSV do extrato, não o PDF**: cabeçalho `Data,Valor,Identificador,Descrição`
  (dd/mm/aaaa; valor com ponto decimal; **negativo = débito**; `Identificador` = UUID na Nu).
- **Fatura**: `pdftotext -layout` (existe neste host) e leia as seções `TRANSAÇÕES DE X A Y`
  (compras, IOF, juros, multa, renegociação) e `Pagamentos e Financiamentos`; linhas no formato
  `DD MMM •••• 1234 <descrição> R$ 0,00`, com o sinal de crédito em `−`/`—`.
- **Transferência entre contas da mesma titular não é receita nem despesa.** As contas se cruzam
  (ex. 28/09/2026: a Nu recebe R$ 2.800 e o Inter paga R$ 2.800 de "Pagamento de cartão e
  empréstimo"). Marcar a transferência interna e **excluir da DRE**, senão receita e despesa dobram.
- **A DRE depende de composição, não só de valor**: a aba `DRE` é **tabela dinâmica** sobre
  `transações` (competência nas colunas). Modelo novo só aparece lá se preencher
  `Composição no Lucro Líquido / EBITDA / OPEX-ou-LB` — e "Tarifas Bancárias" já é categoria
  existente para taxas.
- **Taxa de parcelamento do cartão precisa do par bruto + taxa** para aparecer na DRE sem falsear
  o resultado (o dono pediu que apareça): lançar só a despesa derruba o resultado em valor que não
  é queda real.
- **Estado ao iniciar a remodelagem (15/10/2026)**, para não redescobrir: 23 abas; **449
  transações "A processar"**; erros em `CCI_extrato` (154 × `#VALUE!`), `transações` (6 × `#N/A`)
  e `Sheet14` (72 × `#N/A`, 302 linhas — parece tentativa anterior de remodelagem, do mesmo
  formato da `transações`).

## Receita de produto educacional (Jornada de IA) — casa das turmas

A Jornada de IA (cursos 1/2/3) vende vaga a **pessoa física**, sem contrato de cliente —
modelo aprovado pelo dono em 15/10/2026 ("casa das turmas"), já em produção:

| Onde | O que é |
|---|---|
| `clientes` | cadastro agregado **`Alunos PF`** (não é empresa; as vagas são por pessoa) |
| `contratos` | **`JD1` "Jornada de IA"**, cliente `Alunos PF`, `Em andamento`, sem data de assinatura (não há instrumento); `Valor total` = **acumulado das vagas vendidas**, explicado em `Observações` |
| `symplexis` | **um symplexi por turma** — ex. `JD1-1` "Curso 2 - Assistentes de IA (turma outubro/2026)" |
| `recebimentos` | **uma linha por vaga vendida** sob `JD1` (não agrupar), `Status=Recebido`, `iD.Transação` = crédito no Inter (resolve a `Data efetuada`) |

Regras que a venda impõe:

- **O valor da parcela é o preço cheio pago pelo aluno** (ex. R$ 1.497,00 = Curso 2). No cartão, o
  crédito que chega ao Inter é **líquido da taxa de parcelamento** (~15%; ex. R$ 1.272,60, taxa de
  R$ 224,40). Registre o cheio no recebimento e cite o líquido na `Observações` — a taxa não tem
  perna no extrato, então não existe transação para ela.
- **Reconhecimento é pela entrada no Inter**, não pela conta Nu onde o dinheiro da venda cai
  primeiro (decisão do dono): o crédito é o evento de recebimento, inclusive quando o pagador do
  PIX é a própria ID (transferência entre contas da mesma titular).
- Na `transações` (Gestão Financeira) a linha do crédito vira
  `Centro de Custo=Receita` · `Dimensão=Recebimento` · `Categoria=Faturamento` ·
  `Sub-categoria=Parcela/Serviço` · `Projeto` = o detalhado do `__projetos`
  (`Alunos PF - Jornada de IA - Curso 2 - Assistentes de IA (turma outubro/2026)`) ·
  `Mês de competência` · `Q/R/S = Resultado Operacional / Lucro Bruto / Faturamento Líquido` + `Racional`.
- Consequência contábil a declarar ao dono: a Symplexis mostra o **faturamento bruto** (1.497) e a
  Gestão Financeira a **receita líquida** que entrou na conta (1.272,60); a diferença é a taxa de
  adquirência.

## Modelagem v2 — extrato unificado (3 fontes) + DRE por competência

A planilha passou a ter um segundo andar, ao lado do modelo antigo (que segue funcionando,
porque a Symplexis importa `transações` por IMPORTRANGE):

| Aba | Papel |
|---|---|
| `v2_extrato` | camada 1 — extrato unificado: **Inter** (iData), **conta Nu** (CSV) e **cartão Nu** (fatura PDF), com `conta`, `competencia`, `natureza`, `id_origem` |
| `v2_transacoes` | camada 2 — extrato + classificação (`categoria`, `subcategoria`, `projeto`, composições, `fonte`, `status`, `motivo`) |
| `v2_plano_de_contas` | composições (LL / EBITDA / OPEX ou LB) × categoria × sub-categoria |
| `v2_dre` | DRE por competência (SUMIFS sobre `v2_transacoes`), meses em `mmm-yyyy` |
| `v2_pendencias` | o que ficou para revisão humana (com motivo) |

Um comando roda tudo e entrega a DRE do mês em HTML na identidade da ID:

```bash
PY=/data/data/com.termux/files/home/capitolium/id-nfse-motor/.venv/bin/python
$PY /data/data/com.termux/files/home/capitolium/work/dre_id.py --mes 2026-09 [--baixar-nu] [--atualizar-inter]
```

Pipeline interno: `nubank_download.py` → `nubank_parse.py` → `fin_v2_etl.py` (consolida) →
`fin_v2_classificar.py` (julga) → `fin_v2_gravar.py` → `fin_v2_dre.py` → `fin_v2_reabilitar.py`
(classifica as linhas em aberto da aba `transações` antiga, casando por `iD.Transação`).

### Classificação é JULGAMENTO, não motor

Regra do dono (15/10/2026): **não existe motor de regras classificando transação**. O que existe:

1. **Symplexis como fonte primária da realidade financeira** — casar o crédito com a parcela em
   `recebimentos` (valor + janela de ~20 dias) dá categoria **e projeto** reais; o cadastro de
   `clientes`/`contratos` identifica a contraparte.
2. **Dicionário histórico** — a própria aba `transações` já classificada serve de evidência, mas
   **só com sinal compatível** (entrada nunca herda categoria de despesa).
3. **Decisões explícitas com motivo documentado** (contraparte + sinal), derivadas da Symplexis e
   da KB; script só **aplica em lote** o mapa auditável, gravando `fonte` e `motivo` por linha.

### Armadilhas validadas (custam horas se ignoradas)

- **A descrição do extrato do Inter é só o NOME da contraparte.** O texto que explica a transação
  ("Venda PF - Vaga no curso…", "Parcela do contrato Rural") está em `CCI_detalhes_PIX!D`.
  Sem ele, nenhuma classificação séria é possível.
- **A mesma contraparte pode ser cliente E fornecedor**: "Comercial Nascimento Lima Ltda" é o
  cliente Comercial Lima (créditos de R$ 9.000/20.000) e também a loja onde a ID compra em Propriá
  (débitos de R$ 20–140). Classifique pelo **sinal**, nunca pelo nome.
- **Renegociação de fatura é dívida, não despesa nova**: as parcelas de "Renegociação de
  pendências"/"Crédito de parcelamento" são principal de compras já reconhecidas — lançar como
  despesa duplica o resultado. Só juros/multa/IOF explícitos são despesa.
- **Valor gravado como texto faz o `SUMIFS` devolver 0** (texto é ignorado na soma). Converta para
  número (`float`) antes do `values.update`.
- **Cartão tem sinal invertido**: no PDF, compra é positiva; o efeito econômico é saída →
  grave `valor = -valor_doc`. "Pagamento em DD MMM" é o par do "Pagamento de fatura" da conta Nu
  (transferência interna) e "Saldo restante da fatura anterior" é carry-over (não é transação).
- **Datas do `CCI_extrato`**: as antigas vêm em `dd/mm/aaaa` e as novas em ISO — aceite as duas.
- **Transferências entre as contas da própria ID** (Inter ↔ Nu) aparecem como crédito de um lado e
  débito do outro; ficam fora do resultado e o resíduo da soma é efeito de **cobertura** das fontes
  (extrato da Nu começa em nov/2024), não erro de classificação.
- **Compras no cartão entram por competência da compra**; o pagamento da fatura é a perna interna.
- **Nunca criar regra genérica de "crédito de sócio → despesa".** Um padrão por contraparte +
sinal `+` captura também *empréstimo do sócio* e *devolução de lucro*, que são neutros: em
15/10/2026 isso inflou o resultado operacional em **R$ 16,7 mil** de forma artificial (o número
parecia plausível e só apareceu porque cada regra nova foi comparada com a DRE anterior).
Crédito de sócio sem descrição específica fica "A revisar".
- **Ao gerar relatório a partir da planilha, leia com `UNFORMATTED_VALUE`.** Com
  `FORMATTED_VALUE` o número volta como texto no locale da planilha (en-US: `R$ 75,562.53`) e
  qualquer conversor pt-BR lê `75,56` — truncou todos os totais do período na primeira versão da
  DRE em HTML. A chave de competência também pode voltar como **serial de data** (o Sheets
  interpreta `2024-01` como data ao gravar com `USER_ENTERED`): normalize com base 1899-12-30.
- **Texto começando com `=` é fórmula.** Rótulo de subtotal gravado como `"= LUCRO BRUTO"` virou
  `#ERROR!` na planilha. Use `TOTAL — LUCRO BRUTO`.
- **Relatório HTML: `<b>`, `<i>` e `<small>` são inline e colam.** No primeiro render, o valor do
  KPI apareceu colado na legenda (`R$ 1.497,00após imposto…`). Use `display:block` nos três.
- **`browser_exec` não abre `file://` nem o loopback deste container.** Para conferir visualmente
  um HTML local: Chromium compartilhado → `--print-to-pdf` → `pdfinfo` (páginas) → `pdftoppm` →
  `vision_analyze`. Nunca declarar pronto sem essa checagem (o overflow dos KPIs só apareceu aí).

### Fluxo de trabalho sugerido (manter a um comando)

| Quando | O quê |
|---|---|
| diário 07:00 | cron do iData já grava o extrato do Inter (`CCI_*`) — nada a fazer |
| semanal (10 min) | baixar no app do Nu o **CSV/OFX da conta** e o **PDF da fatura** do mês e jogar nas pastas do Drive `ID → 4. Operação → … Nubank → <mês>` (é a única etapa manual; o resto é comando) |
| mensal (dia 1) | `dre_id.py --baixar-nu --mes <mês anterior>` → HTML em `entregas/` |
| contínuo | revisar `v2_pendencias` (o que ficou "A revisar") e, se for caso recorrente, ensinar a decisão no mapa de julgamento |

### A classificação original da aba `transações` é EVIDÊNCIA PRIMÁRIA

O dono corrigiu (15/10/2026): *"na planilha antiga muitas dessas transações estavam corretamente
classificadas"*. Antes de reclassificar qualquer coisa, reconciliar:

1. Ler a aba `transações` e indexar por `iD.Transação` — **só** as linhas com categoria preenchida
   e cujo racional **não** começa com `[v2` (as com `[v2` foram escritas pelo agente na
   reabilitação e não valem como evidência, sob pena de ler de volta as próprias decisões).
2. Aplicar essa classificação como **camada 0**, antes do histórico e do julgamento.
3. Medir a divergência por categoria **e** sub-categoria (`v2_reconciliar.py`) e perseguir zero.

O que a reconciliação pegou de errado no julgamento automático (182 divergências, R$ 63,3 mil):
`Adiantamento de lucro` classificado como Folha/Pró-labore (é **Distribuição de lucro**, fora do
resultado — distorcia o operacional), `Adiantamento de pró-labore` como Pró-labore, `DARF - INSS`
como DARF federal em vez de Previdência, sub-categorias de faturamento (`Parcela/Serviço Adic.`,
`Parcela/Adiantamento`) achatadas em `Parcela de contrato`, e linhas legítimas deixadas em
"A revisar" (ex. `Pagamento Simples Nacional`). Resultado: pendências de 80 → 54 linhas.

**Atenção ao separar casar de classificar:** o casamento com a Symplexis precisa rodar em **todo
crédito**, mesmo quando a camada 0 já classificou a linha — é ele que materializa a taxa de
parcelamento (comparação parcela × crédito líquido). Com o casamento dentro do `if not cat`, o
ajuste de adquirência deixou de ser gerado (1.157 → 1.155 linhas, sem ninguém notar).

### O que ainda não tem lastro (fica em revisão)

Decisão do dono (15/10/2026) para o resíduo sem classificação: **usar o elo temporal**. Pagamento
pequeno (≤ R$ 100) a pessoa física, no Inter, em mês que já tem passagem/transporte classificado, é
passagem de visita — o padrão é Propriá / Comercial Lima, e o contrato do CL é escolhido pela
**vigência na data** (CL1 até 31/10/2024 · CL2 até 30/04/2025 · CL3 depois). Ao aplicar heurística
de pessoa física, **excluir descritores de transação** (`compra`, `pagamento`, `debito`, `pix`…) e
termos empresariais, senão "Compra no débito" entra como nome próprio — foi o que aconteceu.

## Registrar contrato NOVO na Symplexis (3 abas) — rotina validada

Contrato ganho entra em **três abas**, nesta ordem (a ordem importa: `recebimentos` resolve
cliente/contrato por VLOOKUP em `contratos`):

1. **`contratos`** — uma linha: A `iD` (ex. `SM2`), B rótulo curto do contrato, C cliente,
   D status (`Em andamento` / `Concluído`), E valor total, F data de assinatura, K observações,
   L `Oferta (código catálogo)`. H/I são chips.
2. **`recebimentos`** — **uma linha por parcela** (não agrupar), com B `iD.contrato`,
   C discriminação (`Parcela n/N - <contrato>`), D valor, E `Por receber`, F data prevista,
   I observações (cláusulas e condicionantes só na 1ª parcela). **A, G, H, K, L são fórmula** —
   A numera, G resolve a data por `iD.Transação`, K/L fazem VLOOKUP do contrato.
3. **`symplexis`** — um symplexi por frente: A `SM2-1`, B `iD.contrato`, D nome do symplexi,
   E consultor (people chip), F status, G prazo, H horas, I entregáveis. **C é fórmula
   (VLOOKUP do contrato) e L é fórmula** — não digitar.

Armadilhas que custam tempo se ignoradas:

- **A aba `symplexis` não tem linha sobrando**: a grade termina na última linha preenchida.
  Escrever em faixa fora da grade não é confiável → rodar `appendDimension` (`ROWS`, length N)
  **antes** do `values.update`.
- **Formato não vem de graça**: `USER_ENTERED` grava o número/data, mas a célula nova nasce
  sem formatação (valor aparece cru). Copiar o formato com `copyPaste` + `PASTE_FORMAT` da
  última linha preenchida para as novas linhas (não copia valor nem chip).
- **Locale pt_BR**: `USER_ENTERED` com `dd/mm/aaaa` vira data de verdade; valor monetário entra
  como **número** (string `R$ 1.000,00` é texto e some das somas).
- **Chips**: placeholder `@` + `chipRuns`; H = Doc (`application/vnd.google-apps.document`,
  normalizado para `.kix`), I = PDF (`application/pdf`, uri `.../file/d/<id>/view?usp=drive_link`).
- **A data de assinatura é a do documento, não a do e-mail.** Contrato enviado para assinatura
  às 16:30 de 14/10 estava datado 15/10 no corpo — é a data do instrumento que vale no painel.
- **A pasta `1.1.4. Contratos assinados` expõe id não-gravável neste ambiente**
  (`1O2XeV3DeyJvwc...NZCr`): leitura funciona, `files().create` com esse parent devolve
  `404 File not found`. Arquiva-se a via na pasta do contrato dentro de `4.2.14 <cliente>` e o
  chip aponta para lá; ao chegar a via final assinada pelas duas partes, mover para 1.1.4.
- **Conferência obrigatória em três camadas**: (a) reler `FORMATTED_VALUE` das linhas novas;
  (b) reler os `chipRuns` (o nome exibido tem que ser o do arquivo, não `@`);
  (c) rodar `painel_metas.py --sem-html --sem-historico` — se o contrato novo não aparecer em
  "Novos contratos", a data de assinatura não entrou ou ficou antes do corte.
- Salvar um **snapshot das faixas antes de escrever** (`valueRenderOption="FORMULA"` em JSON no
  work/) — é o rollback se algo desalinhar.

## Reconciliação automática: cron de parcelas pagas

O passo a passo acima virou rotina automática — `symplexis_conferir_parcelas.py` +
watchdog `watchdog-symplexis-parcelas.sh` em `$HERMES_HOME/scripts` (dispatcher em
`~/.hermes/scripts/`), agenda `25 7 * * *` em `no_agent`: **calado quando nada muda**.

Use o script, não a mão, para conferir parcelas abertas. Para alterar a regra de casamento
ou o layout, leia o script antes de mudar — estas invariantes existem por motivo:

- **A ordem dos dois crons não é arbitrária.** A reconciliação roda **depois** do iData
  porque só grava o vínculo quando o `iD.Transação` já existe na aba `_transações`;
  adiantar deixaria a fórmula de "Data efetuada" sem data — vínculo sem data não entra em
  nenhum total por ano/mês.
- **Casamento por valor + janela de data, cronológico e sem reaproveitar o crédito.** Sem
  o "sem reaproveitar", parcelas repetidas de mesmo valor (as 6× R$ 2.500 da SM1) se
  cruzam e marcam a parcela errada como paga.
- **Gravação restrita a colunas de dado** (E Status, H iD.Transação, I Observações) —
  nunca em coluna de fórmula.
- **Trava de layout:** compara o cabeçalho sem acento/caixa antes de gravar; coluna
  renomeada ou movida precisa dar falha explícita, não gravação na coluna errada.
- `SYMX_DRY_RUN=1` imprime o casamento sem gravar — rode antes de qualquer mudança de regra.

### Armadilhas ao escrever/leitura de valores e índices (validadas em produção)

- **Valor pt-BR:** `'R$ 3.446,99'` traz o separador decimal na **vírgula**. Trocar vírgula
  por ponto cegamente lê `3.44699` e o casamento silenciosamente não acha nada. Use a
  presença da vírgula para decidir o separador. E conversely: um valor ilegível numa linha
  em aberto é **falha explícita**, nunca "nada a fazer" — silêncio em rotina de conferência
  esconde o defeito.
- **Releitura de verificação começa na coluna A.** Se os índices de coluna são absolutos
  desde A (é o caso), reler de `E1:M` e continuar usando-os desalinha tudo e produz falso
  "vínculo sem data" em linha que gravou certo.
- **Formate valor em pt-BR com helper próprio.** O formato `{:,.2f}` do Python sai em
  en-US (`R$ 3,446.99`) e suja observação e relatório.
- **Data ambígua dd/mm com dia ≤ 12 entra como mês/dia.** `USER_ENTERED` com `01/10/2026` gravou
  **10 de janeiro**; só quando o dia passa de 12 (ex. `14/10/2026`) o Sheets resolve como dd/mm.
  Para qualquer data com dia ≤ 12 — em especial `Mês de competência` — grave o **serial**
  (base 1899-12-30; 2026-10-01 = 46296) com `RAW`, aplique `numberFormat DATE mmm-yyyy` e confira
  relendo `FORMATTED_VALUE` (tem que sair `Oct-2026`, não `Jan-2026`).
- **Na aba `transações` da Gestão Financeira, A, B, L, M e O são FÓRMULAS** (numeração, status,
  descrição do extrato, anexos, URL). Escreva só C–K (dados), N (pasta) e P–T (competência,
  composição e racional). O status das linhas classificadas é texto (`Processada`), ou seja,
  sobrescreve a fórmula — é o comportamento esperado, não um defeito.
- **Não misture planilhas num mesmo `values.batchUpdate`**: `transações`, `_projetos` e
  `_recebimentos` são da **Gestão Financeira**; `contratos`, `recebimentos`, `symplexis`,
  `clientes` e `__projetos` da **Symplexis** (que não tem aba `parâmetros`: a lista de projetos é
  `GF.parâmetros!F = {"Gestão Interna"; "Parcerias"; "Branding"; '_projetos'!E2:E}`).
- **`__projetos` (Symplexis) é 100% fórmula** (D = `{symplexis!D2:D}`) e a GF o importa: criar
  contrato + symplexi já publica o projeto em `_projetos` e na lista de validação — não se escreve
  nele, nem é preciso criar linha em `clientes` (o cliente do contrato é texto livre).
- **Localize a linha da transação pelo ID, nunca pela última linha**: em dia com mais de uma
  transação (14/10 teve crédito e débito) a última linha não é a da receita.
## Backfill da planilha (método validado 19/08/2026)

O `entrypoint_ingestão_inter.py` alimenta só **"ontem"**. Para cobrir atrasos:

```python
from etl.fluxos.alimentar_planilha_de_gestão_financeira import (
    alimentar_planilha_com_transações_do_período, registrar_saldo_do_período)
# para cada bloco mensal (ini, fim) na janela em atraso:
alimentar_planilha_com_transações_do_período(str(ini), str(fim))   # extrato + detalhes + pastas de anexos (Drive)
registrar_saldo_do_período(str(ini), str(fim))                     # saldo diário
```

- **Rate limit:** `obter_saldo` por dia dispara 429 no Inter → o motor espera 60s sozinho.
  Backfill de ~4 meses de saldo leva vários minutos → rodar em background
  (`terminal(background=True)` + `notify_on_complete`).
- **Verificação pós-backfill:** ler `CCI_saldo` (alvo = "ontem", gap 0) e datas máximas de cada
  aba `CCI_*`. Data de extrato para antes se não houve movimentação (não é buraco).
- **Idempotência:** após backfill, o cron segue de "ontem" sem duplicar.

## Ler FÓRMULAS (IMPORTRANGE / links)

`values().get` retorna valores **renderizados**, não fórmulas. Para detectar `IMPORTRANGE`,
use `valueRenderOption="FORMULA"` e varra **todas as colunas** (algumas abas têm 200+).

## Pitfalls
- **Google Sheets retorna 503 transitório no `append`/`update`** — um único 503 derruba o dia
  inteiro do cron iData se a chamada `.execute()` não tem retry. O `google_planilhas.py` do repo
  iData precisa de retry + exponential backoff em 429/5xx (500/502/503/504); erros permanentes
  (404, auth) devem falhar imediato. Corrigido no commit `9249e87` (wrapping `_executar_com_retry`
  em `update` e `append`). Diagnóstico rápido: `HttpError 503 ... The service is currently
  unavailable` = indisponibilidade transitória do Google, NÃO problema de cert/token/config.
- Escopos definem o acesso, não o nome do arquivo: confira `scopes` antes de chamar a API
  (refresh com escopo a menos = `invalid_scope`; escopo ausente na conta = 403).
- E-mail de parcelas/NFS-e ao cliente (cobrança) tem molde e histórico próprios — ver a
  seção "Envio da NFS-e ao cliente" da skill `emissao-nfse`.
- A skill irmã `inter-api-id-consultoria` cobre a API do Banco Inter em si (consultas/relatórios);
  esta cobre o ecossistema de planilhas e acesso. Ao usar o script dela
  (`scripts/inter_api.py`), passe **sempre** `--repo <clone vivo do iData>` e o venv ao lado do
  clone: o default do script aponta para um home que pode não ser o do perfil em uso, e a falha
  vem como `No module named 'etl'` — não é dependência faltando nem clone quebrado.
