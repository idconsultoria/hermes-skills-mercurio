---
name: auxiliar-adm-id
description: "Auxiliar admin da ID: contratos, planilhas, NFS-e, Drive."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ID, contratos, planilhas, finanças, NFS-e, Drive, email, admin, administração]
    scopes: [id]
type: Orchestrator
timestamp: 2026-08-19T14:00:00Z
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

Tokens em `/opt/data/`, usados pelo venv `/opt/data/venvs/google/bin/python`.

| Token | Conta | Escopos | Uso |
|---|---|---|---|
| `google_token.json` | admin@idconsultoria.ai | Gmail apenas | email (Gmail API) |
| `google_token.admin_idconsultoria.json` | admin@idconsultoria.ai | Drive+Sheets+Gmail+Calendar+Docs | **Drive/planilhas/contratos** |
| `google_token.gustavo_idteal.json` | gustavo.idteal@gmail.com | Gmail | email financeiro |
| `google_token.backup_gustavomelloenciv.json` | gustavomelloenciv@gmail.com | Drive+Sheets+Gmail completos | fallback |

**CRÍTICO:** o token de produção para Drive/planilhas é `google_token.admin_idconsultoria.json`
(não o `google_token.json`, que só tem Gmail). Ao carregar um token: **usar os escopos que
ele já possui** (`d.get("scopes")`), senão o refresh falha com `invalid_scope` (erro já visto).

Padrão de carregamento seguro:
```python
d=json.loads(open('/opt/data/google_token.admin_idconsultoria.json').read())
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
- **Onde procurar:** esses emails de Nubank/Inter estão em **`gustavo.idteal@gmail.com`** (`google_token.gustavo_idteal.json`),
  NÃO na caixa admin. A caixa admin não tem Nubank/Inter.
- Buscar sem restringir `from:` demais — os remetentes variam (`no-reply@inter.co`, `todomundo@novidades.nubank.com.br`).
  Ex.: `q="nubank newer_than:60d"` e `q="inter newer_than:60d"` acham tudo (Pix, fatura, extrato).
- **Upload usa o token Drive** `google_token.admin_idconsultoria.json`.

Detalhes técnicos do Google API (download de anexo + upload) em `references/extratos-mensais-google-api.md`.
Mapa de IDs das pastas em `references/mapa-pastas-comprovantes.md`.

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
  `/opt/data/scripts/watchdog-idata-diario.sh` (que chama `runner-idata-diario.sh`) —
  **só notifica o principal se der ERRO**; sucesso fica mudo (exit 0 + stdout vazio = sem
  entrega). Detalhes do modo watchdog no schema de `cronjob`.

## 5 · Emails — busca nos dois

- `admin@idconsultoria.ai` (token `google_token.json`): contratos, NFs, financeiro
  corporativo. Contratos assinados via Clicksign podem vir de `assinatura@clicksign.com`.
- `gustavo.idteal@gmail.com` (token `google_token.gustavo_idteal.json`): financeiro do
  Inter (Pix, ISS), comunicações da conta.
- Buscar contratos/valores com queries Gmail (from/to/assinad/parcela/valor).

## 6 · NFS-e

- Ver skills `emissao-nfse` / `motor-nfse-id`. Motor nfelib em `/opt/data/id-nfse-motor`.
- Aracaju usa protocolo NACIONAL (DPS). Certificado A1 da ID: NÃO em email/Drive — está
  num PC pessoal do Gustavo (pendência).
- Alíquota ISS auto-capturada por cron no dia 5.

---

## Pitfalls (aprendidos em execução real)

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
2. Escolheu o TOKEN certo?
3. Vai ESCREVER em planilha? → revisou fórmula×valor, chips, e confirmação de dados?
4. Segue as skills de apoio (inter, nfse, google-workspace)?
5. Resultado verificado por leitura de volta (não só descrito)?
