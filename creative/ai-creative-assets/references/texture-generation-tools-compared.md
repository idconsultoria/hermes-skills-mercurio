# Texture Generation Tools Compared

> Comparative guide from Sergipetec project (Jun 2026).
> For generating PNG textures: seamless tiles, heightmaps, sprites, beam trails, channel masks.

## Nano Banana 2 (banananano2.ai/tools/ai-texture-generation-tool)

| Aspect | Detail |
|--------|--------|
| **Model** | Google Gemini 3.1 Flash Image |
| **What it does** | Text → seamless tileable 4K PNG (generates from scratch) |
| **Free?** | ✅ Yes, no sign-up needed |
| **Presets** | Stone Wall, Wood Plank, Geometric, Marbled, Fabric Weave, Sci-Fi Metal |
| **Speed** | <15s per generation |
| **Seamless** | Yes, built-in |
| **Limitations** | RGB only (no native alpha), no PBR map extraction |
| **Best for** | Creating textures from scratch: holo grids, sci-fi panels, terrain references |

### When to choose NB2 over alternatives
- You need a texture from a text prompt (no source image)
- You need seamless tileability
- You need 4K resolution for free
- You don't need PBR maps extracted

## GenPBR (genpbr.com)

| Aspect | Detail |
|--------|--------|
| **What it does** | Image → PBR maps (height, normal, roughness, metallic, AO) |
| **Free?** | ✅ Yes (512×512 no account, 1024×1024 with account) |
| **Method** | Deterministic algorithm (not AI/ML) |
| **Speed** | Instant (client-side) |
| **Seamless** | Depends on input |
| **Limitations** | Cannot generate images from text; needs source image |
| **Best for** | Extracting height maps, normal maps from existing textures |

### When to choose GenPBR
- You already have a source texture and need PBR maps extracted
- You need deterministic, reproducible results (version control friendly)
- You want client-side processing (no upload, private)

## Scenario TextureLab (scenario.com)

| Aspect | Detail |
|--------|--------|
| **What it does** | Text → PBR texture stack (albedo + normal + roughness + metallic) |
| **Free?** | ⚠️ Requires account (free tier available) |
| **Method** | AI (custom models + fine-tuning) |
| **Speed** | Seconds |
| **Seamless** | Yes |
| **Best for** | Full PBR material generation from text in one shot |

### When to choose Scenario
- You need the full PBR stack (not just RGB) from a text prompt
- You have a specific art style and want to fine-tune a model

## Decision Matrix

| Need | NB2 | GenPBR | Scenario |
|------|-----|--------|----------|
| Text → seamless texture | ✅ Best | ❌ | ✅ |
| Text → full PBR stack | ❌ | ❌ | ✅ Best |
| Image → height map | ❌ (manual) | ✅ Best | ❌ |
| Image → normal map | ❌ | ✅ Best | ❌ |
| Free, no sign-up | ✅ Best | ✅ 512×512 | ❌ |
| Deterministic output | ❌ | ✅ Best | ❌ |
| Commercial license | ✅ | ✅ | ✅ |
| 4K resolution | ✅ Best | ⚠️ Paid | ⚠️ Paid |

## Sergipetec-Specific Recommendations

| Asset | Best Tool | Why |
|-------|-----------|-----|
| 2 — Heightmap | **GenPBR** (Procedural Mode) + grayscale conversion | Extracts height from procedural or uploaded terrain |
| 12 — Holo Grid | **Nano Banana 2** (Sci-Fi Metal preset) | Seamless by design, free, no account |
| 14 — Beam Trail | **Nano Banana 2** + alpha extraction | Generates the streak; alpha is post-process |
| 4 — Particle Sprite | **Nano Banana 2** + manual resize + alpha | NB2 generates the glow; manual cleanup needed |
