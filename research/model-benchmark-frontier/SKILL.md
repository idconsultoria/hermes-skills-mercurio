---
name: model-benchmark-frontier
category: research
description: Comparação de modelos de IA — inteligência vs parâmetros, fronteira convex hull, análise de hardware local para inferência. Pesquisa multi-fonte, compilação de dataset, geração de gráfico de fronteira + tabelas .md.
triggers:
  - "Gráfico de inteligência vs parâmetros"
  - "Qual modelo é melhor para meu hardware"
  - "Fronteira de capacidade de LLMs"
  - "Análise custo-benefício de setups de inferência local"
  - "Comparar modelos abertos vs fechados"
---

# Model Benchmark Frontier — Pesquisa e Visualização

Skill para pesquisar benchmarks de modelos de IA, compilar datasets multi-fonte,
gerar gráficos de fronteira (inteligência × parâmetros) e analisar capacidade
de hardware local para inferência.

## Gatilhos

Use esta skill quando o usuário pedir:
- Gráficos de inteligência vs parâmetros (scatter + convex hull frontier)
- Comparação de modelos abertos vs fechados
- Qual o melhor modelo para um hardware específico
- Análise de custo-benefício de setups de inferência
- Tabelas comparativas de modelos com fontes

## Workflow: Coleta de Dados

### 1. Identificar fonte de benchmark

**Artificial Analysis Intelligence Index** (recomendado — Jun 2026):
- Leaderboard ao vivo: https://artificialanalysis.ai/leaderboards/models
- Scores de 0-65 para 380+ modelos
- O site é SPA com tabela — use browser_console para extrair dados JS
  ```javascript
  const t = document.querySelector('table');
  const r = t.querySelectorAll('tbody tr, tr');
  const d = [];
  r.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 4) {
      d.push({
        name: cells[0].textContent.trim(),
        score: parseInt(cells[3].textContent.trim())
      });
    }
  });
  ```
- BenchLM (https://benchlm.ai/benchmarks/artificialAnalysis) tem a tabela em markdown com 128 modelos

### 2. Coletar dados de parâmetros

**llm-evolution.com** (244 modelos catalogados):
- SPA interativa — usar browser_console para extrair dados
  ```javascript
  const tables = document.querySelectorAll('table');
  const models = [];
  tables.forEach(table => {
    const rows = table.querySelectorAll('tbody tr, tr');
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 2) {
        const model = cells[0].textContent.trim();
        const params = cells[1].textContent.trim();
        if (model && params && params !== 'Undisclosed') {
          models.push({model, params});
        }
      }
    });
  });
  ```
- Clique nos headers das famílias para expandir antes de extrair

**Fontes de parâmetros para modelos fechados:**
- Musk leak: Claude Opus ≈ 5T, Claude Sonnet ≈ 1T
- Benchmarks de banda (ex: artigo Estimating Size of Claude Opus)
- Especulação de mercado
- Sempre marcar como "(est.)" no gráfico

**Fontes oficiais para modelos abertos:**
- DeepSeek, Qwen, Llama, Gemma, Mistral — specs oficiais
- NVIDIA NIM model cards para Kimi K2.6, MiMo-V2.5-Pro

### 3. Cruzar dados

Model names diferem entre AA leaderboard e llm-evolution. Ex:
- "DeepSeek V4 Pro (Max)" no AA → "DeepSeek V4 Pro" no llm-evolution
- "Claude Opus 4.8 (max)" no AA → precisa de estimativa de parâmetros

Usar matching por substring do nome do modelo, não match exato.

## Workflow: Geração do Gráfico

### Setup
```bash
python3 -m venv venvs/chart
venvs/chart/bin/pip install matplotlib scipy numpy
```

### Convex Hull Frontier

O gráfico deve mostrar:
- X: parâmetros totais (escala log)
- Y: score de inteligência (0-65)
- Pontos: círculo (confirmado) / quadrado (estimado)
- Cores: verde (#00D4AA) para open weights, azul (#4B9EFF) para fechados
- Linha: fronteira dourada (#E8B830) do envelope convexo superior
- Labels para modelos notáveis com setas

### Algoritmo da fronteira

```python
# Para cada valor de parâmetro, manter só o score máximo
param_max = {}
for p, s, n in unique.values():
    if p not in param_max or s > param_max[p][0]:
        param_max[p] = (s, n)

# Construir fronteira: sempre subindo
frontier = []
for p in sorted(param_max.keys()):
    s, n = param_max[p]
    if not frontier or s > frontier[-1][1]:
        frontier.append((p, s))
```

### Pitfalls conhecidos

1. **Emojis no matplotlib**: DejaVu Sans não tem glyphs 💡⚠️ — substituir por texto ASCII ou instalar fontes
2. **Label overlap**: na região densa (500B-2T), labels colidem — usar offsets manuais no dict
3. **MoE total vs active**: deixar claro que usa parâmetros TOTAIS (não active), não confundir leitor
4. **Modelos sem parâmetros**: GPT-5.5, Claude, Gemini são "Undisclosed" — documentar fonte da estimativa
5. **Fontes**: matplotlib sem fontes Hermes/Inter — usar fonte monospace para annotations, sans-serif para labels
6. **Legenda**: separar 4 categorias (open confirmed, open estimated, closed confirmed, closed estimated)

## Workflow: Análise de Hardware

Para perguntas de "qual modelo roda em qual GPU":

### Cálculo de VRAM

```python
# Fórmula base
vram_gb = (params_billions * bits_per_param) / 8

# Quantizações comuns (GGUF):
# Q2_K:    2.6 bits
# Q3_K_M:  3.5 bits  
# Q4_K_M:  4.5 bits
# Q5_K_M:  5.5 bits
# Q6_K:    6.6 bits
# Q8_0:    8.0 bits
# FP16:    16.0 bits
```

### MoE Offload (--cpu-moe)

Para modelos MoE grandes:
- GPU precisa só dos parâmetros ATIVOS + shared layers
- Routed experts ficam na RAM do sistema
- Comando: `llama-cli --cpu-moe -m model.gguf`
- Fork do antirez: https://github.com/antirez/llama.cpp-deepseek-v4-flash
- GGUF pré-quantizados: huggingface.co/antirez/deepseek-v4-gguf

### VRAM por modelo (DeepSeek V4 Flash, 284B/13B active)

| Quant | Total | GPU (active) | RAM (experts) |
|-------|-------|-------------|---------------|
| IQ2   | 40 GB | 4 GB        | 36 GB         |
| Q3    | 60 GB | 5 GB        | 55 GB         |
| Q4    | 80 GB | 7 GB        | 73 GB         |

### Tabela de setups

| Setup | Custo | Melhor modelo local | Performance |
|-------|-------|--------------------|-------------|
| RTX 3060 12GB + 64GB RAM | ~$500 | DS V4 Flash IQ2 (12-18 tok/s) |
| RTX 3090 24GB + 128GB RAM | ~$1K | DS V4 Flash Q4 (10-15 tok/s) |
| RTX 5090 32GB + 192GB RAM | ~$2.5K | DS V4 Flash Q4 (18-25 tok/s) |
| 2× RTX 5090 + 256GB RAM | ~$5K+ | DS V4 Flash nativo + Qwen 397B |

## Formato de Entrega

1. **Gráfico**: PNG dark theme, 16:10, 200dpi
2. **Tabela .md**: dados da fronteira + dataset completo + notas metodológicas
3. **Hardware guide**: .md com tabelas de setups, VRAM, comparação com SOTA cloud
4. **Fontes sempre citadas**: AA Intelligence Index, llm-evolution, specs oficiais

## Referências

- scripts/generate_chart.py — script gerador do gráfico de fronteira (reutilizável)
- references/vram_by_model.md — tabela VRAM × quantização para modelos populares
