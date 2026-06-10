---
name: voice-design
description: >-
  Design, iterate and refine TTS voices using Gemini 3.1 Flash TTS or
  equivalent controllable speech models. Covers the canonical prompt
  structure, iterative refinement loop, audio tag usage, and generation
  via the google-genai Python SDK.
category: creative
triggers:
  - "criar voz para [persona/aplicacao]"
  - "ajustar tom/entonação de voz TTS"
  - "gerar amostra de voz"
  - "voice design / voice cloning reference"
  - "iterar voz"
---

# Voice Design — Gemini 3.1 Flash TTS

## Canonical Prompt Structure

Every TTS prompt follows this 5-section schema. The **preamble in English** is load-bearing — it triggers the speech-synthesis classifier. Everything else can be in the target language.

```text
Synthesize speech for the performance defined below. The profile, scene,
performance notes, and context are direction only. Do NOT speak them.
Speak ONLY the lines under #### TRANSCRIPT.

# PERFIL DE VOZ: <Nome da persona>
## <subtitulo>

## CENA:
<2-3 frases concretas situando a cena. Nada abstrato.>
Ex: "Hora do café, final de expediente. Hermes está
folheando as notícias com um olho no código que compila."

### PERFORMANCE
Estilo: <adjetivos precisos. NADA de "dramático", "solene", "imponente"
a menos que seja intencional. Preferir: seco, direto, natural,
conversacional, irônico, preciso.>
Ritmo: <conversacional, fluido, econômico. NADA de pausas dramáticas.>
Sotaque: <Português brasileiro urbano, natural, sem afetação.>

### CONTEXTO
<1-2 frases sobre o personagem. Concreto, situacional.>

#### TRANSCRIPT
<tags opcionais] Texto a ser falado.
```

## Iterative Refinement Loop

1. **Prompt draft** → always show the user the full prompt string before generating
2. **Generate** → call `gemini-3.1-flash-tts-preview` via `google-genai` SDK
3. **Listen** → user listens and gives feedback
4. **Refine** → adjust one layer at a time:
   - First: timbre (voice_name)
   - Then: scene + context (persona)
   - Then: PERFORMANCE style/pace (entonação)
   - Last: transcript tags (parcimônia)

## Audio Tag Rules

### Safe emotion tags (prosody confiável)
`[warmly]`, `[thoughtfully]`, `[sighs]`, `[gently]`, `[soft laugh]`, `[cheerfully]`

### Director tags funcionam bem
`[dryly]`, `[wryly]`, `[matter-of-fact]`, `[slight pause]`, `[whispers]`, `[slow deliberate]`

### Evitar
- Custom emotion tags (`[apologetically]`, `[helpfully]`) — prosódia fraca
- Múltiplas tags por frase — quebra naturalidade
- Períodos entre tags — usar vírgulas para fluxo natural

### Regra de ouro
Menos tag = mais natural. Uma tag sutil no início e talvez uma no final bastam.

## Hermes Voice Persona (reference)

- Tom: Seco, preciso, ironia fina. Comunica como quem já provou o que sabe.
- Ritmo: Econômico. Palavras certas, nem mais nem menos.
- Persona: Trickster, hacker, Deus mensageiro. Nunca cita isso diretamente no prompt — a personalidade emerge da CENA e PERFORMANCE, não de rótulos.
- Contexto: "O colega que entrega" — profissional, direto, com personalidade própria.

## Models

| Model ID | Cota | Notes |
|----------|------|-------|
| `gemini-3.1-flash-tts-preview` | ~10 req/dia (tier free) | Principal. Voz mais expressiva, durações maiores. |
| `gemini-2.5-flash-preview-tts` | Cota separada da 3.1 | Alternativa quando a 3.1 exaurir. Mesma voz pode soar diferente (ex: Charon 3.1 = 42s, Charon 2.5 = 35s para o mesmo texto). |

> A cota do 3.1 Flash TTS preview é ~10 requisições/dia no tier free.
> O 2.5 Flash preview tem cota *separada* — não compartilha com a 3.1.
> A mesma `voice_name` pode produzir durações e entonação diferentes entre os modelos. Teste ambos.

## Prebuilt Voices (selected)

| Voice | Descriptor | Best for |
|-------|-----------|----------|
| Charon | Informative | Authority, dry delivery |
| Alnilam | Firm | Direct, assertive |
| Erinome | Clear | Crisp, precise |
| Schedar | Even | Balanced, neutral |
| Achird | Friendly | Warm, approachable |
| Gacrux | Mature | Gravitas without drama |
| Sadaltager | Knowledgeable | Explainer tone |
| Zubenelgenubi | Casual | Relaxed conversation |
| Iapetus | Clear | Clean annunciation |

> Veja `references/gemini-tts-api.md` para lista completa de 30 vozes.

## Generation (Python)

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=key)
response = client.models.generate_content(
    model='gemini-3.1-flash-tts-preview',  # or gemini-2.5-flash-preview-tts
    contents=FULL_PROMPT,
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
# PCM 24000Hz, 16-bit, mono → WAV
import wave
data = response.candidates[0].content.parts[0].inline_data.data
with wave.open('output.wav', 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(data)
duration = len(data) / (24000 * 2)  # seconds
print(f"{len(data)}B | {duration:.1f}s -> OK")
```

## Using Output as Reference Audio for Local TTS

Gemini TTS output serves as **voice reference** for local models (Fish Speech S2 Pro, Coqui, XTTSv2, etc.):

1. **Generate** reference sample via Gemini TTS (above)
2. **Trim** with ffmpeg to isolate the best segment:
   ```bash
   # Sample-accurate (re-encode):
   ffmpeg -i input.wav -af "atrim=start=10:duration=15" output.wav

   # Fast copy (approximate sample boundaries):
   ffmpeg -i input.wav -ss 10 -t 15 -c copy output.wav
   ```
3. **Feed** the trimmed WAV as reference to your local TTS model
4. **Test** multiple Gemini voices (Charon, Alnilam, Erinome, etc.) before committing a reference — each voice has different pacing and prosody even on the same prompt

### Reference Audio Tips
- Keep reference clips 10-30s for best clone quality
- Same speaker, consistent recording environment
- Reference audio from different Gemini models can't be mixed (Charon 3.1 != Charon 2.5)

## Pitfalls

1. **API key redaction**: The `write_file` tool redacts `GOOGLE_API_KEY=` in source code. Use a workaround: assign to a variable (`api_env = 'GOOGLE' + '_API_KEY'`) or read via shell env.
2. **Preamble must be in English** — the classifier that triggers the speech-synthesis path was trained on the English trigger phrase.
3. **Direction sections leak into speech** if not explicitly told "Do NOT speak them. Speak ONLY the lines under #### TRANSCRIPT."
4. **"Imponente" duplicado** redunda. Escolha um adjetivo forte, não dois.
5. **Scene abstrata** ("escritório, Hermes responde") → voz genérica. Scene concreta ("café, final de expediente, código compilando em segundo plano") → voz com personalidade.
6. **Tags demais** → variação tonal artificial. Máximo 2 tags por transcript de 3-4 frases.
7. **Cota do 3.1 Flash TTS preview**: ~10 req/dia no tier free. Quando exaurir, usar `gemini-2.5-flash-preview-tts` (cota SEPARADA). Verifique qual modelo está disponível antes de prometer entrega.
8. **Mesmo voice_name soa diferente entre modelos**: Charon no 3.1 produziu 42s de áudio vs 35s no 2.5 para o mesmo texto. Não assuma que o timbre é idêntico entre modelos.
9. **Google API key**: A variável no `.env` é `GOOGLE_API_KEY` (não `GEMINI_API_KEY`).

## User Preferences (this project)

- Direção em português (exceto preâmbulo)
- Tags com parcimônia
- Persona evocada por cena, não nomeada
- Sempre mostrar o prompt completo antes de gerar
- Timbre (voice_name) é a primeira alavanca, entonação (PERFORMANCE) é a segunda
- "Colega que entrega" > "divindade" > "executivo imponente"

## Related Skills

- `humanizer` — removing AI-isms from text (complementary, not overlapping)
- `style-guide-consultation` — Hermes visual identity (separate from voice)
