---
name: text-to-speech
category: content-production
description: >-
  Umbrella skill for all TTS operations — voice design, Gemini prompt engineering,
  multi-provider fallback chain, self-hosted Fish Speech, voice cloning, and
  Hermes TTS command provider. Covers the full lifecycle from voice persona
  design to audio delivery.
metadata:
  hermes:
    tags: [tts, voice, gemini, fish-speech, audio, prompting, speech]
    related_skills: [hermes-agent]
---

# Text-to-Speech (TTS)

Umbrella skill. Covers:
- [Voice design & prompting](#gemini-31-flash-tts) — Gemini TTS prompt structure, voice selection, audio tags
- [Hermes TTS system](#hermes-tts-command-provider-chain) — multi-provider fallback, config
- [Self-hosted inference](#fish-speech-s2-pro-gguf-self-hosted) — Fish Speech on ARM64
- [Voice design patterns](#voice-design-process) — iterative refinement, persona creation

## Gemini 3.1 Flash TTS

### Model
```
gemini-3.1-flash-tts-preview
```
Output: PCM 24000 Hz, 16-bit, mono (save as WAV).

### Canonical prompt structure

```
Synthesize speech for the performance defined below. The profile, scene,
performance notes, and context are direction only. Do NOT speak them.
Speak ONLY the lines under #### TRANSCRIPT.
```

This preamble in **English** triggers the TTS classifier. Below it:

| Section | Content | Language |
|---------|---------|----------|
| `# PERFIL DE VOZ: <name>` | Character name and tagline | Same as transcript |
| `## CENA:` | Concrete sensory scene (2-4 sentences) | Same as transcript |
| `### PERFORMANCE` | Style, Pace/Ritmo, Accent/Sotaque lines | Same as transcript |
| `### CONTEXTO` | 2-3 sentence who/what/why | Same as transcript |
| `#### TRANSCRIPT` | The actual speech. Minimal audio tags | Target language |

**Key rules:**
- Preamble stays in **English** (classifier trigger)
- All other sections in the **same language as the speech**
- **Concrete scene** > abstract labels
- Set overall tone via PERFORMANCE section, not tags

### Audio tags

Safe emotional tags: `[warmly]` `[thoughtfully]` `[sighs]` `[gently]` `[soft laugh]`

Director tags: `[dryly]` `[wryly]` `[matter-of-fact]` `[whispers]` `[measured]`

⚠️ Max 1-2 tags per transcript. Stacking causes unnatural tonal swings.

### Voice selection

| Voice | Style | Best for |
|-------|-------|----------|
| **Charon** | Informative | Imponente, denso, grave, solene |
| **Erinome** | Clear | Preciso, limpo, direto |
| **Iapetus** | Clear | Clean, neutral |
| **Schedar** | Even | Equilibrado, steady, lacônico |
| **Achird** | Friendly | Acessível, caloroso |
| **Sadaltager** | Knowledgeable | Autoridade intelectual |
| **Zubenelgenubi** | Casual | Tom descontraído, irônico |
| **Gacrux** | Mature | Solene com textura |
| **Puck** | Upbeat | Animado, energético |
| **Kore** | Firm | Firme, seguro |
| **Sulafat** | Warm | Aconchegante, humano |
| **Vindemiatrix** | Gentle | Suave, delicado |
| **Callirrhoe** | Easy-going | Relaxado |
| **Pulcherrima** | Forward | Assertivo |

Full 30-voice table in `references/gemini-tts-api.md`.

### API call (Python)
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=GOOGLE_API_KEY)
response = client.models.generate_content(
    model='gemini-3.1-flash-tts-preview',
    contents=PROMPT,
    config=types.GenerateContentConfig(
        response_modalities=['AUDIO'],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name='Charon',
                )
            )
        ),
    )
)
data = response.candidates[0].content.parts[0].inline_data.data
with wave.open('out.wav', 'wb') as wf:
    wf.setnchannels(1); wf.setsampwidth(2)
    wf.setframerate(24000); wf.writeframes(data)
```

## Hermes TTS Command Provider Chain

Single command provider for ALL TTS, configured in `config.yaml`:

```yaml
tts:
  provider: hermes-tts
  providers:
    hermes-tts:
      type: command
      command: "python3 /opt/data/.hermes/scripts/hermes-tts.py --input {input_path} --output {output_path}"
      output_format: wav
      timeout: 600
```

The script tries three-stage fallback:
1. **Gemini 3.1 Flash TTS** (Charon voice) → best quality
2. **Gemini 2.5 Flash Preview TTS** → fallback on quota exhaustion (429)
3. **Fish Speech S2 Pro q8_0** → local voice clone (last resort)

The voice instruct preamble is baked into the script: Charon voice, Brazilian Portuguese, male, mid-deep pitch, warm but precise tone, subtle irony.

## Fish Speech S2 Pro GGUF (self-hosted)

Deployed via Docker on Oracle ARM64. OpenAI-compatible endpoint.

**Quick commands:**
```bash
cd /home/ubuntu/selfhost/fish-speech/
docker compose up -d --build      # start
docker compose down               # stop
```

**Inference:**
```bash
curl -X POST http://localhost:8882/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"s2-pro-q8_0","input":"Texto para falar."}' -o out.wav
```

**Model quants** (tested on 4x ARM64 CPU, 24GB RAM):
| Quant | Size | RTF | Notes |
|-------|------|-----|-------|
| q8_0 | 5.3 GB | ~38x | Default. Best quality |
| q6_k | 4.3 GB | ~33x | Similar speed |
| q5_k_m | 3.8 GB | ~26x | Fastest |

**Voice cloning:** Place reference WAV files (3-15s, 16-bit mono) in `models/`.

## Voice Design Process

Iterative refinement loop for creating TTS voices with Gemini:

1. **Draft persona** — write # PERFIL, ## CENA, ### PERFORMANCE, ### CONTEXTO
2. **Generate sample** — single short phrase under #### TRANSCRIPT
3. **Evaluate** — is the prosody right? Tone matching?
4. **Refine** — tweak CENA (most impactful), PERFORMANCE (pace, delivery)
5. **Repeat** until the voice sounds right

### Tag discipline
- Use tags sparingly (0-2 per transcript)
- Set overall tone via PERFORMANCE section
- Tags work for emphasis; overuse breaks naturalness

## Diagnostics: TTS tool failure investigation

When `text_to_speech` returns an error, trace the resolution chain:

1. **Which config file?** `$HERMES_HOME/config.yaml` (HERMES_HOME=/opt/data)
2. **What provider?** Check `tts.provider` value in config
3. **Built-in or command?** Names like `edge/openai/gemini` are built-in. Anything else is a command provider
4. **Script exists?** Check command path from config, verify underlying service

**Common failures:**
| Error | Cause | Fix |
|-------|-------|-----|
| `exited with code 1` | API unreachable or script bug | Check service/docker status |
| `timed out` | Command too slow | Bump timeout in config |
| `produced no output` | Script ran but no output file | Run manually with placeholders |
| Wrong provider name | Second config at different path | Compare config files |

## Pitfalls

- **Over-tagging:** Max 1-2 tags per transcript. Set tone via PERFORMANCE
- **Classifier bypass:** Without English preamble, model may read direction aloud
- **Portuguese prompts:** Preamble in English, rest in Portuguese works fine
- **Transient output:** Gemini returns PCM, not WAV — must wrap in WAV header
- **Fish Speech cold start:** First inference loads model (~1-2 min)
- **API authorization:** Do NOT call Gemini API without explicit user instruction
