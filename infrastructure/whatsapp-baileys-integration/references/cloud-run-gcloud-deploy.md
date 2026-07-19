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
ENVIOS_POR_EXECUCAO: "3"
ASSESSOR_1_NOME: Assessor XP Teste
ASSESSOR_1_GEMINI_API_KEY: AIza...
ASSESSOR_1_GEMINI_MODEL: gemini-3.1-flash-lite
ASSESSOR_1_BAILEYS_CREDS_B64: "eyJub2...Ijp7..."
ASSESSOR_1_ID_PASTA_PENDENTES: 1w8i7...
ASSESSOR_1_NOME_ABA_CLIENTES: Clientes
ASSESSOR_1_NOME_ABA_LOGS: Registros
```

### Flags comuns

| Flag | Descrição |
|------|-----------|
| `--task-timeout=1200s` | Timeout por tarefa (NÃO use `--timeout`) |
| `--command=./entrypoint.sh` | Entrypoint customizado |
| `--env-vars-file=file.yaml` | Env vars com valores longos (base64, JSON) |
| `--max-retries=3` | Retentativas em caso de falha |

### Verificar jobs existentes (referência)

```bash
gcloud run jobs list --region=us-east1
gcloud run jobs describe <job-name> --region=us-east1 --format="yaml"
```

### Executar e ver logs

```bash
# Executar e aguardar
gcloud run jobs execute <job-name> --region=us-east1 --wait

# Ver logs da execução mais recente
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=<job-name>" --limit=30 --format="text(textPayload)"
```

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
