# OGG Conversion Pattern

O script `hermes-tts.py` sempre gera OGG (Opus) como formato final, independente do caminho de saída.

## Fluxo

```
Gemini TTS → PCM/WAV bruto → arquivo .tmp.wav
                                    ↓
                            ffmpeg -i .tmp.wav -c:a libopus .tmp.ogg
                                    ↓
                            os.replace(.tmp.ogg → args.output)
```

## Por que não WAV direto?

- WAV é grande (~384 kbps para 24kHz 16-bit mono)
- OGG Opus é ~64 kbps — ~6x menor com qualidade similar
- Telegram toca OGG inline como áudio; WAV chega como arquivo para download

## O gotcha do ffmpeg

ffmpeg escolhe o muxer pela **extensão do arquivo de saída**:

```
ffmpeg -i input.wav -c:a libopus output.wav    → ERRO (exit 218)
  # "Codec opus not supported in WAVE format"

ffmpeg -i input.wav -c:a libopus output.ogg    → OK
```

Solução: escrever para `.ogg` primeiro, depois mover com `os.replace()` para o path final.

## O path final termina em .wav mas é OGG

A ferramenta `text_to_speech` gera o path com base em `output_format` do config.yaml. Mesmo com `output_format: ogg`, o Hermes pode gerar `.wav` se cacheou o config antigo. O conteúdo real é sempre OGG — o player detecta pelo magic bytes (`OggS`), não pela extensão.
