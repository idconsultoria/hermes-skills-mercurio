# OmniVoice Selfhost — ARM64 Reference

Concrete implementation of the "PyTorch CUDA bloat on ARM64" pattern (see SKILL.md).
Self-hosted OpenAI-compatible TTS service running on Oracle Ampere (ARM64) via Docker.

## Architecture

```
Hermes container ──HTTP──> OmniVoice API (port 8880)
                                │
                          omnivoice-omnivoice-api-1 (Docker)
                                │
                          Host: Oracle ARM64, 4 CPU, 24GB RAM
```

## Dockerfile Pattern (CPU-only ARM64)

```dockerfile
FROM --platform=linux/arm64 python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

# LAYER 1: PyTorch CPU (ARM64, from CPU-only index)
RUN pip install --no-cache-dir \
    torch==2.4.0 torchaudio==2.4.0 \
    --index-url https://download.pytorch.org/whl/cpu

# LAYER 2: App deps (no torch to avoid CUDA pull)
RUN pip install --no-cache-dir \
    transformers accelerate pydub gradio tensorboardX webdataset \
    numpy soundfile librosa fastapi "uvicorn[standard]" python-multipart

# LAYER 3: OmniVoice WITHOUT deps (torch from layer 1)
RUN pip install --no-cache-dir --no-deps omnivoice

COPY main.py /app/main.py
COPY web/index.html /app/web/index.html
ENV HF_HOME=/app/models DEVICE=cpu MODEL_ID=k2-fsa/OmniVoice
EXPOSE 8880
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8880", "--workers", "1"]
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /health` | GET | Model loaded + device info |
| `GET /v1/models` | GET | OpenAI-compatible model list |
| `GET /v1/voices` | GET | Voice presets (female, male, child, whisper...) |
| `GET /v1/languages` | GET | Available language IDs |
| `POST /v1/audio/speech` | POST | OpenAI-compatible TTS |
| `POST /v1/audio/clone` | POST (form) | Voice cloning from reference audio |
| `POST /v1/audio/design` | POST (form) | Voice design via text attributes |
| `GET /web` | GET | Web UI (TTS / Clone / Design tabs) |
| `GET /docs` | GET | Swagger UI |

## Voice Management

### Via Web UI (`/web`)
- **Clone tab**: Upload reference audio (WAV/MP3/FLAC/OGG/M4A, 3-10s clean), enter text, generate → optionally "Save as voice" for persistence
- **TTS tab**: Select voice preset + enter text → generate
- **Design tab**: Describe voice attributes (gender, age, pitch, accent) → generate

### Via API — save a cloned voice
```bash
curl -X POST http://localhost:8880/v1/audio/clone \
  -F "text=Esta é minha voz de referência." \
  -F "ref_audio=@minha-voz.wav" \
  -F "save_as=gustavo" \
  -F "language_id=pt"
```

Saved voices appear in `GET /v1/voices` and become selectable in the web UI.

### Voice presets (built-in)
`auto`, `female`, `male`, `female_en`, `male_en`, `female_br`, `male_br`, `child`, `elderly`, `whisper`

Free-form instruct strings also work as `voice` param: `"female, low pitch, british accent"`

## Model Configuration

Model choice is env-var driven, not web UI. Set in docker-compose.yml:
```yaml
environment:
  - MODEL_ID=k2-fsa/OmniVoice       # change to any compatible model
  - DEVICE=cpu
  - HF_HOME=/app/models
```

## Performance (CPU ARM64)

| Metric | Value |
|--------|-------|
| RTF (Real-Time Factor) | ~100x on 4-core ARM64 (1s audio → ~100s) |
| Num steps default | 32 (set 16 for 2x speed at slight quality loss) |
| Model RAM | ~4-6GB |
| Container size | ~3GB (without CUDA bloat) |

## Hermes TTS Integration

O Hermes pode usar o OmniVoice como provedor de TTS. Duas abordagens:

### Opção A — OpenAI provider + base_url (se VOICE_TOOLS_OPENAI_KEY estiver setada)

```yaml
tts:
  provider: "openai"
  openai:
    base_url: "http://172.19.0.1:8880/v1"
    model: "omnivoice"
    voice: "female"
    api_key: "not-needed"
```

> **⚠️ Requer `VOICE_TOOLS_OPENAI_KEY` no `/opt/data/.env`.** Mesmo com
> `base_url` customizada, o Hermes TTS provider OpenAI valida a env var
> antes de fazer a request. Descomentar e setar valor dummy:
> `VOICE_TOOLS_OPENAI_KEY=nao-usado`

### Opção B — Command provider (sem API key)

Criar script em `/opt/data/.hermes/scripts/omnivoice-tts.py` que chama a API
via curl, depois configurar:

```bash
hermes config set tts.provider omnivoice
hermes config set tts.providers.omnivoice.type command
hermes config set tts.providers.omnivoice.command \
  "python3 /opt/data/.hermes/scripts/omnivoice-tts.py \
   --text-file {input_path} --output {output_path}"
hermes config set tts.providers.omnivoice.output_format wav
hermes config set tts.providers.omnivoice.timeout 300
hermes config set tts.providers.omnivoice.max_text_length 2000
hermes config set tts.providers.omnivoice.voice_compatible true
```

A opção B funciona sem chave alguma — o script faz POST direto pro container.

### Testar
```python
from openai import OpenAI
client = OpenAI(base_url="http://172.19.0.1:8880/v1", api_key="not-needed")
with client.audio.speech.with_streaming_response.create(
    model="omnivoice", voice="female", input="Teste",
    extra_body={"language_id": "pt"}
) as r:
    r.stream_to_file("fala.wav")
```

## SSH Tunnel (for web UI access)

```bash
ssh -L 8880:localhost:8880 ubuntu@<server-ip>
# Then: http://localhost:8880/web
# Or:   http://localhost:8880/docs (Swagger)
```
