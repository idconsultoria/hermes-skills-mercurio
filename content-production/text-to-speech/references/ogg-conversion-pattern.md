# OGG Conversion Pattern

O script `hermes-tts.py` sempre gera OGG (Opus) como formato final.

## Fluxo atual

```
Gemini TTS -> PCM/WAV bruto -> arquivo.wav (temporario)
                                |
                        ffmpeg -i arquivo.wav -c:a libopus args.output (.ogg)
```

Nao ha `os.replace()` — o ffmpeg escreve direto no `args.output` que ja
termina em `.ogg` (definido por `output_format: ogg` no config.yaml).

## O bug do wav_temp (ja corrigido)

O script usava `wav_temp = args.output + ".wav"` para criar o arquivo
WAV temporario. Quando `args.output` termina em `.ogg` (ex: `tts.ogg`),
isso gerava `tts.ogg.wav` — funcional, mas feio.

A correcao foi trocar para `args.output.rsplit(".", 1)[0] + ".wav"`:
`tts.ogg` -> `tts.wav`. Clean.

## O gotcha do ffmpeg

ffmpeg escolhe o muxer pela **extensao do arquivo de saida**:

```
ffmpeg -i input.wav -c:a libopus output.wav    -> ERRO (exit 218)
  # "Codec opus not supported in WAVE format"

ffmpeg -i input.wav -c:a libopus output.ogg    -> OK
```

Solucao: garantir que `output_format` no config.yaml seja `ogg` para que
a ferramenta `text_to_speech` gere caminho `.ogg` e o ffmpeg use o muxer
OGG corretamente.

## O config certo vs o config distracao

`load_config()` le de `$HERMES_HOME/config.yaml` (aqui: `/opt/data/config.yaml`).
O arquivo em `/opt/data/.hermes/config.yaml` NAO e lido pela tool — e uma
config secundaria/legacy.

Sempre verificar o config REAL quando o output_format nao parece estar
sendo respeitado.
