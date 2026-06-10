# WeasyPrint: CSS Compatibility on ARM64 Linux

WeasyPrint is the only viable HTML→PDF renderer on this ARM64 Linux system
(no Chromium/Puppeteer available — Google doesn't publish linux-arm64 builds,
and the Debian `.deb` requires glibc 2.42 while the system has 2.41).

## CSS Features WeasyPrint Does NOT Support

| CSS Feature | Symptom | Fix |
|-------------|---------|-----|
| `-webkit-background-clip: text` + `-webkit-text-fill-color: transparent` | Text gradient becomes a solid rectangle | Replace with `color: <solid-color>` |
| `@keyframes` animations | Ignored silently | Remove or leave — no effect |
| `box-shadow` with blur | May render as solid block | Remove `box-shadow` from `.page` wrapper |
| `border-radius` on `.page` wrapper | May clip content | Remove from outer wrapper, keep on inner cards |
| `overflow: hidden` on page | May clip content | Remove |
| `display: flex; justify-content: center; padding` on body | Breaks page flow | Replace with bare body: `background: color; color: color; font-family: ...` |
| `@page { margin: 0; }` | No margins, content goes to edge | Use `@page { size: A4; margin: 1.2cm 1.5cm; }` |
| Inline SVGs with `<defs>` gradients | Usually works | Test each one |
| `backdrop-filter: blur()` | Will fail silently | Remove |

## Workflow

1. **Keep the browser-perfect HTML untouched.** The source HTML (with gradients,
   shadows, animations) is the canonical version for browser viewing.
2. **Create a PDF-optimized copy** with only the minimal CSS substitutions above.
3. **Render with weasyprint:**
   ```bash
   uv run python3 -c "
   from weasyprint import HTML
   HTML('input.html').write_pdf('output.pdf')
   "
   ```
4. **Verify page count** — if the PDF has far more pages than expected,
   `break-inside: avoid` on too many elements is the usual culprit.
   Remove it from all but the largest blocks.

## Quick Substitution Checklist (sed-safe)

```bash
# In the PDF copy only:
s/-webkit-background-clip: text.*//g
s/-webkit-text-fill-color: transparent;//g
s/background: linear-gradient.*$//g
s/border-radius: 20px/border-radius: 0/g
s/overflow: hidden;//g
s/box-shadow: 0 20px.*//g
s/@page { size: A4; margin: 0; }/@page { size: A4; margin: 1.2cm 1.5cm; }/g
```

## Why Chromium Is Unavailable

- Google's `chrome-for-testing-public` does **not** distribute linux-arm64 builds.
- The `chromium-browser-snapshots` bucket has no `Linux_ARM64_Cross` entries
  with valid builds (empty directory structure).
- Debian's `chromium_*.deb` extracts fine with `ar x` + `tar xf`, but
  depends on `glibc >= 2.42`. This system has `glibc 2.41`.
- `apt-get install` requires root — not available here.
- `puppeteer` and `playwright` download attempts time out on this network
  (large ~150 MB downloads).
- Playwright's system-dependency installer requires `su` (fails).
- The extracted Debian chromium binary also needs `libopenh264.so.8`,
  `libdouble-conversion.so.3`, and other libraries not present.
