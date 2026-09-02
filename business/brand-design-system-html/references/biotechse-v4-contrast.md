# Biotechse v4 — Correção de contraste na composição

**Correção feita na sessão 2026-08-26 (v3 → v4)**

**Sinal:** Usuário apontou: "A parte em que você explica a composição da marca está usando fundo claro, com ícone mint e tipografia clara, não dá pra ler bem."

**Causa:** Os 3 cards do conceito central ("B" grotesk / DNA / folha) usavam glass claro translúcido
(teal ~10-16% sobre fundo claro) mas o texto era branco (`#fff`) e ícone/título mint (`#00ffa3`).
Branco sobre claro = ilegível, mesmo com glass.

**Correção validada (WCAG calculado):**
- Fundo trocado para teal escuro sólido: `#0d6f6e → #055c5b → #024140`
- Branco sobre `#055c5b`: **7.8:1** (AA)
- Parágrafo `#f0faf7` sobre `#055c5b`: **7.3:1** (AA)
- Mint `#00ffa3` sobre `#055c5b`: **5.9:1** (AA)

**Regra para próximos DS:** Se o conteúdo (texto/ícone) é claro (branco/mint), o container NÃO pode ser
glass claro. Use container escuro da marca. Inversamente, se container é claro, texto deve ser charcoal.

**Entrega:** `biotechse-design-system-v4.html` (54KB) — validada com html.parser balanceado,
`--charcoal-mut` escurecido para `#414141` e bloco `.cg3 .item` com fundo sólido.
