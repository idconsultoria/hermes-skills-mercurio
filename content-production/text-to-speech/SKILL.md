---
name: text-to-speech
category: content-production
description: Umbrella skill for TTS: voice design, Gemini prompting, multi-provider fallback, self-hosted Fish Speech, and Hermes TTS provider. Full lifecycle from persona to audio.
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
| **Charon** | Informative | Imponente, denso, grave, solene. **NOTA:** Charon NÃO é entidade separada — é o tom/infusão de personalidade do Hermes (seco, irônico, trickster). A voz é do Hermes, modulada pelo estilo Charon. |
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
      output_format: ogg
      timeout: 600
```

**Nota sobre formato:** O script sempre gera OGG (Opus) internamente — mesmo que o path que a ferramenta passa termine em `.wav`, o conteúdo do arquivo é OGG. Isso porque ffmpeg rejeita codec Opus dentro de container WAV (`Codec opus not supported in WAVE format`). O fluxo é: gera WAV temp do Gemini → converte com ffmpeg para `.ogg` → move para o path final esperado pela ferramenta via `os.replace()`.

The script tries three-stage fallback:
1. **Gemini 3.1 Flash TTS** (Charon voice) → best quality
2. **Gemini 2.5 Flash Preview TTS** → fallback on quota exhaustion (429)
3. **Fish Speech S2 Pro q8_0** → local voice clone (last resort)

The voice instruct preamble is baked into the script: Charon voice, Brazilian Portuguese, male, mid-deep pitch, warm but precise tone, subtle irony.

Detalhes do fluxo de conversão WAV→OGG e o gotcha da extensão ffmpeg em `references/ogg-conversion-pattern.md`.

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

Gerou um áudio com TTS? A entrega precisa ser adaptada por plataforma.

### Format compatibility

| Platform | MEDIA inline | send_message | Best format |
|----------|-------------|--------------|-------------|
| **WhatsApp** | ✅ `.wav` via `MEDIA:` na resposta direta | ❌ send_message não suporta MEDIA | `.wav` (nativo) |
| **Telegram** | ✅ via `MEDIA:` na resposta | ✅ via `send_message` com MEDIA:path | `.ogg` (opus) — mais leve, toca inline |
| **Discord** | ✅ | ✅ | `.ogg` ou `.wav` |

### Conversion workflow

O script `hermes-tts.py` faz a conversão automaticamente (WAV → OGG via ffmpeg). Ao entregar manualmente:

```bash
# WAV → OGG (opus, ~10x menor)
ffmpeg -i input.wav -c:a libopus output.ogg
```

**⚠️ ffmpeg e extensão de saída:** ffmpeg escolhe o muxer baseado na extensão do arquivo de saída. Se o destino terminar em `.wav`, ffmpeg tenta muxer WAV, que não aceita codec Opus (exit 218). Sempre use `.ogg` no destino ou force o formato com `-f ogg`.

### Delivery rules

1. **Trigger: usuário enviou áudio** — responder com áudio via `text_to_speech`. Não responder em texto. `MEDIA:/path/to/file` na resposta entrega o áudio nativamente.
2. **Se for pra mesma plataforma** onde o pedido veio: inclui `MEDIA:/path/to/file` na resposta direta.
3. **Telegram:** O output do TTS (OGG interno) toca inline como áudio, mesmo com nome `.wav`. Usar `send_message(target='telegram', message='MEDIA:/path/to/file')`.
4. **WhatsApp:** MEDIA na resposta funciona com `.wav`. `send_message` NÃO suporta MEDIA.
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

**Log de execução:** Cada chamada ao script registra provider, timestamp, tamanho e status em `/opt/data/.hermes/scripts/tts_log.jsonl`. Consulte para depurar falhas passadas.

## Pitfalls

- **Over-tagging:** Max 1-2 tags per transcript. Set tone via PERFORMANCE
- **Classifier bypass:** Without English preamble, model may read direction aloud
- **Portuguese prompts:** Preamble in English, rest in Portuguese works fine
- **Transient output:** Gemini returns PCM, not WAV — must wrap in WAV header
- **Fish Speech cold start:** First inference loads model (~1-2 min)
- **API authorization:** Do NOT call Gemini API without explicit user instruction
- **ffmpeg + extensão .wav:** ffmpeg escolhe muxer pela extensão do output. Opus em `.wav` falha (`Codec opus not supported in WAVE format`, exit 218). Sempre usar extensão `.ogg` no destino do ffmpeg, ou mover o .ogg gerado para o path final com `os.replace()`.
- **Script output format:** O script `hermes-tts.py` sempre gera OGG (Opus), mesmo que o path da ferramenta termine em `.wav`. O conteúdo é OGG válido e toca inline no Telegram.

## Execution Log

Toda execução do TTS é registrada em `/opt/data/.hermes/scripts/tts_log.jsonl` (JSONL).

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
- `output_bytes` — tamanho do áudio gerado em bytes (0 se falhou)
- `duration_audio_sec` — duração aproximada do áudio em segundos
- `output_file` — caminho do arquivo gerado
- `format` — formato real do áudio (ogg ou wav)
- `success` — true/false
- `error` — mensagem de erro (null se sucesso)
