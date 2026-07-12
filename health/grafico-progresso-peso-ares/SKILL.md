---
name: grafico-progresso-peso-ares
category: health
description: "Gráfico de progresso de peso estilo Ares — matplotlib, vermelhos, claro.

Carregue esta skill quando precisar gerar o gráfico padrão de progresso de peso do Projeto Ares. Renderiza PNG via matplotlib com paleta cardinal/crimson sobre fundo off-white, proporção 10×5.5, linha de tendência, linha de meta e eixo Y a partir de 70 kg. Usa venv dedicado em /opt/data/.venv-chart/."
type: Health
timestamp: 2026-07-12T00:00:00Z
---

# Gráfico Padrão de Progresso em Peso Corporal (Ares)

Renderiza um gráfico PNG via matplotlib com a identidade visual Ares (vermelhos sobre fundo claro).

## Localização

Script executável via `/opt/data/.venv-chart/bin/python3` (venv com matplotlib).
Output: `/opt/data/projeto-ares/progresso_peso.png` → entregar via `MEDIA:`.

## Paleta de Cores (Ares Light)

| Token | Hex | Uso |
|-------|-----|-----|
| bg_color | `#FAF6F3` | Fundo off-white quente |
| card_bg | `#FFFFFF` | Cards, boxes, legenda |
| line_color | `#C41E3A` | Cardinal red — linha principal |
| line_glow | `#E63950` | Bright red — marcadores |
| target_color | `#CC4444` | Vermelho médio — linha de meta |
| target_fill | `#FFE0E0` | Rosa claro — zona alvo |
| grid_color | `#E8D8D4` | Grid quente claro |
| text_color | `#3D1C1A` | Marrom escuro — texto |
| muted_color | `#A08080` | Rose acinzentado — dados secundários |
| marker_edge | `#8B1A2B` | Bordô — borda dos marcadores |
| trend_color | `#B8543A` | Terracota — linha de tendência |

## Configuração do Gráfico

| Parâmetro | Valor |
|-----------|-------|
| Tamanho | 10" × 5.5" (landscape) |
| DPI | 150 |
| Eixo Y | Inicia em 70 kg (limite inferior 69.5) |
| Grid | Mutor a cada 0.5 kg |
| Data | Formato `dd/Mon` (ex: 15/Jun) |
| Fonte | Monospace (padrão matplotlib) |
| Estilo geral | Light mode, sem spines, legendas sutis |

## Elementos Obrigatórios

1. **Linha principal** — `plt.plot` com marker `'o'`, linewidth 2.5, markersize 8, cor `line_color`, borda `marker_edge`
2. **Área preenchida** — `fill_between` entre a curva e 69.5, alpha 0.06
3. **Rótulos de dados** — `annotate` com offset alternado (14 / -18) dependendo se o peso está acima ou abaixo de 78.5
4. **Linha de tendência** — regressão linear (numpy polyfit grau 1), plotada como `linestyle=':'` (pontilhada), alpha 0.7
5. **Linha de meta horizontal** — `axhline` em 73.8 kg, tracejada (`--`), alpha 0.6, com label e annotation
6. **Zona alvo** — `axhspan` entre 69.5 e 73.8, alpha 0.04
7. **Linha de peso inicial** — `axhline` em 79.3 kg, pontilhada fina (`:`), alpha 0.25
8. **Stats box** — canto superior direito (fora do eixo, `transform=ax.transAxes, x=1.02`): Atual, Total, Restam, Ritmo (kg/sem), Projeção (semanas)
9. **Footer** — abaixo do eixo X: "Pesos em jejum · data_inicial a data_final"

## Estrutura do Script

```python
#!/opt/data/.venv-chart/bin/python3
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
import numpy as np
from datetime import datetime

# Dados (hardcoded do CSV, sobrescrever a cada execução)
dates_str = [...]
pesos = [...]

# Paleta Ares Light (tabela acima)

# Config matplotlib rcParams
plt.rcParams.update({
    'font.family': 'monospace',
    'text.color': text_color, 'axes.labelcolor': text_color,
    'xtick.color': muted_color, 'ytick.color': muted_color,
    'figure.facecolor': bg_color, 'axes.facecolor': bg_color,
    'savefig.facecolor': bg_color,
})

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)

# 1. Trendline
x_num = mdates.date2num(dates)
z = np.polyfit(x_num, pesos, 1); p = np.poly1d(z)
x_smooth = np.linspace(x_num[0], x_num[-1], 100)
ax.plot(mdates.num2date(x_smooth), p(x_smooth),
        color=trend_color, linewidth=1.2, linestyle=':', alpha=0.7, zorder=3, label='Tendência')

# 2. Area fill
ax.fill_between(dates, pesos, 69.5, alpha=0.06, color=line_color)

# 3. Main line
ax.plot(dates, pesos, color=line_color, linewidth=2.5, marker='o',
        markersize=8, markerfacecolor=line_glow, markeredgecolor=marker_edge,
        markeredgewidth=1.5, zorder=5, label='Peso (kg)')

# 4. Data labels
for i, (d, p) in enumerate(zip(dates, pesos)):
    offset = 14 if p < 78.5 else -18
    ax.annotate(f'{p:.1f}', (d, p), textcoords='offset points',
                xytext=(0, offset), ha='center', fontsize=8,
                color=text_color, fontweight='bold')

# 5. Target line
target = 73.8
ax.axhline(y=target, color=target_color, linewidth=1.5, linestyle='--',
           alpha=0.6, zorder=3, label=f'Meta: {target} kg')
ax.axhspan(69.5, target, alpha=0.04, color=target_color, zorder=1)
ax.annotate(f'  {target} kg (14% BF)', xy=(dates[-1], target),
            xytext=(6, -2), textcoords='offset points', fontsize=8,
            color=target_color, fontweight='bold', ha='left', va='top', alpha=0.8)

# 6. Initial weight
initial = 79.3
ax.axhline(y=initial, color=muted_color, linewidth=0.8, linestyle=':', alpha=0.25, zorder=2)

# 7. Axis config
ax.set_ylim(69.5, max(pesos) + 0.8)
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.set_ylabel('Peso (kg)', fontsize=9, labelpad=8, color=line_color)
ax.set_axisbelow(True)
ax.grid(True, color=grid_color, alpha=0.6, linewidth=0.5)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
for spine in ax.spines.values():
    spine.set_visible(False)

# 8. Title
ax.text(0.0, 1.12, 'PROJETO ARES', transform=ax.transAxes,
        fontsize=18, fontweight='bold', color=line_color)
ax.text(0.0, 1.04, 'Progresso de Peso Corporal',
        transform=ax.transAxes, fontsize=11, color=muted_color)

# 9. Stats box
last_peso = pesos[-1]
total_loss = initial - last_peso
remaining = last_peso - target
day_count = (dates[-1] - dates[0]).days
rate = total_loss / day_count * 7
projected_weeks = remaining / rate if rate > 0 else 0
stats_text = (
    f'Atual:  {last_peso:.1f} kg\n'
    f'Total:  -{total_loss:.1f} kg\n'
    f'Restam: {remaining:.1f} kg\n'
    f'Ritmo:  -{rate:.2f} kg/sem\n'
    f'Proj.:  ~{projected_weeks:.0f} sem'
)
ax.text(1.02, 0.97, stats_text, transform=ax.transAxes, fontsize=8.5,
        verticalalignment='top', color=text_color, linespacing=1.7,
        bbox=dict(boxstyle='round,pad=0.5', facecolor=card_bg,
                 edgecolor=grid_color, alpha=0.9))

# 10. Legend
legend = ax.legend(loc='lower left', fontsize=7.5, framealpha=0.7,
                   facecolor=card_bg, edgecolor=grid_color, ncols=2)
for text in legend.get_texts(): text.set_color(text_color)

# 11. Footer
ax.text(0.0, -0.14, f'Pesos em jejum · {dates_str[0]} a {dates_str[-1]}',
        transform=ax.transAxes, fontsize=7, color=muted_color, alpha=0.6)

plt.tight_layout()
plt.savefig('/opt/data/projeto-ares/progresso_peso.png', dpi=150,
            bbox_inches='tight', facecolor=bg_color, edgecolor='none')
plt.close()
```

## Como usar

1. Atualizar `dates_str` e `pesos` com os dados do `peso.csv`
2. Executar com: `/opt/data/.venv-chart/bin/python3 /caminho/do/script.py`
3. Entregar a imagem: `MEDIA:/opt/data/projeto-ares/progresso_peso.png`

## Pitfalls

- ⚠️ Sempre usar `/opt/data/.venv-chart/bin/python3` — o sistema Python (`/usr/bin/python3`) não tem matplotlib instalado
- ⚠️ `dates_str` deve manter formato `YYYY-MM-DD`
- ⚠️ O stats box posiciona-se fora do eixo (`x=1.02`) — se a figura encolher demais, pode cortar; testar antes
