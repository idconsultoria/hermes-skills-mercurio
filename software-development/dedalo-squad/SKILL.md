---
name: dedalo-squad
description: "Pipeline Dédalo Squad — mapeamento de processos com POPs e diagramas BPMN 2.0 a partir de áudios no Google Drive.

Load this skill when the user wants to process organizational interviews into structured documentation: discover audio files in ANY Google Drive folder structure, create a tracking spreadsheet, transcribe interviews, generate POPs (Procedimentos Operacionais Padrão), create BPMN 2.0 diagrams (XML + PNG), and track everything in Google Sheets. Covers the full lifecycle: discovery, bootstrap, execution, monitoring, retry, and troubleshooting."
category: software-development
---

# Dédalo Squad — Pipeline de Mapeamento de Processos

> Pipeline de IA que transforma entrevistas em áudio em POPs e diagramas BPMN 2.0,
> orquestrado por uma planilha Google Sheets e armazenado no Google Drive.

## Visão Geral

O Dédalo Squad é um pipeline de 5 agentes de IA que processa entrevistas gravadas
em áudio para produzir documentação estruturada de processos organizacionais:

```
ÁUDIOS → [Diarizador] → TRANSCRIÇÕES → [Escriba] → QUESTIONÁRIO
                                                        ↓
         ← [Coladinho] ← POP ← [Popeye] ←──────────────┘
                              ↓
                         [Disgrama] → BPMN XML → [Render] → PNG
```

O pipeline pode ser usado de duas formas:

- **Modo discovery:** a partir de uma pasta qualquer do Drive, escaneia a estrutura,
  cria planilha e cliente JSON, e popula tudo automaticamente.
- **Modo operação:** com planilha e cliente JSON já prontos, executa o pipeline
  (processo individual, lote paralelo, retry).

## Pré-requisitos

O repositório Dédalo Squad deve estar clonado. Se não estiver:

```bash
git clone https://github.com/idconsultoria/dedalo_squad.git /opt/data/dedalo_squad
cd /opt/data/dedalo_squad
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Credenciais obrigatórias:**
- `agemini/conectores/credenciais/service_account.json` — service account Google com Drive, Sheets e Generative Language API
- `.env` com pelo menos `GEMINI_API_KEY_1` (múltiplas chaves para paralelismo)
- A service account precisa de acesso de **Editor** nas pastas Drive e planilhas

**Setup do renderizador BPMN (recomendado):**
```bash
cd /opt/data/dedalo_squad/render && bash setup.sh
```
Requer Node.js 18+ e Chromium. Sem isso, XMLs BPMN são gerados mas PNGs não são renderizados.

---

## Fase 1 — Discovery: de pasta do Drive a projeto

### Fluxo completo

Dada uma URL de pasta do Google Drive (ex: `https://drive.google.com/drive/folders/<ID>`),
seguir este fluxo para criar um projeto completo:

```
1. Escanear pasta     →  descobrir subpastas e arquivos de áudio
2. Criar planilha     →  Google Sheets com colunas do pipeline
3. Criar cliente JSON →  dados/geracao_de_pops/clientes/<nome>.json
4. Criar pastas Drive →  PASTA_DE_SUBPRODUTOS, PASTA_DE_COLETAS, etc.
5. Popular planilha   →  preencher cada linha com IDs e links
6. Executar pipeline  →  Fase 2
```

### Passo 1: Escanear a pasta do Drive

Usar a API do Google Drive para listar o conteúdo recursivamente.
A service account deve ter acesso à pasta.

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH = '/opt/data/dedalo_squad/agemini/conectores/credenciais/service_account.json'
creds = Credentials.from_service_account_file(SA_PATH, scopes=[
    'https://www.googleapis.com/auth/drive.readonly'
])
drive = build('drive', 'v3', credentials=creds)

def listar_pasta(pasta_id):
    """Lista subpastas e arquivos de áudio recursivamente."""
    resultados = []
    page_token = None
    while True:
        response = drive.files().list(
            q=f"'{pasta_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()
        for f in response.get('files', []):
            if f['mimeType'] == 'application/vnd.google-apps.folder':
                sub = listar_pasta(f['id'])
                resultados.append({
                    'tipo': 'pasta',
                    'nome': f['name'],
                    'id': f['id'],
                    'url': f"https://drive.google.com/drive/folders/{f['id']}",
                    'filhos': sub
                })
            elif f['mimeType'].startswith('audio/'):
                resultados.append({
                    'tipo': 'audio',
                    'nome': f['name'],
                    'id': f['id'],
                    'mime': f['mimeType']
                })
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return resultados
```

**Heurística de identificação de processos:**
- Cada subpasta de nível 1 é um **processo candidato**
- Se a subpasta contém pelo menos 1 arquivo de áudio → é um processo
- O nome da subpasta vira o identificador (ex: `FIN-001 - Contas a Pagar` → código `FIN-001`, nome `Contas a Pagar`)
- Se não houver subpastas (áudios soltos na raiz), tratar cada arquivo como um processo

### Passo 2: Criar a planilha Google Sheets

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH = '/opt/data/dedalo_squad/agemini/conectores/credenciais/service_account.json'
creds = Credentials.from_service_account_file(SA_PATH, scopes=[
    'https://www.googleapis.com/auth/spreadsheets'
])
sheets = build('sheets', 'v4', credentials=creds)

# Criar planilha
spreadsheet = sheets.spreadsheets().create(body={
    'properties': {'title': 'Processos - POPs e Diagramas'}
}).execute()
ID_PLANILHA = spreadsheet['spreadsheetId']
print(f"Planilha: https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/edit")

# Cabeçalho fixo do pipeline (não alterar a ordem)
HEADERS = [
    'Nome da pasta',
    'Identificador do Processo',
    'Nome',
    'Categoria',
    'Área',
    'url_entrevistas',
    'url_acompanhamento',
    'url_imagens',
    'Transcrição da entrevista',
    'Transcrição do acompanhamento',
    'Questionário preenchido',
    'POP resumido',
    'POP detalhado',
    'POP Detalhado Revisado',
    'Raciocínio do Agente',
    'XML estratégico',
    'XML operacional',
    'Planejamento do diagrama',
    'url_subprodutos',
    'url_diag_estrategico',
    'url_diag_operacional',
    'Link do Notion',
    'Status',
    'Pasta de subprodutos',
    'Camunda estratégico',
    'Camunda operacional'
]

sheets.spreadsheets().values().update(
    spreadsheetId=ID_PLANILHA,
    range='Processos!A1',
    valueInputOption='RAW',
    body={'values': [HEADERS]}
).execute()
```

### Passo 3: Criar pastas no Drive e o cliente JSON

```python
# Criar as 4 pastas de suporte no Drive
def criar_pasta_drive(nome, parent_id=None):
    metadata = {'name': nome, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        metadata['parents'] = [parent_id]
    return drive.files().create(body=metadata, fields='id').execute()['id']

# Sugerir criar dentro de uma pasta raiz "Dédalo Squad - <cliente>"
PASTA_RAIZ_ID = criar_pasta_drive('Dédalo Squad - Meu Cliente')
PASTA_SUBPRODUTOS_ID = criar_pasta_drive('Subprodutos', PASTA_RAIZ_ID)
PASTA_COLETAS_ID = criar_pasta_drive('Coletas', PASTA_RAIZ_ID)
PASTA_CAPAS_ID = criar_pasta_drive('Capas', PASTA_RAIZ_ID)
PASTA_PROMPTS_ID = criar_pasta_drive('Prompts', PASTA_RAIZ_ID)
```

Criar o arquivo JSON do cliente:

```python
import json

cliente_config = {
    "process_sheet": {
        "ID_PLANILHA": ID_PLANILHA,
        "INTERVALO": "Processos!A3:AK"
    },
    "google_drive_folders": {
        "PASTA_DE_SUBPRODUTOS": PASTA_SUBPRODUTOS_ID,
        "PASTA_DE_COLETAS": PASTA_COLETAS_ID,
        "PASTA_DE_CAPAS": PASTA_CAPAS_ID,
        "PASTA_DE_PROMPTS": PASTA_PROMPTS_ID
    },
    "notion": {
        "API_KEY": "***",
        "DATABASE_DE_PROCESSOS": "",
        "DATABASE_DE_UNIDADES_E_PLATAFORMAS": "",
        "DATABASE_DE_CARGOS": ""
    }
}

config_path = '/opt/data/dedalo_squad/dados/geracao_de_pops/clientes/meu_cliente.json'
with open(config_path, 'w') as f:
    json.dump(cliente_config, f, indent=4, ensure_ascii=False)
```

### Passo 4: Popular planilha com as pastas de áudio

**Importante:** não é necessário mover ou copiar os áudios para `PASTA_DE_COLETAS`.
A coluna `url_entrevistas` pode apontar diretamente para a pasta original do Drive
onde os áudios estão. O `PASTA_DE_COLETAS` é apenas uma convenção organizacional,
não um requisito técnico do pipeline.

Para cada processo descoberto no Passo 1:

```python
rows = []
for processo in processos_descobertos:
    nome_pasta = f"{processo['codigo']} - {processo['nome']}"
    
    # Usar a URL original da pasta de áudios (não precisa mover nada)
    url_entrevistas = processo['pasta_url']
    
    rows.append([
        nome_pasta,               # Nome da pasta
        processo['codigo'],        # Identificador do Processo
        processo['nome'],          # Nome
        'Operacional',             # Categoria (default — ajustar depois)
        processo.get('area', ''),  # Área (inferida da estrutura se possível)
        url_entrevistas,           # url_entrevistas → aponta para pasta original
        '',                        # url_acompanhamento
        '',                        # url_imagens
        # ... demais colunas vazias (preenchidas pelo pipeline)
    ] + [''] * (len(HEADERS) - 8))
```

**Heurística para código, nome e área:**
- Se a subpasta segue o padrão `XXX-NNN - Descrição` → extrair código (`XXX-NNN`) e nome (`Descrição`)
- Se a subpasta tem formato livre (`Descrição qualquer`) → gerar código sequencial (`PRC-001`, `PRC-002`...) e usar o nome da pasta como nome
- Se houver subpasta pai com nome de departamento (ex: `Financeiro/Contas a Pagar`) → usar como área
- Se a estrutura for plana (áudios soltos na raiz) → cada arquivo vira um processo, código extraído do nome do arquivo

# Escrever na planilha
sheets.spreadsheets().values().update(
    spreadsheetId=ID_PLANILHA,
    range=f'Processos!A2',
    valueInputOption='RAW',
    body={'values': rows}
).execute()
```

**Heurística para código e nome:**
- Se a subpasta tem formato `XXX-NNN - Descrição` → extrair código e nome
- Se a subpasta tem formato `Descrição` → gerar código sequencial (ex: `PRC-001`)
- A área/departamento pode ser inferida da subpasta pai (ex: `Financeiro/Contas a Pagar` → área = `Financeiro`)

### Passo 5: Configurar service account

Compartilhar a planilha e as pastas Drive com o email da service account:
```python
# O email está no JSON de credenciais
with open(SA_PATH) as f:
    sa_email = json.load(f)['client_email']

# Compartilhar planilha
drive.permissions().create(
    fileId=ID_PLANILHA,
    body={'type': 'user', 'role': 'writer', 'emailAddress': sa_email}
).execute()

# Compartilhar pastas
for pasta_id in [PASTA_RAIZ_ID, PASTA_SUBPRODUTOS_ID, PASTA_COLETAS_ID]:
    drive.permissions().create(
        fileId=pasta_id,
        body={'type': 'user', 'role': 'writer', 'emailAddress': sa_email}
    ).execute()
```

---

## Fase 2 — Operação: executar o pipeline

### Ambiente

Sempre ativar o venv e exportar o cliente:

```bash
cd /opt/data/dedalo_squad && source .venv/bin/activate
export DEDALO_CLIENT=meu_cliente
```

### Processar um único processo

```bash
python3 run_one.py FIN-001
```

Com backoff de 3 tentativas no nível do runner + backoff interno nas chamadas Gemini.

### Processar múltiplos processos (paralelo controlado)

```bash
for p in FIN-001 FIN-002 FIN-003; do
    python3 run_one.py "$p" 2>&1 && echo "OK: $p" || echo "FAIL: $p" &
done
wait
```

**Limite seguro:** 5 processos simultâneos para o free tier Gemini (15 RPM).

### Processar todos de uma vez (pipeline completo)

```bash
python3 run_sergipetec.py
```

Isso executa `executar_paralelamente(criar_pop_e_diagrama_para_processo, ...)` com os workers disponíveis.

### Pipeline programático

```python
from elaboracao_de_pops_e_diagramas import *
import os

# Carregar planilha
planilha = conectores.google_sheets.buscar_dados_sheets(ID_PLANILHA, INTERVALO)

# Coletar API keys
api_keys = []
for i in range(1, 10):
    key = os.environ.get(f'GEMINI_API_KEY_{i}')
    if key and key.strip() and not key.startswith('PREENC') and len(key) > 20:
        api_keys.append(key)

# Executar (paralelo, round-robin de API keys)
executar_paralelamente(criar_pop_e_diagrama_para_processo, planilha, api_keys)
```

---

## Fase 3 — Monitoramento e retry

### Dashboard: a planilha

A planilha Google Sheets é o dashboard de progresso. Verificar estas colunas:

| Coluna | Significado |
|--------|-------------|
| `Transcrição da entrevista` | ✅ preenchida → áudio foi diarizado |
| `Questionário preenchido` | ✅ preenchida e sem "preciso que você forneça" → Escriba OK |
| `POP detalhado` | ✅ preenchida e contém "## Objetivo" → Popeye OK |
| `XML estratégico` | ✅ começa com `<?xml` → Disgrama estratégico OK |
| `XML operacional` | ✅ começa com `<?xml` → Disgrama operacional OK |
| `Camunda estratégico` | "Renderizado" → PNG estratégico OK |
| `Camunda operacional` | "Renderizado" → PNG operacional OK |
| `url_diag_estrategico` | link `drive.google.com/file/d/...` → upload OK |
| `Status` | "Sem áudio" → processo pulado (sem áudios na pasta) |

### Forçar reexecução (cache poisoning)

O pipeline **não reprocessa colunas já preenchidas**. Se um agente falhou silenciosamente
e escreveu placeholder, limpar as células downstream antes de reexecutar.

**Colunas a limpar para reexecução completa de um processo:**
`R, S, T, U, V, W, X, Z, AA, AE, AG, AK` (questionário, POPs, XMLs, status render, links PNG, status)

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SA_PATH = 'agemini/conectores/credenciais/service_account.json'
with open('dados/geracao_de_pops/clientes/meu_cliente.json') as f:
    config = json.load(f)
ID_PLANILHA = config['process_sheet']['ID_PLANILHA']

creds = Credentials.from_service_account_file(SA_PATH, scopes=['https://www.googleapis.com/auth/spreadsheets'])
svc = build('sheets', 'v4', credentials=creds)

# Encontrar a linha do processo (ex: FIN-001)
result = svc.spreadsheets().values().get(
    spreadsheetId=ID_PLANILHA, range='Processos!B3:B'
).execute()
rows = result.get('values', [])
target_row = None
for i, row in enumerate(rows):
    if row and row[0] == 'FIN-001':
        target_row = i + 3  # +3 porque range começa em B3
        break

# Limpar células downstream
cols_to_clear = ['R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z', 'AA', 'AE', 'AG', 'AK']
requests = [{'range': f'Processos!{col}{target_row}', 'values': [['']]} for col in cols_to_clear]
svc.spreadsheets().values().batchUpdate(
    spreadsheetId=ID_PLANILHA,
    body={'valueInputOption': 'RAW', 'data': requests}
).execute()
```

---

## Troubleshooting

### HttpError 429 (rate limit Gemini)

O backoff automático cobre 5 tentativas (2s → 32s). Se persistir:
- Reduzir workers para 3
- Adicionar mais API keys (`GEMINI_API_KEY_3`, `GEMINI_API_KEY_4`)
- Aguardar 2 minutos e reexecutar o processo individualmente

### HttpError 400 "cell > 50.000 characters"

O pipeline trunca automaticamente valores >49K chars com `... [TRUNCADO]`.
O conteúdo completo está nos Google Docs na pasta de subprodutos do Drive.

### Placeholders nos outputs ("preciso que você forneça o conteúdo...")

**Causa:** o agente recebeu input vazio porque a etapa anterior falhou.
**Solução:** limpar células downstream e reexecutar (ver "Forçar reexecução" acima).

### Processo sem áudio

Se `baixar_arquivos_pasta()` retornar lista vazia (pasta sem arquivos de áudio),
o pipeline marca "Sem áudio" e segue para o próximo. Isso é normal para processos
documentais ou ainda não entrevistados.

### Áudios da lixeira aparecendo na listagem

Resolvido — o `google_drive.py` usa `trashed=false` na query.

### XML BPMN malformado

O Disgrama pode gerar resposta de texto em vez de XML se o POP de entrada for vago.
Verificar o POP detalhado — se for placeholder genérico, limpar e reexecutar.

### Renderização PNG falhou

1. `which chromium-browser || which google-chrome-stable` → Chromium instalado?
2. `node --version` → Node.js 18+?
3. `ls render/node_modules/bpmn-js` → `setup.sh` foi executado?

---

## Anatomia do Pipeline

### Estrutura de subprodutos (criada automaticamente)

```
PASTA_DE_SUBPRODUTOS/
└── COD-001 - Nome do Processo/
    ├── 1. Transcrições/
    │   └── Transcrição das Entrevistas (Google Doc)
    ├── 2. Questionário respondido/
    │   └── Questionário Respondido (Google Doc)
    ├── 3. POPs/
    │   ├── POP Detalhado (Google Doc)
    │   ├── POP Resumido (Google Doc)
    │   └── Raciocínio do Agente (Google Doc)
    └── 4. XMLs/
        ├── Estratégico.bpmn (XML)
        ├── Operacional.bpmn (XML)
        ├── Estratégico.png (renderizado)
        ├── Operacional.png (renderizado)
        └── Raciocínio do Agente - Diagrama * (Google Docs)
```

### Modelo de IA

Todos os agentes usam `gemini-3.1-flash-lite` (1000 req/dia, 15 RPM no free tier).
O modelo é configurável por agente em `agemini/agentes/*.py` (constante `MODELO`).

### Backoff (padrão do repositório)

| Camada | Arquivo | Tentativas | Delay |
|--------|---------|:---:|-------|
| Gemini (interno) | `agemini/modelos/gemini.py` | 5 | 2s → 4s → 8s → 16s → 32s, jitter ±25% |
| Google Sheets | `agemini/conectores/google_sheets.py` | 3 | 2s, 4s, 8s |
| Runner | `run_one.py` | 3 | 10s → 20s → 40s |

### Safeguards

- **Sem áudio:** detecta pasta vazia → marca "Sem áudio" e retorna
- **Trashed:** query `trashed=false` no Drive (ignora lixeira)
- **Truncamento:** células >49K chars truncadas com `... [TRUNCADO]`
- **Cache:** não reprocessa colunas já preenchidas (limpar manualmente para forçar)

---

## Arquivos de Referência

| Recurso | Caminho / URL |
|---------|---------------|
| Repositório | `https://github.com/idconsultoria/dedalo_squad` |
| Clone local | `/opt/data/dedalo_squad/` |
| README | `/opt/data/dedalo_squad/README.md` |
| Orquestrador | `elaboracao_de_pops_e_diagramas.py` |
| Runner individual | `run_one.py` |
| Runner paralelo | `run_sergipetec.py` |
| Backoff | `agemini/backoff.py` |
| Config clientes | `dados/geracao_de_pops/clientes/` |
| Renderizador BPMN | `render/` |
| Service account | `agemini/conectores/credenciais/service_account.json` |
| Env vars | `.env` |
