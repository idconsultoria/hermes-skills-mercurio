# TTS Benchmarks — Oracle ARM64

> Extracted from ai-voice-selfhost SKILL.md — performance benchmarks for TTS models tested on Oracle ARM64 (4 CPU, 24GB RAM, 0 GPU).

## Models Tested Overview

| Model | RAM | RTF (ARM64 CPU) | 10s audio | Steering | Port |
|-------|-----|-----------------|-----------|----------|------|
| Gemini 3.1 Flash TTS (cloud API) | — | ~1x (cloud) | ~10s | ✅ 200+ tags + prompt | cloud |
| OmniVoice (k2-fsa) — DEPRECATED on ARM64 | ~7.3GB | ~111 | ~18 min | ❌ só presets | 8880 |
| Qwen3-TTS 1.7B VoiceDesign | ~8-10GB | 14-28 (measured) | 2.5-4.5 min | ✅ VoiceDesign instruct | 8881 |
| Fish Speech S2 Pro q8_0 (5B) | ~4.6GB | ~38 (mid-text) | ~6 min | ✅ ref áudio + inline tags | 8882 |
| Fish Speech S2 Pro q6_k (5B) | ~3.7GB | ~33 (mid-text) | ~5.5 min | ✅ ref áudio + inline tags | 8882 |
| Fish Speech S2 Pro q5_k_m (5B) | ~3.2GB | ~26 (mid-text) | ~4.3 min | ✅ ref áudio + inline tags | 8882 |

## Qwen3-TTS Measured Performance

**Date:** Jun/2026. Server cold → warm.

- 0.64s audio → 10.5s (RTF 16.4, warm)
- 1.0s audio → 15.3s (RTF 15.3, warm)
- 4.96s audio → 138s (RTF 27.8, first req after restart)
- 6.9s audio → 103s (RTF 15.0, warm)
- 14.2s audio → 208s (RTF 14.6, warm)

First request after container restart is always slower (model warmup). Subsequent requests stabilize at RTF 14-16.

## Fish Speech S2 Pro — GGUF Quantization Benchmarks

**Date:** Jun/2026. Oracle ARM64 4-core.
**Test phrase:** "Olá, me chamo Hermes. Sou inteligência de fronteira."

| Quant | File | RAM | RTF | Áudio gerado | Notas |
|-------|------|-----|-----|-------------|-------|
| `q8_0` | 5.3GB | ~4.6GB | ~38x | 3.34s / 126s | **Padrão em produção** |
| `q6_k` | 4.3GB | ~3.7GB | ~33x | 3.85s / 128s | Mais leve, ~13% mais rápido |
| `q5_k_m` | 3.8GB | ~3.2GB | ~26x | 4.60s / 118s | Mais rápido, ~32% menos RAM |

Sample rate: 44100 Hz, 32-bit float mono. s2.cpp binário: ~1.4MB, compilado nativamente.

**User preference:** q8_0 as production default (q5_k_m and q6_k removed by user decision). Other quants remain as testing options but are not maintained. Multi-quant architecture in server.py allows switching via `model` parameter without rebuild.

## Fish Speech S2 Pro — Voice Cloning Metrics

**q8_0, ref 15s, Oracle ARM64 4-core:**

| Fase | Tempo | Notas |
|------|-------|-------|
| Init + codec load | ~56s | Fixo por invocação |
| Reference encode | ~27-39s | Só na primeira vez ou sem `--save-voice` |
| Generate (1.5s áudio) | ~68s | Prefill + loop autoregressivo |
| **Total (~1.5s áudio)** | **~73-85s** | RTF ~48-57x |
| RAM | ~6.8GB max | Modelo 4.6GB + buffers |
