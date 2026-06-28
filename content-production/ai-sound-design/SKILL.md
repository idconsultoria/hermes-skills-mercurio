---
name: ai-sound-design
title: AI Sound Design — SFX & Ambient Audio
description: "Generate, process, and optimize sound effects and ambient audio using AI tools and

Load this skill when you need to create sound effects, ambient audio, or UI sounds for web/game/film projects. Covers prompt engineering for ElevenLabs SFX V2, settings optimization (Prompt Influence, duration, reverb), audio post-processing with ffmpeg (normalization, format conversion), and seamless loop creation for ambient drones."
category: content-production
triggers:
  - user asks for sound effects, SFX, UI sounds, ambient music, drone, audio loop
  - generate audio assets for web/game/film
  - ffmpeg audio processing
type: Media
timestamp: 2026-06-21T05:11:49Z
---

# AI Sound Design — SFX & Ambient Audio

## Overview

Generate production-ready sound effects and ambient audio using AI text-to-audio tools, then process with ffmpeg for web delivery. Focused on UI sound families (hover, click, open, close, whoosh) and ambient drones/loops.

---

## ElevenLabs SFX — Prompt Engineering

### Platform specs
- **Model:** ElevenLabs SFX V2 (48kHz, broadcast quality)
- **4 variations** per generation
- **Duration:** 0.1–30s (manual or auto)
- **Looping toggle:** seamless repeat for ambient sounds
- **Prompt Influence slider:** default 30%, controls literalness
- **Export:** WAV 48kHz (master) → MP3 320kbps (delivery)
- **Licensing:** commercial use on paid plans (Starter $5/mo+)

### The prompt formula
```
[Source/Object] + [Action] + [Environment/Context] + [Mood modifier]
```

Place emotion/genre FIRST, technical specs SECOND (ElevenLabs reads LTR with decreasing weight).

### Principles
1. **Specific materials** — "metal", "ceramic", "crystal", not generic
2. **Acoustic environment** — "dry small room" ≠ "cathedral reverb"
3. **Precise action** — "short tick fast attack" > "sound"
4. **Duration explicit** — "0.08s", "fade out 0.3s"
5. **Mood last** — "cinematic", "cold", "technological"
6. **No contradictions** — "soft but aggressive" confuses the model
7. **Onomatopoeia + description** — works better than either alone

### Settings for UI SFX (CRITICAL)
| Parameter | Value | Why |
|-----------|-------|-----|
| **Prompt Influence** | **80%** | Consistency between variations > creativity |
| **Duration** | **Manual** (0.1–0.4s) | Timing precision required for UI |
| **Reverb** | `dry studio, no reverb` | Site applies its own via Web Audio API |
| **Mood throughline** | `cold`, `clean`, `precision` | Family cohesion across all samples |

### Typical UI SFX samples and durations
| Sample | Duration | Character |
|--------|----------|-----------|
| `hover.mp3` | 0.1s | Crystal tick, ultrashort attack |
| `click.mp3` | 0.15s | Ceramic/metal percussive tap |
| `open.mp3` | 0.25s | Rising shimmer, pitch glide up |
| `close.mp3` | 0.25s | Descending contralto tone |
| `whoosh.mp3` | 0.4s | Bandpass air sweep with body |

### Troubleshooting
| Problem | Fix in prompt |
|---------|---------------|
| Too long | Add `under 0.5s`, `tight transient, minimal tail` |
| Too busy | Add `clean`, `minimal layers` |
| Weak impact | Add `high impact`, `punchy attack` |
| Too bright | Add `warm`, `no piercing highs` |
| No personality | Add `cold`, `technological`, `crystal clear` |

---

## Audio Loop Crossfade (ffmpeg)

When AI-generated audio has fade-in/fade-out that breaks seamless looping:

### PowerShell-safe ffmpeg (avoid bracket issues)

```powershell
# Step 1: Cut fades (trim 2s start + 2s end)
# Replace 116 with (duration - 4) seconds
ffmpeg -i input.m4a -ss 2 -t 116 drone_trimmed.wav -y

# Step 2: Extract first 2s of body as loop head
ffmpeg -i drone_trimmed.wav -t 2 drone_loop_head.wav -y

# Step 3: Crossfade body end with loop head
ffmpeg -i drone_trimmed.wav -i drone_loop_head.wav -filter_complex "[0:a][1:a]acrossfade=d=2[out]" -map "[out]" -codec:a libvorbis -b:a 192k output.ogg -y
```

### Why the 2-stream approach
`acrossfade` requires TWO audio input streams. Single-file approaches fail with `Cannot find an unused audio input stream` in PowerShell due to bracket escaping issues. The 3-step method above works reliably on Windows.

### Loudness normalization
```powershell
ffmpeg -i input.wav -af "loudnorm=I=-18:LRA=7:TP=-1" -b:a 320k output.mp3 -y
```

### Format conversion best practices
| Source → Target | Command |
|----------------|---------|
| WAV master → MP3 320kbps CBR | `-af loudnorm=I=-18:LRA=7:TP=-1 -b:a 320k` |
| WAV master → OGG Vorbis q8 | `-codec:a libvorbis -b:a 192k` |
| Batch all WAVs in folder | `Get-ChildItem -Filter "*.wav" | ForEach-Object { ffmpeg -i $_.FullName -af "loudnorm=..." "$($_.BaseName).mp3" -y }` |

---

## GenPBR — What it does and doesn't do

- **Does:** Extract Normal, Roughness, Metallic, AO, Height maps from an EXISTING image
- **Does NOT:** Generate images from text prompts (use Nano Banana 2, Midjourney, or SD for that)
- **Does NOT:** Create alpha channels or manipulate transparency
- **Does NOT:** Generate vector graphics (SVG)
- **Use for:** Converting a source texture into PBR map stack
- **Don't use for:** Creating assets from scratch, transparent sprites, masks
- **Free tier:** 512×512 (no account), 1024×1024 (free account), client-side processing

---

## Workflow: UI SFX production pipeline

```
1. Research → identify tools per asset type
2. Generate 4 variations per sample (ElevenLabs)
3. Audition → pick best take
4. Download WAV master archive
5. Normalize loudness (-18 LUFS) → convert to MP3 320kbps
6. Name exactly per spec (hover.mp3, click.mp3, etc.)
7. Integrate into site (replace procedural fallback)
```

---

## References
- ElevenLabs SFX docs: https://elevenlabs.io/docs/overview/capabilities/sound-effects
- Promptomania guide: https://promptomania.com/models/elevenlabs/elevenlabs-sfx
- GenPBR: https://genpbr.com
- ffmpeg loudnorm filter docs
