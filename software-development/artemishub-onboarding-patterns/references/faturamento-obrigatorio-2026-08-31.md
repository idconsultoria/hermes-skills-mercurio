# Faturamento obrigatório com isenção — ArtemisHub (2026-08-31)

**Solicitante:** Tácio — tornar `faixa_faturamento` obrigatória, salvo empresas muito novas (ex.: pré-incubação) ou sem faturamento.

## Regra
- **Obrigatório:** usuário deve selecionar uma das `FAIXAS_FATURAMENTO` (6 faixas + "Sem faturamento" + "Prefiro não informar").
- **Isenções:** `faixa == "Sem faturamento"` OU `data_fundacao < 12 meses` OU `empresas_parque.status_parque == "pre_incubada"` → backend não exige, mas frontend ainda incentiva escolher "Sem faturamento" explicitamente.

## Frontend

**`src/types/cadastro-empresa.ts`**
```ts
export const Etapa10Schema = z.object({
  faixa_faturamento: z.enum(FAIXAS_FATURAMENTO, {
    required_error: "Selecione a faixa de faturamento",
    invalid_type_error: "Selecione a faixa de faturamento",
  }),
  recebeu_investimento: z.array(z.string()).default([]),
  qtd_colaboradores_aprox: z.coerce.number().min(0).optional(),
});
function isEmpresaIsentaDeFaturamento(data) { /* Sem faturamento || data_fundacao <12m */ }
export const CadastroEmpresaSchema = z.object({ etapa1: ..., etapa10: Etapa10Schema })
  .superRefine((data, ctx) => { void isEmpresaIsentaDeFaturamento; });
```
Pitfall Zod: após `superRefine`, `CadastroEmpresaSchema` vira `ZodEffects` e perde `.shape`. Quebra `validateStep` que fazia `CadastroEmpresaSchema.shape[key].safeParse`.

Fix `src/components/cadastro-empresa/CadastroEmpresaForm.tsx`:
```ts
import { Etapa1Schema, ..., Etapa10Schema } from '@/types/cadastro-empresa';
const etapaSchemas = { 1: Etapa1Schema, 2: Etapa2Schema, ..., 10: Etapa10Schema };
const result = etapaSchemas[s].safeParse((data as any)[key]);
```
Também: `DEFAULT_FORM.etapa10 = { faixa_faturamento: undefined as any, ... }` e `handleSubmit` com `safeParse` completo + `msgs[err.path.join('.')]` + `setStep(10)` se erro na etapa 10.

**UI `Etapa10Form.tsx`**
```tsx
<CadastroField label="Faixa de faturamento anual" required error={errors['faixa_faturamento']||errors['etapa10.faixa_faturamento']} hint="Obrigatório. Selecione a faixa... Se ainda não fatura, escolha ‘Sem faturamento’ — pré-incubadas são isentas...">
  <CadastroSelect value={(data.faixa_faturamento as string)||''} error={!!...} />
</CadastroField>
```
`src/lib/cadastro-hints.ts` atualizado para mesma mensagem.

## Backend

`PUT /api/empresas/{id}/complemento` (`backend/main.py`):
```python
if c.etapa10 is not None:
    faixa = (c.etapa10 or {}).get("faixa_faturamento")
    if not faixa or not str(faixa).strip():
        is_isenta = (faixa == "Sem faturamento")
        # data_fundacao em public.empresas
        cur.execute("SELECT data_fundacao FROM public.empresas WHERE id::text=%s", (empresa_id,))
        # status_parque em public.empresas_parque (não em empresas!)
        cur.execute("SELECT status_parque FROM public.empresas_parque WHERE id::text=%s", (empresa_id,))
        if not is_isenta:
            raise HTTPException(400, "Dados Financeiros: selecione a faixa de faturamento (ou ‘Sem faturamento’...)")
```

Pitfall: `status_parque` não existe em `public.empresas` — consultar a tabela errada causa `column does not exist`; se engolido em `except Exception: pass`, a isenção nunca acontece e todo `pre_incubada` leva 400 indevido.

## Validação 2026-08-31
- `npx tsc --noEmit` 0, `npm run build` 13s, `docker compose build && up -d` health ok, `vitest 8/8`
- UI exige `*` em "Faixa de faturamento anual", sem seleção bloqueia Próximo/Finalizar com erro vermelho
- Backend: `PUT .../complemento` sem faixa + `pre_incubada` → 200 (isento); sem faixa + `incubada` fundada há 2 anos → 400
