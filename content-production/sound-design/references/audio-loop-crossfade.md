# Audio Loop Crossfade — Ffmpeg Pipeline

> Técnica para transformar áudio AI (ElevenLabs Music, Suno, Udio, etc.) com fades embutidos em loop perfeito.
> Validado: ElevenLabs Music .m4a com ~2s fade in/out.

## Problema

AIs de música (ElevenLabs Music, etc.) geram áudio com fade in/out suaves nas bordas (~2s cada). Com `loop=true` no Web Audio API, o final do arquivo encontra o início — e os dois fades criam um gap audível ou um "bump" de volume.

## Solução: 3-passos ffmpeg (PowerShell)

### Passo 1 — Cortar fades

Remove os 2s iniciais (fade in) e ajusta a duração para também cortar os 2s finais (fade out).

```powershell
ffmpeg -i drone.m4a -ss 2 -t 116 drone_trimmed.wav -y
```

- `-ss 2`: pula 2s do início
- `-t 116`: pega 116s do ponto de corte (total 120s − 4s = 116s)
- Ajuste `-t` para: `duração_total_em_segundos - 4`

### Passo 2 — Extrair cabeça do loop (primeiros 2s do corpo)

```powershell
ffmpeg -i drone_trimmed.wav -t 2 drone_loop_head.wav -y
```

### Passo 3 — Crossfade final + conversão para OGG

```powershell
ffmpeg -i drone_trimmed.wav -i drone_loop_head.wav -filter_complex "[0:a][1:a]acrossfade=d=2[out]" -map "[out]" -codec:a libvorbis -b:a 192k drone_ambient.ogg -y
```

O que acontece:
- `drone_trimmed.wav` (116s) toca normalmente
- Nos últimos 2s (114s→116s), `acrossfade` cruza com `drone_loop_head.wav`
- Resultado: arquivo de ~116s onde final emenda perfeitamente no início
- Já sai como OGG Vorbis ~192k, pronto para web

## Parâmetros do acrossfade

| Parâmetro | Efeito |
|-----------|--------|
| `d=2` | Duração do crossfade em segundos |
| `c1=tri` | Curva de fade out (triangular) |
| `c2=tri` | Curva de fade in (triangular) |
| `o=0` | Overlap mode (0 = crossfade padrão) |

Para fades mais longos (ex: 3s), ajuste todos os valores: `-ss 3`, `-t duração-6`, `d=3`.

## Verificação

```powershell
ffprobe -i drone_ambient.ogg -show_entries format=duration,size -v quiet -of csv=p=0
```

Esperado: ~114s (120 − 4 − 2 do crossfade), tamanho < 3MB.

## Variações

### Para .wav em vez de .m4a como entrada:
```powershell
ffmpeg -i drone.wav -ss 2 -t 116 drone_trimmed.wav -y
```

### Para .mp3 como entrada:
```powershell
ffmpeg -i drone.mp3 -ss 2 -t 116 drone_trimmed.wav -y
```

### Para loop com fade detectado de 3s:
```powershell
ffmpeg -i drone.m4a -ss 3 -t 114 drone_trimmed.wav -y
ffmpeg -i drone_trimmed.wav -t 3 drone_loop_head.wav -y
ffmpeg -i drone_trimmed.wav -i drone_loop_head.wav -filter_complex "[0:a][1:a]acrossfade=d=3[out]" -map "[out]" -codec:a libvorbis -b:a 192k drone_ambient.ogg -y
```
