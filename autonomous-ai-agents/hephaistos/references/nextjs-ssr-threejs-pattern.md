# Next.js 16 + Three.js SSR Pattern

> Como usar @react-three/fiber com Next.js 16 (que bloqueia `ssr: false`)

## Problema

No Next.js 16, `dynamic(() => import(...), { ssr: false })` é **bloqueado**:

```
`ssr: false` is not allowed
```

Isso impede a abordagem tradicional de carregar Three.js apenas no cliente.

## Solução: Client-side mount guard

No próprio componente Three.js, usar `useState` + `useEffect` para verificar montagem:

```tsx
"use client";

import React, { useRef, useMemo, useEffect, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, MeshDistortMaterial } from "@react-three/drei";

export function Hero3D() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null; // ← SSR-safe: não renderiza nada no servidor

  return (
    <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 45 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true }}
      >
        {/* Three.js scene */}
      </Canvas>
    </div>
  );
}
```

## Por que funciona

1. `useState(false)` + `useEffect(() => setMounted(true), [])` → no SSR, `mounted` é `false`, retorna `null`
2. No cliente, o `useEffect` dispara e seta `mounted = true` → re-renderiza com o `<Canvas>` Three.js
3. O Three.js (`@react-three/fiber`, `three`) nunca é executado no servidor

## Importação

No componente pai, importar normalmente (SEM `dynamic`):

```tsx
import { Hero3D } from "./Hero3D"; // ← importação direta, sem dynamic
```

## Stack validada

- Next.js 16.2.9
- React 19.2.4
- @react-three/fiber 9.6.1
- @react-three/drei 10.7.7
- three 0.184.0

## Links

- [[hephaistos/SKILL.md]] — pitfall sobre Next.js 16 SSR com Three.js
