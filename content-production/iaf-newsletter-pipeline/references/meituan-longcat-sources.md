# Meituan LongCat — Fontes Oficiais

Portal central: https://www.longcatai.org/
GitHub org: https://github.com/meituan-longcat
Tech blog: https://tech.meituan.com/history.html

## Releases por data (Q2 2026)

| Data | Release | Fonte Oficial |
|------|---------|---------------|
| 02/04 | LongCat-Next (multimodal nativo) | [tech.meituan.com/2026/04/02/LongCat-Next.html](https://tech.meituan.com/2026/04/02/LongCat-Next.html) |
| 07/04 | LongCat-Flash-Prover (prova formal Lean4) | [github.com/meituan-longcat/LongCat-Flash-Prover](https://github.com/meituan-longcat/LongCat-Flash-Prover) |
| 20/04 | LongCat-AudioDiT (TTS zero-shot) | [tech.meituan.com/2026/04/20/LongCat-AudioDiT.html](https://tech.meituan.com/2026/04/20/LongCat-AudioDiT.html) |
| 27/04 | LARYBench (benchmark ação incorporada) | [tech.meituan.com/2026/04/27/LongCat-LARYBench.html](https://tech.meituan.com/2026/04/27/LongCat-LARYBench.html) |
| 15/05 | General 365 (benchmark raciocínio) | [tech.meituan.com/2026/05/15/LongCat-General-365.html](https://tech.meituan.com/2026/05/15/LongCat-General-365.html) |
| 25/05 | LongCat-Video-Avatar 1.5 (avatares) | [tech.meituan.com/2026/05/25/LongCat-Video-Avatar-1.5.html](https://tech.meituan.com/2026/05/25/LongCat-Video-Avatar-1.5.html) |
| 05/06 | ACL 2026 — 6 papers aceitos | [tech.meituan.com](https://tech.meituan.com/) (buscar por "ACL 2026") |
| 12/06 | WBench (benchmark mundos interativos) | [tech.meituan.com/2026/06/12/LongCat-WBench.html](https://tech.meituan.com/2026/06/12/LongCat-WBench.html) |
| 18/06 | Poster AIGC (geração de cartazes) | [tech.meituan.com](https://tech.meituan.com/) (buscar por "poster AIGC") |

## Padrão editorial

O tech.meituan.com publica artigos técnicos detalhados (arquitetura, benchmarks, citações) para cada release do LongCat. É a fonte primária. O portal longcatai.org agrega todos os modelos com links para GitHub, HuggingFace, ModelScope e papers. Use estes como fonte preferencial sobre agregadores de notícias (AIToolly, Pandaily, etc.).

## Benchmarks-chave (para referência rápida)

| Modelo | Benchmark | Score | Nota |
|--------|-----------|-------|------|
| AudioDiT 3.5B | SIM Seed-ZH | **0.818** | Similaridade de locutor, SOTA entre modelos abertos |
| AudioDiT 3.5B | CER Seed-ZH | **1.09%** | Taxa de erro de caractere em chinês |
| Flash-Prover | MiniF2F-Test | **97.1%** | Prova formal em Lean4 (72 tentativas) |
| Flash-Prover | ProofNet Auto-Formalização | **100%** | Conversão para linguagem formal |
| Video-Avatar 1.5 | EvalTalker | **65.9%** | Preferência vs Kling Avatar 2.0 |
| General 365 | Acurácia Gemini 3 Pro | **62.8%** | SOTA no benchmark (26 modelos testados) |
| LongCat-Flash-Thinking-2601 | AIME-25 | **100.0%** | Modo "re-thinking", score perfeito |
| LongCat-Flash-Thinking-2601 | BrowseComp | **73.1%** | Melhor entre todos os modelos |

## Armadilha conhecida

Agregadores podem publicar roundups mensais ou trimestrais que listam releases antigos como se fossem novos (ex: AIToolly em 27/06/2026 listou releases de abril-junho como "novidades"). Sempre verifique a data de cada release na fonte oficial do Meituan antes de incluir na newsletter.
