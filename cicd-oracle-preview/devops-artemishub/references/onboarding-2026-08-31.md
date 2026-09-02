# Onboarding 2026-08-31 — Diagnóstico e patch (porte ICT + Dados Financeiros)

**Sintoma reportado por Tácio:** na página "Dados Financeiros" (Etapa 10) ao clicar em "Finalizar cadastro", caixa vermelha `Unexpected token 'I', "Internal S"... is not valid JSON`.

## Causa raiz — 2 bugs encadeados

### 1. `porte=ICT` incompatível entre tabelas
- `public.empresas` CHECK: `('MEI','ME','EPP','Startup','ICT','Grande','NaoInformado')` — aceita ICT.
- `public.empresas_parque` CHECK (legado Supabase): `('MEI','ME','EPP','Startup','Média','Grande','NaoInformado')` — **sem ICT, com Média**.
- `POST /api/empresas` insere em `empresas` OK, depois espelha em `empresas_parque` com `emp.porte or 'Startup'` → `ICT` → `psycopg.errors.CheckViolation: empresas_parque_porte_check` → sem `try/except` vira `500 Internal Server Error` texto puro (21 bytes, `Content-Type: text/plain`). Frontend faz `await res.json()` → `SyntaxError: Unexpected token 'I'`.

Logs 31/08 14:25-14:33 BRT confirmaram 4 tentativas com `porte=ICT`, todas com `Failing row contains (..., ICT, pre_incubada, Energia, {Energia,TIC}, ...)`.

### 2. `PUT /api/empresas/{id}/complemento` quebrado após patch inicial
Tentativa de envolver `with db()` em `try:` deixou o corpo das etapas 3-10 **fora** do `with` (indentação: `with` continuou 4 espaços, body 8 → após `try` deveria ser 8 e 12). Sintomas:
- `the connection is closed` (cursor usado após `with` fechado)
- `invalid input syntax for type integer: "Ate 360 mil"` (teste com comprehension que sobrescreveu `v`)
- `conn.commit()` estava indentado dentro de `if c.etapa9:` apenas → commit parcial.

## Fix aplicado (31/08/2026, Oracle 129.146.163.107)

### Backend `backend/main.py`
```python
_PORTE_PARQUE_MAP = {"ICT":"NaoInformado", ... ,"Média":"Média"}
def _porte_para_parque(porte): ...
# empresa_parque_defaults: "porte": _porte_para_parque(payload.get("porte"))
# create_empresa parque: _porte_para_parque(emp.porte)  (antes: emp.porte or 'Startup')
# create_empresa envolvido em try/except → 400 {"detail":"Dado inválido: ..."} vs 500 texto
# upsert_empresa_complemento: try: with db() ... (with indentado a 8) + except HTTPException: raise
```

### DB
```sql
ALTER TABLE public.empresas_parque DROP CONSTRAINT empresas_parque_porte_check;
ALTER TABLE public.empresas_parque ADD CONSTRAINT empresas_parque_porte_check
  CHECK (porte = ANY (ARRAY['MEI','ME','EPP','Startup','Média','Grande','ICT','NaoInformado']::text[]));
```

### Frontend `src/components/cadastro-empresa/CadastroEmpresaForm.tsx`
```ts
const text = await res.text();
let json:any={}; try{json=text?JSON.parse(text):{}}catch{json={detail:text}}
if(!res.ok) setSubmitError(json.detail||json.error||text)
```
E para complemento: verifica `compRes.ok`, loga `j.detail`, só mostra `setSubmitError` se `400`.

## Validação
```bash
curl -X POST /api/empresas -d '{"porte":"ICT",...}' → 200 (parque NaoInformado)
curl -X PUT /api/empresas/$ID/complemento -d '{"etapa10":{"faixa_faturamento":"Até R$ 360 mil","qtd_colaboradores_aprox":5}}' → {"ok":true}
DB: SELECT faixa_faturamento,qtd_colaboradores_aprox,recebeu_investimento → Ate 360 mil | 5 | {Investidor-anjo}
```

## Lições / pitfalls para próxima sessão
- Sempre mapear enums entre tabelas espelhadas (`empresas` vs `empresas_parque`).
- Todo endpoint que faz DML deve devolver JSON em erro (`HTTPException` com `detail`), nunca deixar `psycopg` estourar como 500 texto.
- Ao envolver `with db()` em `try`, reindentar `with` e todo o body; manter `conn.commit()` fora dos `if`s.
- Frontend nunca fazer `await res.json()` sem `res.text()`+safe parse — 500s podem ser texto.
