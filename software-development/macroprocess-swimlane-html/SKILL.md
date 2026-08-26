---
name: macroprocess-swimlane-html
description: "Mapa macroprocesso swimlane em HTML interativo p/ clientes da ID (a partir do doc do Drive)."
category: software-development
type: Orchestrator
timestamp: 2026-08-26
---

# Macroprocess Swimlane — HTML interativo (ID)

Entregável de mapeamento de processos para clientes da ID (ex.: Solution Master —
com Safety, Medical, Telecom, Back Office; Grupo Recanto). Um **mapa de processo
swimlane em HTML**, sem build, que abre em qualquer navegador: baias por departamento,
tarefas em sequência como blocos clicáveis, e setas que conectam bloco-a-bloco
(estilo BPMN).

Consolidação (2026-08-26) das três skills duplicadas `html-process-diagrams`,
`interactive-process-map-html` e `macroprocess-swimlane-html` nesta única skill
canônica. Referências técnicas absorvidas em `references/`.

## Quando usar / gatilho
Principal pede "HTML interativo do processo de <segmento>", "baias de cada
departamento", "fluxo em sequência", "pop-up em cada etapa", "mapa de processos",
"swimlane", "fluxograma BPMN", "macroprocesso" do cliente. Cliente de
mapeamento/aumentação de processos (Solution Master, Grupo Recanto).

## Fonte da verdade — NUNCA inventar etapas
O conteúdo vem do **documento de macroprocesso no Drive da ID** (Google Docs), não da
KB (que só guarda resumo). Carregue `google-workspace` e `docs get <DOC_ID>` o
documento (preserva headings + tabelas). Procure com
`drive search "<segmento> SOLUTION"` (ex.: "Telecom SOLUTION", "Safety SOLUTION").
- Extrair por etapa: título, **departamento** (dono), resumo ("O que acontece"),
  **entrada**, **saída**, **tratamento de erros** (falha + consequência). Também o
  bloco de "gargalos e pontos críticos" quando o doc traz.
- Se um campo está genuinamente ausente (ex.: coluna SLA/Duração), **deixar vazio e
  avisar o principal** — nunca chutar tempos nem inventar etapas.

## Modelo de dados (validado com Solution Master Telecom, 11 tarefas × 8 departamentos)
- `LANES[]` — departamentos (as baias).
- `ETAPAS[]` — cada etapa: `num` (1..N, ordem do fluxo), `titulo`, `dept` (lane DONA),
  `parceiros[]` (departamentos que participam — handoffs), `resumo`, `entrada`,
  `saida`, `falha`, `consequencia`.
- `BOTTLENECKS[]` — lista de gargalos/pontos críticos para a seção final.
- **1 tarefa = 1 bloco (regra dura).** Cada etapa aparece UMA vez, na lane do seu
  departamento dono. NÃO renderizar blocos "participa/parceiro" duplicados na mesma
  coluna de outras lanes — isso leu como "3 blocos numa etapa" e confundiu.
  Departamentos parceiros entram como **badges dentro do card do dono** (`↔ Departamento`),
  e também aparecem no pop-up (modal) e nas tags. Legenda: `➜` sequência · `↔` parceria.

## Layout / identidade ID (constante — use sempre)
- **Fundo claro** por padrão (white/#f7fafc bg, cards white, navy text `#0a1a30`), teal
  escurecido `#0d9488` para setas/badges; alternativa teal-on-navy (`--teal:#14b8a6`,
  `--navy:#0a1929`, gradiente radial). Nunito Sans (Neulis Neue p/ títulos).
- **Espaçamento generoso** (iteração até satisfazer): cards min-width ~224px,
  min-height ~118px, cell padding ~11-13px, lane width ~210px, fonte 13-13.5px.
  "Está apertado" = aumente.
- Nome do arquivo com **versão** (`telecom-macroprocesso-v1.html` / `-v2.html`...) e
  JAMAIS reutilizar nome — o principal costuma querer comparar versões.

## Setas de sequência — conectam BLOCOS, não colunas
- Setas ligam um bloco ao próximo como flowchart/BPMN: da **borda direita** do bloco N
  à **borda esquerda** do bloco N+1 — não uma seta estática de "coluna".
- Roteamento **ortogonal (cotovelos de 90°)**, não curvas Bezier diagonais:
  `M x0 y0 L elbowX y0 L elbowX y1 L x1 y1`, `elbowX = min(x0+18, x1-8)`; linha reta
  quando mesma lane (`|y1-y0|<10`). Como 1 bloco por coluna, o segmento vertical desce
  por células vazias e nunca cruza um card.
- Renderizar num overlay SVG (`position:absolute` no `.swimlane` rolável,
  `pointer-events:none`), coords de `getBoundingClientRect()` menos a origem do
  swimlane — robusto a scroll horizontal.

### Setas — ponta da flecha ancorada NO PONTO (pitfall que custou revisão)
Um gap aparecia entre a linha e a seta. **Fix: ancorar o marker na PONTA, não na base.**
`refX` escolhe qual coordenada do marker senta na ponta da linha.
- ❌ `refX=8.5` com triângulo cuja base está em `x=0` → a ponta fica atrás do fim da
  linha → gap visível.
- ✅ Âncora na ponta: viewBox `0 0 12 10`, `refX="11.5"`, `refY="5"`, triângulo
  `M 0.5 0.8 L 11.5 5 L 0.5 9.2 z` — as hastes (base, x≈0.5) COBREM a linha por trás da
  ponta e a ponta termina exatamente na borda do bloco. Snippet completo + recipe:
  `references/svg-arrowheads-and-screenshots.md`.

## Redraw responsivo (sem intervenção manual)
Recomputa setas em `resize`, `document.fonts.ready`, `window load`, e mudanças de
layout via `ResizeObserver` *debounced* (90ms). Fontes carregando tarde desalinham as
setas se você desenhar só uma vez. Snippet: `references/orthogonal-arrows.md`.

## Validação antes de entregar (nunca entregar artefato visual cego)
Não depende de screenshot. Checks determinísticos (container pode não ter Chromium;
o harness `browser_exec` pode falhar com `PermissionError` — é ambiental, não
bloqueia):
1. **Sintaxe JS:** extrair o bloco `<script>` para um `.js` e rodar `node --check`.
2. **Consistência dos dados** (python): todo `dept` e `parceiros` existem em `LANES`;
   `num` é sequência contínua `1..N` sem lacunas.
3. **Paridade do grid:** contagem de colunas — header e body devem casar.
4. **Prova visual (quando der):** render headless Chromium → PNG. ⚠️ Conhecimento de
   campo: `--virtual-time-budget` **LOOPA para sempre** em páginas cujo JS redesenha
   com `setTimeout` (ResizeObserver + debounce) — a captura nunca estabiliza. Fazer
   uma variante com observers desabilitados (`if(false){`) ou capturar rápido sem a
   flag. Ver `references/svg-arrowheads-and-screenshots.md`. Depois inspecionar o PNG
   com `vision_analyze` (setas ortogonais, nada cruzando card, espaçamento ok).

## Pitfalls
- **Não fabricar etapa da fonte.** Campo ausente = deixar vazio e avisar.
- Após montar, espelhar o entendimento do fluxo (dono→parceiro) ao principal antes de
  assumir o próximo passo; em projeto vivo o "passo atual" pode estar à frente da KB.
- Setas com runs verticais longos em mapas 11+ tarefas × 8 lanes → espere esparsidade
  (células vazias à direita/inferior); chamar a atenção e oferecer variantes
  compact-column ou responsivo empilhado.
- Não deixar o run vertical de uma seta cruzar outro card — mantê-lo dentro da coluna
  fonte (só o dono + células vazias).

## Template pronto
`templates/swimlane-macroprocess.html` — copiar, preencher `LANES`, `ETAPAS`,
`BOTTLENECKS` do doc de origem. Utilizável direto ou como base do layout.
