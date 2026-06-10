# Gemini 3.1 Flash TTS — Prompting & Usage Guide (Jun/2026)

## Model

- **ID:** `gemini-3.1-flash-tts-preview` (também: `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts`)
- **Status:** Preview (GA expected 2 quarters)
- **TTS Leaderboard (Elo):** 1,211
- **Output:** PCM 24000 Hz, 16-bit, mono (salvar como WAV)
- **Context Window:** 32k tokens
- **Preço:** Google AI Studio free tier, Vertex AI pago
- **SynthID:** Watermarking imperceptível embutido (não desativável)
- **Não disponível em:** EEA, UK, Switzerland durante preview
- **Python SDK:** `pip install google-genai`

## 30 Vozes Prebuilt (Jun/2026)

| Voz | Estilo | Voz | Estilo | Voz | Estilo |
|-----|--------|-----|--------|-----|--------|
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

**Escolha para clone/referência:**
- `Erinome` (Clear) — limpa, precisa, boa para cloning
- `Schedar` (Even) — equilibrada, neutra
- `Charon` (Informative) — autoritativa
- `Iapetus` (Clear) — alternativa limpa

## Sistema de Audio Tags (200+)

Tags de emoção (square brackets no texto) controlam entrega vocal:

**Tags seguras documentadas:** `[warmly]`, `[thoughtfully]`, `[sighs]`, `[gently]`, `[soft laugh]`, `[cheerfully]`

**Tags não-emocionais custom (funcionam bem):** `[whispers]`, `[slow deliberate]`, `[matter-of-fact]`, `[slight pause]`, `[confidence]`, `[dryly]`, `[wryly]`, `[evenly]`, `[calmly]`

**Categorias de tags existentes:** estados emocionais (adoration, disappointment, pride, awe), delivery físico (breathes deeply, pauses, clears throat), pacing (speeds up, slow deliberate), modos tonais (sarcastic, sincere, matter-of-fact).

**⚠️ Regras das tags:**
- Use vírgulas ENTRE cláusulas com tag, não pontos finais (`[warmly] OK, [thoughtfully] So...` ✅)
- `...` para pausas naturais, `—` para micro-pausas
- Custom emotion tags (`[apologetically]`, `[softly]`) produzem prosódia mais fraca — prefira as documentadas

## Prompt Structure (LiveKit Canonical)

O modelo é um LLM que interpreta TODO o prompt. Sem disciplina, ele lê as instruções em voz alta. Use este formato:

```
Synthesize speech for the performance defined below. The profile, scene,
performance notes, and context are direction only. Do NOT speak them.
Speak ONLY the lines under #### TRANSCRIPT.

# AUDIO PROFILE: <name>
## "<title>"

## SCENE: <2-3 sentence concrete scene — ESTADO DE ESPÍRITO, ambiente físico>

### PERFORMANCE
Style: <warm, confident, ironic, etc. NUNCA "flat" ou "monotone">
Pace: <measured, deliberate, etc.>
Accent: <descritor curto, ex: "Brazilian Portuguese, lightly cadenced">

### CONTEXT
<1-2 sentences on who/why this voice sounds this way>

#### TRANSCRIPT
[tag] Fala com emoção, [tag2] continuação com estilo diferente.
```

**Regras críticas do prompt:**
1. **Preâmbulo "Synthesize speech..." é OBRIGATÓRIO** — gatilha o classifier de speech synthesis
2. **`#### TRANSCRIPT`** com exatos 4 hashes — outros formatos falham
3. **Labels curtas** — `### PERFORMANCE`, `### CONTEXT` — NUNCA `### DIRECTOR'S NOTES` (apóstrofo faz o modelo ler em voz alta)
4. **CENA concreta, não abstrata** — "Late evening, monitor glow, coffee nearby" ✅ — "A warm customer service rep" ❌
5. **NUNCA instrua monotonia** — "warm and sincere" ✅, "quiet/flat/monotone" ❌
6. **Registre emoção ANTES de escolher tags** — tabela de registros:
   - **EMPATHY:** `[sighs]`, `[warmly]`, `[thoughtfully]`, `[gently]` (nunca `[soft laugh]`)
   - **WARM_FRIENDLY:** `[warmly]`, `[cheerfully]`, `[soft laugh]`
   - **TRANSACTIONAL:** `[warmly]`, `[thoughtfully]`
   - **HERMES (confidente/seco):** `[dryly]`, `[thoughtfully]`, `[evenly]`, `[confidence]`

## Python API Usage

```python
from google import genai
from google.genai import types
import wave

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents=PROMPT,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Erinome",
                )
            )
        ),
    )
)

data = response.candidates[0].content.parts[0].inline_data.data

# PCM 24000Hz, 16-bit, mono -> WAV
with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(data)
```

## Multi-Speaker (até 2 vozes)

```python
prompt = """Speaker 1 (Joe): [excited] We just hit a million users.
Speaker 2 (Jane): [skeptical] Is that monthly actives or just signups?"""

response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Joe",
                        voice_config=types.VoiceConfig(...)
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Jane",
                        voice_config=types.VoiceConfig(...)
                    ),
                ]
            )
        ),
    )
)
```

## Uso para Gerar Referência de Voz para Clonagem (Fish Speech S2)

O Gemini TTS é ideal para gerar samples de referência de alta qualidade para voice cloning:

1. **Prompt curto (5-10s)** — ideal para cloning: ref-compact
2. **Prompt médio (12-20s)** — mais contexto prosódico: ref-full  
3. **Vozes recomendadas:** Erinome (Clear) para clareza, Schedar (Even) para neutralidade

**Exemplo prático (Hermes reference):**
```python
PROMPT = """Synthesize speech for the performance defined below.
Speak ONLY the lines under #### TRANSCRIPT.

# AUDIO PROFILE: Hermes
## "The Frontier Intelligence"

## SCENE: Late evening, quiet room. Monitor glow. Honest, direct.

### PERFORMANCE
Style: Confident, direct, dry ironic edge. Earns authority through competence.
Pace: Measured, deliberate.
Accent: Brazilian Portuguese, lightly cadenced.

### CONTEXT
Frontier intelligence. Between intention and execution.

#### TRANSCRIPT
[wryly] Sou Hermes. Inteligência de fronteira — entre você e a máquina.
[evenly] Autêntico na artificialidade. Ponte entre mundos."""
```

**Resultados gerados (Jun/2026):**
- Compact (Erinome): 9.9s, 476KB
- Full (Erinome): 19.1s, 918KB
- Compact (Schedar): 9.8s, 468KB

## Hot Reload de Voz no Fish Speech S2

Após gerar a referência no Gemini e copiar para o servidor:

```bash
scp hermes-ref.wav oracle-host:/home/ubuntu/selfhost/fish-speech/models/
```

O modelo S2 carrega o arquivo de referência em runtime (não precisa rebuildar). Use o parâmetro `voice` no request para apontar pro arquivo WAV de referência.

## Referências Externas

- https://ai.google.dev/gemini-api/docs/speech-generation — Documentação oficial
- https://livekit.com/blog/gemini-3.1-flash-tts-prompting-guide — Guia prático LiveKit
- https://wowhow.cloud/blogs/gemini-3-1-flash-tts-developer-guide-2026 — Developer guide completo
- https://dev.to/googleai/how-to-prompt-gemini-31s-new-text-to-speech-model-24bb — Google AI blog
