---
name: auxiliar-adm-id
description: "Auxiliar admin da ID: contratos, planilhas, NFS-e, Drive."
version: 1.1.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ID, contratos, planilhas, finanças, NFS-e, Drive, email, admin, administração]
    scopes: [id]
type: Orchestrator
timestamp: 2026-09-27T02:00:00Z
---

# Auxiliar Administrativo da ID

Skill de **operação administrativa/financeira** da ID Consultoria: concentra o
conhecimento operacional de como acessar e usar as estruturas da ID (Drive, planilhas,
contratos, NFS-e, emails, API do banco). Serve de **ponte** entre uma demanda do
principal e a execução correta nas ferramentas da ID.

## Quando acionar

Acionar em demandas que envolvam:
- Elaborar, armazenar, atualizar ou consultar **contratos** (inclusive chips no Drive).
- Consultar ou editar **planilhas financeiras** ([ID] Gestão Financeira, [ID] Gestão de
  Symplexis).
- Buscar ou emitir **notas fiscais** (NFS-e da ID).
- Operar o **Drive da ID** (pasta 4.2 Symplexis, contratos assinados, etc.).
- Buscar informações nos **emails** (admin@idconsultoria.ai, gustavo.idteal@gmail.com).
- Consultar **extrato/saldo da conta Inter** (API do banco).

## Ferramentas de apoio (skills relacionadas)

- `inter-api-id-consultoria` — consultas/relatórios da conta Inter (extrato.read).
- `emissao-nfse` / `motor-nfse-id` — emissão de NFS-e/NF-e da ID via nfelib.
- `google-workspace` — Sheets/Drive/Docs/Gmail via API (OAuth).
- `analise-contratual` — revisão de contratos/minutas (LGPD etc.).
- `id-design-guide` — identidade visual de relatórios/entregas.

---

## 1 · Acesso Google (OAuth) — QUAL token usar

**HERMES_HOME = `/opt/mercurio-data`** (legado `/opt/data` descontinuado desde 27/08/2026). Todos os tokens ficam em `$HERMES_HOME/*.json` e o venv é `$HERMES_HOME/.venv` ou `id-nfse-motor/.venv`.

> **2026-09-01 11:08 UTC — estado real verificado:** `admin@idconsultoria.ai` **RECUPERADO** de `/home/ubuntu/selfhost/hermes/data/google_token_admin.json` no host Oracle (sem ligar contêiner `hermes_mercurio`) e restaurado em `$HERMES_HOME/google_token.json` (+ `.secrets/`). `gustavo.idteal@gmail.com` **RECRIADO via OAuth** em `$HERMES_HOME/google_token.gustavo_idteal.json` (refresh `1//06X0c7...`, validado `gmail.getProfile → gustavo.idteal@gmail.com`). `gustavomelloenciv@gmail.com` permanece **VETADO**.

| Token esperado | Conta | Escopos | Uso | Estado 01/09/2026 11:08 UTC |
|---|---|---|---|---|
| `$HERMES_HOME/google_token.json` (e `.secrets/google_token.json`) | **admin@idconsultoria.ai** | Drive+Sheets+Gmail+Calendar+Docs | **Drive/planilhas/contratos + Gmail admin** | ✅ ATIVO — `admin@idconsultoria.ai` (msgs 1663, refresh `042KPgOStXCe...`, origem Oracle `hermes/data/google_token_admin.json`) |
| `$HERMES_HOME/google_token.gustavo_idteal.json` (e `.secrets/`) | **gustavo.idteal@gmail.com** | Gmail+Drive+Sheets+Calendar+Docs (8 scopes) | **email financeiro — Nubank/Inter/Mercado Pago (extratos/faturas)** | ✅ ATIVO — `gustavo.idteal@gmail.com` (msgs 3117, refresh `06X0c7_Lvvm...`, recriado via OAuth 01/09/2026) |
| `gustavomelloenciv@gmail.com` | gustavomelloenciv@gmail.com | Drive+Sheets+Gmail completos | **FALLBACK PROIBIDO** — nunca usar para demandas da ID (determinação do principal 01/09/2026) | ⛔ VETADO — nenhum arquivo ativo o contém (verificado `grep -c gustavomelloenciv = 0`) |

**Regra de ouro (01/09/2026): NUNCA usar `gustavomelloenciv@gmail.com` para demandas da ID.** Usar exclusivamente `admin@idconsultoria.ai` (Drive + Gmail admin) e `gustavo.idteal@gmail.com` (Gmail financeiro). Se o `getProfile()` retornar `gustavomelloenciv`, abortar e pedir re-auth.

**CRÍTICO:** ao carregar um token, **usar os escopos que ele já possui** (`d.get("scopes")`), senão o refresh falha com `invalid_scope`.

Padrão de carregamento seguro (resiliente a HERMES_HOME):
```python
import os, json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
HH = os.environ.get("HERMES_HOME", "/opt/mercurio-data")
# admin — Drive
d=json.loads(open(f"{HH}/google_token.json").read())  # deve ser admin@idconsultoria.ai
# financeiro — Gmail
d2=json.loads(open(f"{HH}/google_token.gustavo_idteal.json").read())  # gustavo.idteal@gmail.com
for d in (d, d2):
    if not d.get("type"): d["type"]="authorized_user"
    c=Credentials.from_authorized_user_info(d, d.get("scopes"))
    if c.expired and c.refresh_token: c.refresh(Request())
```

## 2 · Drive da ID — estrutura e contratos

- **Raiz:** pasta `ID` (`1e_fvyB_gqI0fC1876lSQ3mpWcIMbPFcE`).
- **Engagements:** `4. Operação` → `4.2. Symplexis` → subpastas por cliente
  (`4.2.1. Comercial Lima`, `4.2.8. Cury`, `4.2.9. Real Invest`, `4.2.14. Solution Master`,
  `4.2.15. SergipeTec`, `4.2.16. Biotech SE`...).
- **Contratos assinados:** pasta `1.1.4. Contratos assinados` — PDFs assinados dos
  contratos. Os campos de "Contrato assinado" nas planilhas apontam para cá.
- Cada engagement tem pastas `Contrato N`, `Coletas`, `Entregáveis do Contrato`, etc.

**Contratos já mapeados (para reuso):**
| Cliente | Contrato | Minuta | Assinado |
|---|---|---|---|
| Comercial Lima CL3 | PRISMª | `PRISMª - Contrato` doc | `PRISMª - Contrato Assinado.pdf` |
| Solution Master SM1 | Blindagem de Processos | doc `1PGW8JD...` | PDF na 1.1.4 |
| Ravello RV1 | BI | doc | PDF na 1.1.4 |
| Sergipetec SP1/SP2 | Diagnóstico IA + Artemishub | doc | **físico** (a escanear) |

## 2.5 · Comprovantes e anexos (1.2.3) — extratos/faturas mensais das contas

Pasta `1. Gestão → 1.2. Finanças → 1.2.3. Comprovantes e anexos` (`1eTxFJbDt9942o1FDFxXkfCpIx-cjk9lP`).
Estrutura de trabalho mensal: subpasta **`Contas`** → uma pasta por banco → ano → mês.

Padrão de nomes/estrutura por banco (validado 20/08/2026 ao arquivar julho/2026):

- **Nubank** (`Contas/ID.TEAL - Nubank...` → `3. 2026` → `N. Mês`). Cada mês tem duas subpastas:
  - `Extrato/` → arquivos `66606f3e-…-AAAA-MM-DD-DA-DA-AAAA-MM-DD.{csv,ofx,pdf}` (uuid-EC-TCB do Nu Empresas).
  - `Fatura/` → `Nubank_AAAA-MM-DD.pdf` (data = vencimento da fatura).
  - Mês do ano-novo a criar se faltar (`7. Julho` etc.); numerar os meses (`1. Janeiro…`).
- **Inter** (`Contas/ID.TEAL - Inter...` → `2026` → `Mês`). Extratos O MÊS na **raiz** da pasta do mês,
  com nome `Extrato-DD-MM-AAAA-a-DD-MM-AAAA-{CSV,TXT,PDF,OFX}.ext` (4 formatos). Pastas `Dia NN`
  (comprovantes Pix diários) ficam ao lado, não mexer.

Fluxo de coleta mensal (origem: caixas de email → Drive):
1. **Inter:** email `no-reply@inter.co` "Seu extrato está disponível" chega ~dia 20 do mês seguinte e traz OS 4
   anexos do mês (CSV/TXT/PDF/OFX). Baixar todos e subir na raiz da pasta do mês.
2. **Nubank extrato:** email `todomundo@nubank.com.br` "Seu extrato da conta Nu Empresas" chega ~dia 1º do mês
   seguinte, com 3 anexos (`*uuid*-AAAA-MM-DD-AAAA-MM-DD.{csv,ofx,pdf}`) → subpasta `Extrato/`.
3. **Nubank fatura:** email "A fatura do seu cartão Nu Empresas está fechada" (~dia 15) traz anexo
   `Nubank_AAAA-MM-DD.pdf` → subpasta `Fatura/`.
- **Onde procurar:** esses emails de Nubank/Inter/Mercado Pago estão em **`gustavo.idteal@gmail.com`** (`$HERMES_HOME/google_token.gustavo_idteal.json`),
  NÃO na caixa admin. A caixa admin não tem Nubank/Inter.
- Buscar sem restringir `from:` demais — os remetentes variam (`no-reply@inter.co`, `todomundo@novidades.nubank.com.br`, `no-reply@mercadopago.com.br`).
  Ex.: `q="nubank newer_than:60d"` e `q="inter newer_than:60d"` acham tudo (Pix, fatura, extrato).
- **Upload usa o token Drive** `$HERMES_HOME/google_token.json` (**admin@idconsultoria.ai**) — nunca o fallback `gustavomelloenciv@gmail.com`.

Detalhes técnicos do Google API (download de anexo + upload) em `references/extratos-mensais-google-api.md`.
Mapa de IDs das pastas em `references/mapa-pastas-comprovantes.md`.

### Automação: `symplexis_conferir_parcelas.py` (cron diário `c073c0ae3ad2`)

Confere as parcelas da aba `recebimentos` contra o extrato do Inter e grava as que caíram
mas seguem em aberto. Agenda `25 7 * * *` (= 04h25 BRT, **depois** do iData das 07:00 UTC
que popula `_transações`), `no_agent` + watchdog `watchdog-symplexis-parcelas.sh`
(HERMES_HOME/scripts, dispatcher em `~/.hermes/scripts/`): **calado quando nada muda**.

Regras que o script impõe (não negociar):
- Casa crédito x parcela por **valor** (tolerância R$ 0,01) + janela de data, em ordem
  cronológica e **sem reaproveitar o mesmo crédito** — as 6 parcelas iguais de R$ 2.500
  da SM1 não se cruzam.
- Só grava quando o `iD.Transação` **já existe** na aba `_transações`; senão deixa para a
  rodada do dia seguinte (o VLOOKUP de "Data efetuada" ficaria sem data).
- Grava **só** E (Status), H (iD.Transação) e I (Observações). Colunas de fórmula (A/G/J/K/L)
  são intocáveis.
- **Trava de layout**: confere o cabeçalho (comparando sem acento) antes de gravar; coluna
  renomeada/movida = falha explícita, não gravação em coluna errada.
- Relê e exige `Status=Recebido` **e** `Data efetuada` preenchida — vínculo sem data é o
  defeito que a planilha não perdoa.
- `SYMX_DRY_RUN=1` simula e imprime o casamento sem gravar.

Pitfalls reais (encontrados 01/10/2026 ao criar o script):
- **`parse_valor` pt-BR**: `'R$ 3.446,99'` — Presence de vírgula é o que define o separador
  decimal. A versão ingênua (trocar vírgula por ponto) lia `3446.99` como `3.44699` e o
  script **saiu em silêncio fingindo que não havia parcela casada**. Regra: silêncio só
  quando houve leitura de verdade; linha aberta com valor ilegível = `falha()`.
- **Releitura de verificação deve começar na coluna A**: ler de `E1:M` e continuar usando
  os índices `C_*` (absolutos desde A) desalinha tudo e produz falso "vínculo sem data".
- `drv.files().list` logo após upload pode **não devolver o item recém-criado** (latência de
  indexação) — o OFX "sumiu" da verificação e estava lá, íntegro. Confirmar com
  `files.get(fileId)` + busca global por nome antes de reenviar (senão duplica).
- `brl()` para formatar: `{valor:,.2f}` sai em en-US (`R$ 3,446.99`); a planilha e os
  relatórios são pt-BR.

### Automação: conferência de parcelas (cron `c073c0ae3ad2`, 07:25 UTC)

Confere as parcelas da aba `recebimentos` contra o extrato do Inter e grava as que caíram
mas seguiam em aberto. **MODO AGENTE com gate de mudança** (`monitor` =
`coletar-symplexis-parcelas.sh`, `no_agent=false`, toolsets só `terminal`).

Desenho (escolha do Gustavo 02/10/2026 — "quero o agente, mas uso mínimo, sem gastar
tool call"):
- O cruzamento crédito×parcela é **aritmética, não interpretação** → fica no script. O
  agente recebe o cruzamento já pronto no prompt e só **decide e relata**.
- Dia sem novidade: o script imprime **uma linha constante** → hash igual → o gate
  **suprime o agente** (zero token). O agente nem é chamado.
- Com parcela: N linhas `SYMPLEXIS_PARCELA …` → hash muda → agente acorda com 1 tool call
  (`--registrar`) e 1 linha de resposta.
- `enabled_toolsets=["terminal"]`: o agente não tem nem Sheets nem web. O que ele precisa
  já veio no prompt.

**A armadilha que quase mordeu:** o gate compara o hash em bytes. Se a saída tiver
**timestamp** (`gerado_em: 2026-10-02`), o hash muda todo dia → o agente dispara todo dia
com nada para fazer. Saída de gate precisa ser **estável**: sem data, sem contagem que
oscile, ordem determinística. Conversely, com evento, uma linha por evento.

**Falha SEMPRE notifica — e é por isso que falha vira LINHA, não exit != 0:** com
`monitor`, `exit != 0` faz o gate tratar como erro de fonte, **preservar o hash antigo e
suprimir o run** — exatamente a falha silenciosa que o principal não aceita. Então:
- coleta: qualquer erro → `SYMPLEXIS_FALHA motivo=…` em stdout, **exit 0**;
- `--registrar`: erro → stderr + **exit 1** (aqui a falha DEVE ser barulhenta, porque o
  agente já está acordado e vai reportar).

Classes: `SymplexisErro` para falha operacional com motivo legível; nada de `SystemExit`
dentro do fluxo do coletor.

Regras que o registro impõe (não negociar):
- Casa crédito x parcela por **valor** (±R$ 0,01) + janela de data, em ordem cronológica
  e **sem reaproveitar o mesmo crédito** — as 6 parcelas iguais de R$ 2.500 da SM1 não se
  cruzam.
- Só grava quando o `iD.Transação` **já existe** na aba `_transações`; senão recusa
  (o VLOOKUP de "Data efetuada" ficaria sem data).
- Grava **só** E (Status), H (iD.Transação) e I (Observações). Colunas de fórmula
  (A/G/J/K/L) são intocáveis.
- **Trava de layout**: confere o cabeçalho (comparando sem acento) antes de gravar;
  coluna renomeada/movida = recusa, não gravação em coluna errada.
- Relê a partir da **coluna A** e exige `Status=Recebido` **e** `Data efetuada` preenchida.

**O Inter aceita no máximo 90 DIAS CORRIDOS** entre `dataInicio` e `dataFim` — 90 já dá
`400 Período inválido` (medido 02/10/2026: 89d passa, 90d falha). O script trava em 89.

Ambiente: `/opt/mercurio-data/work/idata/.venv/bin/python` (tem `requests` +
`googleapiclient`; o `id-nfse-motor` **não** tem pandas, e `api_inter` não precisa dele).

**Juros/mora (decisão do Gustavo, 02/10/2026):** parcela liquidada **acima** do previsto não
é falha de casamento — é registro. O `cruzar()` faz **duas passadas**, nesta ordem:

1. **exato** (mesmo valor, ±centavos) — o caso normal, calado;
2. **com juros/mora** — crédito acima do previsto, dentro de `min(10% da parcela, R$ 500)`
   (`SYMX_JUROS_PCT` / `SYMX_JUROS_TETO`).

A ordem é obrigatória: se uma parcela tem crédito exato e outra tem crédito com juros, passar
por todos os exatos primeiro evita que a parcela errada capture o crédito cheio. Dentro de
cada passada: ordem cronológica e **sem reaproveitar crédito** — 6 parcelas iguais de
R$ 2.500 casam na sequência certa (coberto por teste).

Limites que **não** casam, de propósito: pagamento **a menos** (parcial/adiantamento) e
juros **acima do teto**. Ambos ficam para decisão humana.

Ao registrar com divergência, o `--registrar` recebe `LINHA:ID:PAGO_VALOR` e escreve em
Observações: "recebido R$ X — diferença de R$ Y, provavelmente juros/mora". O valor
previsto (coluna D) **não** muda: juros vivem na camada financeira (transação/extrato).

**Armadilha real do teto:** `faixa_juros` devolvia `None` para "não casou" e o chamador
testava `is not None` — então `False` (acima do teto) contornava a faixa. Devolve
**booleano** e teste por verdade. `None` como sentinela + `is not None` é armadilha.

Teste-guardião: `scripts/tests/test_symplexis_cruzamento.py` (8 casos: exato, juros, teto,
a menos, precedência, não-reuso, 6 parcelas iguais, data anterior). Rodar antes de mexer no
`cruzar`.

## 3 · Planilhas financeiras — as 2 principais

### A) [ID] Gestão Financeira (`1cOMQM2B1ircEdFJ5iiAGiUO7-Mx_qSo51uWDRtAV_gE`)
Painel de controle financeiro, alimentado pela automação iData (API Inter).
Abas-chave alimentadas (CCI_*): `CCI_extrato`, `CCI_saldo`, `CCI_detalhes_PIX`,
`CCI_detalhes_PAGAMENTO`, `CCI_detalhes_COMPRA_DEBITO`, `CCI_detalhes_OUTROS`. Aba
`transações` = classificação contábil. Há também DRE, lucro por projeto, sankey,
proventos, projeção de caixa (camada de análise/relatório, defasada).

### B) [ID] Gestão de Symplexis (`1qV_L-WMOMDKQwIgLj_l9frokFVO032nsVbM_Qbw8kR0`)
**Planilha-mestra de engagements (symplexis).** Abas:
- `clientes` — cadastro (iD, empresa, contato, email, telefone, função). **email é chip (col D)**.
- `contratos` — iD, contrato, cliente, status, valor total, assinatura, vigência,
  **"Contrato editável"(H) e "Contrato assinado"(I) são SMARTS CHIPS (rich links)**;
  Backlog (J) também é chip. Observações (K) para o que não vai em outro lugar.
- `symplexis` — engagements/entregas (iD, iD.Contrato, contrato, nome symplexi,
  consultor (E=chip), status, prazo, horas, entregáveis, cronograma, data de entrega...).
- `consultores` — col A = people chips.
- `recebimentos` — parcelas (iD, iD.contrato, Discriminação, Valor, Status, Data prevista,
  Data efetuada, iD.Transação, Obs, Auxiliar, Cliente (K=fórmula), Contrato (L=fórmula)).
  **A/K/L são fórmulas** (não preencher manualmente); preencher B,C,D,E,F e tomar cuidado.
- Relatórios: `Tabela dinâmica 1`, `sankey_*`, `_transações`, `__projetos`, `conexões`.

**Conexões:** a Gestão Financeira ↔ Symplexis: a GF importa `__projetos`/`recebimentos`
da Symplexis; a Symplexis importa `transações!A:AB` da GF (como `_transações`).

### SMARTS CHIPS — como escrever (padrão da planilha)
Campos de contrato (minuta/assinado) e emails/consultores são **smart chips** (rich links
/ people chips), não texto simples. Para criar via API, usar `updateCells` com placeholder
`@` e `chipRuns`:
- Rich link (contrato): `chip: {richLinkProperties: {uri, mimeType}}` — ex. mime
  `application/vnd.google-apps.document` (minuta) ou `application/pdf` (assinado).
- People chip (email/consultor): `chip: {personProperties: {email, displayFormat:"DEFAULT"}}`.

Update: range da célula + `fields:"userEnteredValue,chipRuns"`. O `@` vira o chip e o
Google renderiza o nome do arquivo.

### Cuidados críticos ao editar planilhas
1. **`INSERT_ROWS` (values.append com insertDataOption) desloca linhas e bagunça
   fórmulas/chips** nas linhas existentes. Prefira `values.update` em células específicas
   ou insira via batchUpdate com cuidado e **verifique a posição real depois**.
2. **Não preencher células de fórmula** (col A/K/L de recebimentos; campos derivados) —
   deixar as fórmulas calcularem; só gravar valores de entrada.
3. **Data de entrega** de um symplexi pode vir do email de entrega do projeto.
4. **Valor de contrato** = o que está no documento; **recebimentos** vêm do extrato.
   Não colocar "nº de parcelas faturadas" em observação se isso vai em outro campo.
   Não usar observações para dados que pertencem a outros campos.
5. **Status de recebimento:** usar os valores aceitos pela planilha (`Recebido`,
   `Por receber`, `confirmado por IA` — este é transitório para revisão manual). Para
   parcelas pendentes por contrato, usar `Por receber`.

## 4 · API do Banco Inter (extrato/saldo)

- Detalhes completos na skill `inter-api-id-consultoria`.
- Certificado (1 ano) + client_id/secret no repo `idconsultoria/iData`
  (`etl/extratores/api_inter.py` + `auth/extrator_de_extrato_inter/`).
- Erro `SSLV3_ALERT_CERTIFICATE_EXPIRED` = certificado expirado → renovar no Inter.
- Automação diária: cron iData roda o entrypoint "ontem" (extrato + saldo → abas CCI_*
  da Gestão Financeira). Schedule 07:00 BRT (job cron `e60e713b0b62`). Desde 22/08/2026 o
  job é **watchdog silencioso**: `no_agent=true` + script
  `$HERMES_HOME/scripts/watchdog-idata-diario.sh` (que chama `runner-idata-diario.sh`) —
  **só notifica o principal se der ERRO**; sucesso fica mudo (exit 0 + stdout vazio = sem
  entrega). Detalhes do modo watchdog no schema de `cronjob`.

## 5 · Emails — busca nos dois

- `admin@idconsultoria.ai` (token `$HERMES_HOME/google_token.json`): contratos, NFs, financeiro
  corporativo. Contratos assinados via Clicksign podem vir de `assinatura@clicksign.com`.
- `gustavo.idteal@gmail.com` (token `$HERMES_HOME/google_token.gustavo_idteal.json`): financeiro —
  **Nubank (fatura+extrato), Inter (extratos), Mercado Pago (extratos), Pix, ISS**, comunicações da conta.
  **NUNCA usar `gustavomelloenciv@gmail.com` — fallback vetado 01/09/2026.**
- Buscar contratos/valores com queries Gmail (from/to/assinad/parcela/valor).

## 6 · NFS-e

### Envio de NFS-e de parcela ao SergipeTec (contrato Artemishub)

Padrão consolidado (jul/ago/set 2026). Ao receber o PDF da NFS-e da parcela:

- **Remetente:** `admin@idconsultoria.ai` (token `$HERMES_HOME/google_token.json`) — como "Principal ID Consultoria".
- **Destinatários:** `compra@sergipetec.org.br` **e** `asplan.sergipetec.org.br` (Érica Santos é a interlocutora de compras).
- **Assunto:** `Nota Fiscal de <ordinal> parcela do contrato Artemishub` (1ª, 2ª, 3ª...).
- **Anexo:** renomear a NF para `NFS-e_<n>-<total>_Artemishub.pdf` antes de anexar.
- **Corpo:** bloco "Dados da Nota Fiscal" (Parcela, Valor, Competência, Serviço = código 0802 · CNAE 6204-0/00, Município, Emitente com CNPJ) + "Dados para pagamento: Chave Pix (CNPJ) 54.569.818/0001-59" + assinatura ID.
- **Script pronto:** `$HERMES_HOME/work/nfse-2026/enviar_nfse_3-3_artemishub.py` (roda `--dry-run` primeiro; `$HERMES_HOME/google_token.json`). Serve de molde para as próximas parcelas — só trocar texto, valor, competência e o PDF.
- **CND Municipal NÃO vai por padrão** — o setor de compras pede depois, se quiser (determinação do Gustavo, 18/09/2026).
- **Aprovar o texto com o Gustavo antes de enviar** e, após o envio, ler a mensagem de volta (`messages.get` na thread) para confirmar SENT + anexo, não confiar só no retorno do `send`.
- `gws`/`google_api.py gmail send` **não anexa arquivos** — usar MIME (`MIMEApplication` + `messages.send` com `raw`), como no script acima.

### Geral

- Ver skills `emissao-nfse` / `motor-nfse-id`. Motor nfelib em `$HERMES_HOME/id-nfse-motor` (legado `/opt/data/id-nfse-motor`).
- Aracaju usa protocolo NACIONAL (DPS). Certificado A1 da ID: NÃO em email/Drive — está
  num PC pessoal do Gustavo (pendência).
- Alíquota ISS auto-capturada por cron no dia 5 (job `3dfe43219f1b` usa `$HERMES_HOME/id-nfse-motor` com fallback).
- Atenção: o motor nfelib (`id-nfse-motor/.venv`) é o venv que tem `googleapiclient` instalado neste host — usar `/opt/mercurio-data/id-nfse-motor/.venv/bin/python` para os scripts de Gmail/Drive.

---

## Pitfalls (aprendidos em execução real)

- **`email.message` neste host NÃO tem `set_content`/`ContentManager`** (Python 3.11.16 arm64
  empacotado): use `msg.attach(MIMEText(corpo, "plain", "utf-8"))`, nunca `msg.set_content(...)`.
  Erro real: `AttributeError: 'MIMEMultipart' object has no attribute 'set_content'`.
- **Cobrança de parcela em atraso a cliente — padrão de 3 scripts** em
  `$HERMES_HOME/scripts/` (criado 26/09/2026 no caso Solution Master SM1 parcela 3/6):
  - `sm_verificar_pagamento.py` — lê o extrato do Inter e imprime `PAGO <data> <valor> <desc>` /
    `NAO_PAGO` / `ERRO <motivo>`. Só imprime; nunca envia.
  - `enviar_cobranca_sm.py --parcela N --thread <id> [--dry-run]` — monta e envia a cobrança em
    **resposta à thread da NFS-e** (`In-Reply-To`/`References`), destinatários herdados do e-mail
    original. Confere `getProfile()` == admin@idconsultoria.ai antes de enviar.
  - `cobranca-sm-parcela3.sh` — orquestrador do cron: verifica → só envia se `NAO_PAGO`; com
    `ERRO` **não cobra** (evita cobrança dupla por falha de leitura). `COBRANCA_SM_DRYRUN=1`
    força modo teste. Devolve uma linha `RESULTADO:` para o agente do cron relatar.
  - Regra de ouro: **nunca** disparar cobrança de cliente sem a trava do extrato. Se a consulta
    ao banco falhar, reportar ao Gustavo e deixar a decisão com ele.
- **Ao localizar a thread de uma NFS-e**: `messages.get` com `format="metadata"` +
  `metadataHeaders=[...]` (sem isso os headers vêm vazios); data real de envio via
  `internalDate` (ms); conversa via `threadId`. Padrão declarado pelos clientes: "pagamos no dia
  25 de cada mês" — a data da NF e a data prevista em `recebimentos` são o marco da cobrança.
- **Fuso do cron**: o host roda em **UTC** e `config.yaml` tem `timezone: ''`, então `0 11 * * *`
  = 08h BRT. Para one-shot, prefira ISO com offset explícito
  (`2026-09-28T08:00:00-03:00`) — evita depender da resolução de fuso do agendador.

- **NUNCA usar `gustavomelloenciv@gmail.com`** — fallback vetado pelo principal em 01/09/2026. Abortar se `getProfile()` retornar esse email e solicitar re-auth dos tokens corretos.
- **Token certo por tarefa** (Drive/Sheets vs Gmail) — usar escopos do token.
- **INSERT_ROWS quebra layout** — preferir update pontual + conferir.
- **Chips em várias colunas** — não só contrato; email (clientes), consultor
  (symplexis/consultores), backlog (contratos).
- **Cliente pode ser PF/razão social diferente do nome fantasia** (ex.: Ravello = Cerâmica
  Capri; BiotechBR = BiotechSE — mesma empresa renomeada).
- **Sem contrato formal** não impede registro: usar status/valor conforme fato (ex.:
  Real Invest pagou direto; Biotech pró-bono).
- **Confirmar com o principal linha a linha** antes de gravar em planilha original
  (valores, status, datas, escala).
- Datas de vencimento de parcelas pendentes: procurar no contrato/NF/email antes de
  estimar.

## Checklist antes de responder a demanda adm/financeira

1. Identificou qual ESTRUTURA da ID está envolvida? (drive/planilha/emails/nfse/inter)
2. Escolheu o TOKEN certo? Validou com `getProfile()` que NÃO é `gustavomelloenciv@gmail.com`?
3. Vai ESCREVER em planilha? → revisou fórmula×valor, chips, e confirmação de dados?
4. Segue as skills de apoio (inter, nfse, google-workspace)?
5. Resultado verificado por leitura de volta (não só descrito)?

---

## Auditoria 2026-09-01 — busca pelos tokens corretos

**Solicitado por Gustavo em 01/09/2026:** procurar onde estão `admin@idconsultoria.ai` e `gustavo.idteal@gmail.com` e documentar. **Atualizado 01/09/2026 11:08 UTC após autorização.**

**Busca executada (sem ligar contêiner `hermes_mercurio`):**
- `ssh ubuntu@129.146.163.107` via `deploy_key.pem` (skills `devops-artemishub`/`moodle-id-operacoes`) → `sudo cat /home/ubuntu/selfhost/hermes/data/google_token_admin.json` (origem) → `base64` → gravado em `$HERMES_HOME/google_token.json` (+ `.secrets/`), `chmod 600`, validado `gmail.getProfile → admin@idconsultoria.ai` (1663 msgs).
- `sudo ls /home/ubuntu/selfhost/hermes/data/google_token*.json` → `google_token.json` / `.bak` / `google_token_admin.json` / `google_token_gustavo.json`; os 3 primeiros eram `gustavomelloenciv@gmail.com` (refresh `04YzGys...`), apenas `google_token_admin.json` era `admin@idconsultoria.ai` (refresh `042KPgOStXCe...`). `grep -l idteal` só achou sessions — nenhum token `idteal` existia antes.
- `find /opt/mercurio-data -maxdepth 4 -name "*token*"` antes da recuperação: só fallback `gustavomelloenciv`.
- Após OAuth `setup.py --auth-url` → `--auth-code http://localhost:1/?state=kFF6...&code=4/0ATs...` → gerado `$HERMES_HOME/google_token.gustavo_idteal.json` (e `.secrets/`), validado `gmail.getProfile → gustavo.idteal@gmail.com` (3117 msgs, refresh `06X0c7_Lvvm...`). Admin preservado em `/tmp/google_token_admin_backup.json` e restaurado em `google_token.json` para não sobrescrever.
- `grep -c gustavomelloenciv` nos dois tokens ativos = 0; `contêiner hermes_mercurio` **não foi ligado** em nenhum momento (só `docker export`/`cat` via SSH).

**Conclusão:** tokens corretos **restaurados e validados** em `$HERMES_HOME`:
- `$HERMES_HOME/google_token.json` → `admin@idconsultoria.ai`
- `$HERMES_HOME/google_token.gustavo_idteal.json` → `gustavo.idteal@gmail.com`
Skill volta a operar coleta de extratos/faturas (Nubank/Inter) sem fallback. Documentado nesta versão 1.1.0-patch2.
