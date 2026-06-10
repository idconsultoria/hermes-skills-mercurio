# TTS Log Diagnostics — tts_log.jsonl

O script `hermes-tts.py` registra toda execução em
`/opt/data/.hermes/scripts/tts_log.jsonl` (JSONL).

## Formato

```json
{
  "timestamp": "2026-06-10T06:45:04+00:00",
  "provider": "Gemini 3.1 Flash",
  "text_length_chars": 47,
  "output_bytes": 50124,
  "duration_audio_sec": 1.57,
  "output_file": "/opt/data/audio_cache/tts_20260610_064504.wav",
  "format": "ogg",
  "success": true,
  "error": null
}
```

## O que olhar primeiro

### 1. Extensão vs formato

O campo `format` é hardcoded como `"ogg"` no script (linha 294). **Não confie
nele como evidência do formato real.** O campo `output_file` é a fonte da
verdade:

| output_file | format (log) | Realidade |
|-------------|--------------|-----------|
| `.ogg`      | `ogg`        | ✅ OGG/Opus legítimo |
| `.wav`      | `ogg`        | ❌ **Falso positivo** — o WAV foi escrito direto, ffmpeg falhou (exit 218) ou não foi chamado |

### 2. ffmpeg exit 218 = codec/container mismatch

Se o output for `.wav` mas o script tentou `-c:a libopus`, ffmpeg dá exit 218:
"Codec opus not supported in WAVE format".

**Causa:** O config.yaml tinha `output_format: wav` em vez de `ogg`. O script
recebe `args.output` terminando em `.wav`, tenta muxar Opus dentro de WAV.

**Diagnóstico rápido:**
```bash
grep output_format /opt/data/config.yaml
```

### 3. Cadeia de fallback

O script tenta em ordem:
1. `gemini-3.1-flash-tts-preview` (Gemini 3.1 Flash)
2. `gemini-2.5-flash-preview-tts` (Gemini 2.5 Flash Preview)
3. Fish Speech S2 Pro (via HTTP)

O campo `provider` no log mostra qual realmente serviu. Se o provider for
"Gemini 2.5 Flash Preview", o 3.1 provavelmente bateu QUOTA_EXHAUSTED.

### 4. Falso positivo (success:true com erro oculto)

Antes da correção do `wav_temp` e do `output_format: ogg`, o script podia
logar `success: true` mesmo quando o ffmpeg falhava, porque:
- O WAV gerado pelo Gemini era salvo em disco antes do ffmpeg
- Depois o log registrava o tamanho desse WAV como `output_bytes`
- O ffmpeg falhava silenciosamente ou o erro não chegava ao log

**Sintoma de falso positivo:**
- `format: ogg` + `output_file: ... .wav`
- Tamanho do arquivo compatível com WAV/PCM (não comprimido Opus)
- Nenhum erro no campo `error`

**Verificação:**
```bash
# Confirmar codec real do arquivo
ffprobe /caminho/do/arquivo.wav 2>&1 | grep -E "Audio:|Stream"
# WAV/PCM → sem codec Opus = falso positivo
```

## Comandos de diagnóstico

```bash
# Últimas 5 execuções
tail -5 /opt/data/.hermes/scripts/tts_log.jsonl | python3 -m json.tool

# Buscar entradas com formato suspeito (.wav + format:ogg)
grep '.wav"' /opt/data/.hermes/scripts/tts_log.jsonl

# Verificar configuração atual
grep output_format /opt/data/config.yaml
grep -E "^tts:" /opt/data/config.yaml

# Confirmar que ffmpeg consegue converter
ffmpeg -i /tmp/test.wav -c:a libopus /tmp/test.ogg 2>&1 | grep -E "Error|exit"
```
