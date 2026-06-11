# VRAM × Quantização — Tabela de Referência

Fonte: insiderllm.com, knightli.com, llmconfigurator.com

## Modelos Populares (Q4_K_M)

| Modelo | Params total | FP16 | Q8 | Q4_K_M | Q3_K_M | Q2_K |
|--------|-------------|------|----|--------|--------|------|
| Qwen3.5-9B | 9B | 18 GB | 9 GB | 5 GB | 4 GB | 3 GB |
| Qwen3.6 27B | 27B | 54 GB | 27 GB | 17 GB | 13 GB | 9 GB |
| Qwen3.5 35B-A3B* | 35B | 70 GB | 35 GB | 20 GB | 15 GB | 11 GB |
| Gemma 4 31B | 31B | 62 GB | 31 GB | 22 GB | 16 GB | 10 GB |
| Mistral Small 4 | 24B | 48 GB | 24 GB | 14 GB | 10 GB | 8 GB |
| Llama 3.3 70B | 70B | 140 GB | 70 GB | 40 GB | 30 GB | 23 GB |
| Llama 4 Scout* | 109B (17B act) | 218 GB | 109 GB | 55 GB | 43 GB | 36 GB |
| Qwen3.5 122B A10B* | 122B (10B act) | 244 GB | 122 GB | 70 GB | 53 GB | 40 GB |
| DeepSeek V4 Flash* | 284B (13B act) | 160 GB | — | 80 GB | 60 GB | 40 GB |
| DeepSeek V4 Pro* | 1.6T (49B act) | 865 GB | — | 432 GB | 324 GB | 216 GB |

*MoE — parâmetros ativos entre parênteses

## GPUs × Modelos Máximos (Q4_K_M)

| GPU | VRAM | Máximo modelo dense | Máximo modelo MoE (+offload) |
|-----|------|--------------------|------------------------------|
| RTX 4060 Ti | 16 GB | Mistral Small 4 (14 GB) | Qwen3.5 35B-A3B (--cpu-moe) |
| RTX 3090 | 24 GB | Qwen3.6 27B (17 GB) | DeepSeek V4 Flash Q3 (--cpu-moe) |
| RTX 4090 | 24 GB | Qwen3.6 27B (17 GB) | DeepSeek V4 Flash Q3 (--cpu-moe) |
| RTX 5090 | 32 GB | Qwen3.6 27B c/ contexto grande | DeepSeek V4 Flash Q4 (--cpu-moe) |
| 2× RTX 3090 | 48 GB | Llama 3.3 70B Q4 (40 GB) | DeepSeek V4 Flash Q3 nativo (60 GB c/ tensor parallel) |
| 3× RTX 3090 | 72 GB | Qwen 122B Q4* | DeepSeek V4 Flash Q4 c/ offload parcial |
| 4× RTX 4090 | 96 GB | Qwen 122B Q8 (offload) | DeepSeek V4 Flash Q4 nativo |

*Com tensor parallelism (precisa de NVLink ou PCIe)

## Fórmulas

```python
vram_gb = params_b * bits / 8 + kv_cache_gb
kv_cache_gb = layers * ctx_len * 2 * dtype_bytes * batch / 1e9
# Ex: 32 layers, 32K ctx, FP16: ~3.2 GB

# Quantização GGUF bits aproximados:
Q2_K = 2.6 | Q3_K_M = 3.5 | Q4_K_M = 4.5 | Q5_K_M = 5.3 | Q6_K = 6.6 | Q8_0 = 8.0
```
