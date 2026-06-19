# Vitest + Next.js + jsdom Setup (exFAT-safe)

> Configuração completa de testes para projetos Next.js em filesystems sem suporte a symlinks.

## Instalação (exFAT/NTFS)

```bash
npm install --no-bin-links --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitejs/plugin-react
```

## vitest.config.ts

```typescript
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    setupFiles: ["./src/test-setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.ts", "src/**/*.test.tsx", "src/**/*.d.ts"],
      thresholds: { statements: 80, branches: 75, functions: 80, lines: 80 },
    },
  },
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
});
```

## src/test-setup.ts

```typescript
import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// jsdom não tem matchMedia — mock obrigatório para componentes com GSAP/prefers-reduced-motion
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

## package.json scripts

```json
{
  "test": "npx vitest run",
  "test:watch": "npx vitest",
  "test:coverage": "npx vitest run --coverage",
  "check": "npx biome ci src/ && npx vitest run && npx tsc --noEmit"
}
```

## Execução em exFAT

`npx vitest` não funciona (symlink). Usar: `node ./node_modules/vitest/vitest.mjs run`

## Testes de componente (exemplo)

```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import GlowCard from "./GlowCard";

describe("GlowCard", () => {
  it("should render children", () => {
    render(<GlowCard className="test"><p>Content</p></GlowCard>);
    expect(screen.getByText("Content")).toBeDefined();
  });
});
```

## Pitfalls

- `matchMedia` mock É obrigatório — sem ele, qualquer componente com GSAP ou `prefers-reduced-motion` falha com `TypeError: window.matchMedia is not a function`
- Em exFAT, `npx` não resolve symlinks. Chamar binários diretamente via `node ./node_modules/<pkg>/...`
- `@testing-library/jest-dom/vitest` (não `/jest`) — o import errado causa `toBeInTheDocument is not a function`
