# GPU Acceleration Options for TTS Inference

Research compiled June 2026. All data from official docs and benchmarks.

## Option 1: Hugging Face ZeroGPU (Free)

- **GPU:** A100 80GB (time-sliced, shared)
- **Free tier:** ~3-5 min/day of GPU time
- **Pro tier:** $9/mo → ~25-40 min/day (H200)
- **Setup:** Create a Space with Docker, add `@spaces.GPU` decorator
- **Cold start:** <5s (model in CPU RAM, moved to GPU on call)
- **Sleep:** 48h idle (free), customizable (pro)
- **Endpoint:** `*.hf.space` public URL
- **No credit card required** for free tier
- **Limitation:** Quota resets daily, bursty access only

### Quota math (free tier, 5 min/day):
- 10s audio on A100: ~1.5-2s GPU → ~150 req/day
- 30s audio: ~5s GPU → ~60 req/day
- 60s audio: ~10s GPU → ~30 req/day

### Setup pattern:
```python
import spaces

model = load_model()  # loaded on CPU RAM

@spaces.GPU(duration=30)
def generate(text, instruct):
    model.to("cuda")
    result = model.generate(...)
    model.to("cpu")
    return result
```

## Option 2: Google Cloud TTS / Gemini TTS

- **Gemini API is excluded** from the $300 GCP free trial (since March 2026)
- **Standard Cloud TTS (Chirp3 HD, WaveNet)** IS covered by $300 credits

### Gemini TTS pricing:
| Model | Input | Output |
|-------|-------|--------|
| Gemini 2.5 Flash TTS | $0.50/1M tokens | $10.00/1M tokens |
| Gemini 3.1 Flash TTS (preview) | $1.00/1M tokens | $20.00/1M tokens |

- 10s audio ≈ 250 output tokens → $0.0025 ($2.Flash)
- **Auth:** Requires OAuth2 (service account), NOT API key
- Google Cloud TTS API does NOT accept API keys (returns 401)
- Has voice steering via `prompt` parameter

### Standard Cloud TTS (no steering):
| Model | Free/month | Overage |
|-------|-----------|---------|
| Chirp 3 HD | 1M chars | $30/1M chars |
| WaveNet | 4M chars | $4/1M chars |
| Neural2 | 1M chars | $16/1M chars |

### Auth setup:
```bash
# Create service account in GCP Console
# Download JSON key
export GOOGLE_APPLICATION_CREDENTIALS="service-account.json"
```

## Option 3: Hugging Face Inference Endpoint (Paid)

- Dedicated GPU (T4, L4, A10G, A100)
- Scale-to-zero (no cost when paused)
- **T4 pricing:** $0.50/hr
- Typical monthly cost for bursty use: $20-40/month
- 5-minute setup via HF Console
- OpenAI-compatible endpoint available
- Accepts web requests from anywhere

## Option 4: RunPod / Vast.ai (Cheapest raw GPU)

- Spot instances from $0.20/hr (T4, RTX 3090)
- No auto-pause (pay even when idle)
- More setup work (Docker templates)
- Best for sustained heavy use

## Quick Decision Matrix

| Workload | Best Option | Cost |
|----------|-------------|------|
| Sporadic (<50 req/day) | HF ZeroGPU free | $0 |
| Moderate (50-500 req/day) | HF ZeroGPU Pro ($9/mo) | $9/mo |
| Regular (500+ req/day) | HF Endpoint T4 | ~$25-40/mo |
| Heavy batch processing | RunPod spot | ~$0.20/hr |
| No infra to manage | Gemini TTS (prepaid $10) | $0.0025/req |

## Performance Reference (Qwen3-TTS 1.7B)

| Hardware | RTF | 10s audio |
|----------|-----|-----------|
| A100 80GB (HF ZeroGPU) | ~0.15-0.20 | ~1.5-2s |
| RTX 4090 24GB | ~0.65-0.85 | ~6.5-8.5s |
| T4 16GB (HF Endpoint) | ~1.8-2.2 | ~18-22s |
| AMD Ryzen 9 7950X (CPU) | ~9.8-12.5 | ~98-125s |
| Oracle ARM64 4-core (CPU) | ~14.8 | ~2.5 min |
| Apple M3 Max (MPS) | ~2.5-3.5 | ~25-35s |

Sources:
- https://tinycomputers.io/posts/the-real-cost-of-running-qwen-tts-locally-three-machines-compared.html
- https://qwen3-tts.app/blog/qwen3-tts-performance-benchmarks-hardware-guide-2026
- https://toolfreebie.com/hugging-face-spaces-free-gpu/
- https://cloud.google.com/text-to-speech/pricing
- https://ai.google.dev/gemini-api/docs/billing
