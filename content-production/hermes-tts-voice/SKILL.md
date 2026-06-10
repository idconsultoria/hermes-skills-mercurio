---
name: hermes-tts-voice
description: "Sistema de TTS multi-provedor do Hermes — fallback automático Gemini 3.1 Flash → Gemini 2.5 Flash Preview → Fish Speech S2 Pro (voice clone Charon). Inclui sintonia de voz (pitch, tom, persona), voice cloning, e configuração do command provider."
version: 1.2.0
author: Hermes Agent
tags: [tts, voice, gemini, fish-speech, s2-pro, charon, voice-clone, audio]
---

# Hermes TTS Voice System

## Arquitetura

```
text_to_speech tool
  → hermes-tts command provider
    → 1. Gemini 3.1 Flash TTS  (voz Charon, melhor qualidade)
    → 2. Gemini 2.5 Flash Preview TTS  (fallback cota)
    → 3. Fish Speech S2 Pro q8_0  (voice clone Charon, fallback local)
```

O script `hermes-tts.py` tenta cada provedor em ordem. Se um falha (cota, erro), passa para o próximo.

## Provedores

### Gemini TTS (Cloud — Google)

| Modelo | Qualidade | Cota |
|--------|-----------|------|
| `gemini-3.1-flash-tts-preview` | Excelente (vozes pré-definidas) | ~10 req/dia |
| `gemini-2.5-flash-preview-tts` | Muito boa | Cota separada da 3.1 |

Vozes built-in (30 vozes pré-definidas):
- **Profissionais/Informativas:** Charon, Kore, Atlas, Helios, Puck
- **Suaves/Calorosas:** Alnilam, Iris, Aura, Stella, Luna, Nova
- **Energéticas:** Fenrir, Echo, Rhea
- **Outras:** 15+ vozes adicionais disponíveis na API

A voz Charon é a padrão do sistema — tom informativo, mid-deep, precisa.
Alnilam é a alternativa mais suave e calorosa.

**Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`

**Payload:**
```json
{
  "contents": [{
    "parts": [{"text": "Voice: Charon. Brazilian Portuguese...\\n\\nTexto a falar"}]
  }],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "voiceConfig": {
        "prebuiltVoiceConfig": { "voiceName": "Charon" }
      }
    }
  }
}
```

⚠️ `responseModalities` é `"AUDIO"` (maiúsculo). O formato antigo (`"audio"` minúsculo, sem `speechConfig`) causa HTTP 400 no modelo `gemini-3.1-flash-tts-preview`.
⚠️ Gemini retorna **PCM puro** (s16le, 24kHz mono), não WAV. O script `hermes-tts.py` já empacota em WAV automaticamente. Para uso manual, converter com: `ffmpeg -f s16le -ar 24000 -ac 1 -i out.pcm out.wav`.
⚠️ Autenticação alternativa: usar header `x-goog-api-key: $GOOGLE_API_KEY` em vez de query param `?key=...`.

### Fish Speech S2 Pro (Local — Oracle ARM64)

**URL:** `http://fish-speech:8882/v1/audio/speech`

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `model` | `s2-pro` | Usa q8_0 por padrão |
| `prompt_audio` | `"default"` ou caminho absoluto | Áudio de referência para voice cloning |
| `prompt_text` | texto | Transcrição do áudio de referência |
| `input` | texto | Texto a sintetizar |

**Modelo:** s2-pro-q8_0.gguf (~4.6GB weights, 6.5GB RAM em uso)
**Performance:** ~5-30s de CPU por 1s de áudio (depende do tamanho do prompt)
**Armazenamento:** `/app/models/ref-charon.wav` (referência do clone)

## Configuração

### config.yaml

⚠️ **Localização correta:** O Hermes lê `$HERMES_HOME/config.yaml` (atualmente
`/opt/data/config.yaml`). O arquivo em `~/.hermes/config.yaml` **NÃO é lido**
quando `HERMES_HOME` está setado — é uma red-herring deixada por execuções
anteriores do `hermes setup`. O provider `hermes-tts` abaixo precisa estar no
**arquivo principal**, não no `.hermes/`.

```yaml
tts:
  provider: hermes-tts
  providers:
    hermes-tts:
      type: command
      command: "python3 /opt/data/.hermes/scripts/hermes-tts.py --input {input_path} --output {output_path}"
      output_format: wav
      max_text_length: 5000
```

### Variáveis de ambiente
- `GOOGLE_API_KEY` — chave da Google para Gemini TTS
- `FISH_SPEECH_URL` (opcional, default: `http://fish-speech:8882/v1/audio/speech`)

## Sintonia de Voz

O parâmetro de voz é controlado via `VOICE_INSTRUCT` no script. Formato:

```
Voice: {nome}. {idioma}, {gênero}, {pitch}, {tom}.
{descrição da persona}.
```

Exemplo (Charon — padrão):
```
Voice: Charon. Brazilian Portuguese, male, mid-deep pitch,
warm but precise tone, subtle irony.
Speak naturally with a conversational pace — like a competent colleague.
```

Exemplo (Alnilam — mais suave):
```
Voice: Alnilam. Brazilian Portuguese, female, medium pitch,
warm and friendly tone.
Speak with a gentle, engaging pace — like a helpful friend.
```

**Dica:** O preâmbulo (Voice: ...) é enviado como prefixo do texto. Gemini respeita instruções de voz; Fish Speech usa o áudio de referência + tom do preâmbulo.

## Voice Cloning (Fish Speech)

O clone da voz Charon está em `/app/models/ref-charon.wav` (recorte de 15s do Gemini 3.1).

**Para recriar a referência:**
1. Gerar áudio no Gemini 3.1 Flash com a voz desejada
2. Cortar ~15s com ffmpeg ou sox
3. Copiar para o host Oracle: `scp ref-charon.wav ubuntu@172.19.0.1:/home/ubuntu/selfhost/fish-speech/models/`
4. Rebuildar container: `cd ~/selfhost/fish-speech && docker compose build --no-cache s2-server && docker compose up -d s2-server`

## Uso Direto da API

### Gemini TTS (via curl)
```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Say cheerfully: Have a wonderful day!"}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Charon"}}}}}' \
  -o response.json
python3 -c "import json,base64; d=json.load(open('response.json')); open('out.pcm','wb').write(base64.b64decode(d['candidates'][0]['content']['parts'][0]['inlineData']['data']))"
# Gemini retorna PCM 24kHz mono; converter para WAV:
ffmpeg -f s16le -ar 24000 -ac 1 -i out.pcm out.wav
```

### Fish Speech (via curl)
```bash
curl -s -X POST http://localhost:8882/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"s2-pro","input":"Texto aqui","prompt_audio":"default","prompt_text":"Prompt de referencia."}' \
  -o out.wav
```

## Delivery para Plataformas

| Plataforma | Formato Aceito | Notas |
|------------|---------------|-------|
| WhatsApp | MP3, OGG Opus | WAV não funciona (erro "não foi possível carregar") |
| Telegram | OGG Opus (voz), MP3 (arquivo) | Prefere OGG para bolha de voz |
| Discord | MP3, WAV | WAV funciona |

Converter WAV para MP3 antes de enviar para WhatsApp:
```bash
ffmpeg -y -i input.wav -codec:a libmp3lame -b:a 64k output.mp3
```

O Hermes `text_to_speech` tool gerencia isso automaticamente quando o `output_format` no config.yaml é `wav` — a plataforma converte na entrega. Se falhar, converter manualmente para MP3.

## Diagnóstico de Falhas: Tool vs Config

Quando o `text_to_speech` tool falha (ex: provider errado, exit code 1), **não pule para
workaround de terminal** — o problema quase sempre é config. O fluxo de diagnóstico é:

1. **Conferir o provider ativo:** `grep -A2 '^tts:' $HERMES_HOME/config.yaml | grep provider`
   - O config principal é em `$HERMES_HOME/config.yaml` (definido pela env `HERMES_HOME`)
   - O arquivo `~/.hermes/config.yaml` **NÃO é lido** quando `HERMES_HOME` está setado
2. **Se o provider não é um built-in** (edge, openai, gemini, elevenlabs, xai, mistral, minimax, neutts, kittentts, piper),
   o Hermes procura em `tts.providers.<nome>` com `type: command`
3. **Testar o comando direto:** rodar o script manualmente com o mesmo comando do config
4. **Corrigir via API do Hermes** (nunca editar o YAML manualmente — o `patch` tool bloqueia escrita em config):
   ```bash
   /opt/hermes/.venv/bin/python3 -c "
   from hermes_cli.config import load_config, save_config
   cfg = load_config()
   cfg.setdefault('tts', {})['provider'] = 'hermes-tts'
   cfg['tts'].setdefault('providers', {})['hermes-tts'] = {
       'type': 'command',
       'command': 'python3 /opt/data/.hermes/scripts/hermes-tts.py --input {input_path} --output {output_path}',
       'output_format': 'wav',
       'max_text_length': 5000,
   }
   save_config(cfg)
   "
   ```

Sempre que o tool reportar um provider diferente do esperado, assuma que o config
está apontando para o provider errado — investigue antes de desviar para terminal.

## Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| Gemini devolve 429/403 | Cota exaurida | Fallback automático para 2.5 Flash → Fish Speech |
| Gemini devolve 400 com `gemini-3.1-flash-tts-preview` | Payload incompatível (formato antigo) | Usar `responseModalities: ["AUDIO"]` com `speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName` |
| Gemini devolve 404 | Nome do modelo errado | Usar `gemini-3.1-flash-tts-preview` (com `-preview`) |
| Gemini devolve "nenhum candidate" / empty response | Modelo respondeu sem gerar áudio (instabilidade do preview) | Fallback automático para próximo provedor. Tentar novamente mais tarde. |
| Fish Speech "generation produced no frames" | Faltando `--prompt-text` ao usar `--prompt-audio` | Servidor corrigido (fornece default) |
| Geração muito lenta (+30min) | CPU ARM64 sem GPU | Esperar — processo não está travado |
| Container não responde | s2.cpp ocupado | Só restartar se não responder por >1h |
| Script hermes-tts.py não acha GOOGLE_API_KEY | Linha comentada no .env | Script lê a última ocorrência não-comentada; verificar se há uma ativa |

## Performance Esperada (Fish Speech S2 Pro q8_0, Oracle ARM64 4CPUs)

| Texto | Áudio | Tempo Geração | RAM |
|-------|-------|---------------|-----|
| "Teste." (~1s) | ~0.5s | ~60s | 5.8 GB |
| Frase média (~5s) | ~3s | ~150s | 6.2 GB |
| Parágrafo (~15s) | ~10-15s | ~600-2000s | 6.5-9.3 GB |

RTF médio: ~40-80× (tempo real × fator). Cada segundo de áudio leva 40-80 segundos de CPU.

## Comandos Rápidos

```bash
# Testar Gemini TTS direto
python3 /opt/data/.hermes/scripts/hermes-tts.py --input <(echo "Olá mundo") --output /tmp/test.wav

# Verificar Fish Speech
curl -s http://localhost:8882/health | python3 -m json.tool

# Verificar status do container Oracle
ssh oracle-host 'docker ps --filter name=fish-speech --format "{{.Names}} {{.Status}}"'
