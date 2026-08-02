# ID Consultoria — Brand Design Tokens

Extracted 2026-07-29 from `idconsultoria/SiteId` (React/Vite/Tailwind).

## Source Files

| File | What |
|------|------|
| `tailwind.config.js` | Brand colors, font families, box shadows |
| `src/constants.ts` | `theme.colors`, `theme.fonts`, company info |
| `index.html` | Google Fonts preloads (Nunito, Bricolage Grotesque, Syne, DM Sans, IBM Plex Mono) |

## Colors

| Token | Hex | Tailwind Class | Usage |
|-------|-----|---------------|-------|
| **Primary** | `#4AC6D3` | `brand-primary` | CTAs, links, accents, glow |
| **Secondary** | `#5FDBA7` | `brand-secondary` | Success states, hover highlights |
| **Depth** | `#005465` | `brand-depth` | Navbar, footer, dark backgrounds |
| **Background** | `#050a0f` | `brand-bg` | Main page background (dark theme) |

### Brand Shadows

```css
--shadow-brand-sm: 0 0 10px rgba(74, 198, 211, 0.3);
--shadow-brand-md: 0 0 20px rgba(74, 198, 211, 0.4);
--shadow-brand-lg: 0 0 40px rgba(74, 198, 211, 0.5);
```

## Typography

| Role | Font Stack |
|------|-----------|
| **Headings** | `Bricolage Grotesque`, Nunito, sans-serif |
| **Body** | `Nunito`, system-ui, sans-serif |
| **Mono** | `IBM Plex Mono`, source-code-pro, monospace |
| **Display** | `Syne`, sans-serif |
| **Alt body** | `DM Sans`, sans-serif |

### Google Fonts URL

```
https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&family=Bricolage+Grotesque:wght@300;400;500;600;700;800&family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;700&family=IBM+Plex+Mono:wght@300;400;500;600&display=swap
```

## Company Info

- **Name:** ID Consultoria e Treinamento
- **Domain:** idconsultoria.ai
- **Tagline:** Inteligência de Mercado com IA para PMEs
- **Email:** contato@idconsultoria.ai

## Mapping to Moodle Boost Union

| ID Token | Boost Union Setting | Notes |
|----------|-------------------|-------|
| `#005465` (Depth) | `brandcolor` | Main brand color for navbar, footer |
| `#4AC6D3` (Primary) | `linkcolor`, `buttonbrandcolor` | Links and CTA buttons |
| `#4AC6D3` (Primary) | Custom SCSS `$primary` | Bootstrap variable override |
| `#5FDBA7` (Secondary) | Custom SCSS `$success` | Success/green states |
| `#050a0f` (BG) | Login background | Dark theme for login page |
| Nunito | `customfonts` via Google Fonts URL | Body font |
| Bricolage Grotesque | Custom SCSS `headings` | Display font for headings |

## Extraction Workflow (reusable)

For any brand's design system, extract tokens before applying to a target platform:

```bash
# 1. Clone the brand's site repo
gh repo clone <org>/<site-repo> /tmp/brand-check -- --depth 1

# 2. Read design token sources
cat /tmp/brand-check/tailwind.config.js     # colors, fonts, shadows
cat /tmp/brand-check/src/constants.ts        # theme object
cat /tmp/brand-check/index.html              # Google Fonts URLs

# 3. Map to target platform's customization system
# (Moodle → mdl_config_plugins, WordPress → Customizer, etc.)
```
