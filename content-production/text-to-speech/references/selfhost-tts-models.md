---
name: ai-voice-selfhost
description: "Self-host TTS models (OmniVoice, Qwen3-TTS, Fish Speech) on Oracle ARM64 with Docker.

Load this skill to self-host TTS models locally. Covers OmniVoice, Qwen3-TTS, and Fish Speech S2 Pro GGUF on Oracle ARM64 with Docker, Python and C++ inference patterns, OpenAI-compatible endpoint creation, and Hermes TTS provider integration."

Load this skill to self-host TTS models locally. Covers OmniVoice, Qwen3-TTS, and Fish Speech S2 Pro GGUF on Oracle ARM64 with Docker, Python and C++ inference patterns, OpenAI-compatible endpoint creation, and Hermes TTS provider integration."
version: 1.2.0
author: Hermes agent (learned from session)
category: infrastructure
---

# AI Voice Selfhost — TTS no Oracle ARM64

## Trigger

User asks to deploy a TTS model (OmniVoice, Qwen3-TTS, etc.) on the Oracle ARM64 server, expose an API, or configure Hermes to use a local TTS endpoint.

## Architecture Pattern

```
selfhost/<model-name>/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── main.py          # FastAPI OpenAI-compatible wrapper
└── web/             # Optional web UI

Hermes config:
  tts.providers.<name>:
    type: command
    command: "python3 /opt/data/.hermes/scripts/<bridge>.py ..."
```

## Pattern B — C++ Native Inference (via subprocess)

For heavyweight models (3B+ params) where Python inference is too slow/expensive, use a native C++ engine wrapped by a thin FastAPI server:

```
selfhost/<model-name>/
├── server/
│   ├── Dockerfile          # Python slim (only FastAPI + uvicorn)
│   └── server.py           # FastAPI wrapper → subprocess.run(C++_binary, ...)
├── engine/
│   └── <binary>            # C++ compiled binary (mounted in container)
├── models/
│   └── <model>.gguf        # GGUF quantized model (read-only mount)
├── docker-compose.yml
└── .env
```

**Key differences from Pattern A** (Python inference):
- Docker image is MINIMAL — Python only for the HTTP layer, no torch/transformers
- Inference happens in a native binary via `subprocess.run()` with a generous `timeout=600`
- Model is pre-quantized (GGUF) and mounted as a read-only volume — no HF download at startup
- Binary needs to be compiled natively for ARM64 (cross-compile or build on target)
- Supports MULTI-QUANT architecture: multiple GGUF quantizations in one container, selected per request via `model` field

**Multi-quant registry pattern (server.py):**
```python
MODEL_REGISTRY = {
    "s2-pro-q8_0": {
        "path": os.environ.get("MODEL_Q8_0", f"{MODELS_DIR}/s2-pro-q8_0.gguf"),
        "quant": "q8_0", "size_gb": 5.3,
    },
    "s2-pro-q6_k": {
        "path": os.environ.get("MODEL_Q6_K", f"{MODELS_DIR}/s2-pro-q6_k.gguf"),
        "quant": "q6_k", "size_gb": 4.5,
    },
    "s2-pro-q5_k_m": {
        "path": os.environ.get("MODEL_Q5_K_M", f"{MODELS_DIR}/s2-pro-q5_k_m.gguf"),
        "quant": "q5_k_m", "size_gb": 3.8,
    },
}
```

Use `_resolve_model(model_id)` to look up the path and metadata, falling back to DEFAULT_MODEL. Each model path can be overridden via env var for flexible deployment. Mount ALL model GGUF files as read-only volumes in docker-compose.

**docker-compose.yml — multi-quant example:**
```yaml
services:
  s2-server:
    volumes:
      - ./models:/app/models:ro   # all .gguf files here
    environment:
      - MODELS_DIR=/app/models
      - MODEL_Q8_0=/app/models/s2-pro-q8_0.gguf
      - MODEL_Q6_K=/app/models/s2-pro-q6_k.gguf
      - MODEL_Q5_K_M=/app/models/s2-pro-q5_k_m.gguf
```

**Adding a new quant:**
1. Download GGUF to `./models/` (wget from HuggingFace)
2. Add entry to MODEL_REGISTRY with env var + path
3. Add MODEL_* env var to docker-compose.yml
4. `docker compose up -d` — no rebuild needed (file is mounted, not baked in)

**Example (s2.cpp → Fish Speech S2 Pro):**
```python
# Inside FastAPI endpoint:
result = subprocess.run(
    [S2_BIN, "-m", MODEL_PATH, "-t", TOKENIZER_PATH, "--text", text, "-o", output_path],
    capture_output=True, timeout=600,
)
```

**When to use Pattern B:** model ≥3B params, has a GGUF/C++ port available, inference in Python would be too slow or memory-heavy.

**When to use Pattern A** (original): model <3B params, Python inference is acceptable, no GGUF port exists, needs HuggingFace model downloading.

## Step-by-Step

```bash
mkdir -p selfhost/<model-name>
# On the Oracle host:
ssh oracle-host 'mkdir -p /home/ubuntu/selfhost/<model-name>'
```

### 2. Dockerfile — ARM64 PyTorch CPU Pitfall

**CRITICAL:** Model packages (`omnivoice`, `qwen-tts`) pull `torch` with CUDA dependencies (+10GB) when installed normally. Two patterns:

**A) Model that depends on torch** (like `omnivoice`):
```dockerfile
# Install torch FIRST from CPU index
RUN pip install --no-cache-dir \
    torch==2.3.0 torchaudio==2.3.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Then install model WITH --no-deps to avoid pulling CUDA torch
RUN pip install --no-cache-dir --no-deps omnivoice

# Then install remaining deps manually
RUN pip install --no-cache-dir \
    transformers accelerate soundfile fastapi "uvicorn[standard]" ...
```

**B) Model that does NOT pull torch** (like `qwen-tts`):
```dockerfile
# Install torch CPU first
RUN pip install --no-cache-dir \
    torch==2.5.1 torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Then install model normally with all deps
RUN pip install --no-cache-dir \
    qwen-tts fastapi "uvicorn[standard]" python-multipart
```

**Always check model's pyproject.toml/setup.py** to see if torch is a direct dependency before deciding pattern A or B.

### 3. FastAPI Wrapper (main.py)

Expose at least these endpoints:
- `GET /health` — model loaded, device info
- `GET /v1/models` — OpenAI-compatible model list
- `POST /v1/audio/speech` — OpenAI-compatible TTS

```python
@app.post("/v1/audio/speech")
async def synthesize(req: SpeechRequest):
    # 1. Map voice to model's instruct/inference format
    # 2. Generate audio
    # 3. Return WAV/MP3 with Content-Type + X-RTF header
```

Load model in `@app.on_event("startup")` or lifespan.

### 4. docker-compose.yml

**CRITICAL: Add the `ai_mesh` external network.** The Hermes container and all Hermes-accessible services share the `ai_mesh` network (created by Hermes' own docker-compose). Adding it here gives DNS-based service discovery — the bridge script can use the service name (e.g. `qwen3-api`) instead of the Docker gateway IP (`172.19.0.1`), avoiding connectivity flakiness.

```yaml
name: <model-name>
services:
  api:
    build: .
    ports:
      - "<port>:<port>"
    volumes:
      - <volume_name>:/app/models
    environment:
      - DEVICE=cpu
      - MODEL_ID=<hf-model-id>
      - HF_HOME=/app/models
    restart: unless-stopped
    networks:
      - ai_mesh          # ← ESSENCIAL: permite Hermes resolver por DNS

networks:
  ai_mesh:
    external: true       # ← rede já existe, não criar

volumes:
  <volume_name>:
```

**Verify Hermes can reach the service** (from inside the Hermes container):
```bash
curl -s --connect-timeout 3 http://<service-name>:<port>/health
```
Use the container's service name (from docker-compose) as the hostname — Docker DNS resolves it automatically on `ai_mesh`.

Use a DIFFERENT port per model (8880=OmniVoice, 8881=Qwen3-TTS, etc.).

### 5. Deploy

```bash
# Copy files to host
scp Dockerfile main.py docker-compose.yml oracle-host:/home/ubuntu/selfhost/<model-name>/

# Build and start
ssh oracle-host "cd /home/ubuntu/selfhost/<model-name> && docker compose build && docker compose up -d"

# Monitor first startup (model download on first run)
ssh oracle-host "docker logs -f <container-name>"
```

### 6. Hermes Command Provider Integration

⚠️ **User preference: command provider ONLY, never native TTS provider.** This user
tried the native `tts.provider google` setup and it did not work. ALL TTS must be
configured as command provider — including cloud APIs like Gemini. The bridge script
pattern below is the ONLY approved approach. Do NOT use:
```
hermes config set tts.provider google          # ❌ rejected — native provider
```
Instead, always:
```
hermes config set tts.providers.<name>.type command   # ✅ approved
hermes config set tts.providers.<name>.command "python3 ..."
```

**CRITICAL: `tts.provider` must match the key name used in `tts.providers`.** If your
provider is called `hermes-tts`, you MUST set both:
```yaml
tts:
  provider: hermes-tts          # ← must match the key below
  providers:
    hermes-tts:                  # ← same name
      type: command
      command: "python3 /opt/data/.hermes/scripts/hermes-tts.py --input {input_path} --output {output_path}"
      output_format: ogg
      timeout: 600
```
If the names don't match, Hermes falls back silently to Edge TTS (default).

### Fallback Chain Pattern (Multi-Provider)

For maximum reliability, use a SINGLE command provider script that implements
fallback internally — not multiple providers in Hermes config:

```yaml
tts:
  provider: hermes-tts
  providers:
    hermes-tts:
      type: command
      command: "python3 /opt/data/.hermes/scripts/hermes-tts.py --input {input_path} --output {output_path}"
      output_format: ogg
      timeout: 600
```

The script at `/opt/data/.hermes/scripts/hermes-tts.py` implements the chain:

```
1. Gemini 3.1 Flash TTS (voz Charon) — cloud API, melhor qualidade
2. Gemini 2.5 Flash Preview TTS — fallback se cota 3.1 esgotar (HTTP 429)
3. Fish Speech S2 Pro q8_0 (voice clone) — último recurso local
```

**Script structure:**
```python
# Read text from --input file
with open(args.input) as f:
    text = f.read().strip()

# Try cloud first
for model_id, label in [("gemini-3.1-flash-tts-preview", "Gemini 3.1"),
                         ("gemini-2.5-flash-preview-tts", "Gemini 2.5")]:
    try:
        audio = call_gemini_tts(model_id, text, label)
        break
    except QuotaError:
        continue  # try next

# Fallback to local
if audio is None:
    audio = call_fish_speech(text)

# Write output
with open(args.output, "wb") as f:
    f.write(audio)
```

The Gemini API uses `generateContent` with `responseModalities: ["audio"]` and
returns inline base64 audio. The Fish Speech endpoint is
`http://fish-speech:8882/v1/audio/speech` (via `ai_mesh` DNS).

**Client timeout MUST exceed server timeout.** The server's `subprocess.run(timeout=N)`
is the backend limit. The HTTP client (curl, bridge script) must use a timeout value
GREATER than the expected generation time. A short client timeout kills the connection
but does NOT stop the server subprocess, wasting resources:
```python
# Server (FastAPI) — generous limit for CPU-bound models
result = subprocess.run(s2_args, capture_output=True, timeout=3600)

# Client (bridge script) — MUST exceed server timeout
req = urllib.request.Request(FISH_URL, ...)
with urllib.request.urlopen(req, timeout=1800) as resp:  # 30 min
    wav_data = resp.read()
```

**Key env vars for the bridge script:**
- `GOOGLE_API_KEY` — for Gemini TTS (from `/opt/data/.env` or environment)
- `FISH_SPEECH_URL` — defaults to `http://fish-speech:8882/v1/audio/speech`
- The voice profile is now `VOICE_PROFILE` (LiveKit canonical format instead of the old `VOICE_INSTRUCT` string). It includes SCENE, PERFORMANCE, CONTEXT sections in Portuguese plus a `#### TRANSCRIPT\n[dryly]` section. See `text-to-speech` umbrella skill for the full structure.

**⚠️ `.env` loading for command provider scripts:** Scripts rodam no Hermes container e o `.env` (`/opt/data/.env`) pode não estar exportado como variável de ambiente real. O script precisa tentar carregá-lo manualmente:

```python
import os
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    env_path = "/opt/data/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    GOOGLE_API_KEY = line.strip().split("=", 1)[1].strip("\"'")
                    break
```

Isso é necessário porque `hermes config set` salva secrets no `.env` mas eles não são automaticamente exportados para o ambiente de scripts command provider.

Create a bridge script at `/opt/data/.hermes/scripts/<model>-tts.py`:

```python
#!/usr/bin/env python3
import sys, json, subprocess, argparse, os

parser = argparse.ArgumentParser()
parser.add_argument('--text-file', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--voice', default='female')
args = parser.parse_args()

with open(args.text_file) as f:
    text = f.read().strip()

payload = json.dumps({
    "input": text,
    "voice": args.voice,
    "language_id": "pt"
})

result = subprocess.run([
    "curl", "-s", "-o", args.output,
    "-X", "POST", "http://<service-name>:<port>/v1/audio/speech",
    # Use service DNS name (ai_mesh network) — NUNCA use gateway IP (172.19.0.1).
    # Gateway IP é flaky: o container pode não estar acessível após restart ou
    # requisição abortada. DNS via ai_mesh é estável.
    "-H", "Content-Type: application/json", "-d", payload
], capture_output=True, timeout=300)

if result.returncode != 0 or os.path.getsize(args.output) < 100:
    print(f"Error", file=sys.stderr)
    sys.exit(1)
```

Configure Hermes:

```bash
hermes config set tts.provider <model-name>
hermes config set tts.providers.<model-name>.type command
hermes config set tts.providers.<model-name>.command "python3 /opt/data/.hermes/scripts/<model>-tts.py --text-file {input_path} --output {output_path} --voice {voice}"
hermes config set tts.providers.<model-name>.output_format ogg
hermes config set tts.providers.<model-name>.timeout 600
hermes config set tts.providers.<model-name>.voice female
hermes config set tts.providers.<model-name>.voice_compatible true
hermes config set tts.providers.<model-name>.max_text_length 2000
```

### 7. SSH Tunnel for Web UI
```bash
ssh -L <port>:localhost:<port> ubuntu@<server-ip>
# Open: http://localhost:<port>/docs (Swagger) or /web (if available)
```

## Models Tested on Oracle ARM64 (4 CPU, 24GB RAM, 0 GPU)

See `references/benchmarks.md` for detailed benchmark tables (RTF values, Qwen3-TTS measurements, GGUF quantization results, voice cloning metrics).

## Known Pitfalls

⚠️ **torch CUDA bloat:** Installing a model package normally on Linux may pull torch with CUDA (+10GB). Always install torch FIRST from `--index-url https://download.pytorch.org/whl/cpu`, then install model with `--no-deps` if it depends on torch.

⚠️ **qwen-tts does NOT depend on torch** — can be installed normally without `--no-deps`. Check each model's pyproject.toml.

⚠️ **Missing dependencies with --no-deps:** When using `--no-deps`, you must manually install all the model's dependencies. Check the model's `pyproject.toml` for the full dependency list. Common missing deps: `transformers`, `accelerate`, `soundfile`, `librosa`, `scipy`, `pillow`, `safetensors`, `tokenizers`, `huggingface-hub`, `numpy`.

⚠️ **OmniVoice — `--no-deps` broke with newer releases.** OmniVoice v0.1.5+ depends on `HiggsAudioV2TokenizerModel` (from `transformers>=5.4.0`). When using `--no-deps omnivoice`, the Dockerfile must explicitly install `transformers>=5.4.0`, not `>=5.3.0`. The symptom is `ModuleNotFoundError: Could not import module 'HiggsAudioV2TokenizerModel'` during `from_pretrained()`. Fix:
```dockerfile
RUN pip install --no-cache-dir "transformers>=5.4.0"
# Remove --no-deps entirely from omnivoice install — newer versions resolve
# dependencies correctly on CPU if torch is already pre-installed
RUN pip install --no-cache-dir omnivoice
```

⚠️ **Model version pinning — always check latest.** The `--no-deps` strategy is fragile across releases. Before deploying any model, check its current `pyproject.toml` for dependency changes. For OmniVoice specifically: the `--no-deps` + manual deps approach worked for v0.1.0 but broke for v0.1.5+. Prefer installing normally (without `--no-deps`) when the model's dependency solver doesn't pull CUDA torch.

⚠️ **First startup downloads model:** The model (~3-7GB) downloads from HuggingFace on first startup. Plan for extra time.

⚠️ **Uvicorn single-worker blocking on CPU-bound models:** When uvicorn runs with a single worker (default), a TTS generation request blocks ALL subsequent requests — including `/health`. If the HTTP client disconnects (timeout, user interrupt), **the worker stays stuck** processing the aborted request indefinitely. The server appears dead until the worker finishes or the container is restarted.

   **Symptom:** `curl /health` connects but never gets a response. Container shows "Up" in `docker ps`. Logs show model is generating.

   **Fix — restart the container:**
   ```bash
   ssh oracle-host 'cd /home/ubuntu/selfhost/<model> && docker compose restart api'
   ```
   The model reloads from cache (fast, ~5s) and the server is responsive again.

   **Prevention:** Set a request timeout in uvicorn or wrap the generation in `asyncio.wait_for()` to auto-kill stuck requests after a reasonable period.

⚠️ **Server.py baked into Docker image — modifications lost on restart.** The `COPY server.py /app/server.py` in the Dockerfile bakes server.py into the image. Any runtime modification (e.g., adding voice cloning `--prompt-audio` support) is lost when the container restarts. Fix: volume-mount server.py over the COPY:
```yaml
volumes:
  - ./server/server.py:/app/server.py
```
Then any edit to server.py takes effect on `docker compose restart s2-server` without rebuild. If already built without volume mount, rebuild:
```bash
ssh oracle-host 'cd ~/selfhost/fish-speech && docker compose build s2-server && docker compose up -d'
```

⚠️ **Fish Speech S2 Pro (5B) — GGUF quantizado é VIÁVEL em CPU, mas lento.** O modelo full float32 é inviável (~20GB RAM, RTF proibitivo). Porém GGUF quantization muda o cenário. O engine C++ nativo `s2.cpp` elimina overhead Python, mas a inferência segue pesada para 5B params em 4 CPUs.

   **GGUF benchmarks**: See `references/benchmarks.md` for RTF, RAM, and audio duration per quantization level (q8_0, q6_k, q5_k_m).
   
   **Multi-quant API:** refatore o server.py para usar MODEL_REGISTRY + _resolve_model(). O template `templates/fish-speech-server.py` já inclui essa arquitetura. Adicione novos quants sem rebuildar o container — modelos são montados como read-only volumes.

   **Model download:** GGUF models (3-5GB) baixam do HuggingFace. Preferir `wget -c` (resume support) sobre `curl` para arquivos grandes. O download speed varia muito (~2MB/s a ~80MB/s) dependendo da carga do CDN. Se lento, matar e reiniciar pode pegar um mirror mais rápido.
   
   **Quant selection:** Multi-quant architecture in server.py allows switching via `model` parameter without rebuild. See `references/benchmarks.md` for performance comparison across quantization levels.

   **Use `s2.cpp` (https://github.com/rodrigomatta/s2.cpp) — NÃO o Docker oficial Python.** O inference em Python com PyTorch seria muito mais lento e consumiria mais RAM. O engine C++ é a única via viável para CPU.

   **Voice cloning — refatorar server.py para expor `--prompt-audio`:** O Fish Speech não tem voice design textual como Qwen, mas suporta voice cloning por referência de áudio via s2.cpp CLI. Em vez de executar `docker exec` diretamente, refatore o server.py (FastAPI) para aceitar `prompt_audio_path` e `prompt_text` opcionais no request, e passar `--prompt-audio` e `--prompt-text` ao s2.bin.

   Exemplo de alteração no server.py:
   ```python
   class SpeechRequest(BaseModel):
       model: str = "s2-pro"
       input: str
       voice: str = "0"
       response_format: str = "wav"
       prompt_audio: Optional[str] = None   # path no container
       prompt_text: Optional[str] = None    # transcrição exata

   # No synthesize():
   s2_args = [S2_BIN, "-m", model_path, "-t", TOKENIZER_PATH,
              "--text", text, "-o", output_path]
   if req.prompt_audio:
       s2_args.extend(["-pa", req.prompt_audio])
   if req.prompt_text:
       s2_args.extend(["-pt", req.prompt_text])
   result = subprocess.run(s2_args, capture_output=True, timeout=INFERENCE_TIMEOUT)
   ```

   ⚠️ **`-max-tokens 0` = zero frames gerados.** O s2.cpp interpreta `-max-tokens 0` literalmente como "gera no máximo 0 tokens". O resultado é `[Generate] Done: 0 frames generated.` NUNCA passe esse flag. Deixe o s2.cpp usar o default (1024 tokens) — remova `-max-tokens` do server.py completamente. Esse bug é fácil de reintroduzir durante refactors — sempre verifique se o argumento não está presente no subprocess.run().

   ⚠️ **`--prompt-text` é OBRIGATÓRIO quando `--prompt-audio` é usado.** s2.cpp retorna `Pipeline error: prompt audio was provided without prompt text.` se `-pt` não for passado junto com `-pa`. No server.py, SEMPRE forneça `-pt` quando `-pa` estiver presente, mesmo que seja um fallback genérico:
   ```python
   if req.prompt_audio:
       pt = req.prompt_text or "Default reference text for voice cloning."
       s2_args.extend(["-pa", req.prompt_audio, "-pt", pt])
   ```
   Não use `if req.prompt_text:` condicional.

   ⚠️ **`:ro` volume mount — output WAV não pode ir em `/app/models/`.** O volume `./models:/app/models` é montado como `:ro` (read-only). Escreva o output WAV em `/tmp/` dentro do container. O arquivo de áudio de referência para cloning pode estar em `/tmp/` ou em `/app/models/` se for copiado antes do mount (`COPY` no Dockerfile).

   **Padrão "default" para reference audio:** O server.py expõe uma env var `REFERENCE_AUDIO` apontando para o caminho default do áudio de referência. O cliente pode passar `"prompt_audio": "default"` para usar esse caminho, sem precisar saber o path real no container. Implementação:
   ```python
   REFERENCE_AUDIO = os.environ.get("REFERENCE_AUDIO", f"{MODELS_DIR}/ref-charon.wav")
   # No endpoint:
   if req.prompt_audio == "default":
       prompt_audio_path = REFERENCE_AUDIO
   ```
   O health check retorna `"reference_audio": {"exists": bool, "path": str}` para debug.

   Para produção, considere usar `--save-voice` para evitar re-encode da referência a cada request (economiza ~30s por chamada).
   ```bash
   docker exec fish-speech-s2-server-1 /app/s2.bin \
     -m /app/models/s2-pro-q8_0.gguf -t /app/models/tokenizer.json \
     -pa /app/models/ref.wav -pt "transcricao" \
     --save-voice --voice "hermes-charon" --voice-dir /app/models/voices/

   docker exec fish-speech-s2-server-1 /app/s2.bin \
     -m /app/models/s2-pro-q8_0.gguf -t /app/models/tokenizer.json \
     --voice "hermes-charon" --voice-dir /app/models/voices/ \
     --text "Texto" -o /tmp/out.wav
   ```

   **Métricas (q8_0, ref 15s, Oracle ARM64 4-core):** See `references/benchmarks.md` for init/encode/generate timing breakdown and RTF values.

⚠️ **Qwen3-TTS voice description for Portuguese — must specify accent:** The default voice produces a pronounced Chinese accent in Portuguese. Always include `"sotaque português brasileiro neutro"` or similar in the voice description. Example that works:
```json
{
  "voice": "Voz masculina, tom grave-médio, confiante e levemente irônico, sotaque português brasileiro neutro, dicção limpa"
}
```

⚠️ **Testing workflow for CPU-bound models (high RTF):**
   - **Step 1:** Test connectivity FIRST (`curl /health`). Do NOT jump to a synthesis request without confirming the server responds.
   - **Step 2:** Start with 2-3 words only (~0.5s audio, ~10-60s gen time depending on model). Send for user feedback before iterating.
   - **Step 3:** Escalate to 1 sentence (~3-5s audio, ~45-150s gen), then longer passages.
   - **Step 4:** Always report timing (`time curl ...` or note duration) so user can calibrate expectations.
   - **Step 5:** One generation at a time. Do NOT run parallel inference requests — uvicorn single worker serializes them anyway.
   - **Step 6:** If a user interrupts a request (sends new message), expect the server to be blocked. Plan for `docker compose restart` recovery.
   - **Step 7:** Communicate clearly during failures — say WHAT happened and WHY, not just that something failed. Users prefer a brief diagnosis over silence or vague "waiting..." messages. If a model won't load, show the exact error trace's root cause (not just "failed to load").
   - **Step 8:** Respect slow generation times — inform user about expected duration upfront, don't fire multiple test requests in parallel.
   - **Step 9:** Never waste the user's time building something that obviously won't work on the hardware. If the model is too large or too slow, say so upfront with concrete numbers (RAM needed vs available, estimated RTF) before starting the build.
   - **Step 10:** **Client timeout MUST exceed server timeout.** The server's `subprocess.run(timeout=N)` is the backend timeout. The HTTP client (curl, bridge script) must use `-m` / `timeout=` value GREATER than the expected generation time. A short client timeout kills the connection but does NOT stop the server subprocess, wasting resources.
   - **Step 11:** For very slow models (RTF >30), use background mode (`notify_on_complete=true`) when testing via Hermes terminal. Foreground timeout is capped at 600s.

⚠️ **Model download on every cold start** if the model cache isn't mounted as a persistent volume. Always use a named volume in docker-compose.yml.

## Pattern C — Cloud TTS for Reference Generation

When a local model needs a voice reference sample (e.g., for Fish Speech S2 voice cloning), use Gemini 3.1 Flash TTS as a cloud-based sample generator. It produces clean, high-quality audio at 24kHz 16-bit PCM that works well as a cloning reference.

**Key details:**
- **Model:** `gemini-3.1-flash-tts-preview` via `google-genai` Python SDK
- **Output:** PCM 24000 Hz, 16-bit, mono → save as WAV
- **30 prebuilt voices** with descriptors (Erinome=Clear, Schedar=Even, Charon=Informative, etc.)
- **200+ audio tags** for expressive control (`[wryly]`, `[thoughtfully]`, `[dryly]`, `[confidence]`, etc.)
- **Prompt structure:** LiveKit canonical — preamble + scene + performance + context + `#### TRANSCRIPT`

**Prompting rules (from LiveKit guide):**
1. Preâmbulo `"Synthesize speech for..."` é OBRIGATÓRIO para gatilhar o classifier
2. `#### TRANSCRIPT` com exatos 4 hashes
3. Cena concreta, labels curtas (`### PERFORMANCE`, `### CONTEXT`)
4. Vírgulas entre cláusulas com tag, não pontos finais
5. NUNCA instrua monotonia — use `"warm and sincere"`, não `"flat"`

**Usage workflow:**
1. Craft a prompt with the target persona (scene + performance + transcript + tags)
2. Generate via Gemini API
3. Copy WAV to server: `scp ref.wav oracle-host:~/selfhost/<model>/models/`
4. Use as voice reference in the local model's request

See `references/gemini-3-1-tts-prompting.md` for full API reference, voice table, tag system, and example prompts.

## GPU Acceleration Options

See `references/gpu-options.md` for a comparison of:
- HF ZeroGPU (free A100 time-sliced)
- Gemini 2.5 Flash TTS (paid API, $0.0025/10s)
- HF Inference Endpoint (dedicated T4, $0.50/h, scale-to-zero)
- Google Cloud $300 free trial (excludes Gemini API since Mar 2026)

## Related Skills

- `oracle-host-access` — SSH from Hermes container to Oracle host
- `deployment-pipeline` — CI/CD for Docker apps on Oracle
- `style-guide-consultation` — default style guide for HTML reports

## References

- `references/gemini-3-1-tts-prompting.md` — Gemini 3.1 Flash TTS prompting guide: voice selection, audio tags, LiveKit canonical prompt structure, Python API, multi-speaker, and reference generation for voice cloning

- `references/qwen3-tts-voicedesign-prompting.md` — Qwen3-TTS VoiceDesign instruct format (structured key-value from official blog), accepted dimensions, and common errors
- `references/fish-speech-s2-pro-research.md` — Fish Speech S2 Pro (5B) research: architecture, GGUF quantization, s2.cpp engine, and comparison with Qwen3-TTS
- `references/benchmarks.md` — Performance benchmarks for all TTS models on Oracle ARM64: RTF tables, Qwen3-TTS measurements, GGUF quantization results, voice cloning metrics
- `references/gpu-options.md` — GPU acceleration options for TTS inference (HF ZeroGPU, GCP, RunPod)
- `references/qwen3-tts-deployment.md` — Qwen3-TTS 1.7B deployment details on Oracle ARM64 (Dockerfile, compose, performance data, known issues)

## Templates

- `templates/fish-speech-server.py` — Known-good FastAPI wrapper for s2.cpp (Pattern B: C++ native inference via subprocess). Copy to `selfhost/<project>/server/server.py` and adjust env vars.