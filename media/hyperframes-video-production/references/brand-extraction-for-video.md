# Brand Extraction for Video Production

Technique used to extract brand identity from a live website for video production.

## Sources to Check (in order)

### 1. Page CSS (curl + grep)
```bash
# Find the CSS file URL from HTML
curl -s "https://brand.com/" | grep -oP 'href="[^"]*\.css[^"]*"'

# Extract color hex values sorted by frequency
curl -s "CSS_URL" | grep -oP '#[0-9A-Fa-f]{6,8}' | sort | uniq -c | sort -rn | head -30

# Extract font families
curl -s "CSS_URL" | grep -oP 'font-family:\s*[^;]+' | sort | uniq -c | sort -rn
```

**Signal-to-noise filtering:**
- Colors with 10+ occurrences = likely brand colors
- Colors with 1-2 occurrences = likely third-party/library noise
- Gray tones (#69727d, #666, #999) = text, not brand
- Green (#2db742) = likely WhatsApp widget, not brand

### 2. @font-face Declarations
```bash
curl -s "CSS_URL" | grep "font-family:'" | sort | uniq -c | sort -rn
```

The font with the most declarations is typically the primary brand font. Check for weight variants (200-900) — a full weight range signals a primary font.

### 3. Logo Extraction
```bash
# Find image URLs on the page
curl -s "https://brand.com/" | grep -oP 'src="[^"]*\.(png|jpg|svg|webp)[^"]*"' | head -30

# Filter for logos
curl -s "https://brand.com/" | grep -oP 'src="[^"]*logo[^"]*\.(png|jpg|svg)[^"]*"'
```

Download the primary logo and analyze it with vision for exact colors, icon details, and typography style.

### 4. Browser Visual Verification
Use `browser_navigate` + `browser_vision` with specific questions:
- "What is the exact logo design — wordmark or icon+text? What colors?"
- "What colors appear on buttons and CTAs?"
- "What typography is used — serif or sans-serif? Bold or light?"
- "What icon style is used — filled, line-art, rounded?"

### 5. CSS Custom Properties (Elementor/WordPress sites)
```javascript
// In browser_console
const html = document.documentElement;
const computed = getComputedStyle(html);
const vars = [];
for (let prop of computed) {
  if (prop.startsWith('--')) vars.push(prop + ': ' + computed.getPropertyValue(prop));
}
```

Note: Many Elementor sites have 0 custom properties — they use inline styles injected by the builder.

### 6. Asset URLs for Partners/Integrations
```bash
curl -s "https://brand.com/" | grep -oP 'src="[^"]*\.(png|jpg|svg|webp)[^"]*"' | sort -u
```

Filter for partner/service names to find their logos. Download all relevant ones for the video.

## Reinterpreting Web Colors for Video

| Web Context | Video Adaptation |
|-------------|-----------------|
| UI blue `#1e87f0` on white bg | Deep navy `#001B3D` for full-screen dark backgrounds |
| Light gray `#f8f8f8` bg | Keep white text on dark — invert the relationship |
| Subtle gray text `#69727d` | Increase contrast — use rgba(255,255,255,0.7) on dark |
| Small accent touches | Amplify — neon versions with glow/box-shadow for motion impact |

**Golden rule:** Stay in the same hue family. Push saturation and lightness, never change the hue.
