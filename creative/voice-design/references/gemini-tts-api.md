# Gemini TTS — API Reference

## Models

| Model ID | Cota | Notes |
|----------|------|-------|
| `gemini-3.1-flash-tts-preview` | ~10 req/dia (tier free) | Principal. Voz mais expressiva, durações maiores. |
| `gemini-2.5-flash-preview-tts` | Cota SEPARADA da 3.1 | Alternativa quando a 3.1 exaurir. |

> Cota limits are per-model — exaurir 3.1 não bloqueia 2.5.
> Mesmo voice_name pode soar diferente entre modelos. Teste ambos.

## Output Format
- PCM 24000 Hz, 16-bit, mono (sample width 2)
- Save as WAV with python `wave` module
- REST returns Base64 PCM; Python SDK returns raw bytes

## 30 Prebuilt Voices

| Voice | Descriptor |
|-------|-----------|
| Zephyr | Bright |
| Puck | Upbeat |
| Charon | Informative |
| Kore | Firm |
| Fenrir | Excitable |
| Leda | Youthful |
| Orus | Firm |
| Aoede | Breezy |
| Callirrhoe | Easy-going |
| Autonoe | Bright |
| Enceladus | Breathy |
| Iapetus | Clear |
| Umbriel | Easy-going |
| Algieba | Smooth |
| Despina | Smooth |
| Erinome | Clear |
| Algenib | Gravelly |
| Rasalgethi | Informative |
| Laomedeia | Upbeat |
| Achernar | Soft |
| Alnilam | Firm |
| Schedar | Even |
| Gacrux | Mature |
| Pulcherrima | Forward |
| Achird | Friendly |
| Zubenelgenubi | Casual |
| Vindemiatrix | Gentle |
| Sadachbia | Lively |
| Sadaltager | Knowledgeable |
| Sulafat | Warm |

## Language Support
Auto-detects input. 70+ languages including Portuguese (pt).

## Audio Tags

### Safe emotion tags (strong prosody)
`[warmly]`, `[thoughtfully]`, `[sighs]`, `[gently]`, `[soft laugh]`, `[cheerfully]`

### Director tags (work well)
`[dryly]`, `[wryly]`, `[matter-of-fact]`, `[slight pause]`, `[whispers]`, `[slow deliberate]`, `[speeds up]`, `[pauses]`, `[clears throat]`, `[determination]`, `[enthusiasm]`, `[awe]`, `[sarcastic]`, `[sincere]`, `[nervous laughter]`, `[confidence]`, `[evenly]`

### Tags to avoid
Custom emotion tags like `[apologetically]`, `[helpfully]`, `[softly]` — produce measurably weaker prosody.

## Multi-Speaker (up to 2 speakers)
Use `MultiSpeakerVoiceConfig` with `SpeakerVoiceConfig` objects. Names in config must match names in prompt.

## LiveKit Canonical Prompt Structure

```
Synthesize speech for the performance defined below. The profile, scene,
performance notes, and context are direction only. Do NOT speak them.
Speak ONLY the lines under #### TRANSCRIPT.

# AUDIO PROFILE: <Name>
## "<Title/Tagline>"

## SCENE:
<2-3 sentence concrete scene>

### PERFORMANCE
Style: <adjectives>
Pace: <delivery>
Accent: <descriptor>

### CONTEXT
<1-2 sentences persona background>

#### TRANSCRIPT
[tags] Text to speak
```

## 9 Rules (from LiveKit research)
1. Always prepend the preamble in English (triggers classifier)
2. Use exactly `#### TRANSCRIPT` (4 hashes)
3. Use short section labels (`### PERFORMANCE`, not `### DIRECTOR'S NOTES`)
4. Classify emotional register before picking tags
5. Stick to documented audio tags for emotion; custom OK for non-emotion
6. Write a concrete scene, not a role label
7. Never instruct flatness — use positive direction ("warm and sincere", not "not monotone")
8. Commas between tagged clauses, not periods (prevents choppy output)
9. Don't quote literal transcript words in Style/Pace direction

## API Key Note
The `write_file` tool redacts `GOOGLE_API_KEY=*** pattern. Workaround:
use variable indirection or read from env/separate config.
