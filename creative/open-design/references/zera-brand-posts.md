# Zera — Posts sociais (specs no Drive)

Contexto de marca: identidade Zera (projeto CFP IA, ex-CFP IA). DESIGN.md canônico no projeto `zera-brand` do Open Design e em `cfp-ia/product/design/DESIGN.md`.

## Onde ficam as specs de post

- **NÃO estão** em `/opt/data/zera-brand/` (só HTMLs de marca, PNGs, SVGs, zips).
- **Estão na pasta "Posts" do Drive**: `1R88p_5x4j7BBm8my3LiUpMT9byR-tMnl` (parent: `1dTbKJfunbcMBrXNf0YTjO7qU4QOJk8Sm`).
- Listar: `$GAPI drive search --raw-query "'1R88p_5x4j7BBm8my3LiUpMT9byR-tMnl' in parents and trashed=false"` (⚠️ SEM `--raw-query` → 400 Invalid Value).

## Post 1 — "Planejamento financeiro não é bicho de sete cabeças"

Dois docs na pasta:
1. `Post 1 - links dos slides individuais (preview)` → `1RORWk4bcIMD-S2SBSw6At72g3nl_pg77rP9uFku-Xkg` — links claude.ai/artifact de cada slide + preview em grade.
2. `Post 1 - Planejamento financeiro nao e bicho de sete cabecas` → `1fDJfi6V6-uc5-VvImIFq8Zd1IcRD_c0Zyh8YRSe8npw` — spec completa (formato + copy de todos os slides + legenda).

**Formato:** carrossel, 5 slides, proporção 4:5 (1080×1350), Instagram.

| Slide | Fundo | Copy |
|---|---|---|
| 1 (capa) | Floresta (`#14532D`) | "Planejamento financeiro não é bicho de sete cabeças" |
| 2 | Menta clara | "A pergunta que todo mundo evita" — "Por onde eu começo a organizar minha vida financeira?" / "Se você nunca fez essa pergunta em voz alta, não tá sozinho." |
| 3 | Floresta | "O que é, de verdade" — "Organizar o que entra e o que sai. Só isso." |
| 4 | Menta clara | "Antes que você pense" — "Não precisa ganhar muito pra começar" |
| 5 (CTA) | Floresta | "O primeiro passo" — "Saber pra onde vai seu dinheiro — a gente te ajuda a começar" + CTA 📩 `@zera.financas` |

**Status (2026-08-14):** estilo visual aprovado pelo Igão (02/08); falta gerar peça final em alta resolução e agendar via Instagram nativo.

## Execução via Open Design

- Projeto `zera-brand` **já existe** no daemon (skill `design-consultation`, status succeeded) com DESIGN.md + design-system-zera.html + artifact.html (identity kit) + zera-brand-experience.html + apresentacao-branding.html.
- Fluxo: `write_file` da spec (ou prompt) no projeto → `start_run(project="zera-brand", skill="canvas-design" | "poster-hero", prompt com copy INLINE e tokens do DESIGN.md, agent="antigravity", model="Gemini 3.5 Flash (High)", requestId=<UUID estável>)` → `get_run` a cada 30–60s → validar com `browser_vision` → exportar PNGs 1080×1350.
- ⚠️ **Copy exata = HTML/CSS fiel (canvas-design/poster-hero/card-xiaohongshu).** `imagegen`/`imagen` alucinam texto em PT-BR — reservados para arte sem texto crítico.

## Tokens de marca (resumo do DESIGN.md)

- `--zr-green` `#22A06B` (primária, chevron superior), `--zr-forest` `#14532D` (profunda, wordmark, títulos), `--zr-mint` `#7FD6A6` (secundária clara), `--zr-mist` `#E8F3EA` (fundo claro), `--zr-bg` `#F7FBF8` (fundo app).
- Tipografia: Poppins (400/500/600/700), fallback system-ui. Números: tabular-nums.
- Símbolo: dois chevrons ascendentes, pontas arredondadas — inferior `#14532D`, superior `#22A06B`; paths viewBox 120: `M26 82 L60 55 L94 82` + `M33 55 L60 31 L87 55`.
- Posts sociais: fundo mist/bg, símbolo + headline Poppins 700, CTA verde, selo CFP discreto. Verde primário em 30–60% da superfície.
