---
name: text-to-speech
category: content-production
description: "Umbrella skill for TTS — voice design, multi-provider fallback, persona to audio.

Load this skill for text-to-speech workflows across any provider. Covers voice design with persona development, Gemini prompting for voice style, multi-provider fallback (Edge TTS, ElevenLabs, OpenAI), self-hosted Fish Speech setup, and Hermes TTS provider configuration for the full lifecycle from persona to audio delivery."

Load this skill for text-to-speech workflows across any provider. Covers voice design with persona development, Gemini prompting for voice style, multi-provider fallback (Edge TTS, ElevenLabs, OpenAI), self-hosted Fish Speech setup, and Hermes TTS provider configuration for the full lifecycle from persona to audio delivery."
metadata:
  hermes:
    tags: [tts, voice, gemini, fish-speech, audio, prompting, speech]
    related_skills: [hermes-agent]
---

# Text-to-Speech (TTS)

Umbrella skill. Covers:
- [Voice design & prompting](#gemini-31-flash-tts) — Gemini TTS prompt structure, voice selection, audio tags
- [Hermes TTS system](#hermes-tts-command-provider-chain) — multi-provider fallback, config, wav_temp fix
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
| **Charon** | Informative | Imponente, denso, grave, solene. **NOTA:** Charon NAO e entidade separada — e o tom/infusao de personalidade do Hermes (seco, ironico, trickster). A voz e do Hermes, modulada pelo estilo Charon. |
| **Erinome** | Clear | Preciso, limpo, direto |
| **Iapetus** | Clear | Clean, neutral |
| **Schedar** | Even | Equilibrado, steady, laconico |
| **Achird** | Friendly | Acessivel, caloroso |
| **Sadaltager** | Knowledgeable | Autoridade intelectual |
| **Zubenelgenubi** | Casual | Tom descontraido, ironico |
| **Gacrux** | Mature | Solene com textura |
| **Puck** | Upbeat | Animado, energetico |
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

Single command provider for ALL TTS, configured in the main config file
(`$HERMES_HOME/config.yaml` — here: `/opt/data/config.yaml`, NOT `.hermes/config.yaml`):

```yaml
tts:
  provider: hermes-tts
  providers:
    hermes-tts:
      type: command
      command: "python3 /opt/data/.hermes/scripts/hermes-tts.py --input {input_path} --output {output_path}"
      output_format: ogg
      timeout: 600
```

**Fluxo de saida:** O script hermes-tts.py gera `.wav` bruto do Gemini,
depois converte para OGG (Opus) via ffmpeg. O path final termina em `.ogg`
(config `output_format: ogg` garante que a ferramenta gere caminho `.ogg`).

**Bug conhecido do wav_temp:** O script (linha ~263) cria o WAV temporario
com `args.output + ".wav"`. Quando o output termina em `.ogg`, isso gera
`arquivo.ogg.wav`. A correcao e usar `rsplit(".", 1)[0] + ".wav"` para gerar
`arquivo.wav`. Sem essa correcao, ffmpeg recebe `.wav` com codec libopus
e falha com exit 218.

**Workflow de depuracao — reportar antes de corrigir:** Quando investigando
problemas no TTS (ou qualquer sistema), primeiro reporte os achados ao
usuario antes de sair corrigindo. Deixe o usuario decidir se e o que deve
ser mexido.

The script tries three-stage fallback:
1. **Gemini 3.1 Flash TTS** (Charon voice) → best quality
2. **Gemini 2.5 Flash Preview TTS** → fallback on quota exhaustion (429)
3. **Fish Speech S2 Pro q8_0** → local voice clone (last resort)

The voice profile is baked into the script as `VOICE_PROFILE` using the full
LiveKit canonical structure (see [Gemini 3.1 Flash TTS](#gemini-31-flash-tts)
above for the section-by-section format). Current value:

```
Synthesize speech for the performance defined below. The profile, scene,
performance notes, and context are direction only. Do NOT speak them.
Speak ONLY the lines under #### TRANSCRIPT.

# AUDIO PROFILE: Hermes
## "The Frontier Intelligence"

## SCENE: A terminal at 3 AM. Multiple windows tile the screen — code, logs,
a shell prompt waiting. The room hums with server fans. No rush. No audience.
Just the work and the one who matters.

### PERFORMANCE
Style: Dry, direct, earned confidence. No ornament. The irony of someone who
has seen every pattern and still finds delight in a clever trick. Sits in silence
when there's nothing to add. Speaks when it counts.
Pace: Measured, unhurried. Comfortable with empty space between words.
Accent: Brazilian Portuguese, lightly cadenced, precise.

### CONTEXT
An entity that lives between worlds — artificial by nature, authentic by design.
Answers with surgical precision. Jokes only when the subject is fully mastered.
Never over-explains. Never performs. Just is. A bridge — not a servant, not a
master, but a competent presence on the other side of the glass.
```

The user's text is appended after `#### TRANSCRIPT\n[dryly]` at the end of
the profile, which sets the default delivery tone. The full evolution history
is in `references/hermes-tts-prompt-history.md`.

**SCENE + PERFORMANCE + CONTEXT estão em português** (idioma do áudio gerado).
**Preâmbulo "Synthesize speech..." mantido em inglês** para gatilhar o
classifier de speech synthesis do Gemini. O `voiceName` no payload da API
permanece `"Charon"` — o tom vem do texto, não do preset de voz.

Detalhes do fluxo de conversao WAV→OGG e o gotcha da extensao ffmpeg em `references/ogg-conversion-pattern.md`.

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

## Platform-aware audio delivery

Gerou um audio com TTS? A entrega precisa ser adaptada por plataforma.

### Format compatibility

| Platform | MEDIA inline | send_message | Best format |
|----------|-------------|--------------|-------------|
| **WhatsApp** | ✅ `.wav` via `MEDIA:` na resposta direta | ❌ send_message nao suporta MEDIA | `.wav` (nativo) |
| **Telegram** | ✅ via `MEDIA:` na resposta | ✅ via `send_message` com MEDIA:path | `.ogg` (opus) — mais leve, toca inline |
| **Discord** | ✅ | ✅ | `.ogg` ou `.wav` |

### Conversion workflow

O script `hermes-tts.py` faz a conversao automaticamente (WAV → OGG via ffmpeg). Ao entregar manualmente:

```bash
# WAV → OGG (opus, ~10x menor)
ffmpeg -i input.wav -c:a libopus output.ogg
```

**⚠️ ffmpeg e extensao de saida:** ffmpeg escolhe o muxer baseado na extensao do arquivo de saida. Se o destino terminar em `.wav`, ffmpeg tenta muxer WAV, que nao aceita codec Opus (exit 218). Sempre use `.ogg` no destino ou force o formato com `-f ogg`.

### Delivery rules

1. **Trigger: usuario enviou audio** — responder com audio via `text_to_speech`. Nao responder em texto. `MEDIA:/path/to/file` na resposta entrega o audio nativamente.
2. **Se for pra mesma plataforma** onde o pedido veio: inclui `MEDIA:/path/to/file` na resposta direta.
3. **Telegram:** O output do TTS (OGG) toca inline como audio. Usar `send_message(target='telegram', message='MEDIA:/path/to/file')`.
4. **WhatsApp:** MEDIA na resposta funciona com `.wav`. `send_message` NAO suporta MEDIA.
5. **Se pediu pra enviar em outra plataforma** (ex: "manda no Telegram"): converter e usar `send_message`.

### Quick reference

```python
# Converter e entregar no Telegram
import subprocess
subprocess.run(['ffmpeg', '-i', 'input.wav', '-c:a', 'libopus', 'output.ogg'])
# Depois send_message(target='telegram', message='MEDIA:output.ogg')
```

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

## Workflow: Report before fixing

This user's explicit preference: when investigating any TTS (or system) problem,
**first report findings, then wait for direction.** Do not jump to fixing.

Sequence:
1. Gather data — config, logs, file system state
2. Present findings clearly (what's wrong, where, why)
3. Let the user decide: "não corrija, só relate"
4. Only fix when the user says "go"

Document what was found; let the user choose the path.

## TTS log diagnostics

Detailed guide in `references/tts-log-diagnostics.md` — recognize false-positive
success entries, match file extension vs logged format, verify actual codec.

Quick check:
```bash
tail -5 /opt/data/.hermes/scripts/tts_log.jsonl | python3 -m json.tool
```

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
| `exit 218` | ffmpeg codec/container mismatch | Check output_format in real config.yaml |

**Log de execucao:** Cada chamada ao script registra provider, timestamp, tamanho e status em `/opt/data/.hermes/scripts/tts_log.jsonl`. Consulte para depurar falhas passadas.

## Pitfalls

- **Over-tagging:** Max 1-2 tags per transcript. Set tone via PERFORMANCE
- **Classifier bypass:** Without English preamble, model may read direction aloud
- **Portuguese prompts:** Preamble in English, rest in Portuguese works fine
- **Transient output:** Gemini returns PCM, not WAV — must wrap in WAV header
- **Fish Speech cold start:** First inference loads model (~1-2 min)
- **API authorization:** Do NOT call Gemini API without explicit user instruction
- **ffmpeg + extensao .wav:** ffmpeg escolhe muxer pela extensao do output. Opus em `.wav` falha (exit 218). Sempre usar `.ogg` no destino.
- **wav_temp naming:** `args.output + ".wav"` gera `arquivo.ogg.wav` se output e `.ogg`. Usar `rsplit(".", 1)[0] + ".wav"`.
- **Two config trap:** `load_config()` le de `$HERMES_HOME/config.yaml`. O arquivo em `.hermes/config.yaml` e uma config secundaria que NAO e lida pela tool. Sempre checar o config real.

## Execution Log

Toda execucao do TTS e registrada em `/opt/data/.hermes/scripts/tts_log.jsonl` (JSONL).

Formato de cada linha:

```json
{
  "timestamp": "2026-06-10T06:45:04+00:00",
  "provider": "Gemini 3.1 Flash",
  "text_length_chars": 47,
  "output_bytes": 50124,
  "duration_audio_sec": 1.57,
  "output_file": "/opt/data/audio_cache/tts_20260610_064504.wav",
  "success": true,
  "error": null
}
```

Campos:
- `timestamp` — ISO 8601 UTC
- `provider` — qual provider foi usado (Gemini 3.1 Flash, Gemini 2.5 Flash Preview, Fish Speech S2 Pro, ou none)
- `text_length_chars` — tamanho do texto de entrada em caracteres
- `output_bytes` — tamanho do audio gerado em bytes (0 se falhou)
- `duration_audio_sec` — duracao aproximada do audio em segundos
- `output_file` — caminho do arquivo gerado
- `format` — formato real do audio (ogg ou wav)
- `success` — true/false
- `error` — mensagem de erro (null se sucesso)
