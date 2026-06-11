# WordPress Elementor CSS Extraction for Brand Identity

## Context

Many Brazilian SMB sites (ISPs, local services) use WordPress + Elementor + Litespeed Cache. This stack
serves a single minified CSS file that contains the full design system. Extracting it directly
is faster and more precise than browser_vision alone.

## Technique

### 1. Find the CSS file URL

```bash
curl -s "https://example.com/" | grep -oP 'href="[^"]*\.css[^"]*"'
```

Litespeed caches to paths like `/wp-content/litespeed/css/<hash>.css?ver=<hash>`.

### 2. Extract exact hex colors

```bash
curl -s "$CSS_URL" | grep -oP '#[0-9A-Fa-f]{6,8}' | sort | uniq -c | sort -rn | head -30
```

This reveals the real palette: primary blue (`#1e87f0`), accent orange (`#ff9f00`), neutrals, etc.

### 3. Extract font families

```bash
curl -s "$CSS_URL" | grep -oP 'font-family:\s*[^;]+' | sort | uniq -c | sort -rn
```

Elementor sites typically declare Plus Jakarta Sans, Poppins, Roboto with all weights as `@font-face` blocks.

### 4. Extract Elementor global color variables

```bash
curl -s "$CSS_URL" | grep -oP '(?<=color:|background:|border-color:)\s*[^;]+' | sort | uniq -c | sort -rn | head -20
```

Shows `--e-global-color-*` variable usage and which hex values they resolve to.

### 5. Cross-reference with browser vision

Use `browser_vision` to verify the logo (combination mark vs wordmark, icon shapes, exact blue/orange tones). The CSS gives the web palette; vision gives the logo's printed palette.

### 6. Download assets

```bash
curl -s "https://example.com/" | grep -oP 'src="[^"]*\.(png|jpg|svg|webp)[^"]*"' | sort -u
```

Filter for logo, streaming partner logos, and icons.

## Pitfalls

- Elementor injects styles via `<style>` blocks (not `<link>`), but Litespeed consolidates them into one CSS file
- Browser console `document.styleSheets` may show 0 rules (CORS restrictions on same-origin CSS inspection)
- `getComputedStyle()` on `documentElement` returns 0 custom properties — Elementor scopes them to `.elementor-element` containers
