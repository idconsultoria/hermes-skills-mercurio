# Modelo v8 — referência consolidada (2026-09-09)

Arquivo vivo: `templates/biotechse-proposta-modelo-v8.html` (+ PDF homônimo em `/opt/mercurio-data/deliverables/`).
Aprovado pelo operador como referência da skill. Não editar o v8 — evoluir em `v9+`.

## Formato
- Slide deck 1920×1080, 11 slides, 1 slide = 1 página do PDF (`@page 1920×1080`, `page-break-after: always`).
- Material impresso primeiro: sem nav de tela, sem animação, sem sombras de interface, botões chapados, folio em todo slide.
- 15 placeholders (mapa em `placeholders.md`). `✓ • ×` são glifos tipográficos (ok em print); ZERO emoji.

## Slides
1. Capa (papel timbrado: logo livre, cliente, título, validade 21 dias, protocolo)
2. Resumo executivo (fundo escuro, preço ancorado em ROI)
3. Desafio (contexto + custo de não agir)
4. Diagnóstico (laboratório / biofábrica / campo)
5. Escopo (inclui × não inclui + responsabilidades do cliente)
6. Metodologia (timeline 4 fases)
7. Investimento (3 tiers, Recomendado em destaque)
8. Condições (tabela por marcos + regras)
9. Prova social (fundo escuro, cards neutros a preencher — NUNCA número inventado)
10. Sobre + próximos passos (manifesto + aceite)
11. Final (validade + assinaturas Contratante × Contratada)

## Marca aplicada (v5)
- Logos: arte oficial com fundo transparente, embutida em base64 — `positivo-transparente` no claro (capa, rodapés, sobre, final), `principal-transparente` no escuro (prova), `simbolo` nos 9 marcadores de seção (positivo no claro, negativo no escuro). Sem caixas, selos ou molduras.
- Ícones lineares próprios em linguagem Solar (traço 1.7, round caps, grid 24, `currentColor`).
- Paleta abyss teal `#029190` + mint `#00ffa3` + cream `#f7eadf` + charcoal `#2d2d2d` + off-white `#f2f1f0`; texto corrido em teal-deep `#01706f`.
- Clash Display 400/500 (Fontshare) + Tomato Grotesk self-host (`assets/fonts/`, proxy Hanken).

## Render PDF
```bash
CHROME=/opt/data/.playwright/chromium-1117/chrome-linux/chrome
$CHROME --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=out.pdf "file:///opt/data/work/proposta_<cliente>/Proposta_<cliente>_BiotechSe.html"
```
HTML com ~1MB de base64 leva ~85s; se travar, referenciar PNGs como arquivos externos.

## Histórico (resumo)
- v1: página rolável, logos reconstruídos, emojis.
- v2: slide deck 1920×1080, ainda com reconstruções e emojis.
- v3: ícones lineares, direção impressa, sem notas internas.
- v4: lockup genuíno do manual + notas expurgadas + métricas neutralizadas.
- v5: transparentes oficiais no lugar do fundo temático.
- v6: positiva transparente direta, sem selos.
- v7: logo da capa livre, sem caixa branca.
- v8: símbolo oficial no lugar dos 9 losangos. ← referência atual

## Pendências conhecidas
- Não existe positivo chapado no manual; antes de gráfica final, pedir vetor original ao Tácio.
- `references/portfolio.md` segue vazio — preencher com cases reais autorizados.
