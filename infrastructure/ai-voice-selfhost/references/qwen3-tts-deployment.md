# Qwen3-TTS 1.7B Deployment (Jun/2026)

Deploy realizado em 09/Jun/2026 no Oracle Ampere ARM64.

## Estrutura

```
/home/ubuntu/selfhost/qwen3-tts/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── main.py          # FastAPI + Qwen3TTSModel
```

Bridge script: `/opt/data/.hermes/scripts/qwen3-tts.py`
Config: `tts.providers.qwen3` em `/opt/data/config.yaml`

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    torch==2.5.1 torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    qwen-tts fastapi "uvicorn[standard]" python-multipart

COPY main.py .
EXPOSE 8881
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8881"]
```

## docker-compose.yml

```yaml
name: qwen3-tts
services:
  qwen3-api:
    build: .
    ports:
      - "8881:8881"
    volumes:
      - qwen3_models:/app/models
    environment:
      - DEVICE=cpu
      - MODEL_ID=Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign
      - HF_HOME=/app/models
    restart: unless-stopped
    networks:
      - ai_mesh
networks:
  ai_mesh:
    external: true
volumes:
  qwen3_models:
```

## main.py (endpoints)

- `GET /health` — `{"status":"ok","model_loaded":true,"device":"cpu","model_id":"Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"}`
- `POST /v1/audio/speech` — OpenAI-compatible TTS with audio/wav response
- `GET /docs` — Swagger UI

Schema do `/v1/audio/speech`:
```json
{
  "input": "texto para sintetizar",
  "voice": "descrição da voz em linguagem natural",
  "language_id": "pt"
}
```

## Voice descriptions que funcionam (PT-BR)

| Descrição | Resultado |
|-----------|-----------|
| `"Voz masculina, tom neutro, sotaque português brasileiro"` | ✅ Timbre aceitável, sotaque BR leve |
| `"Voz masculina, tom grave-médio, confiante e levemente irônico, sotaque português brasileiro neutro, dicção limpa"` | ✅ Tom desejado (Hermes SOUL.md) |

**Sempre incluir "sotaque português brasileiro"** — sem isso o modelo assume mandarim/inglês com sotaque chinês.

## Performance (CPU ARM64, 4 vCPUs)

| Áudio gerado | Tempo real | RTF | Notas |
|-------------|-----------|-----|-------|
| 0.64s | 10.5s | 16.4 | Warm, primeira req rápida |
| 1.0s | 15.3s | 15.3 | Warm |
| 4.96s | 2min 18s | 27.8 | Primeira req após restart (mais lenta) |
| 6.9s | 103s | 15.0 | Warm |
| 14.2s | 208s | 14.6 | Warm |

## Problemas conhecidos

### Worker único bloqueante
Uvicorn roda com 1 worker. Enquanto gera áudio, TODAS as outras requests (health, docs, novas sínteses) ficam enfileiradas. Se o cliente desconectar (curl timeout, Ctrl+C), o worker continua processando e nunca mais responde.

**Solução:** `docker compose restart qwen3-api` — modelo recarrega em ~5s do cache.

### Sotaque chinês no português
O modelo Qwen3-TTS foi treinado primariamente em chinês e inglês. Para português sem sotaque chinês, a descrição da voz precisa incluir explicitamente "sotaque português brasileiro neutro".

### Conexão pelo gateway IP
O bridge script original usava `http://172.19.0.1:8881/`. Esse IP (gateway Docker) é flaky — o servidor às vezes fica inalcançável de dentro do container Hermes mesmo com o container rodando. Solução: adicionar o container à rede `ai_mesh` e usar `http://qwen3-api:8881/` (DNS do Docker).
