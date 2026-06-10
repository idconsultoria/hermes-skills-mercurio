# Gemini 3.1 Flash TTS — API Reference

## Model info

- **ID:** `gemini-3.1-flash-tts-preview`
- **Status:** Preview (April 2026)
- **Context:** 32k tokens
- **Output:** PCM 24000 Hz, 16-bit, mono
- **Pricing:** Free tier in AI Studio, paid via Vertex AI
- **SynthID:** Watermarked by default (cannot be disabled)

## Complete voice table (30 voices)

| Voice | Style | Voice | Style | Voice | Style |
|-------|-------|-------|-------|-------|-------|
| Zephyr | Bright | Puck | Upbeat | Charon | Informative |
| Kore | Firm | Fenrir | Excitable | Leda | Youthful |
| Orus | Firm | Aoede | Breezy | Callirrhoe | Easy-going |
| Autonoe | Bright | Enceladus | Breathy | Iapetus | Clear |
| Umbriel | Easy-going | Algieba | Smooth | Despina | Smooth |
| Erinome | Clear | Algenib | Gravelly | Rasalgethi | Informative |
| Laomedeia | Upbeat | Achernar | Soft | Alnilam | Firm |
| Schedar | Even | Gacrux | Mature | Pulcherrima | Forward |
| Achird | Friendly | Zubenelgenubi | Casual | Vindemiatrix | Gentle |
| Sadachbia | Lively | Sadaltager | Knowledgeable | Sulafat | Warm |

## Audio tags reference

### Safe emotional tags (strongest prosody)
`[warmly]` `[thoughtfully]` `[sighs]` `[gently]` `[soft laugh]` `[cheerfully]`

### Custom non-emotion director tags (work well)
`[dryly]` `[wryly]` `[matter-of-fact]` `[whispers]` `[slow deliberate]` `[measured]` `[pauses]` `[determination]` `[enthusiasm]` `[awe]` `[nervous laughter]` `[clears throat]` `[speeds up]` `[sarcastic]` `[sincere]` `[confidence]` `[slight pause]`

### Tag rules
1. **Stacking kills naturalness** — max 1 tag per sentence, zero is often better
2. **Commas between tagged clauses**, not periods (prevents choppy output)
3. **Custom emotion tags** (`[apologetically]`, `[softly]`) produce **weaker prosody** than safe tags
4. **Custom non-emotion tags** (director notes, physical actions) work well

## REST API shape

```json
{
  "contents": [{"parts":[{"text": "PUT PROMPT HERE"}]}],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "voiceConfig": {
        "prebuiltVoiceConfig": { "voiceName": "Charon" }
      }
    }
  },
  "model": "gemini-3.1-flash-tts-preview"
}
```

## Python SDK (google-genai)

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents=PROMPT,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Charon",
                )
            )
        ),
    )
)

data = response.candidates[0].content.parts[0].inline_data.data

# PCM → WAV
import wave
with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(data)
```

## Multi-speaker (2 speakers)

Omit `voice_config` and pass speaker-labeled dialogue as the prompt:

```
Speaker 1 (Alex): [excited] We just hit a million users.
Speaker 2 (Jordan): [skeptical] Is that monthly actives or just signups?
```

Then use `MultiSpeakerVoiceConfig` in the config instead of
`VoiceConfig`. Auto-assigns distinct voices per speaker.

## Sources

- https://ai.google.dev/gemini-api/docs/speech-generation
- https://livekit.com/blog/gemini-3.1-flash-tts-prompting-guide
- https://wowhow.cloud/blogs/gemini-3-1-flash-tts-developer-guide-2026
