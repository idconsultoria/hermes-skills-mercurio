# Fish Speech S2 Pro GGUF — Self-hosted TTS

## Overview

Fish Speech S2 Pro (5B params) quantized to GGUF via the
[rodrigomt/s2-pro-gguf](https://huggingface.co/rodrigomt/s2-pro-gguf) repo.
Runs on CPU via the native C++ engine
[rodrigomatta/s2.cpp](https://github.com/rodrigomatta/s2.cpp).

Deployed on **Oracle ARM64** (4 CPUs, 24 GB RAM), no GPU.

## Directory structure

```
/home/ubuntu/selfhost/fish-speech/
├── docker-compose.yml
├── server/
│   ├── Dockerfile
│   └── server.py          # FastAPI app (multi-quant)
├── models/
│   ├── s2-pro-q8_0.gguf   # default (5.3 GB)
│   ├── tokenizer.json
│   ├── hermes-ref.wav     # reference audio for cloning
│   └── hermes-ref-*.wav   # alternative references
├── s2/
│   └── s2.bin             # compiled s2.cpp binary (ARM64)
```

## Quick commands

```bash
# Start
cd /home/ubuntu/selfhost/fish-speech && docker compose up -d --build

# Stop
docker compose down

# Rebuild after code changes
docker compose build --no-cache && docker compose up -d

# Check logs
docker logs fish-speech-s2-server-1
```

## API endpoints

### Health
```bash
curl http://localhost:8882/health
```
Returns model availability, binary status, tokenizer status.

### Generate speech (OpenAI-compatible)
```bash
curl -X POST http://localhost:8882/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"s2-pro-q8_0","input":"Texto para falar."}' \
  -o out.wav
```

Supported models: `s2-pro-q8_0` (default), `s2-pro-q6_k`, `s2-pro-q5_k_m`.

### List models
```bash
curl http://localhost:8882/v1/models
```

## Network

Connected to `ai_mesh` Docker bridge network for Hermes integration.
Accessible from Hermes container as `fish-speech-s2-server:8882`.

## Performance (4x ARM64 CPU)

| Quant | Size | Test phrase | Audio | Gen time | RTF |
|-------|------|-------------|-------|----------|-----|
| q8_0 | 5.3 GB | 12 palavras | 3.3s | 126s | 38x |
| q6_k | 4.3 GB | 12 palavras | 3.9s | 128s | 33x |
| q5_k_m | 3.8 GB | 12 palavras | 4.6s | 118s | 26x |

RTF varies with text length (longer text = better amortization of model
load overhead).

## Voice cloning

1. Generate a clean reference WAV via Gemini TTS (PCM 24kHz → save as WAV)
2. Copy to `models/` on the server
3. Pass the reference path to the s2.cpp `--reference` flag when supported

Reference files saved on server: `hermes-ref.wav`, `hermes-ref-schedar.wav`.

## Build notes (ARM64)

s2.cpp was compiled natively on the Oracle host:
```bash
git clone https://github.com/rodrigomatta/s2.cpp
cd s2.cpp
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
cp src/s2 ../../s2.bin
```

Built binary: 1.4 MB, statically linked, ARM64.
Required lib: `libgomp1` (included in Docker image via apt).

## Server code

The FastAPI server (`server.py`) supports multi-quant resolution via
`MODEL_REGISTRY` dict. Model selection via `model` field in request body.
Subprocess calls `s2.bin` with `timeout=600` (10 minutes).
