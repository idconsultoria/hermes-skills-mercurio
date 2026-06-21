# ElevenLabs Music — Ambient Drone Generation

> Session: Jun 2026, Sergipetec project. Dark ambient drone in D minor for cinematic 3D website.

## Tool: ElevenLabs Music API (v2)

- Max duration: **5 minutes** (vs SFX which maxes at 30s)
- Use when: ambient background, drone, cinematic pads, any audio >30s
- Output: WAV 44.1kHz or MP3 128–192kbps
- Commercial use: cleared (paid plans)
- Available in: ElevenCreative → Music tab, or via API `POST /v1/music`

## Critical Rule

ElevenLabs Music **defaults to adding vocals**. Always explicitly include:
`instrumental only, no vocals, no lyrics`

## Prompt Formula

```
[Emotion/Genre] + [Instruments/Texture] + [Technical specs] + [Restrictions]
```

ElevenLabs reads left-to-right with **decreasing weight**. Lead with emotion and genre.

## Optimized Prompt — Dark Ambient Drone

```
Instrumental only. Dark ambient cinematic drone in D minor, evolving slowly,
deep pedal bass D2, fifth A2, octave D3, shimmering overtones emerging and
dissolving, warm pad layers, contemplative and technological, no rhythm,
no percussion, no beat, evolving texture, 120 seconds.
No lyrics, no vocals, clean studio production.
```

### Variations:

**More ethereal:**
```
Instrumental only. Cinematic ambient soundscape, slow evolving drone,
cold pads, atmospheric shimmer, filtered harmonic overtones,
Blade Runner 2049 mood, deep and contemplative, 90 seconds.
No vocals, no lyrics, no percussion.
```

**Darker / more tense:**
```
Instrumental only. Dark drone, low rumbling bass, metallic resonances,
slowly shifting harmonic clusters, ominous atmospheric texture,
no traditional melody, no rhythm, 120 seconds.
No vocals.
```

## Conversational Refinement

After first generation, do NOT regenerate from scratch. Use natural language tweaks:
- `"make it darker, less bright"`
- `"add more low end, deeper bass"`
- `"slower evolution, more space between layers"`
- `"make the shimmer softer, more distant"`
- `"extend to 180 seconds"`

## Settings

| Parameter | Recommended |
|-----------|-------------|
| Duration | 90–120s (test 90s first) |
| Structure | None (ambient has no verse/chorus) |
| Vocals | OFF |
| Format | WAV (master) |
| Generations | 4 variations, choose best |

## Post-Processing for Loop

ElevenLabs Music output often has ~2s fade in/out. See `references/audio-loop-crossfade.md` for the ffmpeg pipeline to make it loopable.

## References

- ElevenLabs Music docs: https://elevenlabs.io/docs/overview/capabilities/music
- Prompting best practices: https://elevenlabs.io/docs/overview/capabilities/music/best-practices
- MixMasterAI ambient prompts: https://www.mixmasterai.co/ai-music-prompts/elevenlabs/ambient
