# Fish Speech S2 Pro — Research & Deployment Findings (Jun/2026)

## Modelo

- **Nome:** Fish Audio S2 Pro (`fishaudio/s2-pro` no HuggingFace)
- **Tamanho:** 4B (Slow AR) + 400M (Fast AR) = 5B params no total
- **Formato original:** BF16 (inferência GPU), float32 em CPU forçaria ~20GB
- **GGUF quantizado:** `rodrigomt/s2-pro-gguf` no HuggingFace
- **Engine C++:** `rodrigomatta/s2.cpp` no GitHub (C++17, nativa, suporte ARM64)
- **Licença:** Fish Audio Research License (não Apache 2.0 — comercial requer licença separada)
- **Repo oficial:** https://github.com/fishaudio/fish-speech

## Arquitetura

- **Dual-AR:** Slow AR (4B, eixo temporal, codebook semântico primário) + Fast AR (400M, 9 codebooks residuais)
- **Codec:** RVQ-based audio codec (10 codebooks, ~21 Hz frame rate)
- **Tokenizador:** HiggsAudioV2

## Controle de Voz

Fish Speech **NÃO** tem "voice design from text description" como Qwen3-TTS. O controle funciona por:

1. **Referência de áudio** (10-30s) — clona timbre + prosódia. Melhor performance cross-lingual
2. **Tags inline** — `[laughing]`, `[whisper]`, `[sad]`, `[excited tone]`, `[angry]`, `[volume up]`, `[pause]`, `[emphasis]`, etc. (15.000+ tags únicas)
3. **Presets multimídia** — `<|speaker:i|>` tokens para múltiplos speakers numa geração

Não há parâmetro `instruct` ou descrição de voz textual como no Qwen.

## Português

Suportado (Tier 2, <10k horas de treino). Funciona, mas qualidade inferior ao Tier 1 (inglês/japonês/chinês).

## GGUF Quantization — por que muda tudo

O modelo em float32 (~20GB) é inviável em CPU ARM64. Mas GGUF quantization reduz drasticamente:

| Quant | File size | RAM carregado | RTF ARM64 (medido) |
|-------|-----------|---------------|-------------------|
| q2_k  | 2.4GB     | ~2.0GB        | não testado       |
| q4_k_m| 3.4GB     | ~2.9GB        | não testado       |
| q5_k_m| 3.8GB     | ~3.2GB        | ~25.7x (mid-text) |
| q6_k  | 4.3GB     | ~3.7GB        | ~33.2x (mid-text) |
| q8_0  | 5.3GB     | ~4.6GB        | ~37.6x (mid-text) |
| f16   | 9.3GB     | ~8.5GB        | não testado       |

**Multi-quant benchmark (Jun/2026, mesma frase "Olá, me chamo Hermes. Sou inteligência de fronteira."):**

| Quant | Áudio gerado | Tempo geração | RTF | Tam. arquivo |
|-------|-------------|---------------|-----|-------------|
| q8_0  | 3.34s       | 125.6s        | 37.6x | 590KB |
| q6_k  | 3.85s       | 128.0s        | 33.2x | 680KB |
| q5_k_m| 4.60s       | 118.2s        | 25.7x | 811KB |

Observação: a duração do áudio gerado DIFERE entre quants para o mesmo texto de entrada. q5_k_m produziu 38% mais áudio que q8_0 (4.60s vs 3.34s) — diferenças de precisão afetam timing do speech. O RTF menor do q5_k_m (25.7x vs 37.6x) sugere que quants menores não só carregam mais rápido como também geram menos tokens por segundo de áudio, compensando parcialmente a perda de qualidade.

**Com q8_0 (5.3GB file, ~4.6GB RAM):** O modelo cabe confortavelmente em 24GB RAM total (sobra ~15GB para sistema). A inferência roda em CPU ARM64 4-core com RTF 38-114x.

## s2.cpp — Engine C++ Nativo

O `s2.cpp` (https://github.com/rodrigomatta/s2.cpp) é um port C++17 do Fish Speech S2 Pro que:

- Usa GGUF como formato de modelo (via `ggml`/`llama.cpp` infrastructure)
- Roda puramente em CPU (sem dependência de GPU/Python)
- Compila nativamente em ARM64 Linux (precisa cmake + g++ com suporte C++17)
- Binário resultante: ~1.4MB
- Output: WAV 44100 Hz, 32-bit float mono

**Build steps (ARM64):**
```bash
git clone https://github.com/rodrigomatta/s2.cpp
cd s2.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j4
# Binário em: src/build/s2.bin
```

**Uso via CLI (síntese básica):**
```bash
./s2.bin -m modelo.gguf -t tokenizer.json --text "texto" -o output.wav
```

**Voice cloning CLI (s2.cpp nativo):**

O s2.bin suporta cloning via `--prompt-audio` e `--prompt-text`:

```bash
# Clonagem simples
ssh oracle-host 'docker exec fish-speech-s2-server-1 /app/s2.bin \
  -m /app/models/s2-pro-q8_0.gguf \
  -t /app/models/tokenizer.json \
  -pa /app/models/ref-audio.wav \
  -pt "transcricao exata do audio de referencia" \
  --text "Texto a sintetizar com a voz clonada." \
  -o /tmp/output.wav'

# Salvar como perfil para reuso (evita re-encode da referência)
./s2.bin -m modelo.gguf -t tokenizer.json \
  -pa ref.wav -pt "transcricao" \
  --save-voice --voice "hermes-charon" --voice-dir /app/voices/

# Listar perfis
./s2.bin --voice-dir /app/voices/ --list-voices

# Usar perfil salvo
./s2.bin -m modelo.gguf -t tokenizer.json \
  --voice "hermes-charon" --voice-dir /app/voices/ \
  --text "Texto a gerar" -o output.wav

⚠️ **`:ro` volume:** Se o diretório models/ estiver montado como read-only no Docker, escreva o output em `/tmp/` e copie com `docker cp`.
```

**Parâmetros completos do s2.bin (voice cloning):**

| Parâmetro | Descrição |
|-----------|-----------|
| `-m, --model <path>` | Path do GGUF |
| `-t, --tokenizer <path>` | Path do tokenizer.json |
| `--text <text>` | Texto a sintetizar |
| `-pa, --prompt-audio <path>` | Áudio de referência para voice cloning (3-15s, 16-bit mono WAV) |
| `-pt, --prompt-text <text>` | Transcrição exata do áudio de referência |
| `--voice <id>` | Carregar perfil de voz salvo |
| `--save-voice` | Salvar referência codificada como perfil |
| `--voice-dir <path>` | Diretório de perfis de voz |
| `--list-voices` | Listar perfis disponíveis |
| `-o, --output <path>` | Output WAV path |
| `-threads <n>` | Threads CPU (0=auto) |
| `-temp, --temperature <f>` | Temperatura de amostragem |
| `--trim-silence` | Remover silêncio final |
| `--normalize` | Peak-normalizar para 0.95 |
| `--server` | Iniciar servidor HTTP embutido (porta 3030) |

**Métricas medidas com cloning (Jun/2026, Oracle ARM64, q8_0, ref 15s Charon):**

| Fase | Tempo | Notas |
|------|-------|-------|
| Init + codec load | ~56s | Carrega modelo 4.6GB + codec CPU |
| Reference encode | ~27-39s | Codifica 15s de referência |
| Prefill (413 tokens) | ~33-49s | Processa texto de entrada |
| Generation (30-33 frames) | ~31-35s | Geração autoregressiva lenta |
| Decode | ~4.5s | Decodificação codec |
| **Total (1.4-1.5s áudio)** | **~73-85s** | RTF ~48-57x |
| RAM | ~6.8GB max | Modelo 4.6GB + buffers |

O overhead de init (~56s) é fixo por invocação. Textos mais longos melhoram o RTF pois o prefill já está pago.

## Deploy Pattern — Docker + s2 subprocess

Diferente dos modelos Python (OmniVoice, Qwen), o Fish Speech S2 é servido via **subprocess wrapping**:

```
FastAPI (uvicorn) → subprocess.run(s2.bin, timeout=600) → WAV output
```

### docker-compose.yml
```yaml
name: fish-speech
services:
  s2-server:
    build:
      context: ./server
      dockerfile: Dockerfile
    ports:
      - "8882:8882"
    volumes:
      - ./s2/s2.bin:/app/s2.bin
      - ./models:/app/models:ro
    environment:
      - S2_BIN=/app/s2.bin
      - MODEL_PATH=/app/models/s2-pro-q8_0.gguf
      - TOKENIZER_PATH=/app/models/tokenizer.json
    restart: unless-stopped
    networks:
      - ai_mesh
networks:
  ai_mesh:
    external: true
```

### Dockerfile (minimal — no torch)
```dockerfile
FROM python:3.11-slim
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY server.py .
EXPOSE 8882
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8882"]
```

### server.py (FastAPI wrapper)
```python
@app.post("/v1/audio/speech")
async def synthesize(req: SpeechRequest):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name
    try:
        result = subprocess.run(
            [S2_BIN, "-m", MODEL_PATH, "-t", TOKENIZER_PATH,
             "--text", req.input, "-o", output_path],
            capture_output=True, timeout=600,
        )
        if result.returncode != 0:
            raise HTTPException(500, f"s2 error: {result.stderr.decode()[:300]}")
        with open(output_path, "rb") as f:
            data = f.read()
        return Response(content=data, media_type="audio/wav")
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)
```

## Performance Measurada (Oracle ARM64, 4 vCPUs, 24GB RAM, q8_0)

| Texto | Áudio gerado | Tempo real | RTF | Notas |
|-------|-------------|-----------|-----|-------|
| "teste." (0.5s esperado) | 0.51s | 58.1s | 114 | Overhead de carregamento domina |
| "Olá, me chamo Hermes..." | 3.34s | 125.6s | 38 | Texto de tamanho médio |

**Padrão observado:** RTF cai drasticamente com textos mais longos (de 114x para 38x). O overhead fixo de inicialização (~30-50s) é amortizado em textos maiores.

Para uso prático no Hermes, frases de 10-15 palavras geram ~3-5s de áudio em ~2 min.

## Comparativo com Qwen3-TTS 1.7B no mesmo hardware

| Aspecto | Qwen3-TTS 1.7B | Fish Speech S2 Pro q8_0 |
|---------|----------------|------------------------|
| RAM | ~8-10GB | ~4.6GB |
| RTF (mid-text) | ~15x | ~38x |
| 5s áudio | ~75s | ~190s |
| Voice design textual | ✅ sim (instruct) | ❌ não (ref áudio) |
| Voice cloning | ❌ não | ✅ sim (3-10s ref) |
| Qualidade PT-BR | ✅ boa (com instruct correto) | ✅ Tier 2, aceitável |
| Licença | Apache 2.0 | Research License |
| Setup | Docker + Python | Docker + C++ binary + GGUF download |

**Trade-off:** Qwen é 2.5x mais rápido e tem voice design textual. Fish Speech é mais leve em RAM e permite voice cloning. Escolha depende da prioridade.

## Alternativas menores testadas (rejeitadas)

- **Fish Speech 1.5** (~1.2B) — CC-BY-NC-SA-4.0. Sem GGUF port. Preferir S2 Pro GGUF.
- **OmniVoice** — v0.1.5+ quebrou com `torch.float8_e8m0fnu` em ARM64 CPU. Arquivado.
