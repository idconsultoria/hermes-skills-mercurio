# Hermes TTS Prompt History

O script `hermes-tts.py` usa `VOICE_INSTRUCT` como prefixo do texto a ser
falado. Este arquivo documenta a evolução do prompt desde a primeira versão.

## Versão atual — LiveKit Canonical (VOICE_PROFILE)

O script foi atualizado para usar o formato LiveKit completo em vez da
string `VOICE_INSTRUCT` simplificada. Agora a variável se chama `VOICE_PROFILE`
e contém a estrutura completa com SCENE, PERFORMANCE, CONTEXT:

```
Synthesize speech for the performance defined below. The profile, scene,
performance notes, and context are direction only. Do NOT speak them.
Speak ONLY the lines under #### TRANSCRIPT.

# AUDIO PROFILE: Hermes
## "The Frontier Intelligence"

## SCENE: ...

### PERFORMANCE
Style: ...
Pace: ...
Accent: ...

### CONTEXT
...

#### TRANSCRIPT
[dryly] <texto do usuario>
```

O preâmbulo "Synthesize speech..." está em inglês para gatilhar o classifier
do Gemini. O resto está em português (idioma do áudio). A persona de
deus/trickster/hacker é implícita na cena e no contexto, nunca declarada
diretamente.

Usada em conjunto com `speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName: "Charon"` no payload da Gemini API.

## Histórico de versões

### V0 — raw WAV direct write (antes da cadeia de fallback)
Script original sem ffmpeg. Escrevia o WAV do Gemini direto no `args.output`.
Payload Gemini:
```json
{"responseModalities": ["audio"]}
```
Sem `speechConfig`, sem `voiceConfig`. A voz usada era a padrão do modelo.

### V1 — voiceName adicionado
Payload atualizado para incluir `speechConfig` com `voiceName: "Charon"`.

### V2 — ffmpeg conversion adicionado
Script passou a converter WAV → OGG via ffmpeg depois de receber o áudio
do Gemini. Bug conhecido: `wav_temp = args.output + ".wav"` causava
ffmpeg exit 218 quando output terminava em `.wav`.

### V3 — wav_temp corrigido + output_format: ogg
`wav_temp = args.output.rsplit(".", 1)[0] + ".wav"` produz `arquivo.wav`
limpo. Config.yaml com `output_format: ogg` garante que a tool gere
caminho `.ogg`.

### V4 — LiveKit canonical prompt (atual)
Substitui `VOICE_INSTRUCT` por `VOICE_PROFILE` com estrutura completa:
preâmbulo + cena + performance + contexto + transcript com tag `[dryly]`.

## Prompt experimental — iterações perdidas

Durante o desenvolvimento, as seguintes iterações de prompt foram testadas
mas os textos exatos foram perdidos na compactação de contexto:

| Iteração | Amostras geradas | Resultado |
|----------|-----------------|-----------|
| ref-compact | 1 áudio curto | Prompt compacto |
| ref-full | 1 áudio | Prompt completo com perfil |
| ref-schedar | 1 áudio | Variação de voz (Schedar) |
| natural | 1 áudio | Tom natural |
| colega | 1 áudio | Tom de colega competente |
| daily | 1 áudio | Tom de daily briefing |
| news-charon | 1 áudio longo | Tom jornalístico |

A estrutura CANÔNICA que emergiu dessas iterações está documentada na seção
"Canonical prompt structure" do SKILL.md principal.

## Referência

- Prompt sections em `../SKILL.md` → "Canonical prompt structure"
- API payload em `../references/gemini-tts-api.md`
- ffmpeg conversion em `../references/ogg-conversion-pattern.md`
