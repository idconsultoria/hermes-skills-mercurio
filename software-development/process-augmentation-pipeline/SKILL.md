---
name: process-augmentation-pipeline
description: "Pipeline ID Consultoria: análise de processos, brainstorming de soluções e site 3D.

Load this skill quando o usuário solicitar o pipeline de aumentação de processos da ID Consultoria — mapeamento de dores/oportunidades/gargalos, diagramas de loop causal, brainstorming de soluções de aumentação, avaliação e priorização por setor com compliance check, e empacotamento em site interativo com animações 3D. Cobre as 4 etapas do pipeline: (1) Análise — relatórios setoriais + diagramas de loop causal via Pi Agent com MiniMax M3, (2) Brainstorming — soluções de aumentação guiadas pelo grafo causal com Vulcano obrigatório, (3) Avaliação — tabela multicritério + top 3 por setor + top 3 intersetorial + projeto de implantação, (4) Empacotamento — site Three.js com exportação PDF. Orquestração Hermes com subagentes paralelos. Usa style-guide-consultation (guia ID Consultoria), augmentation-process-design (taxonomia A/B × I/II/III), agy, humanizer, copywriting."
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
| **1. Análise** | Pastas setoriais (POPs + entrevistas + diagramas) | Relatórios .md + diagramas de loop causal HTML/D3.js + análise de ciclos | Pi Agent × setor (MiniMax M3) + Pi Agent final (global) |
| **2. Brainstorming** | Relatórios da etapa 1 + Index de soluções de referência | Soluções de aumentação (1.5-2× número de nós), agrupadas por cluster do grafo causal | Hermes (orquestrador) |
| **3. Avaliação** | Soluções da etapa 2 + relatórios setoriais da etapa 1 | Tabela multicritério (130 soluções) + top 3 por setor + top 3 intersetorial com compliance check + projeto de implantação — consolidados em `tabela-priorizacao.md` | Hermes (orquestrador) |
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
--teal-ciano: #4AC6D3;
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
├── LEIA-ME.md                           ← Guia de navegação para revisão humana
├── etapa-1-analise/
│   ├── setor-<nome>/
│   │   ├── relatorio-dores.md           ← Pi Agent: dores e gargalos do setor
│   │   └── analise-sistemica.html       ← Pi Agent: diagrama causal + ciclos (MESMO prompt)
│   ├── relatorio-integracao.md          ← Pi Agent final: interfaces cross-setor (ÚNICO .md global)
│   └── analise-sistemica.html           ← Pi Agent final: TODOS os nós (~82) + cross-setor
├── etapa-2-brainstorming/
│   └── propostas-solucoes.md
├── etapa-3-avaliacao/
│   ├── tabela-priorizacao.md           ← Hermes: 130 soluções pontuadas + top 3 por setor + compliance check
│   └── solucoes-expandidas.md          ← Hermes: 15 soluções expandidas (~1 pág. cada, ferramentas não-prescritivas, custos em faixas)
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

2. **`analise-sistemica.html`** — Documento único com diagrama de loop causal + análise de ciclos do setor.
   - Segue a especificação `references/spec-analise-sistemica-setorial.md`
   - Diagrama D3.js force-directed com todos os nós do setor, coloridos por natureza
   - Detecção de ciclos, nomeação e análise textual de cada um
   - Classificação de nós por participação em ciclos (ranking de alavancas)
   - **IMPORTANTE:** o Pi Agent deve gerar este HTML no MESMO prompt que o `relatorio-dores.md`. Ambos os arquivos de saída são listados no prompt como deliverables.

**Após todos os setores (Pi Agent final — MiniMax M3):**

3. **`relatorio-integracao.md`** — Relatório ÚNICO de integração entre TODOS os setores.
   - Segue o template `references/template-relatorio-integracao.md`
   - Matriz de interfaces com tipo (ENTRADA/SAÍDA/BIDIRECIONAL) e qualidade (FLUIDA/FRICCIONAL/ROMPIDA)
   - Análise das interfaces críticas com evidência e causa raiz
   - Recomendações de integração cross-setor

4. **`analise-sistemica.html` (GLOBAL)** — Documento cross-setor com foco nas interfaces entre setores.
   - Segue a especificação `references/spec-analise-sistemica.md`
   - Setores como meta-nós + interfaces como conexões + dores transversais
   - Análise de interfaces críticas e ciclos cross-setor

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

**Tempo esperado:** MiniMax M3 leva **5-10+ minutos só lendo** os arquivos antes de começar a escrever. Não confundir leitura com stall — ver 1.3 Monitoramento.

**Prompt do Pi Agent:** deve instruir o agente a produzir DOIS arquivos de saída:
1. `relatorio-dores.md` — seguindo `references/template-relatorio-dores.md`
2. `analise-sistemica.html` — seguindo `references/spec-analise-sistemica-setorial.md`

O prompt deve incluir as instruções completas de ambos os formatos para que o Pi Agent gere os dois no mesmo contexto, garantindo consistência entre os nós do relatório e os nós do diagrama.

**Paralelismo:** Disparar um Pi Agent por setor simultaneamente via `terminal(background=true)`. Usar `process(action='poll')` para acompanhar progresso e `process(action='wait')` para coletar resultados.

**Commit por setor:** `git add etapa-1-analise/setor-<nome>/ && git commit -m "etapa 1: <setor> — N dores, M gargalos, X ciclos" && git push`

### 1.3 Monitoramento do Pi Agent

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

### 1.4 Consolidação global cross-setor (Pi Agent final)

Após TODAS as análises sistêmicas setoriais estarem concluídas e commitadas, o orquestrador (Hermes) dispara **UM último Pi Agent** (MiniMax M3, contexto longo) para produzir os documentos globais.

Este Pi Agent ingere:
- Todos os `relatorio-dores.md` setoriais (4 arquivos)
- Todas as `analise-sistemica.html` setoriais (4 arquivos)

E produz:

1. **`relatorio-integracao.md`** — documento global de integração entre setores seguindo `references/template-relatorio-integracao.md`. Foco nas interfaces (matriz com tipo e qualidade), não repete dores intra-setor.

2. **`analise-sistemica.html` (GLOBAL)** — HTML único cross-setor seguindo `references/spec-analise-sistemica.md`, contendo:
   - Diagrama de loop causal com TODOS os ~80-95 nós individuais (dores + gargalos + ganhos) de todos os setores
   - Conexões cross-setor extraídas do relatório de integração
   - Ciclos cross-setor + intra-setor combinados: nomeação, funcionamento, ranking de alavancas
   - Símbolos +/- e setas direcionais em todas as arestas

**Comando do Pi Agent final:**

```
terminal(
  command="/opt/data/pi-global/bin/pi -p \"$(cat /tmp/pi-prompt-global.md)\" --provider opencode-go --model minimax-m3 --name \"<projeto>-etapa1-global\"",
  workdir="/opt/data/<projeto>-aumentacao/etapa-1-analise",
  background=true,
  notify_on_complete=true
)
```

**Prompt (salvo em `/tmp/pi-prompt-global.md` antes de disparar):** deve instruir o Pi Agent a ler todos os arquivos setoriais, identificar interfaces cross-setor, detectar ciclos que atravessam fronteiras organizacionais, e gerar ambos os documentos de saída. Ver `references/template-relatorio-integracao.md` e `references/spec-analise-sistemica.md` como referência de formato.

**Após conclusão do Pi Agent — commit:**
```bash
git add etapa-1-analise/relatorio-integracao.md etapa-1-analise/analise-sistemica.html
git commit -m "etapa 1: consolidação global — integração + análise sistêmica cross-setor (Pi Agent)" && git push
```

### 1.3 Pitfalls da Etapa 1

- **MiniMax M3 pode estourar contexto** se a pasta tiver muitos arquivos. Priorizar: POPs primeiro, depois diarizações, depois imagens.
- **⚠️ Transcrições das entrevistas são obrigatórias.** Cada processo deve ter sua `Transcrição das Entrevistas` (.md exportado do Google Docs). As dores reais estão nas falas dos entrevistados — sem transcrições, a análise perde a voz do time. Verificar antes de disparar os Pi Agents: `find etapa-1-analise/ -name "*ranscri*" | wc -l` deve ser ≥ número de processos.
- **D3.js em headless:** testar diagrama abrindo o HTML gerado. Se falhar, fallback para `bpmn-diagram-renderer`.
- **Ciclos muito grandes** (10+ nós) são difíceis de nomear. Agrupar subciclos quando possível.

---

## Etapa 2 — Brainstorming de Soluções

### 2.1 O que produz

Arquivo `propostas-solucoes.md` com a lista completa de propostas (1.5× a 2× o número total de nós do grafo sistêmico), cada uma associada a um ou mais nós do diagrama causal. O formato padrão é o estabelecido na execução real do Sergipetec (539 linhas, 38 KB):

- **Header:** metodologia, total de engramas consultados, total de chamadas Vulcano, total de nós e meta de soluções
- **Por cluster:** tabela de referências Vulcano (engrama | case | padrão extraído), seguida de soluções numeradas
- **Cada solução:** nó(s) alvo, categoria × tipo, engrama(s) de referência (obrigatório), descrição (2-4 frases com menção a pessoas/processos reais), mecanismo de ganho com métrica concreta quando disponível
- **Resumo final:** tabela de clusters, matriz Categoria × Tipo com totais consistentes (soma = número total de soluções), tabela de distribuição taxonômica

Cada proposta deve especificar:
- **Nó(s) alvo:** referência `DOR-<SETOR>-NN`, `GAR-<SETOR>-NN` ou `INT-NN`
- **Categoria × Tipo:** notação `A·I`, `B·II`, etc.
- **Engrama(s) de referência:** caso(s) do Vulcano que inspiraram a solução (obrigatório — garante rastreabilidade)
- **Descrição:** 2-4 frases, com menção a pessoas/processos reais quando possível
- **Mecanismo de ganho:** o que muda, por que resolve o nó, com métrica concreta quando disponível (ex.: "redução de ~90% no tempo, de 30-60 min para 2-3 min")

### 2.2 Como executar

**Orquestrador (Hermes) trabalha por grupos de nós correlatos** — usa o próprio grafo causal gerado na Etapa 1 para identificar clusters de nós conectados.

**Para cada grupo:**

1. **Calcula o impacto acumulado:** soma do número de ciclos dos quais cada nó participa (calculado na Etapa 1)
2. **Determina quantas soluções alocar ao grupo:** proporcional ao impacto do grupo ÷ impacto total. Grupos com mais impacto recebem mais propostas.
3. **⚠️ PROTOCOLO VULCANO OBRIGATÓRIO — executar ANTES de propor soluções:**
   - `vulcano_context(query="<descrição do cluster>", max_tokens=2500)` — **1 chamada por cluster**, não opcional
   - Extrair de cada engrama retornado os 4 campos da **Ficha de Engrama** (ver `references/vulcano-brainstorming-protocol.md`):
     a) **Arquitetura da solução** — etapas, componentes, fluxo
     b) **Métricas de ganho** — números concretos de redução de tempo/custo/erro
     c) **Armadilhas** — onde a solução falha, edge cases
     d) **Onde NÃO aplicar** — perfil de organização/processo para o qual a solução é contraindicada
   - Citar o engrama de referência em cada solução proposta (campo `Referência:`), garantindo rastreabilidade
   - Usar como inspiração, **nunca replicar cegamente** — adaptar ao contexto real
   - **Protocolo completo em `references/vulcano-brainstorming-protocol.md`** — inclui Ficha de Engrama, verificação de qualidade e armadilhas
4. **Propõe soluções** originais adaptadas ao contexto real dos processos mapeados

**Repete até atingir o número-alvo** (1.5-2× total de nós). Arquivo final: `propostas-solucoes.md` com todas as soluções e citações de engramas.

**Commit ao final:** `git add etapa-2-brainstorming/ && git commit -m "etapa 2: N propostas de solução — Vulcano (X engramas)" && git push`

### 2.3 Pitfalls da Etapa 2

- ⚠️ **Vulcano subutilizado é o erro mais comum.** A execução real do Sergipetec mostrou que 2 chamadas superficiais produzem soluções genéricas (nota 1.2/10); 7 chamadas com extração ativa produzem soluções arquiteturalmente densas (nota 7.2/10). **NUNCA pular o protocolo Vulcano** — é a diferença entre um brainstorming raso e um de consultoria.
- ⚠️ **Ler engramas passivamente não basta.** Extraia ATIVAMENTE os 4 campos da Ficha de Engrama (arquitetura, métricas, armadilhas, contraindicações) ANTES de propor soluções. A leitura passiva produz "inspiração vaga"; a extração ativa produz padrões de implementação.
- **Não listar ferramentas de IA como soluções.** Ferramenta é meio — a solução é a alteração no processo.
- **Não repetir soluções de referência** sem adaptação ao contexto real. A métrica de qualidade é: > 80% das soluções devem citar o engrama mas demonstrar adaptação profunda (não replicação). No Sergipetec Vulcano, 92% atingiram esse critério.
- **Soluções podem ser pontuais ou sistêmicas.** Na ideação para clientes, não há restrição de isolabilidade — vale propor desde otimizações granulares até reengenharias completas que abrangem múltiplos nós do grafo causal. A restrição de granularidade existe apenas para o catálogo de referências (`augmentation-process-design`), não para as propostas ao cliente.
- **Cobrir lacunas do vault.** Se o Vulcano retornar engramas de baixa relevância para um cluster (ex.: Comunicação Corporativa, Cultura), isso é um sinal de que o vault precisa ser expandido — não um sinal para pular o cluster. Adapte engramas de domínios vizinhos e documente a lacuna para curadoria futura.

---

## Etapa 3 — Avaliação por Setor e Priorização

### 3.0 Princípio

A Etapa 3 **não seleciona um top 10 global**. Em vez disso, classifica as soluções por setor beneficiado (ASP, Jurídico, Inovação, CVT) + intersetorial, e seleciona o **top 3 de cada**. Isso garante que cada setor receba atenção proporcional, evitando que setores com menos dores (ex.: ASP, 10 dores) sejam eclipsados por setores com muitas dores (ex.: Inovação, 46 dores).

**Antes de pontuar, extrair as restrições conhecidas dos processos** a partir das transcrições de entrevistas e POPs da Etapa 1. Exemplos da execução real Sergipetec:

| Restrição | Setor | Impacto |
|-----------|-------|---------|
| Lista de presença física com assinatura obrigatória | CVT | Check-in digital deve preservar artefato físico; pode aumentar, não substituir |
| Termo de Autorização de Imagem obrigatório | CVT | Inscrição online deve incluir coleta do termo |
| Fluxo de aditivos e auxílio creche integralmente físico | Jurídico | Assinatura digital só para contratos principais |
| Retenção documental mínima de 5 anos | ASP | Qualquer solução de digitalização deve incluir backup de longo prazo |

Cada solução candidata ao top 3 deve ser explicitamente verificada contra essas restrições (campo "Compliance check" ou seção "Aderência a restrições").

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

### 3.2 Seleção Top 3 por Setor + Top 3 Intersetorial

1. Classificar cada solução pelo setor primariamente beneficiado (ASP, Jurídico, Inovação, CVT) ou como Intersetorial (impacta ≥2 setores simultaneamente ou ataca interfaces INT-NN)
2. Para cada setor, listar soluções candidatas com nota ponderada e compliance check
3. Selecionar as 3 de maior nota que PASSAM no compliance check
4. Para o top 3 intersetorial, priorizar soluções que atacam interfaces com maior nota de retorno — mesmo que a nota ponderada seja mais baixa (ex.: state machines com nota 5.4 mas retorno 9)
5. Se uma solução viola uma restrição conhecida, ela pode ser **ajustada** (não descartada): documentar o ajuste e reavaliar

### 3.3 Aprofundamento — Projeto de Implantação

Para cada uma das soluções selecionadas, detalhar nesta ordem exata:

1. **Diferencial para a realidade atual** — o que muda e por que importa. **Obrigatório:** as duas primeiras linhas após o heading devem ser:
   - `**Nós associados:** DOR-xxx, GAR-xxx, INT-xxx` — referências diretas aos nós do diagrama causal da Etapa 1
   - `**Categoria × Tipo:** A·I` — notação taxonômica
2. **Processo TO BE** — fluxo redesenhado com a aumentação (preferir diagrama ASCII para versionamento em git)
3. **Aderência a restrições** — como a solução respeita (ou contorna) as limitações conhecidas do processo. Esta seção é absorvida pelo plano de contenção (abaixo) — as restrições de compliance viram riscos com mitigação documentada
4. **Cronograma realista de implantação** — fases, marcos, durações (preferir tabela markdown)
5. **Metas de performance** — KPIs com baseline (valor atual) e target (valor esperado), em tabela markdown
6. **Custos envolvidos** — ferramentas, equipe, treinamento, infraestrutura (implantação + mensal)
7. **Plano de contenção de riscos** — tabela com risco, probabilidade, impacto e mitigação. **Incluir aqui as restrições de compliance como linhas da tabela**, com probabilidade `—` (não é risco, é requisito) e impacto `Crítico`. Exemplo real Sergipetec:

| Risco | Prob. | Impacto | Mitigação |
|-------|:-----:|:-------:|-----------|
| **Compliance: lista física obrigatória (CVT-003)** | — | Crítico | A lista física é preservada e pré-preenchida; o aluno assina — o artefato existe |
| **Compliance: retenção de 5 anos (ASP-003)** | — | Crítico | Versionamento com 30 versões; verificação SHA-256 semanal |

**⚠️ Estrutura completa é inegociável.** O usuário corrigiu explicitamente quando a seção de aprofundamento perdeu os diagramas TO BE, cronogramas faseados e tabelas de risco. O formato completo (Diferencial com metadados → TO BE → Cronograma → Metas → Custos → Riscos) deve ser mantido para cada solução, sem encurtar. A qualidade está na densidade de informação por solução, não no volume de texto narrativo.

### 3.4 Soluções Expandidas (arquivo separado)

As 15 soluções selecionadas são expandidas em **arquivo próprio** (`solucoes-expandidas.md`), separado da tabela de priorização. A `tabela-priorizacao.md` referencia este arquivo e não repete as expansões.

**Formato de cada solução expandida (~1 página):**

- **Header:** nome da solução, nós associados e categoria × tipo
- **Diferencial:** o que muda e por que importa — com menção a evidências das transcrições
- **Processo TO BE:** fluxo redesenhado (preferir diagrama ASCII)
- **Cronograma:** fases com durações (tabela compacta)
- **Metas:** KPIs com baseline e target (tabela)
- **Custos:** faixas de valor (não valores exatos), assumindo preferência por ferramentas de baixo custo e equipe interna
- **Riscos e Compliance:** tabela de riscos com mitigação; restrições de compliance como linhas com impacto Crítico

**Regras de redação:**

- **Ferramentas como referenciais, nunca prescritivas.** Ex.: "plataforma de planejamento visual (planilha enriquecida ou low-code)" — não "Airtable". A Sergipetec decide a implementação concreta.
- **Custos em faixas.** Ex.: "R$ 300–700" — não "R$ 530". A estimativa comunica ordem de grandeza sem falsa precisão.
- **~1 página por solução.** Densidade de informação, não volume de texto. Cada seção é concisa: 1–2 parágrafos de prosa + tabelas para cronograma, metas, custos e riscos.

### 3.5 Visão Consolidada

Ao final, gerar tabela-resumo com os 15 selecionados (3 × 4 setores + 3 intersetorial), custo total de implantação e mensal, e calendário sugerido de 12 semanas.

### 3.5 Pitfalls da Etapa 3

- ⚠️ **Soluções que interagem com artefatos físicos: prefira modelos multimodais a OCR.** Quando uma solução precisa ler documentos físicos (ex.: lista de presença manuscrita), usar modelo multimodal (Gemini Flash, GPT-4V) em vez de OCR tradicional. O multimodal lida com caligrafias variadas, entende contexto da página e recebe instruções em linguagem natural. Correção explícita do usuário na execução Sergipetec (S-009).
- ⚠️ **Terminologia palatável para tomadores de decisão leigos.** Evitar jargão técnico que assusta stakeholders não-técnicos. "State machine" vira **"motor inteligente de processos"** ou **"agente de IA que segue um processo estruturado"**. "OCR" vira **"leitura inteligente de documentos"**. Aplicar em todas as seções voltadas ao cliente (Diferencial, TO BE, sumário executivo). Correção explícita do usuário: "É importante que essas soluções soem palatáveis e empolgantes para os tomadores de decisão que são, em muitos sentidos, leigos."
- ⚠️ **Soluções "em elaboração" exigem estimativa por cluster.** A Etapa 2 frequentemente deixa blocos de soluções não detalhadas (ex.: "S-015 a S-024 — 10 soluções adicionais"). Na pontuação, atribuir a esses blocos a **média estimada do cluster**, indicando claramente que é estimativa (não pontuação individual).
- ⚠️ **Compliance check é obrigatório.** Toda solução candidata ao top 3 deve ser verificada contra as restrições extraídas das transcrições. Uma solução que "substitui" um artefato obrigatório (ex.: lista física) deve ser rejeitada ou ajustada para "aumenta" o artefato.
- **Processo TO BE em diagrama ASCII.** Facilita leitura e versionamento em Markdown. Não usar imagens — o ASCII é auto-contido e diff'ável no git.
- **KPIs com baseline e target.** Para cada meta de performance, declarar o valor atual (baseline) e o valor esperado (target). Ex.: "Tempo de conferência manual: baseline ~4h/mês → target <10 min/mês".

**Commit ao final:**
```bash
git add etapa-3-avaliacao/ && git commit -m "etapa 3: top 3 por setor + top 3 intersetorial — compliance check (N restrições)" && git push
```

A Etapa 3 produz dois arquivos complementares: `tabela-priorizacao.md` (pontuação + seleção) e `solucoes-expandidas.md` (projetos de implantação). Ambos são commitados juntos.

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
**Requisitos:**
- `vercel` CLI instalado e autenticado (`npx vercel login`)
- Projeto configurado como static site (sem build step — o agy já entrega HTML final)
- Domínio customizado se disponível; caso contrário, usar o domínio `.vercel.app` padrão

O deploy é a etapa final — só executar quando todas as 4 telas estiverem completas, testadas e commitadas.

## Etapa 5 — Verificação de Entregáveis vs. Contrato (QA Gate)

### 5.1 Propósito

Antes de entregar ao cliente, verificar se todos os entregáveis previstos no **contrato/escopo do projeto** estão cobertos pelo output real do pipeline. Esta etapa é um **quality gate** que audita e documenta gaps.

**Após auditar, ofereça-se para preencher os gaps encontrados** — se o cliente autorizar (ou se houver instrução explícita no pedido), crie os entregáveis faltantes como etapa adicional no repositório do projeto, não como modificação das etapas existentes (ex.: `etapa-5-nome-do-entregavel/`).

**⚠️ Proprietary frameworks (EAI Score, metodologias proprietárias do cliente) pertencem ao projeto, não à skill.** Se um contrato especifica um framework proprietário da consultoria (ex.: EAI Score), ele deve ser aplicado como uma etapa específica do projeto (`etapa-N/`) e NUNCA incorporado a esta skill genérica. A skill deve permanecer metodologia-agnóstica — ela descreve *como executar o pipeline*, não *qual framework de avaliação usar*. O framework específico vive no repositório do cliente.

**Quando executar:** após Etapa 4 (site deployed), antes da reunião de entrega.

**Tooling:** usar a skill `google-workspace` (comando `GAPI`) para acessar Google Drive e Docs. **Nunca** usar scripts Python ad-hoc com service account.

### 5.2 Método

1. **Encontrar o contrato no Drive:**
   - Tentativa 1 — busca específica: `GAPI drive search "<projeto> contrato"` ou `GAPI drive search "Diagnóstico <projeto>"`
   - Tentativa 2 — busca ampla: `GAPI drive search "contrato"` e filtrar manualmente os resultados por nome que contenha o projeto
   - Contratos podem estar em formato **Google Docs** (`.vnd.google-apps.document`) ou **PDF**. Verificar ambos.
   - Extrair conteúdo com `GAPI docs get <DOC_ID>` (para Google Docs) ou `GAPI drive download <FILE_ID> --export-mime text/plain` (para PDF)
2. Extrair a lista de entregáveis do contrato (Objeto, Anexo I, seção de Entregáveis).
   - **Contratos frequentemente têm Anexos separados** — verificar pasta inteira do Drive, não apenas o documento principal.
   - Entregáveis não-documentais (ex.: reuniões, treinamentos) marcar como 🟡 e documentar o que existe como apoio.
3. Mapear artefatos do repo: para cada entregável, procurar o arquivo correspondente.
4. Classificar: 🟢 completo, 🟡 parcial (existe mas sem conteúdo específico do contrato), 🔴 não existe.
5. Documentar gaps com explicação do que falta e onde deveria estar.
6. Se o usuário autorizou o preenchimento de gaps, criar os entregáveis faltantes como `etapa-<N>-<nome>/` (a próxima etapa disponível), com documentação completa. Não modificar etapas existentes.
7. Tabela de compliance vira sumário executivo da reunião de entrega.

### 5.3 Template

```markdown
| # | Entregável (contrato) | Artefato no repo | Status | Observação |
|---|----------------------|------------------|:------:|------------|
| 1 | Entregável X | `path/para/arquivo` | 🟢 | OK |
| 2 | Entregável Y | — | 🟡 | Classificação existe, sem o framework formal |
```

### 5.4 Pitfalls

- ⚠️ **Usar google-workspace skill** (GAPI CLI) para Drive/Docs — não scripts Python com service account.
- ⚠️ **Contratos podem ter anexos separados** (Anexo I, Termo de Referência). Verificar toda a pasta do Drive.
- ⚠️ **Entregáveis não-documentais** (Sessão Executiva) marcar como 🟡 — site/deck existe mas reunião não é reproduzível no repo.
- ⚠️ **Pipeline entrega MAIS que o contrato** — destacar isso como valor agregado.
- ⚠️ **Contrato pode ser Google Docs (não PDF)** — `GAPI drive search` retorna ambos. Para Google Docs use `docs get <ID>`; para PDF use `drive download <ID> --export-mime text/plain`.
- ⚠️ **Busca genérica por "contrato" retorna muitos resultados** — refinar com nome do projeto + "contrato" ou "diagnóstico". Ex.: `drive search "Diagnóstico de IA"` antes de cair para `"contrato"`.
- ⚠️ **Frameworks proprietários do cliente NÃO pertencem à skill.** Se a Etapa 5 detectar que um entregável contratual exige um framework específico (EAI Score, métrica proprietária, questionário exclusivo), implemente-o como etapa separada no repositório do projeto. A skill descreve o pipeline genérico — o framework específico é conteúdo do projeto.

### 5.5 Handoff — Entrega ao Cliente

Após QA Gate aprovado e eventuais gaps preenchidos, realizar o handoff em 3 passos:

**Passo 1 — Empacotar entregáveis por item contratual:**
Para cada entregável do contrato, criar um ZIP nomeado `<N> - <Nome do Entregável>.zip` contendo exclusivamente os artefatos daquele item. Os ZIPs devem ser auto-contidos e numerados de 1 a N conforme a ordem do contrato.

```bash
# Padrão: usar ZIP via Python (zipfile module) para evitar dependência de zip CLI
python3 -c "
import zipfile, os
with zipfile.ZipFile('1 - Relatorio de Gargalos.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('etapa-1-analise'):
        for f in files:
            zf.write(os.path.join(root, f))
"
```

**Passo 2 — Organizar no Drive do cliente:**
- Copiar POPs, diagramas e documentos de suporte para uma subpasta `Entregáveis/` na raiz do projeto no Google Drive
- Nomear arquivos copiados com prefixo do processo (ex.: `ASP-001 - POP Detalhado`) para identificação independente da estrutura de pastas original
- Usar a API do Google Drive via service account ou GAPI para copiar, não mover — manter originais intactos

**Passo 3 — Comunicar entrega:**
Redigir email à diretoria do cliente em tom consultivo:
- Listar entregáveis contratuais versus o que foi entregue
- Destacar valor agregado (itens extras não contratados)
- Incluir link para a pasta do Drive
- Manter tom direto, sem jargão técnico, mas também sem enrolação
- Enviar rascunho para revisão do consultor antes do envio final

---
## Orquestração Geral

### Sequência de Execução

```
Etapa 1 ──→ Etapa 2 ──→ Etapa 3 ──→ Etapa 4 ──→ Etapa 5 (Verificação Contratual)
  │            │            │            │               │
  │            │            │            │               └── Hermes (auditoria, 1 etapa)
  │            │            │            └── agy (iterativo) + humanizer + copywriting
  │            │            └── Hermes (sequencial, 1 etapa)
  │            └── Hermes (iterativo, grupos de nós)
  └── Pi Agent × setor (paralelo) + Pi Agent final (global)
```

### Modelos

| Etapa | Modelo | Justificativa |
|-------|--------|---------------|
| 1. Análise | **MiniMax M3** (opencode-go) — Pi Agent × setor + Pi Agent final global | Contexto longo + multimodal (lê imagens de diagramas) |
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

# 2. Análises sistêmicas setoriais (HTML)?
ls etapa-1-analise/setor-*/analise-sistemica.html && grep -c "d3" etapa-1-analise/setor-*/analise-sistemica.html

# 3. Relatório de integração global?
ls etapa-1-analise/relatorio-integracao.md

# 4. Análise sistêmica global (HTML cross-setor)?
ls etapa-1-analise/analise-sistemica.html && grep -c "cross-setor\|SETOR-" etapa-1-analise/analise-sistemica.html

# 5. Número de soluções coerente?
grep -c "^### S-" etapa-2-brainstorming/propostas-solucoes.md

# 5b. Vulcano usado? (deve ser ≥ número de clusters)
grep -c "Referência:" etapa-2-brainstorming/propostas-solucoes.md

# 6b. Top 3 por setor identificados?
grep -c "🥇\\|🥈\\|🥉" etapa-3-avaliacao/tabela-priorizacao.md

# 6c. Soluções expandidas em arquivo separado?
ls etapa-3-avaliacao/solucoes-expandidas.md && grep -c "^## " etapa-3-avaliacao/solucoes-expandidas.md

# 7. Site funcional?
ls etapa-4-site/*.html

# 8. Git remoto atualizado?
git log --oneline -5
```

---

## Pitfalls Gerais

⚠️ **Pi Agent com MiniMax M3 pode ser caro.** Monitorar tokens por setor via `pi-session-audit`. Se estourar orçamento, reduzir contexto (só POPs, sem diarização).

⚠️ **Cores das classificações nos diagramas:** Tríade: Cultural = #66E8F1 (electric-teal), Técnica = #4AC6D3 (teal-ciano), Organizacional = #4AC6D3 (teal-ciano). Gold removido da paleta ID.

⚠️ **TODAS as arestas devem ter arrowheads** (setas direcionais preenchidas). Arestas tracejadas (reforço negativo/mitigação) NUNCA devem ter `marker-end: null`. O marcador é idêntico para ambos os tipos: `url(#arrow)`.

⚠️ **Labels +/- próximos à seta**, não no ponto médio. Posicionar a 78% da distância source→target: `d.source.x*0.22 + d.target.x*0.78`. O label no meio da aresta dificulta a associação visual com a direção da seta.

⚠️ **Linhas tracejadas devem ser visíveis.** Mesma opacidade das sólidas (0.55), largura 1.5px, dasharray 6,4. Se ficarem com opacidade 0.4 ou largura 1px, são praticamente invisíveis em fundo escuro.

⚠️ **Markdown deve ser convertido para HTML** nos textos de análise de ciclos e descrições de nós. `**texto**` → `<strong>texto</strong>`, `*texto*` → `<em>texto</em>`, `` `código` `` → `<code>código</code>`. O navegador não renderiza markdown cru — aparece como texto literal.

⚠️ **Descrições de ciclos e nós: sweet-spot = 2 parágrafos.** Ciclos: 1º parágrafo = mecanismo causal específico, 2º = consequência + ponto de intervenção. Nós: 1º = descrição do problema, 2º = evidência literal + natureza + processos afetados. Descrições de 1 linha são genéricas demais; 3+ parágrafos são excessivos para leitura rápida.

⚠️ **Soluções não são lista de ferramentas.** Correção explícita do usuário. A solução descreve alteração no processo, a ferramenta é meio. Foco em "como o trabalho muda".

⚠️ **Trilha sonora não pode ser obrigatória.** Áudio com autoplay é bloqueado por navegadores. Implementar como opt-in (botão "Ativar som").

⚠️ **agy para sites completos exige estratégia iterativa.** Não gerar tudo de uma vez. Usar o workflow: esqueleto → seções → JS → montagem. Ver skill `agy` para o padrão completo de Full Site Generation.

⚠️ **Não confundir guias de estilo.** O pipeline é sempre ID Consultoria. Se o usuário não especificar marca, ID Consultoria é o padrão deste pipeline.

⚠️ **Relatórios de efetividade de ferramenta: separar intrínseco de extrínseco.** Quando o usuário pede análise da efetividade de uma ferramenta usada no pipeline (Vulcano, Pi Agent, agy), o relatório DEVE ter duas seções distintas: (a) Sumário Executivo analisando a robustez INTRÍNSECA da ferramenta (indexação, conteúdo, arquitetura), e (b) Considerações Finais com limitações EXTRÍNSECAS (protocolo de uso, cobertura do vault, custo de contexto). Não fundir as duas — o usuário corrigiu isso explicitamente. Template completo em `references/relatorio-efetividade-template.md`.

⚠️ **Markdown nunca deve ser convertido via regex no HTML final.** Os caracteres `**`, `*` e `` ` `` aparecem no código JavaScript do D3.js. Aplicar regex de conversão ao HTML completo corrompe o script e faz os nós desaparecerem. A conversão de formatação deve ser feita nas strings Python ANTES de concatená-las ao template HTML. Use `<strong>`, `<code>`, `<em>` diretamente nas f-strings do gerador. Ver `references/generator-template.py` para o padrão correto.

⚠️ **ZIP para revisão humana sempre inclui LEIA-ME.md.** Quando o usuário pedir ZIP da etapa ("faça o ZIP para revisão humana"), gerar o ZIP com zipfile e incluir um `LEIA-ME.md` na raiz do repositório com: estrutura de pastas explicada, ordem sugerida de leitura, como interagir com os HTMLs, tabela de cores e seus significados, resumo dos achados por setor, e menção às próximas etapas. O LEIA-ME.md é commitado junto com o resto. Ver o LEIA-ME.md do Sergipetec como referência de formato.

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
| 2026-06-19 | Hermes (run real Sergipetec) | Pitfall crítico documentado: markdown nunca via regex no HTML final (corrompe JS do D3). Adicionado `references/generator-template.py` como referência canônica de código. Specs atualizadas com regra de tags HTML diretas. |
| 2026-06-19 | Hermes (run real Sergipetec) | Specs atualizadas com identidade visual ID Consultoria (cores gold/teal/indigo, fontes Bricolage+Nunito+IBM Plex). Adicionados símbolos +/- nas arestas dos diagramas. Pitfall: ZIP para revisão humana sempre inclui LEIA-ME.md. Referência: `references/html-regeneration-pattern.md` para regeneração de HTMLs pelo Hermes. |
| 2026-06-19 | Hermes (revisão pós-sessão) | Adicionados 6 pitfalls visuais/D3.js da execução real: cor organizacional #6366F1 (não #4AC6D3), todas as arestas com arrowheads, labels +/- a 78%, linhas tracejadas com mesma opacidade, markdown→HTML obrigatório, sweet-spot 2 parágrafos. `references/html-regeneration-pattern.md` reescrito com todas as regras. |
| 2026-06-19 | Hermes (validação Vulcano) | Etapa 2: protocolo Vulcano tornado **obrigatório** (1 vulcano_context por cluster), adicionada Ficha de Engrama (4 campos: arquitetura, métricas, armadilhas, contraindicações), citação de engrama obrigatória em cada solução. Novo pitfall: subutilização do Vulcano (2 chamadas = nota 1.2/10; 7+ chamadas = nota 7.2/10). Adicionado `references/vulcano-brainstorming-protocol.md` com protocolo completo e verificação de qualidade. |
| 2026-06-19 | Hermes (revisão de efetividade) | Adicionado `references/relatorio-efetividade-template.md` com estrutura de relatório de efetividade de ferramenta (Sumário Executivo intrínseco + Considerações Finais extrínsecas). Novo pitfall: separar limitações da ferramenta das limitações do contexto/projeto. |
| 2026-06-19 | Hermes (revisão Etapa 3) | Metodologia alterada: de top 10 global para top 3 por setor (ASP, Jurídico, Inovação, CVT) + top 3 intersetorial. Adicionado compliance check obrigatório contra restrições extraídas das transcrições (ex.: lista física do CVT, fluxo físico do Jurídico). Novo pitfall: preferir modelos multimodais a OCR para leitura de artefatos físicos (S-009). Seção 3.0 com princípio; 3.2 com seleção setorial; 3.4 com visão consolidada. |
| 2026-06-22 | Hermes (Sergipetec QA Gate) | Etapa 5: propósito atualizado — após auditar gaps, o agente deve oferecer-se para preenchê-los (não apenas reportar). Adicionado pitfall: frameworks proprietários (EAI Score) pertencem ao projeto, não à skill. Adicionada seção 5.5 Handoff com 3 passos (pack ZIPs → Drive → email). Método refinado: busca por "contrato" é muito genérica — tentar termos específicos com nome do projeto primeiro. Adicionados pitfalls: Google Docs vs PDF, busca refinada. Histórico adicionado ao final da seção. |
