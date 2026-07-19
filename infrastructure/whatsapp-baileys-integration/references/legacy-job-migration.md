# Migrating Legacy Cloud Run Jobs → ASSESSOR_N_ Format

When replacing an old Z-API-based job with the new Baileys + ASSESSOR_PREFIX pattern,
extract configuration from two sources:

## Step 1: Extract env vars from the old job

```bash
gcloud run jobs describe <old-job-name> --region=us-east1 --format=json | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
envs = data['spec']['template']['spec']['template']['spec']['containers'][0].get('env', [])
for e in envs:
    print(f'{e[\"name\"]}={e[\"value\"]}')
"
```

This gives you: `GEMINI_API_KEY`, `ZAPI_URL`, `ZAPI_CLIENT_TOKEN`, `ENVIOS_POR_EXECUCAO`.

## Step 2: Find hardcoded defaults in the old codebase

The old job often has Drive IDs and sheet configuration as code defaults (not in the job's
env vars). Scan the orchestrator for `os.environ.get("...", "...")` patterns:

```bash
grep -n "os\.environ\.get\|os\.getenv" <old-orchestrator>.py
```

Common hardcoded values in Agemini-based projects:

| Variable | Typical hardcoded default | Meaning |
|----------|--------------------------|---------|
| `ID_PASTA_PENDENTES` | `1KbzH5g...` | Drive folder for incoming PDFs |
| `ID_PASTA_PROCESSADOS` | `1d3fBC...` | Drive folder for processed PDFs |
| `ID_PLANILHA_CLIENTES` | `1ZRZKN...` | Sheets spreadsheet with client data |
| `ID_DOC_PERSONALIZACAO_ASSESSOR` | `1I9psq...` | Docs document with writing style |
| `NOME_ABA_CLIENTES` | `Clientes` | Sheet tab for client data |
| `NOME_ABA_LOGS` | `Registros` | Sheet tab for execution logs |

## Step 3: Map to new ASSESSOR_N_ format

```yaml
# Old flat format → new prefixed format
# env-vars-<assessor-name>.yaml
ENVIOS_POR_EXECUCAO: "8"
ASSESSOR_PREFIX: ASSESSOR_1

# From old job env:
ASSESSOR_1_GEMINI_API_KEY: <from GEMINI_API_KEY>

# From old code defaults (hardcoded):
ASSESSOR_1_ID_PASTA_PENDENTES: <from ID_PASTA_PENDENTES default>
ASSESSOR_1_ID_PASTA_PROCESSADOS: <from ID_PASTA_PROCESSADOS default>
ASSESSOR_1_ID_PLANILHA_CLIENTES: <from ID_PLANILHA_CLIENTES default>
ASSESSOR_1_ID_DOC_PERSONALIZACAO: <from ID_DOC_PERSONALIZACAO_ASSESSOR default>
ASSESSOR_1_NOME_ABA_CLIENTES: <from NOME_ABA_CLIENTES default>
ASSESSOR_1_NOME_ABA_LOGS: <from NOME_ABA_LOGS default>

# New (user-provided):
ASSESSOR_1_NOME: <real assessor name>
ASSESSOR_1_GEMINI_MODEL: gemini-3.1-flash-lite
ASSESSOR_1_BAILEYS_CREDS_B64: "<base64 of sessions/N/creds.json>"
```

## Step 4: What changes in the job spec

| Field | Old value | New value |
|-------|-----------|-----------|
| Image | `etl-clapp:latest` | `augmentacao-assessores:latest` |
| Entrypoint | `entrypoint_aumentacao_assessores.sh` | `./entrypoint.sh` |
| WhatsApp | Z-API (URL + token + client_token) | Baileys (1 base64 var) |
| Google Auth | `service_account.json` in container | ADC (Cloud Run service account) |

## Step 5: Deploy without executing

```bash
gcloud run jobs deploy xperformance-<name> \
  --image=gcr.io/<project>/augmentacao-assessores:latest \
  --region=us-east1 \
  --cpu=1 --memory=2Gi --task-timeout=1200s \
  --max-retries=3 \
  --command=./entrypoint.sh \
  --env-vars-file=env-vars-<name>.yaml \
  --service-account=<project>-compute@developer.gserviceaccount.com
```

**Do NOT execute until the user confirms.** The old job continues running and production
data is not affected until the user explicitly runs the new job.

## Step 6: Replace (when ready)

1. User provides `ASSESSOR_N_BAILEYS_CREDS_B64` (real WhatsApp session)
2. Update env-vars file with real base64 string
3. Redeploy: `gcloud run jobs deploy ... --env-vars-file=...`
4. Pause old job: `gcloud run jobs update <old-job> --region=<region> --no-execute` (or via console)
5. Execute new job: `gcloud run jobs execute <new-job> --region=<region> --wait`
