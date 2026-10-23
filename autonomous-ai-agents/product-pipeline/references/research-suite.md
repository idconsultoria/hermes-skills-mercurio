# Research Suite — relatórios brutos + versões premium + síntese

Quando a F2 precisa entregar, além dos `.md` de pesquisa, um pacote visual para leitura
executiva: `research/` com brutos, versões HTML premium e uma síntese.

```
decompor em N tópicos
        ↓
N subagentes em paralelo → 1 .md cada em product/research/
        ↓
itens "diretos" (web_search + web_extract) → .md
        ↓
design system HTML único (single-file, tokens) — base visual compartilhada
        ↓
cada .md → .html premium (via agy no host), CSS do design system embutido
        ↓
1 síntese executiva .html (resumo + achados-chave de todos)
```

**Quando usar:** o usuário pede "pasta de pesquisa / base de referências" e espera bruto +
entregável polido + resumo executivo.

## Componentes

**Relatórios `.md`** — um por ângulo, escritos pelos subagentes, em `product/research/`.
Nomes distintos por subagente (colisão de arquivo é erro clássico): definir o nome no contexto
de cada um e `mkdir -p` antes de disparar.

**Design system HTML** — criado uma vez, compartilhado. Custom properties para cor, tipografia,
espaçamento; dark mode; estética minimalista (Notion/Stripe/Linear).
Salvo como `product/research/design_system_minimal_neutral.html`.

**Versões premium** — uma por relatório, single-file, sem dependência externa: navbar, seções com
fundos alternados, gráficos em CSS puro (barras, matriz de quadrante), toggle de dark mode,
animações no scroll, sidebar com IntersectionObserver.

## Regras de formatação (preferência do usuário, valem para todo relatório)

- Rótulos "nível", "status", "projeto" ou "data" **não aparecem** em lugar nenhum.
- Sempre abrir com "Sobre este Relatório": o que é, como foi feito, o que informa.
- Consistência visual máxima: mesmos tokens `:root`, mesma navbar, mesma estrutura de seções.
- Tabelas sempre com `.table-wrap > table` — nunca grid customizado.

## Síntese executiva — padrão MBB

- Capa branca, minimalista, sem gradiente decorativo, sem glassmorphism, sem enfeite.
- Framework **SCR**: Situação → Complicação → Resolução, com a Resolução em 60–70% do espaço.
- Cada afirmação em negrito, com dado de suporte ao lado; números em destaque com micro-barras.
- **Silent read test:** a página se explica sem apresentador. Zero jargão de consultoria.
- Sem metadados irrelevantes na capa (consultoria, fase, confidencialidade, data) salvo pedido.
- `page-break-after` para exportar em PDF.

Padrões completos de McKinsey/BCG/Bain: `references/mbb-executive-summary-standards.md`.

## PDF (opcional, depois do HTML)

Chromium headless com `--print-to-pdf-no-header` e `@page { margin: 0; }` no CSS.
Renderer local: o Chromium ARM64 compartilhado do nó (`$HERMES_HOME/.playwright/...`), nunca
instalar outro. Upload para o Drive é opcional (`gapi drive upload ...`).

## Integração com o agy

Copiar design system + relatórios para o host, rodar `agy --dangerously-skip-permissions --print
"$(cat prompt.md)"` (uma chamada = um HTML) e trazer de volta com `scp`.

Armadilhas: colisão de nome de arquivo; `--dangerously-skip-permissions` obrigatório no modo
`--print`; hero decorativo sem informação é rejeitado pelo usuário.
