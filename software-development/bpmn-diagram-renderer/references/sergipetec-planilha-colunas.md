# Sergipetec — Mapa de Colunas da Planilha

Planilha: `Sergipetec - Processos (POPs e Diagramas)`  
ID: `1it2C5hnWxKe6UMPBW_bLxLivBtHdAHJt3PY-qGMIwVg`  
Aba: `Processos`  
Range de dados: `A3:AK`

| Col | Letra | Nome | Pipeline Stage |
|-----|-------|------|----------------|
| 0  | A | Nome da pasta | — |
| 1  | B | Identificador do Processo | ID (ex: CVT-001) |
| 2  | C | Nome | — |
| 3  | D | Priorização com Gestores | — |
| 4  | E | (vazio) | — |
| 5  | F | Área | — |
| 6-11 | G-L | ... | — |
| 12 | M | url_entrevistas | Link Drive → áudios |
| 13 | N | url_acompanhamento | Link Drive → acompanhamento |
| 14-15 | O-P | ... | — |
| 16 | Q | Transcrição da entrevista | **Diarizador** |
| 17 | R | Questionário preenchido | **Escriba** |
| 18 | S | POP resumido | **Popeye** (saída 2) |
| 19 | T | POP detalhado | **Popeye** (saída 3) |
| 20 | U | Raciocínio do Agente | **Popeye** (saída 1) |
| 21 | V | XML estratégico | **Disgrama** (nível estratégico) |
| 22 | W | XML operacional | **Disgrama** (nível operacional) |
| 23 | X | Planejamento do diagrama | Racionais dos diagramas |
| 24 | Y | Pasta de subprodutos | Link Drive |
| 25 | Z | Camunda estratégico | "Renderizado" ou vazio |
| 26 | AA | Camunda operacional | "Renderizado" ou vazio |
| 27-29 | AB-AD | ... | — |
| 30 | AE | url_diag_estrategico | Link PNG Estratégico |
| 31 | AF | ... | — |
| 32 | AG | url_diag_operacional | Link PNG Operacional |
| 33-35 | AH-AJ | ... | — |
| 36 | AK | Status | "Sem áudio" ou pipeline output |

## Colunas críticas para limpeza em retry

Quando um processo falha e precisa ser reexecutado, limpar APENAS as colunas downstream do ponto de falha:

- **Falha na diarização**: limpar Q até AK (todas)
- **Falha no Escriba**: limpar R até AK
- **Falha no Popeye**: limpar S, T, U, mais V, W, X, Z, AA, AE, AG, AK
- **Falha no Disgrama**: limpar V, W, X, Z, AA, AE, AG, AK
- **Falha na renderização**: limpar Z, AA, AE, AG

## Exemplo de batch update para limpeza

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_service_account_file(SA_PATH, scopes=[...])
svc = build('sheets', 'v4', credentials=creds)

# Limpar colunas R, S, T, U, V, W, X, Z, AA, AE, AG, AK na linha 31
cols = ['R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z', 'AA', 'AE', 'AG', 'AK']
row = 31
requests = [{'range': f'Processos!{c}{row}', 'values': [['']]} for c in cols]
svc.spreadsheets().values().batchUpdate(
    spreadsheetId=ID_PLANILHA,
    body={'valueInputOption': 'RAW', 'data': requests}
).execute()
```
