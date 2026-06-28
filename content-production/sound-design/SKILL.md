---
name: sound-design
category: content-production
description: "Umbrella skill for AI sound effects (SFX) and audio production — prompt engineering, UI sound design, audio post-processing, format delivery.
Load this skill for any sound design task: generating UI SFX with AI tools (ElevenLabs, Noiz AI), creating ambient/drone music, designing sonic identities for brands/interfaces, post-processing audio (normalization, format conversion, loudness), and integrating audio into web/desktop projects."
metadata:
  hermes:
    tags: [audio, sfx, sound-design, elevenlabs, ffmpeg, audio-post-processing]
    related_skills: [text-to-speech]
type: Media
timestamp: 2026-06-21T05:11:49Z
---

# Sound Design — AI SFX & Audio Production

Umbrella skill. Covers:
- [AI sound effect generation](#ai-sfx-generation) — ElevenLabs SFX V2 prompting, platform overview
- [UI sound design patterns](#ui-sound-design-patterns) — hover, click, riser, whoosh, close archetypes
- [Audio post-processing](#audio-post-processing) — ffmpeg normalization, format conversion
- [Prompt engineering for audio](#sfx-prompt-engineering) — framework, formula, token optimization

Load specific reference files for deep dives:
- `references/elevenlabs-sfx-guide.md` — Full ElevenLabs SFX guide with 15 optimized prompts for UI sounds, settings, export workflow, ffmpeg pipeline.
- `references/elevenlabs-music-ambient-drone.md` — Ambient drone generation with ElevenLabs Music: prompt library, conversational refinement, export workflow.
- `references/audio-loop-crossfade.md` — Ffmpeg crossfade technique for seamless audio loops: trimming built-in fades, crossfade parameters, PowerShell commands, verification.

## AI Tool Selection: SFX vs Music

| Need | Tool | Max Duration | Format |
|------|------|-------------|--------|
| UI sounds, one-shots, Foley (<30s) | **ElevenLabs SFX V2** | 30s | WAV/MP3 48kHz |
| Ambient drone, background music, loops (>30s) | **ElevenLabs Music** | 5 min | WAV/MP3 44.1kHz |
| Multi-layer Foley with stems | **Noiz AI** | varies | WAV 48kHz stems |
| Pure instrumental ambient (no vocals) | **Stable Audio** / **MemoTune** / **Sonura** | varies | WAV/MP3 |

**Key distinction:** SFX is for precise one-shot sounds under 30s. Music is for longer compositions. For ambient drone (60–180s loops), use **ElevenLabs Music** with `instrumental only, no vocals` explicitly in the prompt.

### ElevenLabs SFX V2

- **Model:** ElevenLabs SFX V2 — output at 48kHz (broadcast/film standard)
- **4 variations per generation**
- **Duration:** auto or manual (0.1–30s)
- **Looping toggle:** seamless loops for ambient textures
- **Prompt Influence slider:** default 30%; higher = more literal adherence
- **Export:** WAV (48kHz, 24-bit) for master, MP3 320kbps CBR for web delivery
- **Credits:** 40 credits/s when duration is specified
- **License:** commercial use included in paid plans (Starter $5/mo+)

### Noiz AI (alternative)

Prompt-based SFX with layered stems, intensity/timing controls, and embedded metadata. Strong for complex Foley, game audio, and multi-layer sound design where stem separation matters.

### ElevenLabs Music — Ambient Drone & Background

For tracks longer than 30s (ambient drone, cinematic pads, background music). Uses the ElevenLabs Music API (v2), max 5 minutes.

**Prompt formula (reading order matters — LTR decreasing weight):**
```
[Emotion/Genre] + [Instruments/Texture] + [Technical specs] + [Restrictions]
```

**Key rules for ambient:**
- Always add `instrumental only, no vocals` explicitly — model defaults to vocal output
- Lead with emotion and genre, then technical specs
- BPM 60–80 (or no tempo) for ambient
- Use conversational refinement after first generation: `"make it darker"`, `"add more reverb"`

**Optimized ambient drone prompt (Sergipetec style):**
```
Instrumental only. Dark ambient cinematic drone in D minor, evolving slowly, deep pedal bass D2, fifth A2, octave D3, shimmering overtones emerging and dissolving, warm pad layers, contemplative and technological, no rhythm, no percussion, no beat, evolving texture, 120 seconds. No lyrics, no vocals, clean studio production.
```

**Post-processing for seamless loop:**
ElevenLabs Music outputs often have built-in fades (~2s each end). To make loopable:

1. Trim fades: `ffmpeg -i input.m4a -ss 2 -t <duration_minus_4> trimmed.wav`
2. Extract loop head: `ffmpeg -i trimmed.wav -t 2 loop_head.wav`
3. Crossfade: `ffmpeg -i trimmed.wav -i loop_head.wav -filter_complex "[0:a][1:a]acrossfade=d=2[out]" -map "[out]" output.ogg`

**PowerShell (Windows) commands for the above:**
```powershell
ffmpeg -i drone.m4a -ss 2 -t 116 drone_trimmed.wav -y
ffmpeg -i drone_trimmed.wav -t 2 drone_loop_head.wav -y
ffmpeg -i drone_trimmed.wav -i drone_loop_head.wav -filter_complex "[0:a][1:a]acrossfade=d=2[out]" -map "[out]" -codec:a libvorbis -b:a 192k drone_ambient.ogg -y
```

See `references/elevenlabs-music-ambient-drone.md` for full prompt library.

## UI Sound Design Patterns

Standard UI sound archetypes and their acoustic profiles:

| Archetype | Duration | Character | Spectral Profile |
|-----------|----------|-----------|-----------------|
| **Hover** | 0.06–0.10s | Single transient, ultrashort attack | High (8kHz), no tail |
| **Click** | 0.10–0.20s | Percussive tap, clean attack | Mid, warm body |
| **Open** (riser) | 0.20–0.30s | Pitch glide up, brightness | Mid → high |
| **Close** | 0.20–0.30s | Pitch glide down, resolution | Mid → low |
| **Whoosh** (transition) | 0.30–0.50s | Bandpass sweep, air + body | Sub → mid sweep |

### Consistency rules for a UI sound family

1. **Ambiente seco** — `dry studio recording, no reverb` (reverb from host app/environment)
2. **Textura fria** — `cold`, `clean`, `precision` across all samples
3. **Contexto** — `modern UI interface sound design` to set model expectations
4. **Espectro balanceado** — hover is brightest, whoosh is darkest, but all share a cold-technological tonal center

## SFX Prompt Engineering

### Formula

```
[Source/Object] + [Action] + [Environment/Context] + [Character/Mood modifier]
```

### Principles

1. **Specific materials** — "metal", "ceramic", "crystal", not generic
2. **Acoustic environment** — "small dry room" ≠ "large cathedral with reverb"
3. **Precise action** — "short tick fast attack" > "sound"
4. **Duration** — explicit when important: "0.08s", "fade out in 0.3s"
5. **Mood last** — "cinematic", "cold", "technological" as final modifiers
6. **No contradictions** — "soft but aggressive" confuses the model
7. **Onomatopoeia + description** — "metallic tick like crystal" works better than "tick" alone

### Prompt Influence settings

| Setting | When to use |
|---------|-------------|
| **High (70–100%)** | UI ticks, clicks, one-shots — needs exactness |
| **Medium (30–50%)** | Default. Most SFX — natural variation welcome |
| **Low (10–20%)** | Ambient textures, organic sounds — surprises welcome |

For UI SFX always use **High (80%)** and manual duration.

## Audio Post-Processing

### Standard web delivery pipeline (WAV → normalized MP3)

```bash
ffmpeg -i input.wav -af "loudnorm=I=-18:LRA=7:TP=-1" -b:a 320k output.mp3
```

**PowerShell equivalent:**
```powershell
Get-ChildItem -Filter "*.wav" | ForEach-Object {
    $out = $_.BaseName + ".mp3"
    ffmpeg -i $_.FullName -af "loudnorm=I=-18:LRA=7:TP=-1" -b:a 320k $out -y
}
```

### Parameters explained

| Flag | Effect |
|------|--------|
| `loudnorm=I=-18` | Normalizes to -18 LUFS (broadcast standard) |
| `LRA=7` | Loudness range 7 LU (consistent across samples) |
| `TP=-1` | True peak at -1 dBTP (no clipping) |
| `-b:a 320k` | MP3 320kbps CBR (max web quality) |

### Loudness verification

```bash
ffmpeg -i output.mp3 -af loudnorm=print_format=json -f null - 2>&1 | grep -E 'input_i|input_tp|input_lra'
```

### Seamless audio loop (crossfade technique)

For ambient drones, background textures, or any long-form audio that needs to loop without audible seam:

**Problem:** AI-generated music (ElevenLabs Music, etc.) often has built-in fades (~2s each end) that break the loop.

**Solution — 3-step ffmpeg crossfade:**

1. **Trim fades** from start and end:
   ```powershell
   ffmpeg -i input.m4a -ss 2 -t <total_duration_minus_4_seconds> trimmed.wav -y
   ```

2. **Extract loop head** (first 2s of trimmed body):
   ```powershell
   ffmpeg -i trimmed.wav -t 2 loop_head.wav -y
   ```

3. **Crossfade end of body into loop head:**
   ```powershell
   ffmpeg -i trimmed.wav -i loop_head.wav -filter_complex "[0:a][1:a]acrossfade=d=2[out]" -map "[out]" -codec:a libvorbis -b:a 192k output.ogg -y
   ```

**Parameters:** `d=2` (2s crossfade duration), `c1=tri c2=tri` (triangular curves, default). Adjust `d` to match the fade length of the source.

**Verification:** Check output duration ≈ original minus 4s (2s trimmed × 2). Size should be < 3MB for a 2min OGG at 192k.

See `references/audio-loop-crossfade.md` for detailed commands and edge cases.

## Export workflow

1. **Generate** 4 variations per sample
2. **Audition** each — check attack, body, tail
3. **Refine prompt** if needed:
   - Too long → add `under X seconds`, `tight transient, minimal tail`
   - No impact → add `high impact`, `deep body`, `punchy`
   - Too bright → add `warm`, `no piercing highs`
4. **Download** WAV as master archive
5. **Normalize + convert** to MP3 320kbps CBR
6. **Deliver** to `assets/audio/sfx/` in project

## Pitfalls

- **Vague prompts** produce generic sounds. Always include material, action, and environment.
- **Auto duration** for UI SFX produces unpredictable lengths. Always set manually.
- **Default 30% Prompt Influence** creates too much variation for UI one-shots. Use 80%.
- **Converting already-compressed** audio (MP3→normalized→MP3) degrades quality twice. Always normalize from WAV master in one pass.
- **ffmpeg + extension mismatch:** ffmpeg selects muxer by output extension. Writing Opus to `.wav` fails (exit 218). Use `.ogg` for Opus.
- **Over-tagging prompts:** more detail improves accuracy but contradictions confuse. Keep the description linear and non-conflicting.
