# Branching pattern — Safety cisão/junção (2026-08-31)

Caso real: principal pediu "a partir da triagem, haja a cisão dos 3 caminhos possíveis, e em seguida a junção na área de faturamento e pós venda" — doc Safety SOLUTION MASTER.

## Por que branching foi necessário

O doc Safety não é linear: Fase 1 (1.1→1.4) define escopo, mas 1.2 Qualificação decide 1 de 3 categorias que são **alternativas mutuamente exclusivas por OS**:
- Categoria 1: Ensaios Elétricos (4 passos: 2.1.1 triagem → 2.1.2 visual → 2.1.3 dielétrico → 2.1.4 certificação/ART)
- Categoria 2: Detecção de Gás/Metrologia (3 passos: 2.2.1 diagnóstico células → 2.2.2 ajuste Zero/Span com gás padrão RBC → 2.2.3 certificado)
- Categoria 3: Linha de Vida/Trava-Quedas NR-35 (7 passos em 2 subfluxos: 3A recertificação trava-quedas + 3B instalação linha vida com projeto, memorial, ensaio de arrancamento, placa + As-Built + ART)

Todos convergem em Fase 3 (3.1 faturamento → 3.5 recorrência 11º mês). Modelo linear 1..N explodiria para 4+14+5=23 colunas vazias.

## Solução implementada (safety-macroprocesso-v13.html)

**Layout em 3 blocos:**
1. **Fase 1 linear** — flex row com 4 cells + `➜` separators, scroll-x
2. **Branch section** — `div.branch-section` (border `#cdd7e4`, radius 14px) com:
   - header: diamond `◈` + "Cisão após a Triagem (Etapa 1.2) — 3 caminhos"
   - linha de contexto: "1.2 Qualificação ➜ DECISÃO DE CATEGORIA ➜ 1 dos 3 caminhos"
   - grid 3 colunas: `grid-template-columns:1fr 1fr 1fr; gap:16px` (responsive: 1fr em <900px)
   - cada coluna: label pill colorido + sublabel + 1 cell macro (border-left na cor) + `ul.steps-mini` com sub-etapas + partners badges `↔`
   - footer merge: `⬢ Junção — todos convergem` pill navy + `➜ 3.1 Faturamento`
3. **Fase 3 linear** — flex row com 5 cells

**Data model:**
```js
const FASE1 = [{num:"1.1", titulo, dept, parceiros, cor, resumo, entrada, saida, falha, consequencia}, ...4]
const BRANCHES = [{id:"2A", label:"Caminho 1 — Ensaios Elétricos", sublabel, cor, titulo, dept, parceiros, resumo, entrada, saida, falha, consequencia, detalheSubpassos:[]}, ...3]
const FASE3 = [{num:"3.1", ...}, ...5]
```

**Render:**
- `renderFase1()` / `renderBranch()` / `renderFase3()` separados
- `cardHtml()` reutilizado
- modal unificado: `[...FASE1, ...BRANCHES.map(b=>({...b,num:b.id})), ...FASE3].find(e=>e.num===key)` — branch modal mostra bloco extra "Sub-etapas deste caminho"

**Cores por categoria:**
- Ensaios Elétricos: `#2563eb` (blue)
- Gás/Metrologia: `#0f766e` (teal)
- Linha Vida/NR-35: `#6d28d9` (purple)

**Legenda estendida:**
`➜ Sequência · ◈ Cisão · ⬢ Junção · ▣ 1 bloco = 1 tarefa macro`

## Pitfalls capturados

- Não tente colocar 14 sub-etapas como colunas do swimlane — cria matriz esparsa ilegível e setas cruzando cards. Agrupe por categoria macro.
- Fabricantes homologados (Hércules/MSA/Honeywell) aparecem como parceiros/badges, não como lanes próprias — mesma regra "1 tarefa = 1 bloco no dono".
- Observação "metrologia via parceiro" do doc vira nota no resumo do Caminho 2, não um 4º caminho.
- Validade 12 meses NR-10/NR-35 aparece na régua 11º mês (3.5), não como fase separada.

## Arquivo de referência

`/opt/mercurio-data/deliverables/safety-macroprocesso-v13.html` — abrir como exemplo antes de gerar novo branching. Para docs lineares (Telecom v12, Medical v13) não usar branching.
