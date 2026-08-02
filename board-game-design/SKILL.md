---
name: board-game-design
description: "Board game design pipeline: concept to physical production.

Carregue esta skill quando for orquestrar o design de um board game — do pitch ao protótipo digital para playtest e produção física. Cobre arquitetura de agentes (Hermes orquestra, Pi Agent executa, Antigravity revisa), pesquisa de mercado BGG, GDD completo, implementação de protótipo web, balanceamento e produção. Compartilha volume /opt/data/code com os executores."
category: autonomous-ai-agents
type: Orchestrator
timestamp: 2026-07-31T00:00:00Z
related_skills: [boardgame-design-principles]
---

# Board Game Design Pipeline

> **Orquestrador:** Hermes
> **Executores:** Pi Agent (local) + Antigravity (revisor visual)
> **Foco:** Design de board games assimétricos → protótipo digital para playtest → produção física
> **Inspiração:** Product Pipeline + melhores práticas da indústria (Ludessy, BGG, COIN/GMT)
> **Shared volume:** `/opt/data/code/` ↔ `/workspace/code/`

## Filosofia

Design de board game é um processo iterativo onde **playtesting é o coração**. Nenhum GDD sobrevive ao primeiro playtest. O protótipo digital (web app premium) serve como ambiente de validação rápida — testar, iterar e balancear antes de comprometer recursos com produção física.

**O ciclo:** Ideia → Pitch → GDD → Protótipo Digital → Playtest (loop) → Produção Física.

**Princípios:**
- Playtest cedo, playtest sempre. Protótipo de papel no dia 1, digital na semana 2.
- Assimetria exige checks & balances. Toda força tem fraqueza explorável.
- Regras devem ser algorítmicas (if/then/else). Zero ambiguidade.
- O rulebook define se seu jogo vive ou morre na mesa.

## Arquitetura de Agentes

```
┌───────────────────────────────────────────────────┐
│                     Hermes                         │
│  Orquestrador • pesquisa • valida GDD • integra    │
│  Tools: delegate_task, web, file, terminal, pi CLI  │
└──────┬──────────────────────────────┬──────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐        ┌──────────────────┐
│    Pi Agent      │        │   Antigravity    │
│   (local CLI)    │        │   (agy)          │
├──────────────────┤        ├──────────────────┤
│ F1: Pitch        │        │ Revisor visual   │
│ F2: Pesquisa     │        │ do protótipo     │
│ F3: GDD          │        │ digital          │
│ F4a: UI Board    │        │                  │
│ F4b: Implement.  │        │                  │
│ F5: Balanceamento│        │                  │
└──────────────────┘        └──────────────────┘
```

### Hierarquia de uso

```
CARO/ESCASSO     agy --- Consultor externo (design visual, UX board)
ESCASSO          Pi best -- Game designer sênior (DeepSeek V4 Pro via Go)
BARATO/ABUNDANTE Pi cost -- Dev de protótipo (DeepSeek V4 Flash Free/Go)
```

## Estrutura do Projeto

```
<jogo>/
├── game-design/
│   ├── pitch/
│   │   └── game-pitch.md
│   ├── research/
│   │   ├── mercado-bgg.md
│   │   ├── mecanicas-referencia.md
│   │   ├── jogos-similares.md
│   │   └── pesquisa-sintese.md
│   ├── gdd/
│   │   ├── GDD.md
│   │   ├── 01-pitch.md
│   │   ├── 02-core-gameplay.md
│   │   ├── 03-systems.md
│   │   ├── 04-world-narrative.md
│   │   ├── 05-art-audio.md
│   │   └── 06-technical-rules.md
│   ├── prototype/
│   │   ├── design/
│   │   │   ├── design-system.md
│   │   │   ├── design-system.html
│   │   │   ├── board-layout.md
│   │   │   └── feedbacks.md
│   │   ├── src/
│   │   │   ├── index.html
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── assets/
│   │   └── engineering/
│   │       ├── code-tasks.md
│   │       └── feedbacks.md
│   ├── playtest/
│   │   ├── playtest-log.md
│   │   ├── balance-changes.md
│   │   └── feedback-synthesis.md
│   └── production/
│       ├── rulebook.md
│       ├── component-specs.md
│       ├── print-and-play/
│       └── manufacturing/
├── .gitignore
└── README.md
```

---

## Fases do Pipeline

```
[Ideia] → F1: Pitch → F2: Pesquisa → F3: GDD → F4: Protótipo → F5: Playtest → F6: Produção
            ↑             ↑               ↑            ↑                 ↑              ↑
         Hermes→Pi    Hermes+DR     Pi best 6-sect  Pi+agy→Web     Iterações até    Specs p/
                                  GDD completo      Board App      balanceamento    gráfica
```

---

## ⛔ REGRA DE OURO: Hermes NUNCA escreve código

- ❌ Hermes não edita HTML/CSS/JS. Pi gera, agy revisa.
- ❌ Não pular fases. Iteração é o contrato.
- ✅ GDD, regras, mecânicas: Pi best.
- ✅ Protótipo: Pi cost (lotes) + agy (revisão).

---

## Pre-flight Check

```bash
export PATH="/opt/data/pi-global/bin:$PATH"
pi --version
pi -p "list skills" --provider deepseek --model deepseek-v4-flash
ls /opt/data/code/workstation/JOGO/ 2>/dev/null
ssh oracle-host 'echo "n" | timeout 5 /home/ubuntu/.local/bin/agy 2>&1 | head -3'
```

---

## Fase 1: Pitch do Jogo

**Agente:** Pi (modelo best)
**Objetivo:** Transformar ideia bruta em pitch concreto que qualquer pessoa entenda em 15 segundos.

### Estrutura do Pitch (baseado no template Ludessy)

| Seção | Pergunta que responde |
|--------|----------------------|
| **1.1 One-liner** | O que é este jogo em 15 palavras? "Root encontra One Piece." |
| **1.2 Gênero + Referências** | Categoria e 3 jogos de referência. Seja específico. |
| **1.3 Público + Plataforma** | Quem joga? Complexidade (1-5). Duração. Nº jogadores. |
| **1.4 Hook** | Os primeiros 30 segundos. O momento que faz alguém querer jogar. |
| **1.5 Core Verbs** | Os 5-7 verbos atômicos. "Mover, atacar, negociar, explorar, construir, blefar." |
| **1.6 Core Loop** | O que o jogador faz em 1 minuto → 1 sessão → 1 campanha. Diagrama. |
| **1.7 Win/Loss** | Como uma sessão termina? E a campanha? Condições de vitória. |

### Fluxo

```bash
mkdir -p /opt/data/code/workstation/JOGO/game-design/pitch /opt/data/code/workstation/JOGO/prompts

cat > /opt/data/code/workstation/JOGO/prompts/pi-pitch.md << 'PROMPT'
JOGO: [ideia do jogo]
Diretório: /workspace/code/JOGO

Você é um game designer sênior de board games. Produza game-pitch.md com as 7 seções acima.
Inclua <!-- PHASE_COMPLETE: pitch --> ao final.
PROMPT

pi --name "JOGO-pitch" -p "$(cat prompts/pi-pitch.md)" --provider opencode-go --model deepseek-v4-pro
```

**Revisão obrigatória pelo usuário** antes de avançar.

### Saída
```
game-design/pitch/game-pitch.md
```

---

## Fase 2: Pesquisa de Mercado e Mecânicas

**Agente:** Hermes + subagentes

### Objetivo
Pesquisar jogos similares no BGG, estudar mecânicas de referência (COIN, Root, Arcs), e mapear o mercado.

### Tópicos de Pesquisa Obrigatórios

| Tópico | Fontes | Perguntas |
|--------|--------|-----------|
| **Mercado BGG** | BoardGameGeek, Reddit r/boardgames | Jogos com mesmo tema? Ratings? Weight? O que jogadores amam/odeiam? |
| **Mecânicas Referência** | COIN GMT, Root, Dune, Arcs, Oath, Twilight Imperium | Como cada um resolve assimetria? Economia? Combate? |
| **Lições de Design** | GDC talks, entrevistas com designers | O que deu errado em jogos similares? O que foi cortado? |

### Fluxo

1. Subagentes em paralelo para cada tópico
2. BGG é fonte primária: buscar "[tema] board game" → extrair ratings, weight, mecânicas
3. COIN series: estudar como cada facção tem ações, vitória, e recursos DIFERENTES
4. Hermes sintetiza em `pesquisa-sintese.md`

### Saída
```
game-design/research/
├── mercado-bgg.md
├── mecanicas-referencia.md
├── jogos-similares.md
└── pesquisa-sintese.md
```

---

## Companion Skill

Antes de iniciar qualquer fase de design (F1, F3, F5), carregar:
```
skill_view(name='boardgame-design-principles')
```
Esta skill contém os princípios de Eurogame design, metodologia de playtesting, e workflows de balanceamento que complementam o pipeline.

---

## Fase 3: Game Design Document (GDD)

**Agente:** Pi (modelo best) — **A FASE CENTRAL**
**Baseado no:** Template Ludessy de 6 seções + adaptações para board games assimétricos

### Estrutura do GDD

Cada seção responde UMA pergunta. Quem lê o doc frio deve parar após a seção 2 e já saber que jogo é.

#### Sessão 1: The Pitch
> *Pergunta: "O que é este jogo?"*

- One-liner, gênero, referências, público, hook
- Core verbs (5-7 máx)
- Core loop (diagrama, não só prosa)
- Win/loss conditions

#### Sessão 2: Core Gameplay
> *Pergunta: "O que o jogador FAZ, segundo a segundo?"*

- Fluxo do turno (fases: Global → Manutenção → Negociação → Ações)
- Ações disponíveis por facção
- Pacing: duração de turno, sessão, campanha
- Condições de vitória (principal + alternativas + morte súbita)

#### Sessão 3: Systems
> *Pergunta: "Que maquinário faz o jogo funcionar?"*

- **3.1 Economia:** Tabela recurso → fonte → sink → cap
- **3.2 Assimetria:** Cada facção — ações, recursos exclusivos, condição de vitória, fraqueza
- **3.3 Combate:** Iniciativa, resolução (dados/cartas/blefe), dano, saque, respawn
- **3.4 Exploração:** Revelação de mapa, quests, progressão, tech tree
- **3.5 Eventos:** Baralho de eventos, cronômetro da partida, catch-up mechanics
- **3.6 Escalabilidade:** 2 jogadores vs 4 vs 6. O que muda?

#### Sessão 4: World & Narrative
> *Pergunta: "Qual é o mundo e que história se passa nele?"*

- **4.1 Premise:** 2 parágrafos. Onde, quando, por quê.
- **4.2 Tone:** 3 adjetivos. "Tenso, político, épico."
- **4.3 Facções:** Uma linha por facção descrevendo seu PAPEL na experiência, não seu lore.
- **4.4 Locais:** Uma linha por local descrevendo sua função mecânica.
- **4.5 Arco narrativo:** Os 5-10 beats principais da campanha.

#### Sessão 5: Art & Components
> *Pergunta: "Como o jogo se parece e se sente?"*

- **5.1 Direção de arte:** Mood board textual. Referências visuais.
- **5.2 Componentes:** Lista completa — tabuleiro, cartas (quantidade, tamanho), tokens, peças, dados, caixa
- **5.3 Graphic Design:** Iconografia, paleta, tipografia, layout de cartas
- **5.4 Especificações técnicas:** Dimensões, materiais sugeridos, CMYK, 300 DPI, sangria

#### Sessão 6: Technical Rules
> *Pergunta: "Como se ensina este jogo a um novato?"*

- **6.1 Rulebook outline:** Estrutura do livro de regras (não o texto completo)
- **6.2 Setup guide:** Passo a passo do setup (procedural, com variabilidade)
- **6.3 Edge cases:** Regras para situações ambíguas (empate, stack de efeitos, ordem de resolução)
- **6.4 FAQ:** Perguntas que surgirão no primeiro playtest
- **6.5 Glossário:** Termos do jogo definidos em 1 frase

### Fluxo

```bash
mkdir -p /opt/data/code/workstation/JOGO/game-design/gdd

# Pi best gera as 6 seções em 2 lotes
# Lote 1: Seções 1-3 (Pitch, Core Gameplay, Systems)
pi --name "JOGO-gdd1" -p "$(cat prompts/pi-gdd-pt1.md)" --provider opencode-go --model deepseek-v4-pro

# Lote 2: Seções 4-6 (World, Art, Technical Rules)
pi --name "JOGO-gdd2" -p "$(cat prompts/pi-gdd-pt2.md)" --provider opencode-go --model deepseek-v4-pro
```

**Hermes consolida** as 6 seções em `GDD.md` com sumário navegável.

### Revisão do GDD
1. Hermes faz gap analysis: toda mecânica tem regra clara? Dados estão balanceados?
2. Enviar ao usuário para revisão (Google Docs para colaborativo)
3. Iterar até aprovação

### Saída
```
game-design/gdd/
├── GDD.md
├── 01-pitch.md
├── 02-core-gameplay.md
├── 03-systems.md
├── 04-world-narrative.md
├── 05-art-components.md
└── 06-technical-rules.md
```

---

## Fase 4: Protótipo Digital (Web Board Game)

**Agentes:** Pi + agy
**Objetivo:** Web app premium que serve como **tabuleiro virtual para playtest**. Não é o produto final — é ferramenta de validação.

### Requisitos do Protótipo

- ✅ Tabuleiro renderizado (teia de nós, hexes, ou grid conforme GDD)
- ✅ Peças posicionadas e movíveis
- ✅ Hand management (cartas na mão, drag/click para jogar)
- ✅ Resolução de combate automatizada (dados, modificadores)
- ✅ Hotseat multiplayer (troca de jogador sem rede)
- ✅ Log de ações (histórico do turno)
- ❌ NÃO implementar: autenticação, ranking, multiplayer online, monetização

### 4a. UI/UX Design

**Pi best gera:**
- `design-system.md` + `design-system.html` — tokens, componentes renderizados, dark mode
- `board-layout.md` — wireframe: mapa central + sidebars + painel de cartas + log
- agy revisa em loop (mín. 2 iterações, igual product-pipeline F4a)

### 4b. Implementação (Pi cost, 5 layers)

| Layer | Escopo | Tech |
|-------|--------|------|
| **L1: Board Engine** | Renderização do mapa (SVG/Canvas), posicionamento de tiles/peças | Vanilla JS + SVG |
| **L2: Game State** | State machine (fases do turno), controle de jogadores, ações | JS State |
| **L3: UI** | Sidebar, painel de cartas, modal de combate, log de eventos | HTML/CSS |
| **L4: Game Logic** | Movimentação, combate, economia, quests — implementar TODAS as regras do GDD | JS Modules |
| **L5: Hotseat** | Troca de jogador, tela de transição, fog of war por facção | JS |

### 4c. Validação (agy)

agy verifica: renderização correta, todas as ações implementadas, combate segue GDD, UI usável.

Loop agy→Pi→agy até `ACORDO: PROTÓTIPO VALIDADO`.

---

## Fase 5: Playtest e Balanceamento

**Agentes:** Hermes (facilitador) + Pi (analista)
**Princípio:** *"Nenhum GDD sobrevive ao primeiro playtest."*

### Tipos de Playtest (obrigatórios, nesta ordem)

| Tipo | Quem | Objetivo |
|------|------|----------|
| **Solo** | Designer | Loop básico funciona? Turnos têm pacing? |
| **Amigos** | 2-4 pessoas próximas | Regras fazem sentido? Alguém ficou confuso? |
| **Cego (blind)** | Pessoas que NUNCA viram o jogo | Rulebook é claro sem explicação do designer? |
| **Público-alvo** | Jogadores do nicho | Balanço, profundidade, replayability |

### Fluxo de Playtest

1. **Registrar cada sessão** em `playtest-log.md`:
   - Facções, resultado, duração, rodada da vitória
   - Momentos de confusão/frustração
   - Mecânicas ignoradas ou dominantes
   - Quotes dos jogadores

2. **Pi analisa logs** e sugere ajustes:
   - Atributos desbalanceados (PA/PV, custos)
   - Cartas problemáticas
   - Catch-up insuficiente ou abusivo

3. **Iterar:** Ajustar GDD → Atualizar protótipo → Novo playtest
   - **Mínimo 3 ciclos** antes de considerar balanceado

### Saída
```
game-design/playtest/
├── playtest-log.md
├── balance-changes.md
└── feedback-synthesis.md
```

---

## Fase 6: Produção Física

**Agente:** Hermes + Pi

### Entregáveis

| Documento | Conteúdo |
|-----------|----------|
| **rulebook.md** | Livro de regras final: organizado, diagramas, exemplos de turno, FAQ, índice |
| **component-specs.md** | Especificações exatas: dimensões, quantidades, materiais, cores (CMYK), acabamentos |
| **print-and-play/** | PDFs prontos para imprimir: cartas (frente/verso com sangria), tabuleiro (dividido A3), tokens |
| **manufacturing/** | Specs para gráfica: arquivos de corte, sangria, paleta CMYK, quantidade por caixa, MOQ |

### Regras para Rulebook Profissional

- Estrutura: Componentes → Setup → Visão Geral → Turno Detalhado → Fim de Jogo → Facções → FAQ
- Diagramas para setup e exemplos de turno
- Cada regra em UMA frase. Sem períodos compostos.
- Testado com blind playtest — se alguém precisou perguntar, a regra está mal escrita

### Fluxo

1. Pi best gera `rulebook.md` a partir do GDD + feedback de playtest
2. Pi best gera `component-specs.md` com quantidades exatas
3. Pi cost gera PDFs print-and-play
4. agy revisa qualidade visual (se houver assets gráficos)

### Saída
```
game-design/production/
├── rulebook.md
├── component-specs.md
├── print-and-play/
│   ├── cartas.pdf
│   ├── tabuleiro.pdf
│   ├── tokens.pdf
│   └── player-boards.pdf
└── manufacturing/
    └── specs-para-grafica.md
```

---

## Pitfalls de Game Design

⚠️ **Assimetria sem checks & balances** — Toda força tem fraqueza. Yonkou: exército massivo → lento. Capitão: rápido → frágil. Documente a fraqueza de CADA facção.

⚠️ **Catch-up mechanics** — Sem elas, "winner takes all" e abandono de mesa. Bônus de azarão não é opcional.

⚠️ **Complexidade ≠ profundidade** — Muitas regras não fazem jogo profundo. Se pode remover sem afetar decisões, remova.

⚠️ **"Um playtest não é suficiente"** — Mínimo 3 ciclos. Blind playtest é o verdadeiro teste do rulebook.

⚠️ **Regras ambíguas** — Toda mecânica em termos algorítmicos (if/then/else). Zero interpretação.

⚠️ **Protótipo digital é ferramenta, não produto** — Hotseat local. Sem auth, sem deploy, sem backend.

⚠️ **BGG como fonte primária** — Ratings, weight, mecânicas listadas, reviews são ouro.

⚠️ **COIN series** — Benchmark de design assimétrico. Cada facção com ações, recursos e vitória DIFERENTES.

⚠️ **Root** — Exemplo de assimetria acessível via player boards visuais.

⚠️ **Economia sem sinks quebra** — Tabela recurso→source→sink→cap. Sem sink, inflação infinita.

⚠️ **GDD de 50K+ caracteres** — Quebrar em 2 lotes (seções 1-3 e 4-6) para evitar truncamento.

⚠️ **Tone do jogo em 3 adjetivos** — Use-os em TODA revisão de arte/texto. "Isso não soa 'tenso' — corta."

---

## Formato do feedbacks.md

```markdown
## Turno N — @AgenteRemetente

**Para:** @AgenteDestinatário
**Em resposta ao:** Turno N-1

### Conteúdo
...

### O que espero de você:
- [ ] Ação concreta
```

---

## Conexões

| Conexão | Comando |
|---------|---------|
| **Hermes ↔ Pi (one-shot)** | `pi -p "..." --provider opencode-go --model deepseek-v4-pro` |
| **Hermes ↔ Pi (session)** | `pi --name "sessao" -p "..."` + `pi -c -p "..."` |
| **Hermes ↔ agy** | `ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/JOGO && /home/ubuntu/.local/bin/agy -p "..."'` |

> Pi e agy rodam SEM timeout. Nunca usar `timeout` com Pi ou agy.

## Modelos

| Uso | Provider | Model |
|-----|----------|-------|
| **Pi best** | `opencode-go` | `deepseek-v4-pro` |
| **Pi cost** | `opencode` (Zen) | `opencode/deepseek-v4-flash-free` |
| **Pi cost fallback** | `opencode-go` | `deepseek-v4-flash` |

---
