# GSAP Centralized Registration Pattern

> Evita `gsap.registerPlugin()` duplicado entre componentes React — uma única entry point registra os plugins, todos os componentes importam de lá.

## Problema

Em projetos Next.js com múltiplos componentes usando GSAP + ScrollTrigger + useGSAP, cada componente que chama `gsap.registerPlugin(ScrollTrigger, useGSAP)` gera warnings de duplo registro e pode causar comportamento imprevisível.

## Solução

Criar um arquivo único de inicialização (`src/lib/gsap.ts`) que registra os plugins uma vez e exporta tudo:

```ts
// src/lib/gsap.ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, useGSAP);

export { gsap, ScrollTrigger, useGSAP };
```

## Uso nos Componentes

```tsx
// Antes (❌ duplicado em cada componente)
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
gsap.registerPlugin(ScrollTrigger, useGSAP);

// Depois (✅ registro único)
import { gsap, ScrollTrigger, useGSAP } from "@/lib/gsap";
```

## Verificação

- Build deve passar sem warnings de `registerPlugin` duplicado
- Todos os componentes que usam GSAP importam exclusivamente de `@/lib/gsap`
- Nenhum componente importa diretamente de `gsap`, `gsap/ScrollTrigger`, ou `@gsap/react`

## Validado em

Desconsultor (Next.js 16, GSAP 3.15, 2026-06-16): removido registro duplicado de `page.tsx` e `SurveyDashboard.tsx`.
