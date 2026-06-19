# Fraunces Display Font Implementation (Next.js)

## Quando usar
Números grandes (hero stats, dashboard counters, métricas) que precisam de personalidade tipográfica.

## Steps

### 1. layout.tsx — Import e variável
```tsx
import { Fraunces, Outfit, Plus_Jakarta_Sans } from "next/font/google";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  style: ["normal", "italic"],
});

// No html element:
<html className={`${outfit.variable} ${jakarta.variable} ${fraunces.variable} h-full antialiased`}>
```

### 2. globals.css — Registrar no @theme
```css
@theme {
  --font-outfit: var(--font-outfit);
  --font-jakarta: var(--font-jakarta);
  --font-fraunces: var(--font-fraunces);
}
```

### 3. Componentes — Aplicar classe
```tsx
<span className="text-7xl font-black font-fraunces text-teal-400 tabular-nums">
  80.6%
</span>
```

## Font pairing
- **Headings:** Outfit (sans-serif, geometric)
- **Body:** Plus Jakarta Sans (sans-serif, humanist)
- **Display numbers:** Fraunces (serif, optical sizing, personality)

## Referência
- Implementado no Desconsultor, 2026-06-16
