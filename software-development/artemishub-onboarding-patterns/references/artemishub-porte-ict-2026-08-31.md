# ArtemisHub onboarding — porte ICT vs empresas_parque CHECK (2026-08-31)

**Sintoma no UI (Tácio):** na página 10 "Dados Financeiros", ao clicar Finalizar:
`Unexpected token 'I', "Internal S"... is not valid JSON` em caixa vermelha.

**O que realmente quebrou:**
- `POST /api/empresas` faz 2 inserts na mesma transação: `public.empresas` + `public.empresas_parque` (espelho p/ diretório/matchmaking).
- `public.empresas.porte CHECK = ('MEI','ME','EPP','Startup','ICT','Grande','NaoInformado')`
- `public.empresas_parque.porte CHECK = ('MEI','ME','EPP','Startup','Média','Grande','NaoInformado')`
- Form envia `porte=ICT` (Etapa1). Primeiro insert passa, segundo falha:
  `psycopg.errors.CheckViolation: empresas_parque_porte_check DETAIL: Failing row contains (..., ICT, pre_incubada, ...)`
- FastAPI sem handler → 500 texto puro `Internal Server Error` (21 bytes). Frontend faz `await res.json()` → `JSON.parse("Internal Server Error")` quebra na letra `I`.

**Logs que confirmam (host 129.146.163.107, docker compose logs):**
```
psycopg.errors.CheckViolation: new row for relation "empresas_parque" violates check constraint "empresas_parque_porte_check"
DETAIL:  Failing row contains (8d866c09-..., Sergipe Tec, 06.938.508/0001-11, ICT, pre_incubada, Energia, {Energia,TIC}, , null, 0, null, ...)
172.24.0.2 - "POST /api/empresas HTTP/1.1" 500 Internal Server Error
artemishub-frontend "POST /api/empresas HTTP/1.1" 500 21
```
Reproduziu 4x em 31/08 14:25-14:33 BRT, sempre com `ICT`.

**Por que parece ser a Etapa 10:** a etapa 10 salva via `PUT /api/empresas/{id}/complemento` *depois* do POST. Como o POST já falha, o complemento nunca roda. O usuário associa ao último passo.

**Outros gatilhos mapeados:**
- `faixa_faturamento` com acento (`Até R$ 360 mil`) vs CHECK sem acento (`Ate 360 mil`) — já normalizado via `_FAIXA_MAP` em `normalize_enum_value`, mas quebrar se bypassado.
- `recebeu_investimento` é `text[]` — não passar por normalizador de string.

**Correção canônica:**

1. **DB — unificar CHECKs:**
```sql
ALTER TABLE public.empresas_parque DROP CONSTRAINT empresas_parque_porte_check;
ALTER TABLE public.empresas_parque ADD CONSTRAINT empresas_parque_porte_check
  CHECK (porte = ANY (ARRAY['MEI','ME','EPP','Startup','ICT','Média','Grande','NaoInformado']::text[]));
-- opcional: unificar também public.empresas para incluir 'Média'
```

2. **Backend (`backend/main.py`) — mapear antes do espelho:**
```python
_PORTE_PARQUE_MAP = {"ICT": "NaoInformado"}
def _porte_para_parque(porte: str | None) -> str:
    if not porte: return "NaoInformado"
    if porte in ("MEI","ME","EPP","Startup","Grande","NaoInformado","Média","ICT"):
        return porte if porte != "ICT" else "NaoInformado"
    return _PORTE_PARQUE_MAP.get(porte, "NaoInformado")

# em create_empresa, create_empresa_parque, bulk_create_empresa_parque:
# trocar emp.porte or 'Startup' → _porte_para_parque(emp.porte)
# e envolver em try/except:
from psycopg import errors as pg_errors
try:
    cur.execute(...); conn.commit()
except pg_errors.CheckViolation as e:
    conn.rollback()
    raise HTTPException(400, f"Dado inválido: {e.diag.message_detail or str(e)}")
```

3. **Frontend (`CadastroEmpresaForm.tsx`) — parsing resiliente:**
```ts
const text = await res.text();
let json:any={}; try{ json = text?JSON.parse(text):{} } catch{ json={detail:text||res.statusText} }
if(!res.ok){ setSubmitError(json.detail||json.error||`Erro ${res.status}: ${text.slice(0,120)}`); return; }
```

**Verificação pós-fix:**
- `curl -X POST https://artemis.idconsultoria.ai/api/empresas -H 'Content-Type: application/json' -d '{"nome":"Teste ICT","razao_social":"Teste","cnpj":"00.000.000/0001-00","porte":"ICT"}'` deve retornar 200/201, não 500.
- `SELECT porte FROM empresas_parque WHERE cnpj='00.000.000/0001-00'` deve mostrar `NaoInformado` ou `ICT` conforme CHECK final.
- Submissão completa pelo form com Etapa1=ICT + Etapa10 preenchida deve finalizar sem caixa vermelha.

**Lição para pipeline futuro:** sempre manter `empresas` e `empresas_parque` com o mesmo domínio de `porte`; qualquer novo valor em `PORTES` (types/cadastro-empresa.ts) deve virar migração nos dois CHECKs.
