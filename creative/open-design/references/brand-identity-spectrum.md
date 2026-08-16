# Open Design — espectro de identidade de marca (v0.18.2, agosto/2026)

Mapa do que o open-design oferece para construir identidade de marca. Levantado em sessão de 13/08/2026 (projeto Zera). Útil para escolher a composição de skills num `start_run` e para responder "o que o open-design constrói em termos de marca".

## Inventário

- **162 skills** totais (`mcp__open_design__list_skills`); **46 são de marca/design**
- **460 plugins** bundled; ~155 são `design-system-*` de referência (Airbnb, Apple, Arc, BMW, Binance, Cal.com, Canva, Claude, Clay, ClickHouse, Cohere...)
- **154 design systems embutidos** em `/opt/data/open-design-repo/design-systems/` (packages: manifest.json + DESIGN.md + tokens.css)
- **5 design directions** (`od tools directions`)
- **1 runtime padrão**: agy/Antigravity (1.1.12) com 9 modelos (Gemini 3.5 Flash High/Medium/Low, Gemini 3.1 Pro, Claude Sonnet/Opus 4.6, GPT-OSS 120B)

## Skills de criação de identidade

| Skill | Superfície | O que faz |
|---|---|---|
| `design-consultation` | web | Design system do zero + mockups realistas; catálogo que aponta para upstream (Garry Tan gstack) |
| `brandkit` | image | Brand-kit boards, logo systems, identity decks via geração de imagem premium |
| `brand-extract` | image/web | Extrair brand kit completo de site existente (browser interno do daemon) |
| `design-md` | web | Criar/gerenciar DESIGN.md |
| `design-brief` | web | Parsear brief estruturado (I-Lang) → spec concreta |
| `color-expert` | web | Ciência de cores OKLCH/OKLAB, paletas, acessibilidade/contraste |
| `creative-director` | web | Diretor criativo: 5 fases, 20+ metodologias (TRIZ, SCAMPER, Synectics), orquestra lanes |
| `fal-train` | image | Treinar LoRA na marca p/ geração consistente |
| `imagegen` / `imagen` | image | Ícones, ilustrações, social cards, UI mockups |
| `theme-factory` | web | Aplicar temas de fonte/cor em slides/docs/reports |
| `design-taste-frontend` / `gpt-taste` / `frontend-design` / `minimalist-ui` / `industrial-brutalist-ui` | web | Interfaces anti-slop com direção visual |
| `design-review` / `web-design-guidelines` | web | Auditoria visual / conformidade de guidelines |
| `figma-generate-library` / `figma-generate-design` / `figma-use` | web | Design system dentro do Figma |
| `frame-logo-outro` / `remotion` / `after-hours-editorial-template` | video | Vídeo de marca (outro com logo, explainers, storyboards) |
| `minimax-docx` / `minimax-pdf` / `pdf` / `slides` | web | Brand guidelines formais em docx/PDF/PPTX |
| `apple-hig` / `wpds` / `brand-guidelines` (Anthropic) | web | Design systems de referência aplicáveis |
| `swiss-*` templates, `deck-*` templates, `card-*` templates | deck/video | Templates editoriais e de cards sociais |

## Fluxo recomendado (composto pelo agente)

1. **DESIGN.md** — escrever os tokens da marca (cores hex, tipografia, símbolo com paths exatos, tom de voz, anti-referências) e injetar no projeto via `write_file` (o agente do OD lê do projeto, não do filesystem do agente).
2. **Orquestração**: `creative-director` como skill primária (define o que é "bom" antes de mexer em pixels; pesquisa recursos; monta workflow em lanes).
3. **Geração por peça** (runs separados ou `skill` + `skills[]`):
   - logo system → `brandkit`
   - ícones/social cards → `imagegen`/`imagen`
   - guidelines formais → `minimax-pdf`/`minimax-docx`/`slides`
   - landing page → `frontend-design`/`gpt-taste`
   - vídeo → `frame-logo-outro`/`remotion`
   - audit → `design-review`
4. **Auditoria + iteração**: `design-review`, `web-design-guidelines`, crítica do usuário → novos runs com o mesmo `project` (o agente tem o contexto).

## Observações de uso (sessão Zera)

- Um único `start_run` pode consolidar vários deliverables num artefato (pedi brand-kit + design-system + app-mockup → veio 1 HTML de 65KB com 3 seções navegáveis + dark mode).
- O run usa o agy do container — ver Pitfalls da skill principal (shim `-p -`, settings.json allow-rules, token OAuth).
- Pergunta típica do usuário: "o open-design constrói X?" — responder com este mapa, não só com o último run.
