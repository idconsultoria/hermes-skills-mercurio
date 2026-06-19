# Biome v2 Migration Reference

> Padrões descobertos na sessão do Desconsultor (2026-06-16). CLI v2.5.0.

## Breaking Changes v1 → v2

| v1.x | v2.x | Notas |
|------|------|-------|
| `"organizeImports": { "enabled": true }` | `"assist": { "enabled": true }` | Renomeado |
| `"noConsoleLog": "warn"` | `"noConsole": "warn"` | Renomeado |
| `"recommended": true` (no linter.rules) | `"preset": "recommended"` | `recommended` deprecated, será removido |
| `$schema: ".../1.9.4/..."` | `$schema: ".../2.5.0/..."` | Usar versão do CLI |

## Template biome.json v2 (projeto Next.js)

```json
{
  "$schema": "https://biomejs.dev/schemas/2.5.0/schema.json",
  "assist": { "enabled": true },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf"
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedVariables": "error",
        "noUndeclaredVariables": "error"
      },
      "style": {
        "noNonNullAssertion": "error",
        "useConst": "error",
        "useTemplate": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn",
        "noConsole": "warn"
      },
      "complexity": {
        "noForEach": "off",
        "noBannedTypes": "error"
      }
    }
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "double",
      "semicolons": "always",
      "trailingCommas": "all"
    }
  }
}
```

## Pitfalls

- **`--write --unsafe` pode quebrar JSX** — no Desconsultor, `biome check --write --unsafe` gerou `TS1109: Expression expected` em page.tsx, CaptureGate.tsx, DiagnosticWizard.tsx. Usar `git checkout` para reverter se isso acontecer. Preferir `--write` (safe only).
- **Binário nativo em exFAT** — `node_modules/@biomejs/cli-linux-x64/biome` é ELF binário. Em exFAT/FAT32, precisa: `cp node_modules/@biomejs/cli-linux-x64/biome /tmp/biome && chmod +x /tmp/biome`. Depois: `/tmp/biome ci src/`.
- **`noExplicitAny` como warn primeiro** — projetos legados têm muitos `any`. Começar com `"warn"`, subir para `"error"` gradualmente. Mudar direto para `"error"` gera 90+ erros e polui o output.
- **`quoteStyle` deve matchar o projeto** — se o código usa `"double"`, o biome.json deve ter `"double"`. Usar `"single"` gera ~60+ formatações desnecessárias.
