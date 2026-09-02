---
name: artemishub-onboarding-patterns
type: Orchestrator
description: "Use when ArtemisHub onboarding fails."
version: 1.0.0
author: "Mercúrio (background curator) — 2026-08-31"
license: MIT
category: software-development
timestamp: 2026-08-31T00:00:00Z
tags: [artemishub, onboarding, postgres, fastapi, react, check-constraint, debugging]
related_skills: [devops-artemishub, react-fastapi-debugging, systematic-debugging]
---

# ArtemisHub Onboarding Patterns

Classe de problemas do fluxo de cadastro público (`POST /api/empresas` + `PUT /api/empresas/{id}/complemento`) que espelha `public.empresas → public.empresas_parque`.

## Quando usar

- Erro no cadastro que parece ser da última etapa (Dados Financeiros) mas na verdade é do `POST` inicial
- `Unexpected token 'I', "Internal S"... is not valid JSON` no frontend
- `CheckViolation` em `empresas_parque_*_check` nos logs do backend

## Diagnóstico relâmpago

```bash
K=/opt/mercurio-data/skills/cicd-oracle-preview/devops-artemishub/references/deploy_key.pem
ssh -i "$K" ubuntu@129.146.163.107 'cd /home/ubuntu/selfhost/artemishub && docker compose logs --tail=200 | grep -A2 CheckViolation'
docker exec artemishub-db psql -U app -d artemishub -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='public.empresas_parque'::regclass"
docker exec artemishub-db psql -U app -d artemishub -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='public.empresas'::regclass"
```

Compare os domínios de `porte`. Se divergirem (`ICT` vs `Média`), é a causa.

## Causa raiz catalogada (2026-08-31)

- `public.empresas.porte` aceita `ICT`, não aceita `Média`
- `public.empresas_parque.porte` aceita `Média`, não aceita `ICT`
- Form (`PORTES = ['MEI','ME','EPP','Startup','ICT','Grande']`) envia `ICT`
- Backend faz `INSERT INTO empresas_parque (..., porte)` com `ICT` → CHECK falha → 500 texto puro → frontend `await res.json()` quebra em `I`

Detalhe completo em `references/artemishub-porte-ict-2026-08-31.md`.

## Correção canônica

1. **DB — unificar CHECKs**
```sql
ALTER TABLE public.empresas_parque DROP CONSTRAINT empresas_parque_porte_check;
ALTER TABLE public.empresas_parque ADD CONSTRAINT empresas_parque_porte_check
  CHECK (porte = ANY (ARRAY['MEI','ME','EPP','Startup','ICT','Média','Grande','NaoInformado']::text[]));
```

2. **Backend (`backend/main.py`) — mapear antes do espelho**
```python
def _porte_para_parque(porte: str | None) -> str:
    if not porte: return "NaoInformado"
    return "NaoInformado" if porte == "ICT" else porte

# trocar emp.porte or 'Startup' → _porte_para_parque(emp.porte) em create_empresa / create_empresa_parque / bulk_create
# envolver em try/except:
from psycopg import errors as pg_errors
try: cur.execute(...); conn.commit()
except pg_errors.CheckViolation as e:
    conn.rollback()
    raise HTTPException(400, f"Dado inválido: {e.diag.message_detail or str(e)}")
```

3. **Frontend (`CadastroEmpresaForm.tsx`) — parsing resiliente**
```ts
const text = await res.text();
let json:any={}; try{ json=text?JSON.parse(text):{} } catch{ json={detail:text||res.statusText} }
if(!res.ok){ setSubmitError(json.detail||json.error||`Erro ${res.status}: ${text.slice(0,120)}`); return; }
```

4. **Enums acentuados:** sempre `normalize_enum_value`/`_FAIXA_MAP` antes de gravar `faixa_faturamento` (`Até R$ 360 mil` → `Ate 360 mil`).

## Verificação

- `curl POST /api/empresas` com `porte=ICT` deve dar 201, não 500
- `SELECT porte FROM empresas_parque WHERE cnpj='...'` deve ser `NaoInformado` ou `ICT`
- Submissão pelo UI com `ICT` + Etapa 10 deve finalizar sem caixa vermelha

## Referências

- `references/artemishub-porte-ict-2026-08-31.md` — transcript completo do caso
