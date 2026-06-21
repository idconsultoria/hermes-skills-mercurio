# Nano Banana 2 — Texture Generation Guide

> Google Gemini 3.1 Flash Image model. Tool: banananano2.ai/tools/ai-texture-generation-tool
> Free, no sign-up. Generates seamless tileable textures from text prompts.

## Interface

- **Category presets:** Stone Wall, Wood Plank, Geometric, Marbled, Fabric Weave, Sci-Fi Metal
- **Generate button** → 4 variations
- **Duration:** <15s per generation
- **Output:** 4K PNG (download directly)
- **Limitation:** RGB only (no native alpha/transparency)

## Optimized Prompts — Sergipetec Assets

### Asset 12 — Holographic Grid (direct hit)
```
Category: Sci-Fi Metal
Prompt: holographic grid, thin teal lines, bright nodes at intersections,
density variation denser at center, sci-fi war table, dark background #050A0F,
seamless tileable, 1024x1024
```
✅ Download PNG → salvar como `holo_grid.png`. Pronto.

### Asset 2 — Heightmap Reference
```
Category: Stone Wall (or Custom)
Prompt: smooth dark terrain elevation, low amplitude hills and ridges,
technological meseta, organic topography aerial view, no sharp peaks,
seamless tileable, grayscale friendly topography
```
⚠️ Post-process: converter para grayscale 16-bit no Photoshop/GIMP.

### Asset 14 — Beam Trail Streak
```
Category: Custom
Prompt: horizontal light streak, bright white core with teal glow,
soft longitudinal falloff, 256x32 pixels, motion trail,
clean edges, dark background transparent style
```
⚠️ Post-process: extrair alpha (remover fundo escuro), redimensionar para 256×32.

### Asset 4 — Particle Sprite
```
Category: Custom
Prompt: soft glowing particle, white hot core, teal halo,
radial gradient smooth falloff to transparent, round shape,
128x128 pixels, clean edges
```
⚠️ Post-process: redimensionar para 128×128, extrair alpha.

For spritesheet (16 variations), generate multiple with seed-like prompt variations:
```
slightly irregular shape, glowing mote, organic dust particle, teal halo
--- 
tiny spark, star shaped, bright core, teal glow
---
soft circle, wide halo, low intensity center, misty
```

## General-Purpose Texture Prompts

### Sci-fi panel
```
Dark metallic panel with recessed hex patterns, subtle teal edge glow,
industrial sci-fi, seamless tileable, 1024x1024, photorealistic PBR
```

### Dark marble
```
Dark stone surface #050A0F base, subtle veined pattern, matte finish,
seamless tileable, 1024x1024, cold elegant material
```

### Circuit board
```
Dark PCB texture, intricate teal circuit traces, gold contact points,
tech aesthetic, seamless tileable macro detail, 1024x1024
```

## Post-Processing Checklist

1. **Download** the best of 4 variations
2. **Crop/resize** to target dimensions (1024×1024, 128×128, etc.)
3. **Alpha extraction** (if transparency needed): select dark background by color → delete → export PNG 32-bit RGBA
4. **Grayscale** (heightmaps): Image → Mode → Grayscale → Mode → 16-bit
5. **Color palette check:** verify teal-only (#003B46, #1A5266, #4AC6D3, #66E8F1, #A8F5FB)
6. **Tileability test:** wrap on 3D object or tile in 2D editor to verify seamlessness
