---
name: text-to-speech
category: content-production
description: >-
  Text-to-speech generation using cloud APIs (Gemini 3.1 Flash TTS, Edge TTS)
  and self-hosted models (Fish Speech S2 Pro GGUF). Covers prompt engineering,
  voice selection, audio tagging, and deployment on ARM64 CPU.
metadata:
  hermes:
    tags: [tts, voice, gemini, fish-speech, audio, prompting, speech]
    related_skills: [hermes-agent, songsee]
---

# Text-to-Speech (TTS)

## When to use

- Generating voice audio for agent personas or characters
- Setting up TTS providers for Hermes (`tts.provider` in config.yaml)
- Deploying self-hosted TTS models on Oracle ARM64
- Prompt engineering for Gemini 3.1 Flash TTS
- Voice cloning with Fish Speech S2 Pro GGUF

---

## Gemini 3.1 Flash TTS

### Model

```
gemini-3.1-flash-tts-preview
```

Output: PCM 24000 Hz, 16-bit, mono (save as WAV).

### Prompt structure (battle-tested)

The canonical structure separates **direction** from **transcript**:

```
Synthesize speech for the performance defined below. The profile, scene,
performance notes, and context are direction only. Do NOT speak them.
Speak ONLY the lines under #### TRANSCRIPT.
```

This preamble in **English** triggers the TTS classifier. Everything below it
must follow this shape:

| Section | Content | Language |
|---------|---------|----------|
| `# PERFIL DE VOZ: <name>` | Character/agent name and tagline | Same as transcript |
| `## CENA:` | Concrete sensory scene (2-4 sentences). NOT an abstract role label. | Same as transcript |
| `### PERFORMANCE` | Style, Pace/Ritmo, Accent/Sotaque lines | Same as transcript |
| `### CONTEXTO` | 2-3 sentence who/what/why about the speaker | Same as transcript |
| `#### TRANSCRIPT` | The actual speech. With minimal audio tags. | Target language |

**Key rules:**

- The **preamble** stays in English (classifier trigger tested in English).
- All other sections (**CENA, PERFORMANCE, CONTEXTO, TRANSCRIPT**) use the
  **same language as the speech** (e.g. Portuguese for Portuguese speech).
- **CONCRETE SCENE** > abstract labels. "Final de tarde, silêncio. Voz
  honesta, sem pressa" vs. "Warm AI assistant".

### Audio tags

Safe emotional tags (tested, strong prosody):
`[warmly]` `[thoughtfully]` `[sighs]` `[gently]` `[soft laugh]` `[cheerfully]`

Custom non-emotion director tags (work well):
`[dryly]` `[wryly]` `[matter-of-fact]` `[whispers]` `[slow deliberate]` `[measured]`

⚠️ **Pitfall:** Stacking multiple audio tags in the same transcript causes
unnatural tonal swings. Prefer setting the overall tone via the PERFORMANCE
section and using zero or 1-2 tags max in TRANSCRIPT.

### Voice selection (30 prebuilt)

| Voice | Style | Best for |
|-------|-------|----------|
| **Charon** | Informative | Imponente, denso, grave, solene |
| **Erinome** | Clear | Preciso, limpo, direto |
| **Iapetus** | Clear | Clean, neutral |
| **Schedar** | Even | Equilibrado, steady, lacônico |
| **Achird** | Friendly | Acessível, caloroso |
| **Sadaltager** | Knowledgeable | Autoridade intelectual |
| **Zubenelgenubi** | Casual | Tom descontraído, irônico |
| **Gacrux** | Mature | Solene com textura, maduro |
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
    contents=PROMPT,  # the full structured prompt above
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

# PCM 24000Hz 16-bit mono
data = response.candidates[0].content.parts[0].inline_data.data
with wave.open('out.wav', 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(data)
```

---

## Fish Speech S2 Pro GGUF (self-hosted)

Deployed via Docker on Oracle ARM64. Full reference in
`references/fish-speech-s2.md`.

**Quick commands:**

```bash
# Deploy directory
cd /home/ubuntu/selfhost/fish-speech/

# Start
docker compose up -d --build

# Stop
docker compose down

# Endpoint (OpenAI-compatible)
curl -X POST http://localhost:8882/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"s2-pro-q8_0","input":"Texto para falar."}' \
  -o out.wav
```

### Model quants (tested on 4x ARM64 CPU, 24GB RAM)

| Quant | Size | RTF (approx) | Notes |
|-------|------|-------------|-------|
| q8_0 | 5.3 GB | ~38x | Default. Best quality |
| q6_k | 4.3 GB | ~33x | Similar speed to q8 |
| q5_k_m | 3.8 GB | ~26x | Fastest. Slightly lower quality |

### Voice cloning

Place reference WAV files (3-15s, clean speech, 16-bit mono) in
`models/` directory. Use Gemini TTS to generate clean reference samples.

---

## Hermes TTS Command Provider Chain

**This user uses a SINGLE command provider script for ALL TTS**, never the native
`tts.provider` setting. The chain implements three-stage fallback:

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

At runtime, the script at `/opt/data/.hermes/scripts/hermes-tts.py` tries:

```
1. Gemini 3.1 Flash TTS (Charon voice)  →  best quality
2. Gemini 2.5 Flash Preview TTS         →  fallback on quota exhaustion (429)
3. Fish Speech S2 Pro q8_0              →  local voice clone (last resort)
```

The voice instruct preamble is baked into the script as a Python constant:
```
Voice: Charon. Brazilian Portuguese, male, mid-deep pitch,
warm but precise tone, subtle irony. Speak naturally with a
conversational pace — like a competent colleague.
```

Gemini TTS is called via REST API (`generateContent` with `responseModalities: ["audio"]`),
not the `google-genai` SDK. Fish Speech is reached at `http://fish-speech:8882/v1/audio/speech`
via the `ai_mesh` Docker network.

## User preferences (this project)

These preferences were established through iteration and should guide
future TTS work:

- **Command provider ONLY** for all TTS (Gemini cloud + Fish Speech local).
  Native `tts.provider` setting is rejected — the user tried it and it didn't work.
- **Fallback chain** is the approved architecture: 3.1 → 2.5 → Fish Speech.
- **Direction language**: CENA, PERFORMANCE, CONTEXTO in the **same language**
  as the TRANSCRIPT (e.g. Portuguese for Portuguese speech). Preamble stays
  in English (classifier trigger).
- **Audio tag discipline**: Minimal or zero tags in TRANSCRIPT. Set tone
  via PERFORMANCE section instead. Tags cause unnatural swings when stacked.
- **API authorization**: Do NOT call the Gemini API without explicit user
  instruction. Wait for "faça" / "gere".
- **Performance direction**: "Direto, confiante, sem dramaticidade. A
  autoridade vem da naturalidade, não da imposição." Charon voice for
  imponente + denso tone.
- **Record scripts** in `/opt/data/selfhost/omnivoice/` for reference.
  Copy generated WAVs to the server at `models/` for cloning.
- **Debug tool failures first, don't jump to workarounds**: When the TTS
  tool fails, trace the failure path (config → provider resolution → command
  script) before falling back to terminal commands. Running manual scripts
  without diagnosing the tool's failure is a last resort, not a first step.
  The tool is trying to tell you something — listen to its error first.

---

## Diagnostics: TTS tool failure investigation

When `text_to_speech` returns an error that doesn't make sense, trace the
resolution chain before touching terminal workarounds.

### 1. Which config file is loaded?

```bash
echo $HERMES_HOME
cat $HERMES_HOME/config.yaml | grep -A 5 '^tts:'
```

The TTS tool reads `$HERMES_HOME/config.yaml` — NOT `~/.hermes/config.yaml`.
These are **different files** if `HERMES_HOME` points to a path that doesn't
contain a `.hermes` subdirectory. In this environment:
- `HERMES_HOME=/opt/data` → config is `/opt/data/config.yaml`
- `/opt/data/.hermes/config.yaml` is a second file that is **never loaded**
  by the tool (Hermes looks for `<HERMES_HOME>/config.yaml`)

### 2. What provider is configured?

```bash
grep 'provider:' $HERMES_HOME/config.yaml | head -3
```

The `tts.provider` value (e.g. `omnivoice`, `hermes-tts`, `edge`) determines
the full dispatch chain.

### 3. Built-in or custom command?

The Hermes TTS tool (`/opt/hermes/tools/tts_tool.py`) resolves providers:

```
tts.provider = "edge" / "openai" / "gemini" / "elevenlabs" / "minimax" / ...
  → built-in handler (native Python implementation)
tts.provider = ANYTHING ELSE
  → resolves as command provider (type: command under tts.providers.<name>)
  → if no config found → falls through to plugin registry
  → if no plugin → falls through to Edge TTS default
```

Built-in names are hardcoded in `BUILTIN_TTS_PROVIDERS`:
`edge`, `elevenlabs`, `openai`, `minimax`, `xai`, `mistral`, `gemini`,
`neutts`, `kittentts`, `piper`

### 4. If command provider: check the script

```bash
# Find the command in the config file that matches the provider name
grep -A 3 'provider_name:' $HERMES_HOME/config.yaml
# Or scan the tts.providers block
```

Check that:
- The script exists at the path referenced in the command template
- The underlying service (API endpoint, local model server) is running
- The command's shebang and dependencies are satisfied

### 5. Common failure modes

| Error in tool | Likely cause | Check |
|---------------|-------------|-------|
| `provider '<X>' exited with code 1: stderr: Error` | Command provider script failed — API endpoint unreachable or script bug | `ps aux | grep <service>`, check container/docker status |
| `provider '<X>' timed out` | Command took longer than `timeout` in config | Bump timeout or check service responsiveness |
| `provider '<X>' produced no output` | Script ran but output file was empty | Run the command manually with the same placeholders |
| Tool says provider name you didn't configure | Second config file at `$HERMES_HOME/config.yaml` has different values | Compare `$HERMES_HOME/config.yaml` vs `~/.hermes/config.yaml` |

---

## Pitfalls

- **Over-tagging**: Stacking `[dryly] [wryly] [matter-of-fact]` sounds
  robotic. One tag max per sentence, zero is better.
- **Classifier bypass**: Without the English preamble, the model may read
  your direction aloud instead of the transcript.
- **Portuguese prompts**: The preamble MUST stay in English. Everything
  else in Portuguese works fine — the model understands it.
- **Transient output**: The Gemini API returns PCM, not WAV. Must wrap in
  WAV header via `wave` module before saving.
- **Fish Speech cold start**: First inference after container restart
  loads the model (~1-2 min). Subsequent requests are faster.
