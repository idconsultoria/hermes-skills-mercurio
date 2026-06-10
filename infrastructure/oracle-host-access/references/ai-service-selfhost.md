# AI/ML Service Selfhost on Oracle ARM64

Padrão para implantar serviços de IA (TTS, ASR, LLM, visão) no Oracle Ampere ARM64.

## Arquitetura comum

```
selfhost/<service>/
├── Dockerfile              # Build local (ARM64 nativo)
├── docker-compose.yml      # Orquestração
├── .env                    # Secrets
├── main.py / server.py     # App
└── web/                    # Web UI (opcional)
```

## Dockerfile — PyTorch CPU no ARM64 (CRÍTICO)

**NUNCA** use `pip install` direto de um pacote que dependa de torch. O PyPI padrão serve wheels CUDA (com NVIDIA libraries que não funcionam em ARM64 e somam +10GB inúteis).

**Sintoma de build errado:** logs mostram `nvidia-cublas`, `nvidia-cuda-runtime`, `cuda-toolkit`, `cuda-bindings` sendo instalados.

**Padrão correto (2-pass):**

```dockerfile
# Pass 1: PyTorch CPU primeiro (do index oficial CPU)
RUN pip install --no-cache-dir \
    torch==2.4.0 \
    torchaudio==2.4.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Pass 2: app sem dependências (para não reinstalar torch com CUDA)
RUN pip install --no-cache-dir --no-deps omnivoice
# E as demais dependências manualmente:
RUN pip install --no-cache-dir \
    transformers accelerate pydub numpy soundfile librosa \
    fastapi uvicorn python-multipart
```

**Por que isso é necessário:** O `pyproject.toml` do OmniVoice redireciona torch via `tool.uv.sources` para o index CUDA (`cu128`). `pip install omnivoice` sem `--no-deps` baixa torch com CUDA mesmo em CPU.

**Se o build falhar ou estiver lento demais (CUDA packages):**
```bash
# 1. Kill o build
process(action='kill', session_id='...')

# 2. Corrige o Dockerfile (adicionar --no-deps + torch CPU primeiro)

# 3. SCP o Dockerfile corrigido e rebuilda
scp Dockerfile oracle-host:/home/ubuntu/selfhost/<service>/Dockerfile
ssh oracle-host "cd /home/ubuntu/selfhost/<service> && docker compose build --no-cache"
```

## Deploy (Manual via SSH)

```bash
# 1. Copiar arquivos do Hermes container para o host
scp -r /opt/data/selfhost/<service>/* oracle-host:/home/ubuntu/selfhost/<service>/

# 2. Build (no host) — usar background + notify para builds longos
terminal(
    command="ssh oracle-host 'cd /home/ubuntu/selfhost/<service> && docker compose build --no-cache 2>&1'",
    background=True,
    notify_on_complete=True
)

# 3. Subir
ssh oracle-host "cd /home/ubuntu/selfhost/<service> && docker compose up -d"

# 4. Verificar logs (download do modelo na primeira execução)
ssh oracle-host "docker logs --tail 30 <service>-<service>-1"

# 5. Verificar health
ssh oracle-host "curl -s localhost:<porta>/health"
```

**⚠️ Process management:** Sempre usar `notify_on_complete=True` em builds longos. Se precisar matar um build que errou, use `process(action='kill', session_id='...')`. Depois corrige e rebuilda.

## Model Cache

Modelos grandes (1-10GB) baixados do HuggingFace na primeira execução:

```yaml
# docker-compose.yml
volumes:
  - <service>_models:/app/models

# Dockerfile
ENV HF_HOME=/app/models
```

Volume nomeado persiste entre recreações. Primeiro `up -d` sempre leva minutos (download). Depois é instantâneo.

**Verificar progresso do download:**
```bash
ssh oracle-host "docker logs --tail 5 <container-name>"
# Procure por "Fetching N files: X%", "Loading weights: X%"
```

## Recursos — Verificar antes de deixar rodando

Sempre verificar o impacto do container ocioso antes de considerar "pronto":

```bash
ssh oracle-host "docker stats <container> --no-stream --format 'CPU: {{.CPUPerc}} | MEM: {{.MemPerc}} ({{.MemUsage}})'"
```

**Referência (OmniVoice):** 7.3GB RAM, 0.12% CPU idle. Modelo fica carregado em RAM o tempo todo.

## Modelos de IA já implantados no Oracle

| Serviço | Tipo | Modelo | Porta | Cache | RAM idle | Inferência (CPU ARM64) |
|---------|------|--------|-------|-------|----------|----------------------|
| ~~OmniVoice~~ | TTS | k2-fsa/OmniVoice (~4GB) | ~~8880~~ (removido) | — | — | — |
| **Fish Speech S2 Pro** | TTS | fishaudio/s2-pro via s2.cpp GGUF q8_0 | **8882** | bind mount ./models/ | ~4.6GB | Muito lento em CPU (30s+ p/ 2 palavras) |
| ~~Qwen3-TTS~~ | TTS | Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign | ~~8881~~ (down) | qwen3_models | — | RTF 15-28 (reativável via `docker compose up -d`) |

**Reativar Qwen:** `cd /home/ubuntu/selfhost/qwen3-tts && docker compose up -d`
**Ativar no Hermes:** `sed -i 's/provider: omnivoice/provider: qwen3/' /opt/data/config.yaml`

## Hermes TTS — Provider Command

Para integrar um serviço TTS selfhostado ao Hermes, criar um script bridge e configurar o command provider:

### Script bridge (`/opt/data/.hermes/scripts/<service>-tts.py`)

```python
#!/usr/bin/env python3
"""Bridge between Hermes TTS command provider and <service> API."""
import sys, json, subprocess, argparse, os

parser = argparse.ArgumentParser()
parser.add_argument('--text-file', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--voice', default='female')
parser.add_argument('--model', default='omnivoice')
args = parser.parse_args()

with open(args.text_file) as f:
    text = f.read().strip()

payload = json.dumps({
    "model": args.model,
    "input": text,
    "voice": args.voice,
    "language_id": "pt"
})

result = subprocess.run([
    "curl", "-s", "-o", args.output,
    "-X", "POST",
    "http://<service>:8880/v1/audio/speech",   # DNS name via ai_mesh
    "-H", "Content-Type: application/json",
    "-d", payload
], capture_output=True, timeout=300)

if result.returncode != 0 or os.path.getsize(args.output) == 0:
    sys.exit(1)
```

**URL pattern:** Use `http://<service-name>:<port>` (DNS via `ai_mesh`) em vez de `http://172.19.0.1:<port>` (gateway IP). O DNS interno do Docker é mais confiável — não sofre de roteamento inconsistente entre containers em redes customizadas.

### Config (`~/.hermes/config.yaml`)

```yaml
tts:
  provider: <service-name>
  providers:
    <service-name>:
      type: command
      command: "python3 /opt/data/.hermes/scripts/<service>-tts.py --text-file {input_path} --output {output_path} --voice {voice} --model {model}"
      output_format: wav
      timeout: 300
      max_text_length: 2000
      voice_compatible: true
      voice: female
      model: omnivoice
```

### Placeholders do Hermes Command Provider

| Placeholder | Uso |
|-------------|-----|
| `{input_path}` | Arquivo temp com texto |
| `{output_path}` | Onde escrever o áudio |
| `{voice}` | Vindo de `providers.<name>.voice` |
| `{model}` | Vindo de `providers.<name>.model` |
| `{speed}` | Speed multiplier |
| `{format}` | mp3/wav/ogg/flac |

### Config via CLI

```bash
/opt/hermes/.venv/bin/hermes config set tts.provider <service>
/opt/hermes/.venv/bin/hermes config set tts.providers.<service>.type command
/opt/hermes/.venv/bin/hermes config set tts.providers.<service>.command "python3 ..."
/opt/hermes/.venv/bin/hermes config set tts.providers.<service>.output_format wav
/opt/hermes/.venv/bin/hermes config set tts.providers.<service>.timeout 300
/opt/hermes/.venv/bin/hermes config set tts.providers.<service>.voice_compatible true
/opt/hermes/.venv/bin/hermes config set tts.providers.<service>.voice female
```

### Exemplo real — Qwen3-TTS (config.yaml)

```yaml
tts:
  provider: qwen3
  providers:
    qwen3:
      type: command
      command: python3 /opt/data/.hermes/scripts/qwen3-tts.py --text-file {input_path} --output {output_path} --voice {voice}
      max_text_length: 2000
      output_format: wav
      timeout: 600          # 10 min — CPU geração é lenta
      voice_compatible: true
      voice: "A calm male voice, mid-range pitch, confident and slightly ironic, slow and deliberate"  # padrão
```

O bridge script (`qwen3-tts.py`) faz POST para `http://qwen3-api:8881/v1/audio/speech` com payload `{input, voice, language_id}`, onde `voice` vira o `instruct` do VoiceDesign.

## SSH Tunnel para Web UI

```bash
ssh -L <porta_local>:localhost:<porta_container> ubuntu@<ip_publico>
```

Depois: `http://localhost:<porta_local>/web`

## Voice Steering — Modelos Locais com Controle de Emoção/Estilo

O OmniVoice **não** suporta voice steering (emoção, tom, atitude por texto). Apenas atributos físicos de voz.

Modelos que suportam (pesquisado em Jun/2026):

| Modelo | Steering | PT-BR | Licença | Hardware |
|--------|----------|-------|---------|----------|
| **Qwen3-TTS 1.7B** | ✅ `instruct` + VoiceDesign descritivo | ✅ Sim | Apache 2.0 | GPU (ou CPU lento) |
| **Fish Speech S2 Pro** | ✅ Tags livres: `[excited and fast]` | ✅ 80+ línguas | ⚠️ Complexa | GPU |
| **Chatterbox Turbo** | ✅ `[laugh]` + exaggeration | ❌ EN only | MIT | CPU possível |
| **CosyVoice 3.0** | ✅ Emoção via referência | ✅ Sim | Apache 2.0 | CPU possível |

### Qwen3-TTS 1.7B VoiceDesign (implantado)

**Modelo ativo:** `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` (porta 8881)
**Status:** Rodando em CPU ARM64 (RTF ~15-28s por 1s de áudio)
**Diretório:** `/home/ubuntu/selfhost/qwen3-tts/` (no host Oracle)
**Rede:** `ai_mesh` (compartilhada com Hermes e Firecrawl)

### Parâmetros da API (POST /v1/audio/speech)

| Nosso JSON | Mapeia p/ | Exemplo |
|---|---|---|
| `input` | `text` | `"Olá mundo"` |
| `voice` | `instruct` (descrição da voz) | Vide formato abaixo |
| `language_id` | `language` | `"pt"` → `"Portuguese"` |

**⚠️ O `instruct` deve estar em INGLÊS (estruturado) ou CHINÊS.** Enviar em português degrada o resultado — o modelo não interpreta corretamente e reverte ao viés do treino (chinês/inglês americano).

### Formato recomendado de instruct (oficial do blog de lançamento)

Formato `chave: valor.\n` (uma dimensão por linha) — extraído dos exemplos da página oficial qwen.ai/blog:

```
gender: Male.
pitch: Low to mid-range, steady and controlled.
speed: Slow, deliberate pace with measured pauses.
volume: Moderate, conversational, with quiet authority.
age: Adult.
clarity: Clear and precise articulation.
fluency: Fluent, unhurried delivery.
accent: Brazilian Portuguese.
texture: Smooth, warm, velvety quality.
emotion: Confident, with subtle irony.
tone: Direct, laconic, slightly ironic.
personality: Self-assured, bridge between worlds.
```

Dimensões disponíveis (dos exemplos oficiais): `gender`, `pitch`, `speed`, `volume`, `age`, `clarity`, `fluency`, `accent`, `texture`, `emotion`, `tone`, `personality`.

### Exemplos oficiais do blog (qwen.ai/blog?id=qwen3tts-0115)

**Formato estruturado EN (4 exemplos idênticos na página):**
```
gender: Male.
pitch: Low male pitch, generally stable.
speed: Deliberate pace, slowing slightly after the initial exclamation.
volume: Starts loud, then transitions to a projected conversational volume.
age: Middle-aged adult.
clarity: High clarity with distinct pronunciation.
fluency: Highly fluent.
accent: American English.
texture: Resonant and slightly gravelly.
emotion: Initially commanding, shifting to narrative amusement.
tone: Authoritative start, moving to an engaging, descriptive tone.
personality: Confident and performative.
```

**Formato parágrafo descritivo CN:**
```
"体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显，营造出黏人、做作又刻意卖萌的听觉效果。"
```

### Modelos da família Qwen3-TTS

| Modelo | Voice Design | Clone | Steering | Quando usar |
|--------|-------------|-------|----------|------------|
| **1.7B-VoiceDesign** (nosso) | ✅ Descritivo | ❌ | ✅ | Criar vozes novas por texto |
| **1.7B-CustomVoice** | ❌ 9 presets | ❌ | ✅ | Voz fixa + steering de emoção |
| **1.7B-Base** | ❌ | ✅ 3s áudio | ❌ | Clonar voz de amostra + fine-tune |
| **0.6B-CustomVoice** | ❌ 9 presets | ❌ | ❌ | Mais rápido, sem controle |

### Bridge script (`/opt/data/.hermes/scripts/qwen3-tts.py`)

```python
result = subprocess.run([
    "curl", "-s", "-o", args.output,
    "-X", "POST",
    "http://qwen3-api:8881/v1/audio/speech",   # DNS name via ai_mesh
    "-H", "Content-Type: application/json",
    "-d", payload
], capture_output=True, timeout=600)
```

**⚠️ A URL usa DNS name `qwen3-api:8881` (resolvido via Docker ai_mesh) — NÃO o IP do gateway `172.19.0.1`.**

### Rede Docker (`ai_mesh`)

Todos os serviços selfhost que precisam ser alcançados pelo Hermes container devem estar na rede `ai_mesh`:

```yaml
# docker-compose.yml
services:
  qwen3-api:
    # ... config ...
    networks:
      - ai_mesh

networks:
  ai_mesh:
    external: true
```

A rede `ai_mesh` é a mesma do container Hermes (criada pelo compose do Hermes). O Hermes acessa os serviços pelo DNS name do container (ex: `qwen3-api:8881`).

### Pitfalls

**⚠️ Uvicorn single-worker trava com requests abortadas.** O worker fica preso gerando áudio mesmo após o cliente desconectar. Todas as requests subsequentes ficam enfileiradas atrás dele. Soluções:
- `docker compose restart <service>` (reinicia o worker)
- Adicionar `--workers 2` no uvicorn
- Ou configurar `--timeout-keep-alive` para timeout de worker

**⚠️ Testar conectividade ANTES de gerar.** Gerações no CPU levam minutos. Sempre testar primeiro:
```bash
curl -s --connect-timeout 3 http://qwen3-api:8881/health
# Esperado: {"status":"ok","model_loaded":true}
```

**⚠️ Instruct em português causa sotaque chinês.** O `instruct` do VoiceDesign funciona melhor em inglês (formato estruturado) ou chinês. Português no instruct faz o modelo ignorar a descrição e cair no viés do treino.

**⚠️ Performance em CPU.** RTF médio observado: 15-28x (5s de áudio → 75-140s de processamento). Primeira geração após restart é mais lenta (overhead de inicialização do modelo).

## Fish Speech S2 Pro (s2.cpp + GGUF)

**Status:** Implantado via s2.cpp (native C++, não Docker Python)
**Modelo:** `fishaudio/s2-pro` (4.56B params) quantizado como `s2-pro-q8_0.gguf` (5.3GB, ~4.6GB em RAM)
**Diretório:** `/home/ubuntu/selfhost/fish-speech/` (no host Oracle)
**Porta:** 8882 (rede `ai_mesh` - DNS: `fish-speech-s2-server-1:8882`)

### Arquitetura

```
selfhost/fish-speech/
├── docker-compose.yml      # Sobe servidor FastAPI + monta s2.bin + modelo
├── server/
│   ├── Dockerfile           # python:3.11-slim + libgomp1 + FastAPI
│   └── server.py            # Wrapper HTTP que chama s2.bin
├── s2/
│   ├── s2.bin               # Compilado nativo ARM64 (1.4MB)
│   └── src/                 # Clone de rodrigomatta/s2.cpp
└── models/
    ├── s2-pro-q8_0.gguf     # Quant q8_0 (5.3GB)
    └── tokenizer.json        # Tokenizer (12MB)
```

### Build + Deploy

```bash
# 1. Clonar s2.cpp
git clone --recurse-submodules https://github.com/rodrigomatta/s2.cpp.git s2/src

# 2. Build nativo ARM64 (precisa cmake + build-essential)
cd s2/src
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 4
cp build/s2 ../s2.bin

# 3. Download modelo GGUF
wget -c https://huggingface.co/rodrigomt/s2-pro-gguf/resolve/main/s2-pro-q8_0.gguf -P models/
wget -c https://huggingface.co/rodrigomt/s2-pro-gguf/resolve/main/tokenizer.json -P models/

# 4. Build imagem Docker + subir
docker compose build s2-server
docker compose up -d s2-server
```

### API (OpenAI-compatível)

```
POST http://fish-speech-s2-server-1:8882/v1/audio/speech
Body: {"input": "texto", "voice": "0"}
```

- `voice` = `"0"` para voz padrão, ou tags inline como `"excited tone"` (vira `[excited tone] texto`)
- Não tem voice design textual — precisa de referência de áudio pra clonar timbre
- Controle prosódico via tags: `[laughing]`, `[whisper]`, `[sad]`, `[emphasis]`, `[volume up]`, etc.

### Pitfalls

**⚠️ s2.bin precisa de shared libraries no container.** O binário compilado linka contra `libggml-cpu.so.0` (da build do ggml) e `libgomp.so.1` (OpenMP). Montar via volume:

```yaml
volumes:
  - ./s2/src/build/ggml/src:/app/libs
environment:
  - LD_LIBRARY_PATH=/app/libs
```

E instalar `libgomp1` no Dockerfile:
```dockerfile
RUN apt-get install -y --no-install-recommends libgomp1
```

**⚠️ `--max-tokens 0` = zero frames.** O s2.cpp interpreta `-max-tokens 0` como "gerar 0 tokens máximos", produzindo silêncio. Omitir a flag para usar o default (1024 tokens) ou passar um valor positivo.

**⚠️ `--prompt-audio` exige `--prompt-text`.** Se `-pa` for fornecido sem `-pt`, o s2.cpp retorna erro: "prompt audio was provided without prompt text" e gera 0 frames. Sempre passar ambos ou nenhum.

**⚠️ Voice cloning no server.py:** O Wrapper HTTP precisa adicionar os args `-pa` e `-pt` quando o payload tiver `prompt_audio`/`prompt_text`. Referência da implementação no `server.py` do Fish Speech em `/home/ubuntu/selfhost/fish-speech/server/server.py`.

**⚠️ Performance extremamente lenta em CPU.** S2 Pro é 5B params. q8_0 ocupa 4.6GB RAM. Em 4 CPUs ARM64:
- Carregamento do modelo: ~5-10s
- Geração: muito lenta (30s+ para 2 palavras)
- Para uso prático, necessita GPU (Vulkan/CUDA) ou quantização mais agressiva (q4_k_m = 3.4GB)

**⚠️ Sem voice design textual.** Diferente do Qwen3-TTS VoiceDesign, o S2 Pro não cria vozes a partir de descrição textual. Requer áudio de referência (10-30s) para clonar timbre. O controle de estilo é via tags inline no texto.

**⚠️ Licença:** Fish Audio Research License. Gratuito para pesquisa/não-comercial. Comercial precisa de licença separada.

### Quantizações disponíveis (rodrigomt/s2-pro-gguf)

| Arquivo | Tamanho | RAM necessária |
|---------|---------|---------------|
| `s2-pro-q8_0.gguf` | 5.3 GB | 8+ GB |
| `s2-pro-q6_k.gguf` | 4.3 GB | 6-8 GB |
| `s2-pro-q5_k_m.gguf` | 3.8 GB | 4-6 GB |
| `s2-pro-q4_k_m.gguf` | 3.4 GB | 3-4 GB |
| `s2-pro-q3_k.gguf` | 2.9 GB | <3 GB |
| `s2-pro-q2_k.gguf` | 2.6 GB | <3 GB (qualidade degradada) |

### Engine s2.cpp

- Repo: https://github.com/rodrigomatta/s2.cpp
- GGML/C++17, compila em ARM64, suporta CPU/Vulkan/CUDA/Metal
- Sem Python runtime (binário único)
- CLI: `./s2 -m model.gguf -t tokenizer.json --text "..." -o output.wav`
- Suporte a voice cloning: `--prompt-audio ref.wav --prompt-text "transcrição"`
- Suporte a perfis de voz persistentes (`.s2voice`)
- Estado: ALPHA experimental

## OmniVoice — Atributos de Voz (Voice Design)

Atributos suportados (passar como `voice` no TTS ou `instruct` no endpoint `/v1/audio/design`):

- **Gênero:** `female`, `male` (sem `neutral`)
- **Idade:** `child`, `teenager`, `young adult`, `middle-aged`, `elderly`
- **Pitch:** `very low pitch`, `low pitch`, `moderate pitch`, `high pitch`, `very high pitch`
- **Sotaques EN:** `american accent`, `british accent`, `australian accent`, `canadian accent`, `indian accent`, `japanese accent`, `korean accent`, `russian accent`, `portuguese accent`
- **Estilo:** `whisper`

**Não suporta:** `neutral` (gênero), atributos abstratos (confiança, ironia, entusiasmo). A atitude teria que vir da entrega, não do timbre.
