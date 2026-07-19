# Service Account Perde Acesso Quando Pasta é Movida

## Problema

Quando uma pasta do Google Drive é movida para outro pai usando **OAuth do usuário**, a service account que tinha acesso de `writer` perde o acesso ao novo local. Permissões no Drive são por item, não herdadas.

## Sintoma

```python
drive_service.files().list(q=f"'{folder_id}' in parents").execute()  # ✅ lista
drive_service.files().create(body={'name':'x.pdf','parents':[folder_id]}).execute()  # ❌ 404
```

## Solução

Após mover pastas via OAuth, re-compartilhe o novo pai com a SA:

```python
drive_service_user.permissions().create(
    fileId=novo_pai_id,
    body={'type': 'user', 'role': 'writer', 'emailAddress': 'sa@...iam.gserviceaccount.com'}
).execute()
```
