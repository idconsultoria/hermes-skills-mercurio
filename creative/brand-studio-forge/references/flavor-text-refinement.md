# Flavor Text Refinement Protocol

After completing forge_forge, ALL flavor texts are **drafts**. The user expects iterative refinement. Follow this protocol.

## Categories to Refine

1. **Lema/Tagline principal** — 5-15 words. Appears in manual header, HTML hero, PRODUCT.md, DESIGN.md.
2. **Tagline secundária** — 3-8 words. Hero subtitle.
3. **Definição central de voz** — 1-3 sentences. The "soa como..." definition.
4. **Exemplos de voz por contexto** — Newsletter, discussão, boas-vindas, debate. Each with a 1-line description + 1-2 sentence example quote.
5. **Metáfora central** — 1 sentence describing the brand's core metaphor (coworking, workshop, lab, etc.).
6. **Descrição do símbolo/mascote** — 2-4 sentences.
7. **Anti-referências** — List of what the brand is NOT.

## Brainstorm Format

For each category, present:

```
### [Category Name]

**Original:** "[current text]"
→ Problema: why it's weak

**Alternativas:**
A) "[option]" — why this works
B) "[option]" — why this works
C) "[option]" — why this works

**ESCOLHIDO:** A — motivo da escolha
```

## IAF Example (from production)

This is the actual refinement that was applied for the "IA que Funciona" community brand:

| Categoria | Original | Refinado |
|-----------|----------|----------|
| **Lema** | "Inteligências orgânicas melhorando a si mesmas com inteligência artificial" (prolixo) | **"O melhor da IA, com os dois pés no chão"** (brinca com a capivara, otimista sem hype) |
| **Tagline** | "Onde IA que funciona vira prática, não hype" (genérico) | **"IA sem enrolação. Com capivara."** (memorável, tom de comunidade) |
| **Voz** | "soa como um colega de coworking que senta ao lado e te provoca... entusiasmado sem ser ingênuo" | **"é a do profissional que puxa a cadeira no coworking e solta um 'e aí, já pensou por esse lado?' na hora do café. Profundo sem ser pedante, animado sem ser vendido."** (mais visual, "puxa a cadeira" é ação concreta) |
| **Newsletter** | "Capivara, segura essa: e se a IA que funciona for justamente a que para de crescer?" | **"Capivara, segura essa: um pesquisador da DeepMind soltou que modelo grande para de aprender depois de certo ponto. Talvez a IA que realmente funcione seja a que sabe parar."** (mais contexto, menos abstrato) |
| **Discussão** | "Testei o Claude pra extrair 500 NF. 70% de acerto." | **"Passei a tarde de ontem testando o Claude pra extrair 500 notas fiscais. Acertou 7 de cada 10. Alguém aqui já conseguiu melhor que isso sem gastar rios de dinheiro em fine-tuning?"** (mais humano, "rios de dinheiro" é brasileiro) |
| **Debate** | "RAG não virou commodity. O que virou é tutorial de RAG meia-boca." | **"RAG não virou commodity. O que virou commodity é tutorial de RAG com três chunks e um embedding meia-boca. Qualidade de recuperação em domínio fechado ainda separa entrega de 'quase funciona'."** (mais preciso, termina com provocação) |
| **Metáfora** | "Coworking — pessoas trabalham e socializam juntas, se divertindo e tornando o processo mais leve." | **"Um coworking onde o barulho é de teclado e risada — não de buzina de guru. Aqui se trabalha, se testa, se quebra, se aprende junto."** (mais vívida, anti-guru) |
| **Descrição capivara** | Mantida: "feito à mão, com gambiarra consciente, mas que funciona" | **Mantida** (perfeita — brasileira, autêntica, conecta com o nome) |

## Rules

- The user will NOT accept first-pass texts as final. Flag at least the lema and voice definition for refinement.
- Portuguese/BR only. Zero anglicisms.
- Prefer concrete verbs over abstractions ("puxa a cadeira" > "conecta-se").
- Use Brazilian cultural references when they fit (capivara, feira, obra, churrasco, trânsito, Detran).
- Every text must pass the voice-consistency check: remove the brand name — can you still tell which brand this is?
- **Boas-vindas** examples tend to be the most stable — often need less refinement than other contexts.

## Propagation

After user approves the chosen texts:
1. Update all markdown files (manual, PRODUCT.md)
2. Update DESIGN.md description field
3. Update HTML — patch existing file (do NOT regenerate; preserve base64 images). Use `patch` tool for targeted find-and-replace on text changes only.
