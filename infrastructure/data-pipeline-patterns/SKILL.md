---
name: data-pipeline-patterns
description: "Reliability patterns for batch data pipelines: exponential backoff, API safeguards, cell-size truncation, and parallel execution guardrails."
trigger: User is building or debugging a batch pipeline that calls external APIs (Gemini, Google Sheets, Google Drive), or hits rate limits / cell-size errors / empty-input failures.
---

# Data Pipeline Reliability Patterns

Padrões estabelecidos no repositório Dédalo Squad. Carregue esta skill ao construir
ou debugar pipelines que orquestram múltiplas chamadas a APIs externas.

**Support files:**
- `references/google-api-pitfalls.md` — error transcripts + reproduction recipes
- `references/backoff-monkey-patch.md` — monkey-patch pattern + Gemini free tier limits

## 1. Exponential Backoff (padrão do repositório)

Módulo: `agemini/backoff.py`

```python
from agemini.backoff import retry_call, backoff

# Chamada única com retry
result = retry_call(
    lambda: api.call(),
    max_attempts=5,
    base_delay=2.0,
    max_delay=120.0,
    backoff_factor=2.0,
    jitter=True,
)

# Decorator
@backoff(max_attempts=5)
def minha_funcao():
    ...
```

**Camada Gemini:** `agemini/modelos/gemini.py` aplica monkey-patch em
`genai.GenerativeModel.generate_content` e `genai.ChatSession.send_message`.
Todos os agentes herdam automaticamente. Zero mudanças nos agentes.

**Camada Sheets:** `agemini/conectores/google_sheets.py` aplica `retry_call`
com `retry_predicate=lambda e: True` (retry em qualquer erro transiente).

### Pitfalls
- **Rate limit detection:** o predicado padrão `_is_rate_limit` detecta `429`,
  `resource_exhausted`, `quota`, `rate limit`, `too many requests`, `retry`.
  Erros 400 (bad request) NÃO são retryable por padrão — use
  `retry_predicate=lambda e: True` para APIs que podem ter erros transientes
  não-documentados como 429.
- **Thundering herd:** com paralelismo (xargs -P), múltiplos processos podem
  atingir rate limit simultaneamente e todos entrarem em backoff juntos.
  Prefira -P 3~4 com Gemini free tier (15 RPM).

## 2. Google Sheets Cell Limit (50K chars)

O Google Sheets rejeita `values().update()` com **HttpError 400** se qualquer
célula exceder **50.000 caracteres**. A mensagem é:
```
Your input contains more than the maximum of 50000 characters in a single cell.
```

**Solução (aplicada em `google_sheets.py`):** truncar valores >49.000 chars
antes de enviar, com sufixo `... [TRUNCADO]`.

```python
MAX_CELL = 49_000
valores = [[
    (str(v)[:MAX_CELL] + "... [TRUNCADO]") if len(str(v)) > MAX_CELL
    else str(v)
    for v in dados.values
]]
```

Colunas tipicamente afetadas: transcrição de áudio, POP detalhado, raciocínio do agente.
O conteúdo completo sempre está nos Google Docs do Drive — a planilha é só referência.

## 3. Google Drive: `trashed=false` na query

A API do Google Drive, quando chamada com `supportsAllDrives=True` e
`includeItemsFromAllDrives=True`, **inclui arquivos na lixeira** a menos
que `and trashed=false` seja explicitamente adicionado à query.

**Bug:** `baixar_arquivos_pasta()` processava 8 áudios em vez de 1 porque
7 estavam na lixeira mas ainda referenciando a mesma pasta-pai.

**Solução (aplicada em `google_drive.py:230`):**
```python
q=f"'{id_pasta}' in parents and trashed=false"
```

## 4. Safeguard: pular processos sem áudio

Quando a pasta de entrevista está vazia, o pipeline deve abortar graciosamente
em vez de gerar subprodutos baseados em transcrição vazia.

**Solução (aplicada em `elaboracao_de_pops_e_diagramas.py:313`):**
```python
if not arquivos_entrevista:
    logging.warning(f"Processo {codigo}: nenhum áudio encontrado. Pulando.")
    atualizar_celula_planilha(ID, f"Processos!AK{row}", "Sem áudio")
    return
```

## 5. BPMN Rendering (bpmn-js + Chromium)

Módulo: `render/` (Node.js). Consome BPMN 2.0 XML e gera PNG idêntico ao
Camunda Modeler (usa o mesmo motor: bpmn-js).

```bash
cd render && npm install
node render_bpmn.js diagram.bpmn output.png
```

Wrapper Python em `agemini/conectores/render_bpmn.py`:
```python
from agemini.conectores.render_bpmn import renderizar_bpmn, renderizar_e_salvar_no_drive
png_bytes = renderizar_bpmn(xml_string)
url = renderizar_e_salvar_no_drive(xml_string, pasta_drive_id, "Estratégico")
```

Portabilidade: `git clone` + `cd render && bash setup.sh`. Chromium detectado
automaticamente (Debian extraído → Puppeteer built-in → sistema).

### Pitfall: ARM64 vs x86_64
O Chromium do Puppeteer é x86_64. Em máquinas ARM64 (Oracle Cloud, Raspberry Pi),
use o Chromium extraído do `.deb` Debian para aarch64 em
`/tmp/chromium-extracted/usr/lib/chromium/chromium` com
`LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium`.
O script `render_bpmn.js` já trata isso automaticamente.

## 6. Execução paralela segura

Cada processo `run_one.py` escreve em **linhas diferentes** da planilha
(Processos!Q{N}:AK{N}). Não há race condition. Mas a API Gemini free tier
tem 15 RPM — usar `xargs -P 5` com o backoff ativo é seguro.

```bash
printf '%s\n' PROC-001 PROC-002 ... | xargs -P 5 -I {} \
  sh -c 'python3 run_one.py "{}" && echo "OK: {}" || echo "FAIL: {}"'
```
