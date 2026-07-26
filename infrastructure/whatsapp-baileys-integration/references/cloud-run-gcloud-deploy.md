# Cloud Run Deploy — gcloud CLI Patterns

## Build sem Docker Local (`gcloud builds submit`)

Quando `docker` não está disponível na máquina (sem root, sem docker group), use o Cloud Build para construir a imagem remotamente:

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/augmentacao-assessores', '.']
images:
  - 'gcr.io/$PROJECT_ID/augmentacao-assessores'
options:
  logging: CLOUD_LOGGING_ONLY
```

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

A imagem fica disponível em `gcr.io/<project>/augmentacao-assessores:latest` sem precisar de Docker local.

### Acelerar o upload com .gcloudignore

Por padrão, `gcloud builds submit` empacota TODOS os arquivos do diretório. Isso pode gerar tarballs de 200+ MB com `venv/`, `node_modules/`, etc. Crie `.gcloudignore` no raiz do projeto:

```
venv/
node_modules/
sessions/
.git/
.env
*.pyc
__pycache__/
qr_code.png
env-vars.yaml
env-vars.txt
*_teste.py
start_services.sh
dev_setup.sh
```

Com `.gcloudignore`, o tarball cai de ~210 MB para ~150 KB (18 arquivos de código fonte).

## Autenticação gcloud em Ambiente Headless

`gcloud auth login --no-launch-browser` é interativo (pede código via stdin). Em ambientes sem TTY, use PTY + process submit:

```bash
# Passo 1: Iniciar em background com PTY
terminal(command="gcloud auth login --no-launch-browser", background=true, pty=true)
# → session_id: proc_xxx

# Passo 2: Ler a URL gerada e enviar ao usuário
process(action="log", session_id="proc_xxx")
# → output: "Go to the following link in your browser: https://..."

# Passo 3: Usuário cola o código de volta no chat
# Passo 4: Submeter o código ao processo
process(action="submit", session_id="proc_xxx", data="4/0AXEQx...")
```

⚠️ **Cada chamada a `gcloud auth login` gera um PKCE diferente.** O código de uma chamada NÃO funciona em outra. A URL e o código precisam ser do MESMO par state/verifier (mesma sessão pty).

### Definir projeto após auth

```bash
gcloud config set project <PROJECT_ID>
gcloud config list  # verificar
```

Se a conta autenticada não tem acesso ao projeto, o erro é:
`does not have permission to access projects instance [PROJECT_ID]`

## Cloud Run Job Deploy

```bash
# Para env vars longas (base64, JSON), use --env-vars-file com YAML
gcloud run jobs deploy xperformance-assessor-teste \
  --image=gcr.io/idata-421415/augmentacao-assessores:latest \
  --region=us-east1 \
  --cpu=1 --memory=2Gi --task-timeout=1200s \
  --max-retries=3 \
  --command=./entrypoint.sh \
  --env-vars-file=env-vars.yaml \
  --service-account=<project>-compute@developer.gserviceaccount.com
```

### env-vars.yaml format

```yaml
ASSESSOR_PREFIX: ASSESSOR_1
ENVIOS_POR_EXECUCAO: "8"
ASSESSOR_1_NOME: Igor Rodrigues
ASSESSOR_1_GEMINI_API_KEY: AIza...
ASSESSOR_1_GEMINI_MODEL: gemini-3.1-flash-lite
ASSESSOR_1_BAILEYS_CREDS_B64: "eyJub2...Ijp7..."
ASSESSOR_1_GOOGLE_CREDENTIALS_JSON: |
  {
    "type": "service_account",
    "project_id": "idata-421319",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQ...",
    "client_email": "servico@...",
    ...
  }
ASSESSOR_1_ID_PASTA_PENDENTES: 1KbzH5gNxeHFhEH5mQP9RnJ4NXPQNbLwr
ASSESSOR_1_NOME_ABA_CLIENTES: Clientes
ASSESSOR_1_NOME_ABA_LOGS: Registros
```

**⚠️ YAML literal block scalar (`|`) com JSON precisa de indentação.** O conteúdo do JSON deve estar **recuado exatamente 2 espaços** abaixo da chave. YAML rejeita `|` seguido de conteúdo sem indentação. Use Python para gerar:

```python
sa_json = json.dumps(sa, indent=2)
sa_indented = "\n".join(f"  {line}" for line in sa_json.splitlines())
yaml_entry = f"ASSESSOR_1_GOOGLE_CREDENTIALS_JSON: |\n{sa_indented}"
```

A chave `ASSESSOR_1_GOOGLE_CREDENTIALS_JSON` (com o prefixo do assessor) define qual service account o pipeline usa para Google Drive/Sheets. Sem ela, o código cai em ADC (Application Default Credentials da compute default).

### Cloud Scheduler — Execução Recorrente

Para agendar execução do job em horário fixo (ex: seg-sex 08:00 BRT = 11:00 UTC):

```bash
# 1. Habilitar Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com --project=PROJECT_ID

# 2. Criar schedule
gcloud scheduler jobs create http xperformance-assessor-igor \
  --schedule="0 11 * * 1-5" \                  # seg-sex 11:00 UTC = 08:00 BRT
  --uri="https://us-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT_ID/jobs/MEU_JOB:run" \
  --http-method=POST \
  --oidc-service-account-email=SA-EMAIL \
  --location=us-east1 \
  --description="Augmentação Assessor Igor — seg-sex 08h"
```

O `--oidc-service-account-email` precisa de permissão `run.jobs.run` no job alvo (roles/run.invoker).

### Verificar jobs existentes (referência)

```bash
gcloud run jobs list --region=us-east1
gcloud run jobs describe <job-name> --region=us-east1 --format="yaml"
```

### Executar e ver logs

```bash
# Executar e aguardar
gcloud run jobs execute <job-name> --region=us-east1 --wait

# Listar execuções recentes
gcloud run jobs executions list --job=<job-name> --region=us-east1 \
  --format="table(name,status.state)"

# Ler logs da execução específica
gcloud logging read \
  "resource.type=cloud_run_job AND resource.labels.job_name=<job-name> AND labels.run.googleapis.com/execution_name=<exec-name>" \
  --limit=50 --project=PROJECT_ID

# Monitorar status em tempo real (polling)
while true; do
  gcloud run jobs executions describe <exec-name> --region=us-east1 \
    --format="value(status.conditions.type)" | tr '\n' ' '
  sleep 30
done

# Verificar execução mais recente (succeededCount confirma sucesso)
gcloud run jobs executions list --job=<job-name> --region=us-east1 --limit=1 \
  --format="value(status.succeededCount)"
```

### Troubleshooting — Log Analysis

Problemas comuns em execuções de Cloud Run Jobs:

| Sintoma | Causa | O que checar |
|---------|-------|-------------|
| `File not found: <ID>` nos logs | Service account não tem acesso ao recurso | Verificar se o recurso foi compartilhado com o SA email. Usar `google-api.py` com a SA para testar acesso. |
| `Nenhum relatório PDF encontrado` | Pasta de pendentes vazia OU SA não tem acesso | Comparar: 404 aparece com erro explícito, "não encontrado" sem erro = pasta vazia. |
| Job executa 2m30s+ (mais que o normal) | Pipeline com muitos PDFs | Tempo escala com quantidade de arquivos (cada um passa por Gemini). |
| `Completed` mas `succeededCount: 0` | Task falhou e retries esgotaram | `gcloud run jobs executions describe` → `status.conditions` mostra o erro. |
| Token expirado ao executar `gcloud` | OAuth do usuário venceu (~12h) | Usar service account key com permissões de Cloud Run como fallback. |

## Dockerfile Unificado (Python + Node.js)

Para projetos que precisam de Python 3.11 + Node.js 22 no mesmo container:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package.json package-lock.json ./
RUN npm ci --production

COPY . .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
```

## Cloud Run Job Specs Típicas

| Parâmetro | Valor |
|-----------|-------|
| CPU | 1 vCPU (1000m) |
| Memória | 2Gi (Python + Node.js juntos) |
| Timeout | 1200s (20 min) |
| Max retries | 3 |
| Região | us-east1 |
| Service account | `<project-number>-compute@developer.gserviceaccount.com` |
