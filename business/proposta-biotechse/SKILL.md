---
name: proposta-biotechse
description: "Propostas comerciais da BiotechSe — HTML v5 + minuta."

Carregue esta skill quando for elaborar proposta comercial da BiotechSe (biotecnologia agroindustrial) do contexto do cliente ao HTML com identidade v5 + minuta. Adaptação da elaboracao-proposta-comercial para a marca BiotechSe."
version: 1.0.0
author: Mercúrio
license: MIT
metadata:
  hermes:
    tags: [proposta, biotechse, comercial, consultoria, biotecnologia, agro, html, minuta]
    related_skills: [brand-design-system-html, elaboracao-proposta-comercial, analise-contratual]
category: business
type: Orchestrator
timestamp: 2026-08-27T00:00:00Z
---

# Proposta Comercial — BiotechSe

Pipeline adaptado da `elaboracao-proposta-comercial` (ID) para a **BiotechSe**, usando a **identidade visual oficial v5** (liquid glass, paleta abyss teal + mint, Clash Display + Tomato Grotesk).

Entrega principal: **HTML modelo editável** que segue o design system v5 e consome os **assets vetoriais/raster** gerados do PNG principal (`biotechse-assets/logos/`). Opcional: minuta em Google Docs na subpasta Minutas.

## Quando usar
- Criar proposta comercial **da BiotechSe** (bioinsumos, biofábrica, P&D, consultoria agroindustrial) a partir de contexto do cliente (briefing, mensagens, atas, PDFs).
- Usuário pede proposta com a cara da BiotechSe (não da ID).

## Paleta e tipografia (v5)
- **Cores oficiais**: abyss teal `#029190` (primária), mint `#00ffa3` (primária), cream `#f7eadf`, charcoal `#2d2d2d`, off-white `#f2f1f0`. Derivados: teal-deep `#01706f`, mint-deep `#00c77f`.
- **Tipografia**: Clash Display 400/500 (títulos, Fontshare CDN) + Tomato Grotesk 400/500/800 (corpo, licenciada → self-host em `assets/fonts/`, proxy Hanken Grotesk até chegar).
- **Material**: liquid glass colorido e flutuante (gradiente teal→mint 12–16%, 3 orbs, borda superior clara + brilho interno) + Solar Icons Linear 1.5px arredondado.
- **WCAG**: charcoal sobre cream ≈11:1 (AAA). Nunca usar teal puro como cor de texto corrido — use teal-deep.

## Assets oficiais
Todos em `assets/logos/` (copiados de `/opt/mercurio-data/deliverables/biotechse-assets/logos/`):
- `biotechse-logo-positivo.svg` — fundo claro (padrão para propostas, que são documento claro)
- `biotechse-logo-negativo.svg` — fundo escuro
- `biotechse-logo-principal.svg` — equivalente ao PNG enviado
- `biotechse-simbolo-*.svg` — símbolo isolado (capa, rodapé, favicon)
- Variantes raster `*.png` + monocromáticas para marca d'água.

**Regra de uso na proposta**: fundo das páginas é **claro** (`cream → off-white → #eef8f2`), então use sempre a variante **positivo** (B em teal, "se" em mint-deep). Negativo só em blocos escuros pontuais (ex.: faixa de prova social em charcoal).

## Pipeline

### Passo 0 — Coletar contexto (igual ID)
| Dado | Onde usar |
|---|---|
| {{CLIENTE_NOME}} | capa, resumo, final |
| {{CLIENTE_LOGO_URL}} | capa (lado a lado com BiotechSe positivo) |
| {{TITULO_PROPOSTA}} | capa |
| {{SUB_TITULO_PROPOSTA}} | capa |
| Escopo / entregáveis / exclusões | slides Escopo |
| Metodologia e fases | Metodologia |
| Valores, pacotes | Investimento (3 opções) |
| Condições de pagamento e validade | Condições |
| Cases relevantes | Quem já confiou (portfolio BiotechSe) |

### Passo 1 — Rascunho seção a seção (Guia de Princípios)
Seguir `references/guia-principios.md` (12 princípios): storytelling problema→solução→prova→preço; ROI antes do preço; 3 opções com médio recomendado; escopo com exclusões; validade 14–30 dias. **Uma coisa de cada vez — aguardar ok explícito.**

### Passo 2 — Editar o HTML como agente
```bash
mkdir -p /opt/data/work/proposta_<cliente>
cp skills/business/proposta-biotechse/templates/biotechse-proposta-modelo.html \
   /opt/data/work/proposta_<cliente>/Proposta_<cliente>_BiotechSe.html
```
- O template é **referência de marca/estrutura**, não retrato final — edite como agente, adapte narrativa, troque blocos conforme o cliente.
- Substitua `{{...}}` (mapa em `references/placeholders.md`).
- Mantenha identidade v5: orbs, `lg` (liquid glass), Clash/Tomato, cores por token CSS.
- Verifique no navegador: zero overflow, contraste, logos com respiro (área de proteção = altura do símbolo).

### Passo 3 — PDF (opcional)
```bash
node skills/business/elaboracao-proposta-comercial/scripts/render_pdf.mjs \
  /opt/data/work/proposta_<cliente>/Proposta_<cliente>_BiotechSe.html \
  /opt/data/work/proposta_<cliente>/Proposta_<cliente>_BiotechSe.pdf
```
Usar `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright` (ver skill original).

### Passo 4 — Minuta (opcional)
Copiar contrato-modelo para subpasta Minutas (ver `elaboracao-proposta-comercial/references/contratos-drive.md`), preservar capa/contracapa, espelhar valores da proposta.

### Passo 5 — Entregar
- HTML (artefato principal)
- PDF se solicitado
- Link da minuta se criada

## References
- `references/guia-principios.md` — 12 princípios (herdados da ID, com tom BiotechSe)
- `references/placeholders.md` — mapa de {{...}} do template
- `references/portfolio.md` — cases BiotechSe (a preencher com clientes reais da marca)
- `templates/biotechse-proposta-modelo.html` — modelo HTML v5 com liquid glass
- `assets/logos/` — variantes da marca (positivo/negativo/simbolo/mono)

## Pitfalls
1. Usar variante errada do logo (negativo em página clara → contraste quebrado).
2. Usar teal `#029190` como cor de texto corrido (~3.2:1) — use teal-deep.
3. Hotlink de Tomato Grotesk — self-host ou proxy Hanken, nunca site pirata.
4. Gerar proposta inteira sem validação incremental.
5. Inventar cases — usar portfolio real.
