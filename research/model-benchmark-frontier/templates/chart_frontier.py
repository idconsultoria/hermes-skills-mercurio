#!/usr/bin/env python3
"""
Template: Intelligence × Parameters frontier chart generator.
Adapt the CURATED dataset below and run with:
    python3 -m venv venvs/chart && venvs/chart/bin/pip install matplotlib scipy
    venvs/chart/bin/python3 chart_frontier.py
"""

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ── Dataset: (name, params_B, score, estimated_params, open_weights) ────
CURATED = [
    # Add models here in format: (name, params_billions, score, is_estimated, is_open_weights)
    # Example: ("Qwen3.5-9B", 9, 32, False, True)
]

# ── Separate confirmed vs estimated ──
confirmed = [(n, p, s, o) for n, p, s, e, o in CURATED if not e]
estimated = [(n, p, s, o) for n, p, s, e, o in CURATED if e]

# ── Build frontier ──
param_max = {}
for n, p, s, e, o in CURATED:
    key = round(p, 1)  # dedup by param value
    if key not in param_max or s > param_max[key][0]:
        param_max[key] = (s, n)

frontier = []
for p in sorted(param_max.keys()):
    s, n = param_max[p]
    if not frontier or s > frontier[-1][1]:
        frontier.append((p, s))

# ── Plot ──
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(16, 10), facecolor='#0D1117')
ax.set_facecolor('#0D1117')
ax.grid(True, which='major', color='#1E2D3D', linewidth=0.8, alpha=0.6)

# Frontier line
ax.plot([p for p, s in frontier], [s for p, s in frontier],
        color='#E8B830', linewidth=2.5, alpha=0.9, zorder=5)
ax.fill_between([p for p, s in frontier], 0, [s for p, s in frontier],
                color='#E8B830', alpha=0.05, zorder=1)

# Data points
for c_conf in [(n, p, s) for n, p, s, o in confirmed if o]:
    ax.scatter(c_conf[1], c_conf[2], marker='o', s=80, color='#00D4AA',
               edgecolors='#00FFC8', linewidth=0.8, alpha=0.9, zorder=6)
for c_est in [(n, p, s) for n, p, s, o in estimated if o]:
    ax.scatter(c_est[1], c_est[2], marker='s', s=70, color='#00D4AA',
               edgecolors='#00FFC8', linewidth=0.8, alpha=0.5, zorder=6)
for c_cls in [(n, p, s) for n, p, s, o in confirmed if not o]:
    ax.scatter(c_cls[1], c_cls[2], marker='o', s=80, color='#4B9EFF',
               edgecolors='#7BB8FF', linewidth=0.8, alpha=0.9, zorder=6)
for c_cle in [(n, p, s) for n, p, s, o in estimated if not o]:
    ax.scatter(c_cle[1], c_cle[2], marker='s', s=70, color='#4B9EFF',
               edgecolors='#7BB8FF', linewidth=0.8, alpha=0.5, zorder=6)

# Axes
ax.set_xscale('log')
ax.set_xlim(0.1, 12000)
ax.set_ylim(0, 72)
ax.set_xlabel('Parametros Totais (escala log)', color='#CCCCCC', fontsize=13)
ax.set_ylabel('Artificial Analysis Intelligence Index', color='#CCCCCC', fontsize=13)
ax.set_title('Inteligencia × Parametros — Fronteira dos LLMs', color='#FFFFFF',
             fontsize=16, fontweight='bold', pad=20)
ax.tick_params(axis='both', colors='#8B949E', labelsize=9)

fig.savefig('/tmp/intelligence_vs_params_frontier.png', dpi=200,
            bbox_inches='tight', facecolor='#0D1117')
plt.close(fig)
print("Chart saved to /tmp/intelligence_vs_params_frontier.png")
