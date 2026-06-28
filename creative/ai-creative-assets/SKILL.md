---
name: ai-creative-assets
category: creative
description: "Research AI tools for generating visual creative assets (textures, 3D models, sprites, vector icons) and craft optimized prompts + post-processing workflows for production-ready outputs.
Load this skill when the user asks which AI tool to use for a specific asset type (texture, 3D model, sprite, icon), needs optimized prompts for visual asset generation (Nano Banana 2, Meshy AI, Recraft AI, GenPBR, Scenario), or needs to plan a multi-asset pipeline across different AI tools."
metadata:
  hermes:
    tags: [ai-tools, texture-generation, 3d-models, asset-pipeline, prompt-engineering, creative-production]
    related_skills: [sound-design, style-guide-consultation, agy]
type: Creative
timestamp: 2026-06-21T05:11:49Z
---

# AI Creative Assets — Tool Research & Production Prompts

Umbrella skill for AI-powered visual asset generation. Covers:
- [Tool taxonomy by asset type](#tool-taxonomy-by-asset-type) — which AI tools for textures, 3D, icons, sprites
- [Core workflow](#core-workflow) — define → match → prompt → generate → post-process → verify
- [Prompt engineering for visual assets](#prompt-engineering-for-visual-assets) — framework, platform-specific patterns
- [Texture & PBR assets](#texture--pbr-assets) — Nano Banana 2, GenPBR, Scenario
- [3D model assets](#3d-model-assets) — Meshy AI, Hyper3D Rodin
- [Vector icon assets](#vector-icon-assets) — Recraft AI
- [Post-processing guide](#post-processing-guide) — format conversion, alpha extraction, grayscale

Load specific reference files for deep dives:
- `references/texture-generation-tools-compared.md` — Nano Banana 2 vs GenPBR vs Scenario: capabilities, pricing, workflow for each asset type.
- `references/nano-banana-2-texture-guide.md` — Optimized prompts for seamless tileable textures, heightmaps, sprites, beam trails.

## Tool Taxonomy by Asset Type

| Asset Type | Format | Primary Tool | Alternative | Free? |
|-----------|--------|-------------|-------------|-------|
| Seamless textures (PNG) | PNG 1024×1024+ | **Nano Banana 2** | Scenario TextureLab | ✅ Free (NB2) |
| PBR maps (height, normal, metal, roughness) | PNG | **GenPBR** (extracts from source image) | Playtex PBR | ✅ Free (512×512) |
| 3D models (GLB) | GLB | **Meshy AI** | Hyper3D Rodin | ✅ 200 credits/mo |
| SVG icons | SVG | **Recraft AI V4** | — | ✅ 30 gen/day |
| Particle sprites (PNG) | PNG 128×128 | **Nano Banana 2** + alpha extraction | SEELE AI | ✅ |
| Territory masks / channel maps | PNG RGBA | **Midjourney** + Photoshop separation | — | ⚠️ Manual work |
| HDRI environments | .hdr | **Hyper3D Omnicraft** / **Playtex HDRI** | NVIDIA Picasso | ✅ |

## Core Workflow

### Phase 1: Define asset specs
Extract from user request: format, dimensions, color palette, tileability, alpha/transparency needs.

### Phase 2: Match tool to asset type
Use the taxonomy table above. Consider: does the tool generate from scratch (NB2, Meshy, Recraft) or extract from input (GenPBR)?

### Phase 3: Craft platform-specific prompt
Use the prompt formula below, adapted to the platform's syntax.

### Phase 4: Generate and iterate
Most tools generate 4 variations. Audition, refine prompt, regenerate.

### Phase 5: Post-process for production
- **Alpha extraction:** Remove dark background, create transparency channel
- **Grayscale conversion:** For heightmaps, convert to 16-bit grayscale
- **Seamless check:** Verify tileability, especially at edges
- **Resize:** Match spec dimensions (1024×1024, 128×128, etc.)

### Phase 6: Verify against specs
Check format, dimensions, color palette, tileability, file size.

## Prompt Engineering for Visual Assets

### Universal formula
```
[Subject/Material] + [Details/Pattern] + [Style/Mood] + [Technical constraints]
```

### Nano Banana 2 texture prompts
Lead with material and surface detail. NB2 reads the full prompt and excels at tactile realism.

```
Dark anodized metal with subtle engraved teal circuit lines, monolithic sci-fi artifact,
1024x1024 seamless tileable, cold technological mood, 4K quality
```

### Platform-specific tips
- **Nano Banana 2:** Use category presets (Sci-Fi Metal, Geometric) as starting points
- **GenPBR:** Only accepts images as input (no text prompts); use Image Mode or Procedural Mode
- **Meshy AI:** Include dimensions in prompt ("2.4 units cube, centered") and desired format ("GLB with PBR textures")
- **Recraft AI:** Specify SVG-specific params ("stroke 1.8, round caps, currentColor, fill none")

## Texture & PBR Assets

### Nano Banana 2 (banananano2.ai/tools/ai-texture-generation-tool)
- **Best for:** Generating seamless textures from text prompts (no input image needed)
- **Model:** Google Gemini 3.1 Flash Image (Nano Banana 2)
- **Output:** 4K PNG, tileable by design
- **Free:** Yes, no sign-up required
- **Presets:** Stone Wall, Wood Plank, Geometric, Marbled, Fabric Weave, Sci-Fi Metal
- **Limitation:** Generates RGB only — heightmaps and alpha need post-processing

**Texture prompt example:**
```
Seamless holographic grid, thin teal lines, bright nodes at intersections,
density variation denser at center, sci-fi war table, dark background,
1024x1024 tileable
```

### GenPBR (genpbr.com)
- **Best for:** Extracting PBR maps (normal, height, roughness, metallic, AO) from existing images
- **Method:** Deterministic algorithm, not AI — predictable, reproducible
- **Free:** 512×512 no account, 1024×1024 with free account
- **Procedural Mode:** Build textures from sliders without source image
- **Not for:** Generating new images from text

## 3D Model Assets

### Meshy AI (meshy.ai)
- **Best for:** Text/image to 3D model with PBR textures
- **Output formats:** GLB, FBX, OBJ, STL, USDZ, BLEND
- **Free tier:** 200 credits/month
- **PBR maps:** Included (albedo, normal, roughness, metallic)
- **Pipeline:** Text prompt → 3D model → texture → auto-rigging → animation
- **Plugins:** Blender, Unity, Unreal Engine, Maya, Godot

**Prompt formula for 3D:**
```
[Subject] + [Style/Detail] + [Technical constraints]
```

**Example (Sergipetec cube artifact):**
```
Dark cubic artifact, chamfered edges, recessed panels, teal-bright emissive core,
one face has a clear opening, dark anodized metal, sci-fi, PBR textures, GLB format
```

## Vector Icon Assets

### Recraft AI V4 (recraft.ai/ai-vector-generator)
- **Best for:** Text-to-SVG, clean paths, editable layers
- **Free:** 30 generations/day
- **Output:** SVG (native vector), PNG fallback
- **Style control:** Line weight, color palette, stroke caps
- **Integration:** Figma, Framer, Google Docs plug-in

**Prompt formula for icons:**
```
Minimal line icon, [subject], stroke 1.8, round caps, currentColor, fill none, dark theme
```

## Post-Processing Guide

### Common post-processing operations

| Operation | Tool | When needed |
|-----------|------|-------------|
| Alpha extraction | Photoshop / GIMP | Sprites, beam trails, glow textures |
| Grayscale 16-bit | Photoshop / GIMP | Heightmaps from color source |
| Resize | ffmpeg / ImageMagick | Mismatched dimensions |
| Seamless tiling check | Test in 3D viewer | All tileable textures |
| Format conversion | ffmpeg / online | PNG ↔ JPG, etc. |

### Heightmap conversion (color → 16-bit grayscale)
1. Open generated PNG in Photoshop/GIMP
2. Image → Mode → Grayscale
3. Image → Mode → 16-bit
4. Adjust levels so range spans 0–65535
5. Export as PNG

### Alpha extraction (dark background → transparency)
1. Open generated PNG in Photoshop/GIMP
2. Select by color (remove dark background)
3. Invert selection → save as alpha channel
4. Export as PNG 32-bit RGBA

## Pitfalls

- **Nano Banana 2 cannot generate alpha/transparency natively.** All outputs are RGB. Alpha extraction is always post-process.
- **GenPBR does not generate images from text.** Only extracts PBR maps from existing images. Users expecting text-to-texture will be frustrated.
- **Meshy AI free tier is limited (200 credits/mo).** One GLB generation costs ~20–50 credits depending on complexity.
- **Recraft AI generates SVG but check path quality.** Complex prompts may produce bloated paths; optimize with SVGO before shipping.
- **Not all AI texture tools produce truly seamless edges.** Always verify tileability by testing the texture wrapped on a 3D object or tiled in a 2D editor — some tools claim seamlessness but produce visible repeats.
- **Color space mismatch.** PBR maps (roughness, metalness, height) must be imported as Linear, not sRGB. GenPBR docs emphasize this as the #1 cause of "bad results."

## Related

- `sound-design` — for audio SFX and music generation (the audio counterpart to this skill)
- `style-guide-consultation` — for brand-specific color palettes and design tokens
- `agy` — for generating visual output via Antigravity CLI (alternative pipeline for some texture/icon tasks)
