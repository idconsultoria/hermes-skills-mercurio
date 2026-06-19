---
name: process-augmentation-pipeline
description: "Pipeline ID Consultoria: análise de processos, brainstorming de soluções e site 3D.

Load this skill quando o usuário solicitar o pipeline de aumentação de processos da ID Consultoria — mapeamento de dores/oportunidades/gargalos, diagramas de loop causal, brainstorming de soluções de aumentação, avaliação e priorização, aprofundamento das top 10 soluções e empacotamento em site interativo com animações 3D. Cobre as 4 etapas do pipeline: (1) Análise — relatórios setoriais + diagramas de loop causal via Pi Agent com MiniMax M3, (2) Brainstorming — soluções de aumentação guiadas pelo grafo causal, (3) Avaliação e Aprofundamento — tabela multicritério + seleção top 10 + projeto de implantação, (4) Empacotamento — site Three.js com animações cinematográficas, trilha sonora opcional e exportação PDF. Orquestração Hermes com subagentes paralelos. Usa style-guide-consultation (guia ID Consultoria), augmentation-process-design (taxonomia A/B × I/II/III), agy (design/código), humanizer + copywriting (textos)."
version: 1.0.0
category: software-development
tags: [consultoria, processos, aumentacao, pipeline, diagrama-causal, brainstorming, avaliacao, site, threejs, ID-Consultoria]
metadata:
  hermes:
    related_skills:
      - augmentation-process-design
      - agy
      - humanizer
      - copywriting
      - style-guide-consultation
      - pi-agent-coordination
      - autonomous-ai-agents
      - dedalo-squad
      - bpmn-diagram-renderer
      - html-report-hermes
      - vulcano
      - vercel-deploy
---

# Pipeline de Mapeamento e Aumentação de Processos

> **Orquestrador:** Hermes Agent
> **Cliente:** ID Consultoria
> **Objetivo:** Da coleta de campo ao site interativo de entrega — mapear dores, propor soluções de aumentação com IA, priorizar, aprofundar e empacotar com impacto visual cinematográfico.

---

## Visão Geral

Pipeline de 4 etapas que transforma **POPs, diarizações de entrevistas e diagramas de processos** em um **site interativo de entrega ao cliente** com:

| Etapa | Entrada | Saída | Agente(s) |
|-------|---------|-------|-----------|
| **1. Análise** | Pastas setoriais (POPs + entrevistas + diagramas) | Relatórios .md + diagramas de loop causal HTML/D3.js + análise de ciclos | Pi Agent (MiniMax M3, contexto longo) |
| **2. Brainstorming** | Relatórios da etapa 1 + Index de soluções de referência | Soluções de aumentação (1.5-2× número de nós), agrupadas por cluster do grafo causal | Hermes (orquestrador) |
| **3. Avaliação** | Soluções da etapa 2 | Tabela multicritério + top 10 aprofundadas + projeto de implantação | Hermes (orquestrador) |
| **4. Empacotamento** | Top 10 + diagramas + relatórios | Site Three.js com 4 telas + exportação PDF + trilha sonora opcional + deploy Vercel | agy (primário, iterativo) + humanizer + copywriting |

**Regra de ouro:** Cada etapa versiona seus artefatos (stage → commit → push). Repositório Git dedicado, remote GitHub.

---

## Pré-requisitos

### Design Tokens — ID Consultoria

**Sempre carregar `style-guide-consultation` primeiro.** Tokens da marca de consultoria:

```css
--bg-color: #050A0F;
--deep-teal: #003B46;
--electric-teal: #66E8F1;
--teal-ciano: #4AC6D3;
--kintsugi-gold: #C9A227;
--deep-indigo: #1B2A6B;
--font-headline: 'Bricolage Grotesque', sans-serif;
--font-body: 'Nunito Sans', sans-serif;
--font-mono: 'IBM Plex Mono', monospace;
```

**Light mode (para PDF A4 e versão impressa):** fundo `#F7F9FB`, texto `#1C1C1E`, bordas `#DCE4E8`. Manter deep-teal e electric-teal.

### Taxonomia de Soluções

Usar a taxonomia da skill `augmentation-process-design`:

| Dimensão | Valores |
|----------|---------|
| **Categoria** | A (Reengenharia do processo), B (Otimização do processo) |
| **Tipo** | I (Agente de IA), II (Assistente de IA), III (Automação) |

Notação compacta: `A·I`, `B·II`, `B·III`, etc.

### Repositório Versionado

Antes de iniciar qualquer etapa:

```bash
mkdir -p /opt/data/<projeto>-aumentacao
cd /opt/data/<projeto>-aumentacao
git init
gh repo create id-consultoria/<projeto>-aumentacao --private --source=. --push
```

**Estrutura de diretórios esperada:**

```
<projeto>-aumentacao/
├── etapa-1-analise/
│   ├── setor-<nome>/
│   │   └── relatorio-dores.md       ← Pi Agent por setor (template: references/template-relatorio-dores.md)
│   ├── relatorio-integracao.md      ← Hermes pós-setores (template: references/template-relatorio-integracao.md)
│   └── analise-sistemica.html       ← Hermes pós-setores (spec: references/spec-analise-sistemica.md)
├── etapa-2-brainstorming/
│   └── propostas-solucoes.md
├── etapa-3-avaliacao/
│   ├── tabela-priorizacao.md
│   ├── top-10/
│   └── projeto-implantacao.md
├── etapa-4-site/
└── README.md
```

---

## Etapa 1 — Análise de Processos

### 1.1 O que produz

**Por setor (Pi Agent — MiniMax M3):**

1. **`relatorio-dores.md`** — Relatório de dores e gargalos operacionais do setor.
   - Segue o template `references/template-relatorio-dores.md`
   - Dores: queixas explícitas do time (com evidência literal das transcrições)
   - Gargalos: oportunidades de melhoria observadas nos POPs e diagramas
   - Cada item classificado: Cultural (C), Técnica (T) ou Organizacional (O)
   - Códigos: `DOR-<SETOR>-NN` e `GAR-<SETOR>-NN`
   - Matriz de incidência por processo + resumo quantitativo

**Após todos os setores (Hermes — orquestrador):**

2. **`relatorio-integracao.md`** — Relatório ÚNICO de integração entre TODOS os setores.
   - Segue o template `references/template-relatorio-integracao.md`
   - Matriz de interfaces com tipo (ENTRADA/SAÍDA/BIDIRECIONAL) e qualidade (FLUIDA/FRICCIONAL/ROMPIDA)
   - Análise das interfaces críticas com evidência e causa raiz
   - Recomendações de integração cross-setor

3. **`analise-sistemica.html`** — Documento ÚNICO contendo três seções integradas:
   - Segue a especificação `references/spec-analise-sistemica.md`
   - **Seção 1:** Diagrama de loop causal global (D3.js force-directed com TODOS os setores)
   - **Seção 2:** Análise sistêmica — visão geral, padrões de recorrência, influência mútua entre setores
   - **Seção 3:** Análise de ciclos — nomeação, funcionamento, ranking de nós-alavanca, hierarquia de Meadows

### 1.2 Como executar

**Orquestrador (Hermes)** dispara **um Pi Agent** por setor, usando o modelo **MiniMax M3** (contexto longo, multimodal). **Obrigatoriamente como processo de terminal em background** (`terminal(background=true, notify_on_complete=true)`), nunca via `delegate_task`.

O binário do Pi é `/opt/data/pi-global/bin/pi`. O `workdir` deve ser a pasta do setor para que o Pi acesse os arquivos com paths relativos. O `--name` é obrigatório para identificar a sessão depois:

```
terminal(
  command="/opt/data/pi-global/bin/pi -p \"$(cat /tmp/pi-prompt-<setor>.md)\" --provider opencode-go --model minimax-m3 --name \"<projeto>-etapa1-<setor>\"",
  workdir="/opt/data/<projeto>-aumentacao/etapa-1-analise/setor-<nome>",
  background=true,
  notify_on_complete=true
)
```

**Tempo esperado:** MiniMax M3 leva **5-10+ minutos só lendo** os arquivos antes de começar a escrever. Não confundir leitura com stall — ver 1.4 Monitoramento.

**Paralelismo:** Disparar um Pi Agent por setor simultaneamente via `terminal(background=true)`. Usar `process(action='poll')` para acompanhar progresso e `process(action='wait')` para coletar resultados.

**Commit por setor:** `git add etapa-1-analise/setor-<nome>/ && git commit -m "etapa 1: <setor> — N dores, M gargalos" && git push`

### 1.4 Monitoramento do Pi Agent

⚠️ Pi best (MiniMax M3) **não produz stdout durante a fase de leitura** (5-10+ min). O `output_preview` dos processos background ficará vazio, mas isso **não é stall**. Verificar progresso real pelo arquivo de sessão JSONL:

```bash
python3 -c "
import json, glob, os
for path in sorted(glob.glob('/opt/data/home/.pi/agent/sessions/--opt-data-<projeto>*--/202*.jsonl')):
    name = path.split('setor-')[1].split('--')[0] if 'setor-' in path else '?'
    entries = sum(1 for _ in open(path))
    # Get last action
    last = '?'
    writes = 0
    with open(path) as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                if e.get('type') == 'message':
                    for c in e.get('message', {}).get('content', []):
                        if isinstance(c, dict) and c.get('type') == 'toolCall':
                            last = f\"{c.get('name')} {str(c.get('arguments',{}))[:120]}\"
                            if c.get('name') == 'write':
                                writes += 1
    print(f'{name:10s} | {entries:3d} entries | writes={writes} | last: {last}')
"
```

**Sinais de progresso real:**
- Entradas crescendo a cada 30-60s → está lendo arquivos
- `writes > 0` → começou a produzir output
- `last` contendo nome de arquivo .md ou .html → escrevendo o documento final

**Sinal de stall real:** >120s sem crescimento na contagem de entradas.

**Commit ao final do setor:** `git add etapa-1-analise/setor-<nome>/ && git commit -m "etapa 1: <setor>" && git push`

### 1.5 Consolidação global (Hermes)

Após TODOS os Pi Agents concluírem, o orquestrador (Hermes) consolida:

1. **`relatorio-integracao.md`** — lê os 4 `relatorio-dores.md` + dados de integração per-setor e redige o documento global seguindo `references/template-relatorio-integracao.md`.

2. **`analise-sistemica.html`** — lê todos os `relatorio-dores.md` + integração, extrai nós e arestas, e gera HTML único com D3.js + análise textual + ciclos, seguindo `references/spec-analise-sistemica.md`.

**Commit final da etapa 1:**
```bash
git add etapa-1-analise/relatorio-integracao.md etapa-1-analise/analise-sistemica.html
git commit -m "etapa 1: consolidação global — integração + análise sistêmica" && git push
```

**Pitfalls da consolidação:**
- **Não delegar a Pi Agents.** A consolidação é feita pelo Hermes diretamente (leitura + raciocínio + write_file), não por subagentes.
- **Os nós já estão codificados** nos `relatorio-dores.md` — extrair e combinar, não reinventar.
- **O HTML é complexo mas autossuficiente.** Usar D3.js inline no `<script>`, dados como JSON inline, estética ID Consultoria.

### 1.3 Pitfalls da Etapa 1

- **MiniMax M3 pode estourar contexto** se a pasta tiver muitos arquivos. Priorizar: POPs primeiro, depois diarizações, depois imagens.
- **⚠️ Transcrições das entrevistas são obrigatórias.** Cada processo deve ter sua `Transcrição das Entrevistas` (.md exportado do Google Docs). As dores reais estão nas falas dos entrevistados — sem transcrições, a análise perde a voz do time. Verificar antes de disparar os Pi Agents: `find etapa-1-analise/ -name "*ranscri*" | wc -l` deve ser ≥ número de processos.
- **D3.js em headless:** testar diagrama abrindo o HTML gerado. Se falhar, fallback para `bpmn-diagram-renderer`.
- **Ciclos muito grandes** (10+ nós) são difíceis de nomear. Agrupar subciclos quando possível.

---

## Etapa 2 — Brainstorming de Soluções

### 2.1 O que produz

Lista de propostas de solução (1.5× a 2× o número total de nós do grafo sistêmico), cada uma associada a um ou mais nós do diagrama causal.

Cada proposta deve especificar:
- **Nó(s) alvo:** referência `S<setor>-<número>`
- **Categoria × Tipo:** notação `A·I`, `B·II`, etc.
- **Descrição curta:** 2-3 frases
- **Mecanismo de ganho:** o que muda e por que resolve o nó

### 2.2 Como executar

**Orquestrador (Hermes) trabalha por grupos de nós correlatos** — usa o próprio grafo causal gerado na Etapa 1 para identificar clusters de nós conectados.

**Para cada grupo:**

1. **Calcula o impacto acumulado:** soma do número de ciclos dos quais cada nó participa (calculado na Etapa 1.5)
2. **Determina quantas soluções alocar ao grupo:** proporcional ao impacto do grupo ÷ impacto total. Grupos com mais impacto recebem mais propostas.
3. **Consulta as soluções de referência via Vulcano** (`vulcano_search` e `vulcano_context`):
   - Busca semântica no vault de referências com `vulcano_search(query="<descrição do cluster>")` para encontrar engramas relevantes
   - Carrega as mais relevantes com `vulcano_context(query="<cluster>", max_tokens=2000)` para trazer ao contexto
   - Usa como inspiração, sem replicar cegamente
   - **Nota:** o vault de referências contém soluções granulares e isoláveis (padrão do repositório). Na ideação para clientes, vale pensar tanto em soluções pontuais quanto sistêmicas — a restrição de isolabilidade é só para o catálogo de referências, não para as propostas ao cliente.
4. **Propõe soluções** originais adaptadas ao contexto real dos processos mapeados

**Repete até atingir o número-alvo** (1.5-2× total de nós).

**Commit ao final:** `git add etapa-2-brainstorming/ && git commit -m "etapa 2: N propostas de solução geradas" && git push`

### 2.3 Pitfalls da Etapa 2

- **Não listar ferramentas de IA como soluções.** Ferramenta é meio — a solução é a alteração no processo.
- **Não repetir soluções de referência** sem adaptação ao contexto real.
- **Soluções podem ser pontuais ou sistêmicas.** Na ideação para clientes, não há restrição de isolabilidade — vale propor desde otimizações granulares até reengenharias completas que abrangem múltiplos nós do grafo causal. A restrição de granularidade existe apenas para o catálogo de referências (`augmentation-process-design`), não para as propostas ao cliente.

---

## Etapa 3 — Avaliação e Aprofundamento

### 3.1 Tabela de Priorização

Para **cada proposta de solução**, preencher:

| Campo | Descrição |
|-------|-----------|
| Nome da proposta | Título descritivo curto |
| Descrição resumida | 2-3 frases |
| Nota Facilidade (0-10) | 10 = implementa amanhã, 0 = 1 ano+ |
| Potencial de retorno | Valor esperado em métrica concreta (R$ mil, horas, % erros) |
| Nota Retorno (0-10) | 10 = a organização mataria para ter, 0 = irrelevante |
| Nota Viabilidade financeira (0-10) | 0 = gratuito, 10 = licença cara + equipe grande |
| **Nota ponderada** | `(Retorno × 4 + Viabilidade × 3 + Facilidade × 3) ÷ 10` |

**Estimativas reais de custo** (R$, horas, equipe) só aparecem no aprofundamento, não na tabela preliminar.

### 3.2 Seleção Top 10

Ordenar por nota ponderada decrescente. Selecionar as 10 primeiras, com regra:
- Se duas soluções forem **incompatíveis** (uma inviabiliza a outra), pular a de menor nota e avançar na lista até completar 10.

### 3.3 Aprofundamento — Projeto de Implantação

Para cada uma das top 10, detalhar:

1. **Diferencial para a realidade atual**
2. **Processo TO BE** — fluxo redesenhado com a aumentação
3. **Cronograma realista de implantação** — fases, marcos, durações
4. **Metas de performance** — KPIs com baseline e target
5. **Custos envolvidos** — ferramentas, equipe, treinamento, infraestrutura
6. **Plano de contenção de riscos e compliance** — LGPD, segurança, resistência à mudança

### 3.4 Commit

```bash
git add etapa-3-avaliacao/ && git commit -m "etapa 3: top 10 soluções avaliadas e aprofundadas" && git push
```

---

## Etapa 4 — Empacotamento (Site Interativo)

### 4.1 Visão Geral

Site **single-page** com navegação cinematográfica entre 4 telas. **A inspiração principal são UIs de jogos — não deve parecer um site comum.** Ambientação futurista-humanista-tecnológica dentro da identidade visual da ID Consultoria. Cada elemento deve evocar a sensação de estar explorando um mundo digital, não navegando em uma página web.

**Referência de design:** [hubtown.co.in](https://hubtown.co.in) — estudar a abordagem de imersão, transições e atmosfera de jogo aplicada a um site real.

### 4.2 Tecnologia

- **Three.js** (CDN ou bundle) — cenas 3D, animações, partículas, iluminação profissional
- **GSAP ScrollTrigger** — scroll suave cinematográfico entre seções
- **Web Audio API** — trilha sonora opcional e efeitos sonoros
- **html2pdf** — exportação PDF de cada tela
- **CSS custom properties** — design tokens ID Consultoria

**⚠️ Iluminação 3D profissional e realista.** Evitar efeitos genéricos (bloom padrão, point light branca). Investir tempo significativo em: HDR environment maps, light probes, shadow mapping com PCF suave, tone mapping cinematográfico (ACES), rim lights coloridas (teal e gold), key lights anguladas com intensidade dramática. A iluminação deve ser tão cuidada quanto a de um jogo AAA — é o que separa um site comum de uma experiência imersiva.

**⚠️ agy é a ferramenta PRIMÁRIA de design e código do site.** Usar estratégia iterativa: (1) agy gera esqueleto HTML+CSS base com todos os design tokens ID, (2) agy gera JavaScript complexo (Three.js, GSAP, áudio) em chamadas separadas, (3) agy gera seções individuais, (4) script Python monta as peças no HTML final. Alternativamente, usar `agy /goal` para projetos multi-arquivo. Carregar `style-guide-consultation` antes de qualquer prompt ao agy.

### 4.3 Skills de Apoio

| Skill | Quando usar |
|-------|-------------|
| `agy` | **Principal** — gerar esqueleto, seções, JavaScript (Three.js, GSAP, áudio) e montar o site completo via estratégia iterativa |
| `humanizer` | Todo texto do site — remove AI-isms, adiciona personalidade |
| `copywriting` | Frases de impacto da tela de Apresentação, CTAs, headlines |
| `style-guide-consultation` | Carregar tokens ID Consultoria antes de qualquer prompt ao agy |

### 4.4 As 4 Telas

#### Tela 1 — Apresentação

- **Fundo:** cubo 3D gigante rotacionando lentamente, emitindo feixes de energia teal sutis. Terreno com relevo demarcado por linhas topográficas teal em loop.
- **Conteúdo:** frases de impacto resumindo o potencial de valor das soluções + urgência dos gargalos. Convite visual a rolar/deslizar.
- **Ambientação:** iluminação cinematográfica (key light teal, rim light gold).

#### Tela 2 — Mapa de Aumentação

**Seção 1 — Mapa:**
- **Estilo mapa de países reais** com territórios demarcados por divisas imaginárias, inspirando-se em cartografia de videogames (Elden Ring, Civilization, Zelda). Cada setor vira um território com nome, fronteiras orgânicas e geografia fictícia.
- Marcadores = soluções propostas, posicionados dentro de seus territórios como pontos de interesse
- Top 10 piscam e são clicáveis → pop-up estético com:
  - Frase de impacto
  - Descrição curta
  - Cards com informações principais (custo, prazo, ganho)
- Demais soluções: hover mostra nome + descrição curta + posição ranking + nota
- Mouse move → leve pan na câmera 3D

**Seção 2 — Tabela (scroll):**
- Surge sobre o mapa, tomando foco
- Tabela completa com todas as colunas da avaliação (Etapa 3.1)
- Design ID Consultoria: fundo escuro, teal, bordas sutis, tipografia Bricolage/Nunito/IBM Plex

#### Tela 3 — Relatório de Gargalos

- **Fundo:** feixes de luz teal encontrando obstáculos na topografia do terreno
- **Conteúdo:** diagramas de loop causal (versão adaptada e mais bonita dos HTMLs da Etapa 1) + análises textuais dos ciclos + conclusão dos nós-alavanca
- **Interação:** clique em nó expande análise do ciclo

#### Tela 4 — Projetos de Implantação

- **Fundo:** mesmo terreno, mas feixes fluem desimpedidos (sem obstáculos) — metáfora visual de processos desbloqueados
- **Conteúdo:** mesmos pop-ups das soluções top 10 da Tela 2, com setas nas laterais para navegar entre projetos
- Cada pop-up mostra o aprofundamento completo (Etapa 3.3)

### 4.5 Navegação e UX

- **Scroll/Dedlizar:** conduz suavemente entre seções e telas, com fluidez e cadência cinematográficas. Elementos surgem aos poucos conforme a rolagem, com animações impactantes (scale+fade+blur stagger) — nada aparece estático de uma vez.
- **Navbar:** discreta, aparece ao aproximar mouse da borda esquerda (desktop) ou via botão expandir/retrair (mobile). Cliques na navbar disparam transições fluidas e impactantes entre telas — com animação de câmera 3D, partículas ou distorção espacial, não um simples scroll.
- **Transições:** cada troca de tela é um evento visual — morphing de geometria 3D, transições de iluminação, partículas de transição. Nada de fade simples.
- **PDF:** botão discreto em toda tela → download versão A4 (fundo branco, identidade ID)

### 4.6 Trilha Sonora

- Opcional, ativável via botão flutuante
- Efeitos sonoros premium nas transições entre telas
- Gerar com `text-to-speech` skill ou síntese Web Audio API

### 4.7 Commit Final

```bash
git add etapa-4-site/ && git commit -m "etapa 4: site interativo de entrega" && git push
```

### 4.8 Deploy com Vercel

Após o agy finalizar a construção do site, o orquestrador (Hermes) realiza o deploy:

```bash
cd etapa-4-site/
npx vercel --prod --yes
```

**Requisitos:**
- `vercel` CLI instalado e autenticado (`npx vercel login`)
- Projeto configurado como static site (sem build step — o agy já entrega HTML final)
- Domínio customizado se disponível; caso contrário, usar o domínio `.vercel.app` padrão

O deploy é a etapa final — só executar quando todas as 4 telas estiverem completas, testadas e commitadas.

---

## Orquestração Geral

### Sequência de Execução

```
Etapa 1 ──→ Etapa 2 ──→ Etapa 3 ──→ Etapa 4
  │            │            │            │
  │            │            │            └── agy (iterativo) + humanizer + copywriting
  │            │            └── Hermes (sequencial, 1 etapa)
  │            └── Hermes (iterativo, grupos de nós)
  └── Pi Agent (paralelo, 1 por setor)
```

### Modelos

| Etapa | Modelo | Justificativa |
|-------|--------|---------------|
| 1. Análise | **MiniMax M3** (opencode-go) | Contexto longo + multimodal (lê imagens de diagramas) |
| 2. Brainstorming | **DeepSeek V4 Pro** (opencode-go) | Raciocínio criativo, tradução de referências para contexto real |
| 3. Avaliação | **DeepSeek V4 Pro** | Julgamento analítico, estimativas ponderadas |
| 4. Site | **agy** — estratégia iterativa (esqueleto → seções → JS → montagem) + **DeepSeek V4 Pro** (textos, copy, orquestração da montagem) | Design visual superior com agy; código complexo gerado em iterações |

### Commit por Etapa

Cada etapa finaliza com `git add etapa-X/ && git commit && git push`. Isso garante:
- Histórico rastreável
- Rollback por etapa
- Colaboração possível (cliente pode revisar etapa intermediária)

---

## Verificação

```bash
# Checklist pós-execução:
cd /opt/data/<projeto>-aumentacao

# 1. Etapa 1 — relatórios de dores por setor?
ls etapa-1-analise/setor-*/relatorio-dores.md

# 2. Relatório de integração global?
ls etapa-1-analise/relatorio-integracao.md

# 3. Análise sistêmica HTML?
ls etapa-1-analise/analise-sistemica.html && grep -c "d3" etapa-1-analise/analise-sistemica.html

# 4. Número de soluções coerente?
grep -c "^### " etapa-2-brainstorming/propostas-solucoes.md

# 4. Top 10 selecionadas?
ls etapa-3-avaliacao/top-10/ | wc -l

# 5. Site funcional?
ls etapa-4-site/*.html

# 6. Git remoto atualizado?
git log --oneline -4
```

---

## Pitfalls Gerais

⚠️ **Pi Agent com MiniMax M3 pode ser caro.** Monitorar tokens por setor via `pi-session-audit`. Se estourar orçamento, reduzir contexto (só POPs, sem diarização).

⚠️ **Diagrama D3.js em headless.** Testar abrindo o HTML gerado antes de commitar. Se d3 não carregar (bloqueio de CDN), usar implementação inline (d3 inteiro no `<script>`).

⚠️ **Soluções não são lista de ferramentas.** Correção explícita do usuário. A solução descreve alteração no processo, a ferramenta é meio. Foco em "como o trabalho muda".

⚠️ **Trilha sonora não pode ser obrigatória.** Áudio com autoplay é bloqueado por navegadores. Implementar como opt-in (botão "Ativar som").

⚠️ **agy para sites completos exige estratégia iterativa.** Não gerar tudo de uma vez. Usar o workflow: esqueleto → seções → JS → montagem. Ver skill `agy` para o padrão completo de Full Site Generation.

⚠️ **Não confundir guias de estilo.** O pipeline é sempre ID Consultoria. Se o usuário não especificar marca, ID Consultoria é o padrão deste pipeline.

⚠️ **Repositório versionado desde o início.** Não começar a gerar arquivos sem `git init` + remote configurado.

---

## Histórico de Atualizações

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-06-19 | Hermes (Gustavo Mello) | Criação da skill — pipeline completo de 4 etapas para mapeamento e aumentação de processos da ID Consultoria. |
| 2026-06-19 | Hermes (Gustavo Mello) | Etapa 1: Pi Agents obrigatoriamente como terminal background, nunca delegate_task. |
| 2026-06-19 | Hermes (Gustavo Mello) | Etapa 4: agy reposicionado como ferramenta PRIMÁRIA (estratégia iterativa), removida limitação de 75KB. |
| 2026-06-19 | Hermes (Gustavo Mello) | Etapa 2: consulta de referências migrada para Vulcano (vulcano_search + vulcano_context). Removida restrição de isolabilidade para propostas ao cliente — soluções podem ser pontuais ou sistêmicas. |
| 2026-06-19 | Hermes (Gustavo Mello) | Etapa 1 reestruturada: Pi Agents produzem apenas relatorio-dores.md por setor. Relatório de integração e análise sistêmica (HTML único com diagrama + análise + ciclos) são consolidados pelo Hermes após todos os setores. Templates de referência em references/. |
| 2026-06-19 | Hermes (run real Sergipetec) | Etapa 1.2: corrigido binário `pi-agent` → `/opt/data/pi-global/bin/pi`. Adicionado `--name` e `workdir` ao comando. Nova seção 1.4 Monitoramento do Pi Agent com script de verificação de progresso via JSONL. Pitfall: transcrições obrigatórias — verificar antes de disparar Pi Agents. Tempo real validado: 5-10 min leitura + escrita. |
