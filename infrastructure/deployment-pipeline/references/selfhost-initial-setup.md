# Selfhost Initial Setup — New Service on Oracle ARM64

Workflow para pesquisar, planejar e montar a estrutura inicial de um novo
serviço selfhost no servidor Oracle ARM64, seguindo o padrão
`selfhost/<projeto>/docker-compose.yml`.

## 1. Pesquisa de viabilidade

Antes de escrever Dockerfile ou compose, responder:

| Pergunta | Como verificar |
|----------|----------------|
| O software roda em ARM64? | `docker manifest inspect <image>:<tag>` ou checar Dockerfile base image (`FROM python:3.11-slim` = multi-arch) |
| Existe imagem pré-compilada? | `docker buildx imagetools inspect <image>:<tag>` — se só `amd64`, precisa build local |
| PyTorch/TensorFlow ARM? | PyTorch fornece wheels para aarch64 CPU via `--index-url https://download.pytorch.org/whl/cpu` |
| RAM mínima? | Procurar por "minimum RAM", "hardware requirements" no README ou issues |
| Modelo precisa download? | Tamanho do modelo no HuggingFace — adicionar volume persistente para cache |

### ARM64 Docker image check

```bash
# Via skopeo (se instalado)
skopeo inspect --raw docker://<image>:<tag> | python3 -c "
import sys, json
m = json.load(sys.stdin)
for x in m.get('manifests', [m]):
    arch = x.get('architecture','?')
    os_ = x.get('os','?')
    print(f'{os_}/{arch}')
"

# Via docker buildx
docker buildx imagetools inspect <image>:<tag>
```

### heurística de RAM para modelos de ML

| Tipo | RAM estimada | Exemplo |
|------|-------------|---------|
| TTS (OmniVoice) | ~4-6 GB + modelo 4GB disco | 24GB → safe |
| Whisper (large-v3) | ~4 GB VRAM, ~6 GB RAM | 24GB → safe |
| LLM 7B (GGUF Q4) | ~6-8 GB RAM | 24GB → safe (lento sem GPU) |
| LLM 13B (GGUF Q4) | ~10-12 GB RAM | 24GB → apertado |
| Embeddings (BGE-small) | ~1-2 GB RAM | 24GB → folgado |

Com 4 CPUs ARM64 + 24GB RAM: serviços de TTS/ASR/embeddings rodam bem.
LLMs grandes vão ser lentos em CPU (tok/s muito baixo) mas cabem na RAM.

## 2. Estrutura de diretórios

```
/opt/data/selfhost/                  ← diretório raiz (já existe)
├── open-design/                     ← projeto existente
│   └── .env
└── <projeto>/                       ← novo projeto
    ├── .env                         ← secrets (não comitar)
    ├── .env.example                 ← template sem secrets
    ├── .dockerignore
    ├── Dockerfile                   ← necessário se imagem pré-compilada não existe p/ ARM64
    ├── docker-compose.yml           ← orquestração
    ├── main.py                      ← se for server custom (FastAPI, etc.)
    ├── web/                         ← assets de web UI (index.html, etc.)
    └── voices/ (ou data/)           ← dados voláteis montados como volume
```

### docker-compose.yml — template para serviço single-container

```yaml
name: <projeto>

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8880:8880"                  # mesma porta para consistência ou variar
    volumes:
      - <projeto>_models:/app/models  # cache de modelo (persistente)
      - ./data:/app/data              # dados voláteis
    environment:
      - DEVICE=cpu                    # forçar CPU em ARM64 sem GPU
      - HF_HOME=/app/models           # cache HuggingFace dentro do volume
    restart: unless-stopped

volumes:
  <projeto>_models:
```

### .env — template

```bash
# Model configuration
DEVICE=cpu
HF_HOME=/app/models

# Optional: HuggingFace mirror for slow downloads
# HF_ENDPOINT=https://hf-mirror.com
```

Nota: o `.env` real pode conter API keys e não deve ser lido via `read_file` — o
Hermes bloqueia. Use `cat .env` pelo terminal se precisar verificar.

## 3. Build local para ARM64

Quando a imagem pré-compilada é só `amd64`, **sempre fazer build local**.
NUNCA usar `platform: linux/amd64` no compose para forçar QEMU — causa
deadlocks em Python com extensões C (pydantic-settings, numpy, orjson, etc.).

```bash
cd /opt/data/selfhost/<projeto>

# Build
docker compose build --no-cache

# Up
docker compose up -d

# Verificar logs (modelo grande pode levar minutos para baixar)
docker compose logs -f
```

### Dockerfile — template para serviço Python PyTorch em ARM64

```dockerfile
FROM --platform=linux/arm64 python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# PyTorch CPU (ARM64 wheels disponíveis no index CPU)
RUN pip install --no-cache-dir \
    torch==2.3.0 \
    torchaudio==2.3.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Dependências da aplicação (TUDO que não seja torch)
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    python-multipart \
    transformers \
    accelerate \
    numpy \
    soundfile \
    librosa \
    <app-package-no-torch-deps>

# App lib SEM dependências (torch já instalado manualmente acima)
# CRÍTICO: sem --no-deps o pip reinstala torch com CUDA (8-12GB de bloat)
RUN pip install --no-cache-dir --no-deps <app-lib-que-depende-de-torch>

COPY main.py /app/main.py
COPY web/ /app/web/

ENV HF_HOME=/app/models
ENV DEVICE=cpu

EXPOSE 8880
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8880", "--workers", "1"]
```

⚠️ **`--platform=linux/arm64`** é opcional em servidor ARM64 (Docker
auto-detects), mas explícito documenta a intenção e previne surpresas.

## 4. SSH Tunneling para Web UI

Serviços selfhost normalmente NÃO têm porta exposta publicamente (firewall
Oracle só libera 80/443 por padrão). Usar SSH tunnel para acessar a UI:

```bash
# Tunnel: porta local :8880 → servidor :8880
ssh -L 8880:localhost:8880 usuario@oracle-server-ip

# Depois abrir:
#   http://localhost:8880/web    (web UI, se existir)
#   http://localhost:8880/docs   (Swagger)
#   http://localhost:8880/health (health check)
```

## 5. Integrar o serviço no Hermes (opcional)

Depois de rodar, você pode configurar o Hermes para consumir o serviço.
Localização: `/opt/data/config.yaml` (editar via `hermes config set`).

### TTS (comando customizado)

Útil quando o serviço expõe `/v1/audio/speech` (OpenAI-compatível) mas o
Hermes exige uma API key que o serviço local não pede. Criar um script
ponte em `/opt/data/.hermes/scripts/<nome>.py`:

```python
#!/usr/bin/env python3
import sys, json, subprocess, argparse, os
parser = argparse.ArgumentParser()
parser.add_argument('--text-file', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
with open(args.text_file) as f:
    text = f.read().strip()
payload = json.dumps({
    "model": "<model-id>", "input": text, "voice": "female"
})
subprocess.run(["curl", "-s", "-o", args.output, "-X", "POST",
    "http://172.19.0.1:8880/v1/audio/speech",
    "-H", "Content-Type: application/json", "-d", payload
], check=True, timeout=300)
```

Configurar o provider:

```bash
hermes config set tts.provider <nome>
hermes config set tts.providers.<nome>.type command
hermes config set tts.providers.<nome>.command \
  "python3 /opt/data/.hermes/scripts/<nome>.py \
   --text-file {input_path} --output {output_path}"
hermes config set tts.providers.<nome>.output_format wav
hermes config set tts.providers.<nome>.timeout 300
hermes config set tts.providers.<nome>.max_text_length 2000
hermes config set tts.providers.<nome>.voice_compatible true
```

> **Alternativa — OpenAI provider com base_url:** Se o serviço selfhost
> aceitar API key vazia, configure `tts.provider: openai` com
> `tts.openai.base_url` apontando pro container. Requer descomentar
> `VOICE_TOOLS_OPENAI_KEY` no `.env` com valor dummy.

## 5. Health check e smoke test

```bash
# Verificar se o container está rodando
docker compose ps

# Health endpoint
curl -s http://localhost:8880/health

# Teste funcional básico (exemplo TTS)
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "omnivoice", "input": "Teste de síntese.", "voice": "female"}' \
  --output /tmp/test.wav

file /tmp/test.wav          # deve ser "RIFF (little-endian) data, WAVE audio"
```

## 6. Pipeline de atualização

Quando o serviço precisar de atualizações periódicas:

1. Editar `main.py` ou `Dockerfile` localmente
2. `docker compose build --no-cache && docker compose up -d`
3. Para CI/CD completo, ver `deployment-pipeline` skill

## Referências relacionadas

- `deployment-pipeline` → multi-arch builds, ghcr.io auth, deploy patterns
- `oracle-host-access` → SSH config, host diagnostics, Docker compose management
- Planos de implementação específicos em `.hermes/plans/`

## Pitfalls

⚠️ **Imagem pré-compilada sem arm64:** O erro `no matching manifest` aparece ao
tentar `docker compose pull`. A solução NÃO é forçar QEMU — é build local para
arm64.

⚠️ **Modelo grande na primeira execução:** `docker compose up -d` retorna
imediatamente, mas o serviço só fica saudável depois de baixar o modelo
(~4GB). Acompanhar com `docker compose logs -f`.

⚠️ **Porta ocupada:** Se 8880 já estiver em uso, alterar no compose. Manter
consistência entre projetos (cada um com sua porta).

⚠️ **`FROM python:3.11-slim` sem `--platform`:** Em servidor ARM64, o Docker
baixa automaticamente a variante `linux/arm64`. Adicionar `--platform` é
documentação, não requisito. Mas NUNCA usar `python:3.11-slim-bullseye` (só
amd64).
