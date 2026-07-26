---
name: gcp-cloud-build
description: "GCP Cloud Build CI/CD — GitHub triggers, connections, Docker builds.

Load this skill when setting up continuous integration on GCP: connecting GitHub repos to Cloud Build, creating push-to-deploy triggers, debugging connection/authentication issues, and wiring builds to Cloud Run jobs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    keywords: [GCP, Cloud-Build, CI/CD, GitHub, triggers, Docker, Cloud-Run, Secret-Manager, IAM, OAuth, connections]
    related_skills: [github-pr-workflow, production-deployment, whatsapp-baileys-integration]
type: ToolIntegration
timestamp: 2026-07-17T00:00:00Z
---

# GCP Cloud Build — CI/CD Setup

Configuração completa de CI/CD no Google Cloud Build com gatilhos GitHub: conexão, vinculação de repositório, criação de triggers e troubleshooting.

## Pré-requisitos

```bash
# Autenticar no GCP
gcloud auth login
gcloud config set project <PROJECT_ID>

# Verificar APIs habilitadas
gcloud services list --enabled | grep -E "cloudbuild|secretmanager"
```

## 1. Habilitar APIs Necessárias

Cloud Build 2nd-gen connections usam Secret Manager para armazenar tokens OAuth. Se não estiver habilitado, a criação da conexão falha.

```bash
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## 2. Conceder Permissões IAM ao Cloud Build P4SA

O Cloud Build P4SA (service account com prefixo `service-`) precisa de permissão para criar secrets:

```bash
# Encontrar o P4SA (formato: service-<PROJECT_NUMBER>@gcp-sa-cloudbuild.iam.gserviceaccount.com)
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:service-<PROJECT_NUMBER>@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"
```

## 3. Criar Conexão GitHub

```bash
gcloud builds connections create github <CONNECTION_NAME> \
  --region=<REGION>
```

Isso gera um link OAuth. O usuário precisa:
1. Estar **logado no GitHub com a conta dona do repositório**
2. Clicar o link e autorizar o Cloud Build

**⚠️ Pitfall: conta GitHub errada no OAuth.** Se o usuário autorizar com uma conta diferente da dona do repositório, a conexão fica `PENDING_USER_OAUTH` e o repositório não aparece na listagem. **Solução:** transferir o repositório para a conta que autorizou (ver seção 5) ou recriar a conexão.

```bash
# Verificar status da conexão
gcloud builds connections describe <CONNECTION_NAME> \
  --region=<REGION> \
  --format="value(installationState.stage)"
# Deve retornar: COMPLETE
```

## 4. Vincular Repositório e Criar Trigger

```bash
# Vincular repositório (nome SEM owner — Cloud Build já sabe a conexão)
gcloud builds repositories create <REPO_NAME> \
  --connection=<CONNECTION_NAME> \
  --region=<REGION> \
  --remote-uri=https://github.com/<OWNER>/<REPO>.git

# Criar trigger (usar resource name completo do repositório)
gcloud builds triggers create github \
  --name="push-master" \
  --repository=projects/<PROJECT_ID>/locations/<REGION>/connections/<CONNECTION_NAME>/repositories/<REPO_NAME> \
  --branch-pattern="^master$" \
  --build-config="cloudbuild.yaml" \
  --region=<REGION>
```

**⚠️ Pitfall: nome do repositório com barra.** A API `gcloud builds repositories create` rejeita nomes com `/` (ex: `owner/repo`). Use apenas o nome do repo, sem o owner.

## 5. Transferir Repositório Quando Contas Não Batem

Se a conexão OAuth foi feita com a conta X mas o repo está na conta Y:

```bash
# Transferir via gh CLI (precisa estar autenticado como dono ATUAL)
gh api -X POST repos/<OLD_OWNER>/<REPO>/transfer \
  -f new_owner="<NEW_OWNER>"

# Aguardar o novo dono aceitar (chega email/notificação)
# Confirmar:
gh repo view <NEW_OWNER>/<REPO> --json nameWithOwner

# Atualizar remote local
git remote set-url origin https://github.com/<NEW_OWNER>/<REPO>.git
```

## 6. Verificar Builds

```bash
# Listar builds recentes
gcloud builds list --region=<REGION> --limit=5

# Ver detalhes
gcloud builds describe <BUILD_ID> --region=<REGION>

# Ver logs
gcloud builds log <BUILD_ID> --region=<REGION>
```

## 7. Troubleshooting

### `FAILED_PRECONDITION: Repository mapping does not exist`
O trigger clássico (`--repo-owner`/`--repo-name`) não funciona sem a GitHub App instalada. Use o fluxo 2nd-gen (connections).

### `INVALID_ARGUMENT: Malformed name`
Nome do repositório contém `/`. Use apenas o nome do repo, sem `owner/`.

### `PENDING_USER_OAUTH` persistente
A conexão foi criada mas o OAuth não completou ou foi feito com a conta errada. Delete e recrie:
```bash
gcloud builds connections delete <NAME> --region=<REGION> --quiet
```

### `Secret Manager API has not been used`
API não habilitada. Execute o passo 1.

### `could not assert Secret Manager permissions`
P4SA sem permissão. Execute o passo 2.

## 8. Fluxo Completo (Exemplo Real)

```bash
# Setup único
gcloud services enable secretmanager.googleapis.com
gcloud projects add-iam-policy-binding idata-421415 \
  --member="serviceAccount:service-56374966595@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"

# Criar conexão → usuário autoriza → confirmar COMPLETE
gcloud builds connections create github my-connection --region=us-east1
gcloud builds connections describe my-connection --region=us-east1 \
  --format="value(installationState.stage)"

# Vincular repo (idconsultoria/augmentacao-assessores → nome: augmentacao-assessores)
gcloud builds repositories create augmentacao-assessores \
  --connection=my-connection --region=us-east1 \
  --remote-uri=https://github.com/idconsultoria/augmentacao-assessores.git

# Criar trigger
gcloud builds triggers create github \
  --name="push-master" --region=us-east1 \
  --repository=projects/idata-421415/locations/us-east1/connections/my-connection/repositories/augmentacao-assessores \
  --branch-pattern="^master$" \
  --build-config="cloudbuild.yaml"

# Testar: push na master → build automática
git commit --allow-empty -m "trigger test"
git push origin master
gcloud builds list --region=us-east1 --limit=1
```
