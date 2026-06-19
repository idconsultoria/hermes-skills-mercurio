# GSAP ScrollTrigger Refresh on Resize

## Problema
ScrollTrigger calcula posições no mount. Após resize (especialmente orientation change mobile), animações ficam desalinhadas — elementos aparecem na posição errada ou não disparam.

## Padrão
```tsx
import { gsap, ScrollTrigger, useGSAP } from "@/lib/gsap";

// Em qualquer componente que usa ScrollTrigger:
useEffect(() => {
  const handleResize = () => {
    ScrollTrigger.refresh();
  };
  window.addEventListener("resize", handleResize);
  return () => window.removeEventListener("resize", handleResize);
}, []);
```

## Quando aplicar
- Qualquer componente com `ScrollTrigger.batch()` ou `scrollTrigger` em `gsap.fromTo()`
- Aplicar UMA vez no componente pai (geralmente page.tsx), não em cada componente filho

## Cuidados
- `ScrollTrigger.refresh()` é debounce-safe — múltiplas chamadas rápidas são agrupadas
- Não usar com `passive: true` no listener (não é scroll event)
- Se usar `ScrollTrigger.config({ limitCallbacks: true })`, refresh pode não disparar para todos os triggers

## Referência
- P3-08 do audit do Desconsultor, implementado em 2026-06-16
