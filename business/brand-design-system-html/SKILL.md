---
name: brand-design-system-html
description: "Design system de marca de cliente em HTML.

Load this skill when you need to build a client's visual identity as an HTML design system — brand manual, color system, typography, and liquid glass."
version: 1.0.0
author: Mercúrio
category: business
type: Template
timestamp: 2026-09-01T12:00:00Z
tags: [html, design-system, branding, identidade-visual, marca, paleta, tipografia, liquid-glass]
trigger_phrases: ["design system", "design system oficial", "guia de identidade", "system da marca", "paleta oficial", "manual da marca", "tipografia da marca", "style guide cliente", "identidade visual do cliente", "liquid glass"]
---

# Brand Design System em HTML (identidade de marca de cliente)

Montar um design system / guia de identidade **de um cliente** (não da ID nem do Hermes)
entregue como página HTML navegável. Caso real de referência: **Biotechse** (biotech agroindustrial,
sócio Tácio) — ver `references/biotechse-brand.md` para os fatos exatos da marca.

## Quando ativar
- O usuário manda um **manual da marca** (PDF) e/ou imagem de **sistema de cores** e pede o
  "design system oficial".
- Pediu usar referências visuais de outro DS do cliente (ex.: "Aethereum do Artemis") e uma
  lib de ícones específica (ex.: **Solar Icons**).

## Fluxo
1. **Coletar fontes da marca**: manual (PDF — normalmente é *image-driven*, sem camada de texto,
   então extraia o texto (vazio) e **renderize cada página com pymupdf → PNG** e leia com
   vision_analyze página a página). Pegue também a imagem do sistema de cores e qualquer arte/branding.
2. **Extrair a paleta oficial** (hex/RGB/CMYK) direto do manual via visão. Guarde os fatos num
   `references/<cliente>-brand.md` para reaproveitar.
3. **Extrair o conteúdo de marca**: slogan, manifesto, conceito do símbolo, lockup do logo
   (wordmark + sufixo acentuado), aplicações (fundos claro/escuro, símbolo isolado), tipografia.
   ⚠️ Manuais de marca costumam ser **conceituais/aplicativos** — frequentemente NÃO têm malha de
   construção numérica nem área-de-proteção com medidas. Documente a área mínima como **regra
   operacional** (ex.: margem = altura do símbolo) e **nunca invente um grid que não existe**.
4. **Tipografia — verificar que a fonte REALMENTE carrega** (seção crítica, ver Pitfalls).
5. **Auditoria de contraste** antes de entregar (ver seção).
6. **Entregar como HTML versionado** (`<cliente>-design-system-v<N>.html`), nunca reutilizando nome.

## Tipografia — o erro clássico (fonte que "parece outra")
Quando o usuário diz "parece que entrou foi a Bricolage" / "não carrega a Tomato", o problema é:
- **Fonte licenciada não está em CDN gratuito.** Verifique SEMPRE com `curl` no CSS do CDN se o
  `@font-face` da família retornou (ex.: Fontshare/Google). Se a família não existir lá, o navegador
  **silenciosamente cai num fallback** que muda o desenho — e o usuário percebe "outra fonte".
- Fontes comerciais (ex.: **Tomato Grotesk**, The Designers Foundry / ex-Grilli Type) → **self-host**:
  declare `@font-face` apontando para `assets/fonts/<nome>-<peso>.woff2`, crie `assets/fonts/README.md`
  listando os arquivos exatos esperados, e use um **proxy gratuito rotulado** (ex.: Hanken Grotesk)
  na stack até os arquivos licenciados chegarem. **NÃO hotlink de sites de "download grátis".**
- Fontes gratuitas (ex.: **Clash Display**, Fontshare/Indian Type Foundry) → CDN ok.
- Confirme **pesos oficiais**: título pode ser 400/500, e "negrito em texto" pode ser o **ExtraBold**
  da família (ex.: Tomato 800), não um bolder sintético.

## Auditoria de contraste (fazer ANTES de entregar)
Calcule **WCAG programaticamente** para cada par texto/fundo realmente usado no sistema:
- AA normal = **4.5:1**; AA grande = **3.0:1** (≥24px ou ≥18.66px bold).
- Falhas comuns em design system de marca:
  - **Cinza de apoio** (ex. `#5a5a5a`) em textos pequenos (0.72–0.86rem) sobre **glass translúcido
    colorido** — passa o número mas fica ilegível; **escureça** (ex. `#414141`) e remova `opacity`
    que reduz contraste em texto pequeno.
  - **Cor primária da marca usada como cor de texto** (ex. teal `#029190` ~3.2:1 sobre off-white)
    → para texto use o **tom escuro/derivado** da marca (teal-deep), primária só p/ ícones/elementos.
  - **Branco sobre botão na primária** (~3.8:1) → aprofunde o gradiente do botão (partida mais escura).
- Ref. (Biotechse): charcoal `#2d2d2d` sobre cream/off-white = **11–12:1** (AAA); neutros de apoio ≥8:1.

## Identidade no layout
- Incorpore **motivos orgânicos do manual** como SVG divider (linhas DNA/folha em gradiente da marca)
  e o símbolo da marca no rodapé/nav.
- Wordmark com **sufixo acentuado** (ex. "Biotech**se**" em mint) e assinatura do cliente.
- **Liquid glass** (se o cliente usa): glassmorfismo **colorido** e flutuante (gradiente teal→mint
  ~10–16%, 3 orbs de blur que flutuam, borda superior clara + brilho interno), não glass neutro opaco.

## Entrega
- Arquivo versionado `v<N>` e `assets/fonts/` junto quando houver fonte licenciada.
- Se não der para renderizar visualmente (browser sem headless / localhost bloqueado), valide por
  Python: tags balanceadas (html.parser), `@font-face` presentes, todos os hex da paleta no arquivo.

## Pitfalls
- Não assumir que o manual tem grid/área-de-proteção; se não tem, diz isso e padroniza.
- Não fabricar a tipografia da marca; confirmar pesos e nomes (verificar via CDN + usuário).
- Não entregar texto/"palavras" onde o usuário espera HTML visual — sempre página HTML.