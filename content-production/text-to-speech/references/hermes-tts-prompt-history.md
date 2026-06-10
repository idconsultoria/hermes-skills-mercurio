# Hermes TTS Prompt History

O script `hermes-tts.py` usa `VOICE_INSTRUCT` como prefixo do texto a ser
falado. Este arquivo documenta a evolução do prompt desde a primeira versão.

## Versão atual (simplificada)

```python
VOICE_INSTRUCT = (
    "Voice: Charon. Brazilian Portuguese, male, mid-deep pitch, "
    "warm but precise tone, subtle irony. "
    "Speak naturally with a conversational pace — like a competent colleague."
)
```

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

### V3 — wav_temp corrigido + output_format: ogg (atual)
`wav_temp = args.output.rsplit(".", 1)[0] + ".wav"` produz `arquivo.wav`
limpo. Config.yaml com `output_format: ogg` garante que a tool gere
caminho `.ogg`.

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
