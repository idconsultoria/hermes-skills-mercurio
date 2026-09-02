# Coleta de Dados para o PE 8h — Queries Prontas

Este arquivo documenta como compilar os 4 relatórios (R1–R4) que embasam o PE.

## Credenciais

- **Sheets/Drive:** `google_token.json` em `/opt/mercurio-data/google_token.json` (scopes: drive + spreadsheets + docs + gmail + calendar) — usar venv `/opt/mercurio-data/work/idata/.venv/bin/python`
- **Fathom:** `FATHOM_API_KEY` em `/opt/mercurio-data/.secrets/fathom.env` — helper em `/opt/mercurio-data/skills/productivity/fathom/scripts/fathom_api.py`

## R1 — Receita & Pipeline (Symplexis)

- **Planilha:** `[ID] Gestão de Symplexis` → `1qV_L-WMOMDKQwIgLj_l9frokFVO032nsVbM_Qbw8kR0`
- **Abas:** `symplexis` (28 linhas, 14 contratos, status Concluído/Atrasado/Em andamento), `contratos` (valor total, datas), `recebimentos` (59 linhas, Status Recebido/confirmado por IA/Por receber)
- **Query Python:**

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/opt/mercurio-data/google_token.json')
service = build('sheets', 'v4', credentials=creds)
ID='1qV_L-WMOMDKQwIgLj_l9frokFVO032nsVbM_Qbw8kR0'
vals = service.spreadsheets().values().get(spreadsheetId=ID, range='recebimentos!A1:L65').execute().get('values',[])
# Filtrar Status == 'Por receber' → pipeline futuro
```

- **Snapshot 01/09/2026:** pipeline futuro = SM1 5 parcelas R$2.500 (ago–dez/26) = R$12.500 + SP2 1 parcela R$3.446 (set/26) + CL3 4 parcelas R$40k (ago–dez) já parcialmente recebidas. Faturamento histórico: CL3 PRISMª R$164k (15/04/25–20/12/26), CL2 R$60k, etc.

## R2 — Saúde Financeira (Gestão Financeira)

- **Planilha:** `[ID] Gestão Financeira` → `1cOMQM2B1ircEdFJ5iiAGiUO7-Mx_qSo51uWDRtAV_gE` (23 abas)
- **Abas chave:** `DRE` (faturamento líquido, custo serviços, OPEX, EBITDA, lucro líquido — colunas Jan/24 a Jun/25), `CCI_extrato` (transações brutas), `CCI_saldo` (saldo diário), `transações` (classificação), `Lucro bruto por projeto`
- **Snapshot:** faturamento líquido oscila R$8k–R$25k/mês (ex: mar/25 R$25.970 pico, jun/25 R$8.341). Custo serviços ~R$200–R$1.4k/mês.

## R3 — Status de Projetos (Delfos + Symplexis)

- **Delfos:** app próprio (`nexus` renomeado) — backend Docker Oracle + frontend Vercel, design Tácio. BC atual = Delfos. Verificar via repo `workstation/delfos` ou Symplexis aba `symplexis` campo Status.
- **Snapshot:** Artemishub (Sergipetec) Em andamento R$10.340, Ravello BI Em andamento R$2.800, Solution Master Mapeamento R$15k (3/6 parcelas restantes, atraso 3 sem — macroprocessos em avanço), TJSE joint venture Lealdo capital imediato, XPerformance.

## R4 — Dia-a-dia Operacional (Phronesis)

- **Fonte:** Fathom `FathomClient().list_meetings(limit=8, include_summary=True, include_action_items=True)` filtrado por `title contains 'Phronesis'`
- **Série:** `phronesis-reuniao-de-operacoes` — participantes Maxwell, Anízio/Lealdo, Gustavo, Tácio
- **Últimas:** 31/08/2026 (Monte Olimpo/Capitolino + melão RN + Solution Master atraso), 24/08/2026, 17/08/2026 (TJSE joint venture, Biotex captação R$500k–1M por 15% equity)
- **Transcrição Monte Olimpo (31/08):** "Monte Olímpio usa celulares antigos para IPs residenciais e arquitetura x86, contornando bloqueios e reduzindo custos (R$1,50/mês energia). Monte Capitolino = versão empresa. Vender como taxa implementação + manutenção. Plataforma permite executar virtualmente qualquer processo."

## Visualização

- Todos os relatórios saem como **HTML identidade ID** (teal #14b8a6, navy #0a1929, Neulis Neue + Nunito Sans) com **gráfico de barras horizontais** (nunca pizza/donut), exportável para Miro/PDF.
- Ver skill `brand-design-system-html` para template.

## Atualização

- Rodar as queries na véspera da Sessão 1 e levar impresso. Entre sessões, atualizar apenas R1 pipeline se houver nova venda (melão RN).
