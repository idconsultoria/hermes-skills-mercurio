# Quality Gate em exFAT/NTFS

> Como rodar Biome + Vitest + TSC em partições que não suportam `+x` (exFAT, NTFS).

## Problema

Partições exFAT e NTFS não suportam permissão de execução Unix. Binários nativos (`node_modules/.bin/*`, `@biomejs/cli-linux-x64/biome`) e symlinks (`npx`) falham com `EACCES` ou `command not found`.

## Solução: Invoque tudo via `node`

### Biome

```bash
# Copiar binário nativo para /tmp (que suporta +x)
cp node_modules/@biomejs/cli-linux-x64/biome /tmp/biome
chmod +x /tmp/biome

# Usar
/tmp/biome ci src/
/tmp/biome check --write src/
```

### Vitest

```bash
# Chamar diretamente via node (bypassa wrapper .bin/)
node ./node_modules/vitest/vitest.mjs run
node ./node_modules/vitest/vitest.mjs run --coverage
node ./node_modules/vitest/vitest.mjs          # watch mode
```

### TypeScript

```bash
# Chamar diretamente via node
node ./node_modules/typescript/bin/tsc --noEmit
```

### Next.js

```bash
node ./node_modules/next/dist/bin/next build
node ./node_modules/next/dist/bin/next dev
```

## Gate completo (script)

```bash
#!/bin/bash
BIOME=/tmp/biome
VITEST=./node_modules/vitest/vitest.mjs
TSC=./node_modules/typescript/bin/tsc

echo "=== BIOME ==="
$BIOME ci src/ || exit 1

echo "=== VITEST ==="
node $VITEST run || exit 1

echo "=== TSC ==="
node $TSC --noEmit || exit 1

echo "=== BUILD ==="
node ./node_modules/next/dist/bin/next build || exit 1

echo "✅ ALL GATES PASSED"
```

## npm scripts adaptados

```json
{
  "scripts": {
    "lint": "/tmp/biome ci src/",
    "lint:fix": "/tmp/biome check --write src/",
    "test": "node ./node_modules/vitest/vitest.mjs run",
    "test:watch": "node ./node_modules/vitest/vitest.mjs",
    "check": "/tmp/biome ci src/ && node ./node_modules/vitest/vitest.mjs run && node ./node_modules/typescript/bin/tsc --noEmit",
    "build": "node ./node_modules/next/dist/bin/next build"
  }
}
```

## Pitfalls

- **Biome binary é nativo (ELF)** — NÃO funciona com `node ./node_modules/@biomejs/cli-linux-x64/biome`. Precisa ser copiado para /tmp.
- **`npx` nunca funciona em exFAT/NTFS** — o wrapper em `node_modules/.bin/` é um symlink que requer +x. Sempre use `node <caminho direto>`.
- **Versão do Biome schema importa** — o `$schema` no `biome.json` precisa bater com a versão do binário. Biome 2.5.0 rejeita schema 1.9.4 com erros de `organizeImports` e `noConsoleLog`. Migração de v1.9 → v2.5:
  - `$schema`: `"https://biomejs.dev/schemas/2.5.0/schema.json"`
  - `organizeImports` → `assist`
  - `noConsoleLog` → `noConsole`
  - `recommended: true` → usar `preset: "recommended"` (recomendado mas `recommended` ainda funciona)
  - `quoteStyle: "single"` → `"double"` (para projetos que já usam double quotes)
  - `semicolons: "asNeeded"` → `"always"` (para projetos que já usam ponto-e-vírgula)
  - ⚠️ `biome check --write --unsafe` PODE QUEBRAR SINTAXE. Usar com cautela e verificar TSC depois.

## Biome unsafe-fix recovery

Biome `--unsafe` (`biome check --write --unsafe src/`) pode quebrar a sintaxe dos arquivos:
- Substituições de `noArrayIndexKey` podem romper JSX expressions
- `useButtonType` pode remover conteúdo de botões
- Sintomas: `TS1109: Expression expected`

Recuperação:

```bash
# 1. Reverter apenas os arquivos quebrados
git checkout -- <caminho/do/arquivo.tsx>

# 2. Aplicar auto-fix seguro (sem --unsafe)
/tmp/biome check --write src/

# 3. Reaplicar patches cirúrgicos perdidos
# (anotar os patches antes de rodar unsafe)
```

## Validado em

- Desconsultor (exFAT, 2026-06-16): Biome 2.5.0 + Vitest 4.1.9 + TSC + Next.js 16
- Propostadiagnstico (NTFS, 2026-06-16): Vite + esbuild + Vercel deploy
