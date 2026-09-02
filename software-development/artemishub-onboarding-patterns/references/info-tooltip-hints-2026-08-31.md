# InfoTooltip + CADASTRO_HINTS — padrão de ajuda contextual (2026-08-31)

**Sessão:** Tácio relatou dificuldade de entender o que preencher em cada campo do cadastro. Solução: ícone `i` com tooltip por campo.

## Implementação canônica

**1. Componente `src/components/cadastro-empresa/InfoTooltip.tsx`**
- `npm install @radix-ui/react-tooltip --save` (já existia `@radix-ui/*` no projeto)
- `Info` lucide 10×10 dentro de botão 16×16 `rounded-full bg-surface-variant/60 border-outline-variant/50`
- `Tooltip.Provider delayDuration=200` + `Tooltip.Root/Trigger/Content/Arrow`, `sideOffset=6`, `max-w-[260px] bg-[#0a192f] text-white rounded-xl`
- Acessível: `aria-label="Mais informações: ..."`, abre em hover/focus/click, `data-[state]` com fade/zoom

**2. Dicionário central `src/lib/cadastro-hints.ts`**
```ts
export const CADASTRO_HINTS: Record<string,string> = {
  CNPJ: '14 dígitos. Ao completar, buscamos dados oficiais automaticamente.',
  Porte: 'Faixa de faturamento anual (MEI, ME, EPP, Média, Grande, ICT)...',
  // ~50 entradas — ver arquivo real
}
```
Fonte única de verdade; editar um arquivo reflete em todo o formulário.

**3. Fallback automático em `CadastroField.tsx`**
```tsx
import { CADASTRO_HINTS } from '@/lib/cadastro-hints';
import { InfoTooltip } from './InfoTooltip';
interface CadastroFieldProps { label:string; hint?:string; ... }
{(hint ?? CADASTRO_HINTS[label]) && <InfoTooltip content={hint ?? CADASTRO_HINTS[label]} />}
```
- Label no mapa → ícone aparece sem tocar em `Etapa*Form.tsx`
- Override pontual via prop `hint`
- Label fora do mapa → sem ícone (sem ruído)

## Por que este padrão
- Evita editar 10 `Etapa*Form.tsx` a cada ajuste de texto
- Testável/versionável, sem hardcode espalhado
- IDV Artemis: navy `#0a192f`, tipografia existente, sem novo DS

## Validação 2026-08-31
- `npx tsc --noEmit` → 0, `npm run build` → CadastroEmpresa 148kB
- `docker compose build && up -d` no Oracle 129.146.163.107, health ok
- `https://artemis.idconsultoria.ai/cadastro-empresa` mostra `i` ao lado de Porte/CNAE/CEP/TRL etc.

## Pitfall
- Não usar `title` nativo — sem controle de estilo/posição e inacessível no mobile. Radix Tooltip com Portal resolve.
- Não hardcodear hints dentro de cada `CadastroField label="..."` — vira drift quando texto muda.
