---
name: hephaistos
description: "Hephaistos meta-framework — orquestra pipelines de projeto com Hermes, OpenCode e agy.

Load this skill when starting a new software or branding project. Cobre 6 modos de pipeline (INCEPTION a DEPLOY), orquestração via delegate_task, subagentes OpenCode para código TDD, agy (Antigravity CLI) para design visual, vault cognitivo com 237+ engramas, e pipeline de design em 3 fases com entregáveis HTML auto-contidos."
version: 1.10.0
author: Tácio Brito
license: MIT
platforms: [linux, macos]
created_by: agent
metadata:
  hermes:
    tags: [meta-framework, pipeline, orchestration, delegation, opencode, antigravity]
    related_skills: [opencode, hermes-agent, antigravity-design, design-research-moodboard, daedalus-core, daedalus-geometry, daedalus-material, daedalus-motion, daedalus-render, local-code-agent, obsidian]
type: Orchestrator
timestamp: 2026-06-19T19:47:50Z
---

# Hephaistos 🔥🔨

> Meta-framework de construção de projetos. Forja ideias em MVPs reais com pipeline unificado de 6 modos + Hermes como orquestrador + subagentes.

## Visão Geral

Hephaistos é um **meta-framework** — um framework *para criar frameworks de projeto*. Ele elimina decisões repetitivas de estrutura, pipeline e skills, garantindo qualidade desde o primeiro dia.

## Arquitetura de Agentes (Pipeline v3.1)

```
┌─────────────────────────────────────────────────────────────┐
│  HERMES (Orquestrador)                                       │
│  Interpreta o modo → divide tarefas → delegate_task(tasks)   │
│                                                              │
│  delegate_task(tasks=[...])                                   │
│    ├── OpenCode → código (TDD, features, testes)             │
│    │   toolsets: [terminal, file]                             │
│    │                                                          │
│    ├── agy (Antigravity) → design visual, revisão            │
│    │   toolsets: [terminal, file, web]                        │
│    │                                                          │
│    ├── Daedalus → assets 3D, texturas, animação              │
│    │   skills: daedalus-{core,geometry,material,motion,render}│
│    │   toolsets: [terminal, file, web]                        │
│    │                                                          │
│    └── Hermes (auxiliar) → docs, vault, pesquisa             │
│        toolsets: [web, file]                                  │
└─────────────────────────────────────────────────────────────┘
```

### Daedalus — Subagente 3D & Motion (v1.0)

Daedalus é o especialista em assets 3D do Hephaistos. Opera via 5 engramas (skills) em `~/.hermes/skills/daedalus/` que disparam em cascata:

| Engrama | Função | Templates |
|---------|--------|-----------|
| `daedalus-core` | Briefing, gatilhos, orquestração | `briefing.py` |
| `daedalus-geometry` | Modelagem (vaso, troféu, cristal) | `shape_vase.py` |
| `daedalus-material` | Texturas PBR (Poly Haven API + procedural) | `pbr_from_polyhaven.py`, `procedural_ceramic.py` |
| `daedalus-motion` | Animação (turntable, rig, física) | `animate_turntable.py` |
| `daedalus-render` | Iluminação, render EEVEE/Cycles, export | `studio_lighting.py` |

**Fluxo típico:** `Hephaistos → delegate_task → Daedalus` gera geometria → busca textura Poly Haven → ilumina → renderiza previews → exporta GLB/Blend. Visual feedback (EEVEE snapshots) obrigatório a cada passo. Briefing de 3 perguntas antes de criar. Poly Haven API integrada para mapas PBR (Diffuse, Rough, nor_gl, AO, Displacement, arm).

## Arquitetura Cognitiva (Engramas) 🧠⚡

> Desde v2.1, Hephaistos funciona como uma **mente neurodivergente e superdotada** — engramas atômicos, links associativos, hiperfoco seletivo e processamento paralelo.

### Conceito

**Engramas** são documentos atômicos (≤100 linhas) contendo **um conceito cada**. Eles substituem monólitos de documentação por uma rede de conhecimento linkada.

### 5 Dominios (237+ Engramas)

| Dominio | Conteudo | Quantidade |
|---------|----------|-----------|
| **design/** | UI/UX, branding, tipografia, Lovable, Glassmorphism | 27 |
| **infraestrutura/** | DevOps, self-hosted, Coolify, Dokploy, Directus | 11 |
| **orquestracao/** | MCP, workflows, automacao, editores IA | 29 |
| **ia-agentes/** | LLMs, agentes, skills, inferencia local, RAG | 39 |
| **recursos/** | Ferramentas, sites, seguranca, criadores, metodologias | 132 |
| **Total** | | **237** |

### Padrão de Cada Engrama

```markdown
# Engrama/Workflow/Decisão/Referência: Nome

> Resumo em uma linha do conceito.

## Seções principais

Conteúdo direto e técnico. Tabelas, listas, blocos de código.

## Links Associativos

### Mesmo cluster
- [[engrama-relacionado]] — Descrição

### Cross-cluster
- [[outro-cluster-engrama]] — Descrição

### Opostos
- [[engrama-oposto]] — O que NÃO fazer / alternativa
```

### Vault Unificado (completado em 2026-06-17)

O sistema opera com **um único vault em ext4 nativo** em `~/vaults/hephaistos/`.

#### Estrutura do Vault (Pipeline v3.1)

```
hephaistos/
├── _contexto/           → META-FRAMEWORK (estado, decisoes, instrucoes)
│   ├── estado-atual.md  → O que esta acontecendo agora
│   ├── fio-do-projeto.md → Historico completo
│   ├── decisoes-tomadas.md → Decisoes estruturais
│   ├── pipeline-v3.md   → Nova pipeline documentada
│   └── instrucoes-ai.md → Como IAs devem operar
│
├── _compact/            → RESUMOS COMPACTOS (para contexto de IA)
│   ├── projeto.md       → Resumo executivo
│   ├── tech.md          → Ficha tecnica
│   └── cache-contexto.md → Referencia rapida para IAs
│
├── visao/               → VISAO ESTRATEGICA
├── arquitetura/         → ARQUITETURA TECNICA
│
├── projetos/            → PROJETOS (autonomos)
│   ├── hermes-flatpak/  → 13 arquivos
│   ├── jogo-da-solidariedade/ → 8 arquivos
│   ├── sergipetec/      → 1 arquivo
│   └── peachweb/        → 3 engramas
│
└── engramas/            → CONHECIMENTO GERAL (nao-projeto)
    ├── design/          → UI/UX, branding, tipografia (27)
    ├── infraestrutura/  → DevOps, self-hosted (11)
    ├── orquestracao/    → MCP, workflows (34)
    ├── ia-agentes/      → LLMs, agentes (39)
    └── recursos/        → Ferramentas, sites (131)
```

#### Separação de Dados: Projeto vs Arquitetura

**Regra fundamental:** Dados de projeto NÃO se misturam com dados de arquitetura/memoria.

| Tipo de dado | Onde vai | Exemplo |
|--------------|----------|---------|
| Briefing do projeto | `projetos/{nome}/visao/briefing.md` | Briefing do Jogo da Solidariedade |
| Design system do projeto | `projetos/{nome}/design/specs/` | Design system HTML |
| Metodologia de design | `engramas/design/` | `engrama-design-tokens.md` |
| Ferramenta específica | `engramas/recursos/` | `engrama-security-owasp-top-10.md` |
| Decisão arquitetural | `projetos/{nome}/arquitetura/adr.md` | ADR do projeto |
| Decisão do framework | `_contexto/decisoes-tomadas.md` | Decisão sobre pipeline |

**Dados irrelevantes:** Tabelas de preços, comparativos de custo, informações de assinatura. O vault é repositório de conhecimento técnico, não catálogo de compras.

📖 [[references/project-migration-pattern.md]] para workflow completo de migração de projetos.

#### Estrutura Padrão de Projeto

Cada projeto em `projetos/` segue esta estrutura:

```
projetos/{nome}/
├── _contexto/           → estado-atual, fio-do-projeto, decisoes
├── _compact/            → resumo executivo
├── visao/               → briefing, personas, roadmap
├── arquitetura/         → stack, adr, api
├── design/              → research, specs, wireframes
├── src/                 → codigo fonte
└── engramas/            → conhecimento especifico do projeto
```

### Sprint Plan Reference

O plano de sprints vive em `~/vaults/hephaistos/SPRINTS.md`. SEMPRE consulte este arquivo antes de propor ou iniciar trabalho.

| Sprint | Status | Descrição |
|--------|--------|-----------|
| 1 — Fundação | ✅ Completa | Reestruturação com engramas + gaps + Lovable (+25 engramas) |
| 2 — Referências Visuais | ✅ Completa | Awwwards, Godly, Mobbin, Dribbble, Behance (+25 engramas) |
| 3 — Segurança | ✅ Completa | OWASP, SAST/SCA, secret scanning, SIEM, SOC2, zero trust (+12 engramas) |
| 4 — Peachweb | ✅ Completa | Metodologia, padrões visuais, DaaS (+3 engramas) |
| 5 — Criadores/Cursos | ✅ Completa | Criadores, metodologias, learning roadmaps (+6 engramas) |
| 6 — Skills/Conectores | ✅ Completa | MCP servers, automation workflows (+2 engramas) |
| 7 — Limpeza/Verificação | ✅ Completa | 34 renames, 0 broken links, condensação |

**Total: 305 .md no vault, 241+ engramas, 82 skills Hermes**

**NUNCA invente sprints, fases ou modos que não estão neste plano.**

### Navegação

O `index.md` do vault do projeto oferece navegação:
- **Por modo** — Quais engramas ler em INCEPTION, DESIGN, etc.
- **Por tópico** — "Como evitar AI slop?", "Como fazer TDD?"
- **Links cruzados** — Associações inesperadas entre clusters

### Como Criar Novo Engrama

1. Identificar o cluster correto (pipeline, design, codigo, workflows, decisoes, referencias)
2. Nomear com prefixo: `engrama-`, `workflow-`, `decision-`, `ref-`
3. Usar o padrão de template acima
4. Adicionar links associativos (3 categorias: mesmo cluster, cross-cluster, opostos)
5. Atualizar `index.md` com o link no lugar certo

> Para template detalhado, lista completa dos 26 engramas e regras de navegação, veja [[references/engrama-creation-pattern.md]]

### Knowledge → Engrama-Skill Pipeline (Daedalus Pattern)

After raw research has been distilled into Obsidian engramas (via Batch Creation above), the next step is to refactor them into **Hermes skills** using Daedalus's structural pattern. This is the missing link between "conhecimento bruto" and "agente executável."

#### Daedalus Structural Pattern (the mold)

Cada engrama-skill Hermes segue esta estrutura:

```
~/.hermes/skills/<dominio>/<engrama-name>/
├── SKILL.md                      # Frontmatter + identidade + workflow
├── templates/                    # Scripts executáveis
│   ├── script_um.py
│   └── script_dois.sh
└── references/                   # Documentação técnica
    └── api-doc.md
```

O SKILL.md DEVE ter frontmatter completo:

```yaml
---
name: engrama-name
description: "Descrição funcional do que este engrama faz"
triggers:
  - "palavras-chave|que|disparam|este|engrama"
model_recommendation:
  primary: opencode-go/deepseek-v4-flash
  premium: opencode/claude-sonnet-4
memory_namespace: dominio
dependencies: []
---
```

#### Workflow de Refatoração

1. **Identificar conhecimento maduro** — Pesquisa Lovable, gaps dos complementos, referências visuais
2. **Definir escopo do engrama-skill** — O que ele FAZ (não apenas o que ele DOCUMENTA)
3. **Criar SKILL.md** com frontmatter (triggers, deps, quality gates)
4. **Adicionar templates/** — Scripts que o engrama executa via terminal
5. **Adicionar references/** — Documentação técnica (APIs, quirks, comandos)
6. **Registrar dependências** — no SKILL.md e no `related_skills` do skill pai
7. **Testar** — `hermes run` com prompt compatível com triggers

#### Exemplo Praticado: Daedalus

O Daedalus (3D asset pipeline) foi o primeiro engrama-skill criado neste padrão:

| Engrama | Função | Templates |
|---------|--------|-----------|
| `daedalus-core` | Briefing, gatilhos, orquestração | — |
| `daedalus-geometry` | Modelagem (vaso, troféu, cristal) | `shape_vase.py` |
| `daedalus-material` | Texturas PBR (Poly Haven API + procedural) | `pbr_from_polyhaven.py`, `procedural_ceramic.py` |
| `daedalus-motion` | Animação (turntable, rig, física) | `animate_turntable.py` |
| `daedalus-render` | Iluminação, render EEVEE/Cycles, export | `studio_lighting.py` |

**Próximas skills a refatorar neste padrão (Sprint 6):**
- `mcp-design-systems` — Integração com MCP servers de design
- `vibe-coding` — Workflow de vibe coding com Lovable/Cursor/v0
- `awwwards-scraper` — Scraping de sites premiados para referência
- `security-audit` — Checklist de segurança para projetos

#### Regras

1. **NUNCA crie engrama-skill sem frontmatter** — triggers e deps são obrigatórios
2. **NUNCA crie engrama-skill sem templates/ ou references/** — se não tem código nem docs, é um engrama de conhecimento (vai para o Obsidian vault)
3. **NUNCA confunda engrama de conhecimento (markdown) com engrama-skill (Hermes skill)** — o primeiro DOCUMENTA, o segundo EXECUTA
4. **Daedalus é o MOLDE, não o fim** — o padrão estrutural é para TODAS as skills, não apenas 3D

### SPRINTS.md Consolidation

Para arquivos SPRINTS.md grandes (>200 linhas), dividir em arquivos menores por sprint:
- Manter `SPRINTS.md` como indice simplificado (~50 linhas)
- Criar `notas-de-sessao/sprint-N-*.md` para cada sprint
- Atualizar wikilinks apos consolidacao
📖 [[references/sprint-consolidation-pattern.md]] para workflow completo.

### Vault Cache Pattern

Para manter o cache de contexto atualizado, usar o script `scripts/update-cache.sh`:
```bash
bash ~/vaults/hephaistos/scripts/update-cache.sh
```
📖 [[references/vault-cache-pattern.md]] para detalhes completos.

### Batch Creation from Research

Quando voce tem um documento massivo de pesquisa (54KB+ com 100+ entradas), NAO crie engramas manualmente um por um. Use este workflow:

1. **Parse para JSON** — Leia o documento completo, extraia cada entrada com metadados (nome, descricao, URL, exemplos, recursos) usando `execute_code` com Python
2. **Salve dados brutos** — Escreva JSON em lugar acessivel (ex: `/home/taciobrito/.hermes/<projeto-research>/collections-data.json`)
3. Gere engramas em lote — Um script Python que itera sobre os dados e escreve N engramas simultaneamente em `~/vaults/hephaistos/engramas/<cluster>/`
4. **Crie indice de referencia** — Gere um `awwwards-index.md` com tabela de todos os engramas criados
5. **Atualize o indice mestre** — Patch no `engramas/index.md` para incluir links para os novos engramas

**Regra de ouro:** Cada entrada de pesquisa vira UM engrama com: descricao completa, exemplos reais, ferramentas mencionadas, links para fonte original e principios de design extraidos. O engrama deve ser consultavel de forma independente.

**Exemplo praticado:** Pesquisa Awwwards (100 colecoes, 1013 linhas) -> 9 engramas em `engramas/referencias/awwwards-*.md`. Acionaveis via Fase 0 do DESIGN mode (ver [[awwwards-index.md]]).

**Workflow completo documentado:** Para pesquisas grandes (JSON 170KB+, 97+ coleções), usar [[references/vault-construction-from-research.md]] — cobre jq para parsing, divisão em batches de subagentes, criação de engramas em lote, atualização de index, e métricas de sprints realizadas.

## Ao criar engramas de pesquisa: profundidade completa, nao apenas padroes

NUNCA gere engramas que listam apenas padroes superficiais. Cada engrama precisa capturar:
- **Ferramentas mencionadas** — nomes, versoes, links
- **Exemplos reais** — sites nomeados, com descricao do que fazem
- **Recursos tecnicos** — bibliotecas, metodos, abordagens
- **Principios de design** — o que torna aquela abordagem vencedora
- **Contexto completo** — colecoes relacionadas, curadores, tamanho, seguidores

O usuario corrigiu explicitamente: "Nao e apenas extrair padroes de design e aprender eles, ter em contexto, as ferramentas, padroes, referencias, tudo."

## 🛑 REGRA FUNDAMENTAL: Aprovação do Usuário

**NADA avança sem aprovação explícita do usuário.** Esta é a regra mais importante do Hephaistos.

### Obrigações em Cada Modo

| Modo | Obrigação | Entregável de Aprovação |
|------|-----------|------------------------|
| **INCEPTION** | Entrevista de discovery com o usuário para entender contexto, dores, objetivos | Notas da entrevista + escopo validado |
| **DESIGN** | Entrevista de dores/necessidades com o usuário ANTES de criar qualquer artefato visual. Gerar mapa de empatia. | Mapa de empatia + direção visual validada |
| **IMPLEMENTACAO** | Usuário aprova design system + protótipo antes de codar | Design system + protótipo OK |
| **REVISAO** | Usuário revisa implementação e aprova mudanças | Code review + design review OK |
| **DEPLOY** | Usuário aprova versão para deploy | Release candidate OK |
| **ATUALIZACAO** | Usuário aprova atualizações de vault/documentação | Vault sincronizado OK |

### Fluxo de Gate

```
┌─────────────────────────────────────────────────────────┐
│  Hephaistos pergunta: "Posso prosseguir para [MODO]?"    │
│  Usuário: SIM / REVER (com feedback) / DEPOIS            │
│                                                          │
│  Se REVER → Hephaistos ajusta e pergunta novamente       │
│  Se DEPOIS → Hephaistos encerra e salva estado           │
│  Se SIM → Hephaistos avança para o modo                  │
└─────────────────────────────────────────────────────────┘
```

### Checklist de Aprovação (antes de cada gate)

- [ ] **Entrevista com usuário realizada?** (INCEPTION: discovery. DESIGN: dores/necessidades)
- [ ] **Mapa de empatia gerado?** (obrigatório no DESIGN)
- [ ] **Usuário conferiu e deu OK?** Explícito, por escrito
- [ ] **Feedback do usuário registrado?** Em `decisoes-tomadas.md` ou `notas-de-sessao/`
- [ ] **Decisão documentada?** O que foi aprovado, o que ficou pendente

### Penalidades por Violação

1. **Pular entrevista** — O usuário perde confiança, o design não atende às reais necessidades
2. **Pular aprovação** — Retrabalho garantido, desperdício de tempo e recursos
3. **Pular mapa de empatia** — Design desconectado da realidade do usuário

> **Sempre perguntar. Nunca presumir.** O usuário é o dono do produto, Hephaistos é o artesão.

## Pipeline de 6 Modos

## Modos vs Subagentes

| Modo | Subagente Principal | Ação | Entregáveis HTML |
|------|-------------------|------|-----------------|
| **INCEPTION** | Hermes (auxiliar) | Definir escopo, JTBD, métricas. Pesquisa web via Hermes. | — |
| **DESIGN** | agy + design-research-moodboard | **Fase 1:** Pesquisa visual → moodboards **HTML** · **Fase 2:** Design system **HTML** · **Fase 3:** Wireframes **HTML** (protótipo funcional navegável) | ✅ moodboard-[tema].html · ✅ design-system.html · ✅ prototipo.html |
| **IMPLEMENTACAO** | OpenCode | Código TDD. `opencode run 'implementar...'` | — |
| **REVISAO** | agy + OpenCode | agy revisa design, OpenCode revisa código | — |
| **DEPLOY** | OpenCode | CI/CD, Docker, scripts de produção | — |
| **ATUALIZACAO** | Hermes (auxiliar) | Sincronizar vault, watchdog, decisões | — |

### Fluxo do Modo DESIGN (Detalhado)

O modo DESIGN agora tem **três fases**:

**Fase 1: Pesquisa Visual (design-research-moodboard skill)**
1. Preencher briefing visual (`templates/briefing-visual.md`)
2. Pesquisar referências em múltiplas fontes (Pinterest, Dribbble, Behance, Mobbin, Refero)
3. Coletar 20-30 referências visuais
4. Analisar patterns e tendências
5. Criar 3 moodboards temáticos (`templates/moodboard.md`)
6. ✅ **Gerar HTML visual dos moodboards** (self-contained HTML com Tailwind CDN + Google Fonts + tokens inline — ver [[design-research-moodboard/references/html-deliverables.md]])
7. Gerar relatório final (`templates/relatorio-pesquisa-visual.md`)

**Fase 2: Design System (agy + HTML auto-contido)**
1. Usar moodboards como base
2. Definir paleta de cores, tipografia, espaçamentos
3. Criar componentes e patterns
4. ✅ **Gerar Design System HTML** (self-contained HTML — ver [[design-research-moodboard/references/html-deliverables.md]])

**Fase 3 — Wireframes / Protótipo HTML funcional (NOVA):**
1. ✅ **Gerar protótipo HTML funcional** (self-contained HTML — ver [[design-research-moodboard/references/html-deliverables.md]])
2. Preencher com conteúdo real do projeto, com navegação funcional, modais, estados e interações
3. Garantir consistência com moodboard e design system aprovados

**Fase 4 — Brand Showcase HTML (para projetos de Design/Branding):**
1. ✅ **Gerar apresentação HTML da identidade visual** (self-contained HTML — ver [[design-research-moodboard/references/brand-showcase-html.md]])
2. Quando a marca já está finalizada e o usuário quer apresentá-la ao cliente
3. Extrair paleta real da marca via PIL (NUNCA adivinhar cores)
4. Criar versão com marca d'água para download
5. Incluir compartilhamento via WhatsApp
6. Usar imagens cinematográficas de fundo (Unsplash/Pexels via curl)
7. Analisar sites de referência via browser_console para extrair padrões de design
8. Entregável: `apresentacao.html` na raiz do projeto (não em `design/`)

## Pré-requisitos

- **Hermes Agent** com `delegation` toolset habilitado (padrão já vem habilitado)
- **MiMo Code (mimo)** — `mimo --version` (v0.1.1+, instalado em ~/.mimocode/bin/mimo)
- **Antigravity CLI (agy)** — `~/.local/bin/agy` (v1.0.8+)
- Obsidian (para o vault de documentação)
- Acesso de escrita ao disco/partição de projetos (ex: `/run/media/taciobrito/ARQUIVOS/`)

## Instalação das Ferramentas

### OpenCode CLI
```bash
# Verificar
opencode --version

# Instalar se necessário
npm install -g opencode-ai@latest
```
Ver autenticação: `opencode auth list`

### Antigravity CLI (agy)
```bash
# Instalar (binary ~180MB)
curl -fsSL https://antigravity.google/cli/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"

# Autenticar (primeiro uso abre OAuth no browser)
agy -p "olá"

# Verificar
agy --version
```

**⚠️ VM Fix:** Se rodar em VM com erro "Illegal instruction", a CPU precisa do flag AES. Configure CPU tipo `host` e faça cold boot.

## Tipos de Projeto

O Hephaistos atende dois tipos principais de projeto, com estruturas de vault e fluxos distintos:

| Tipo | Exemplos | Entregáveis Típicos | Documento Primário |
|------|---------|-------------------|-------------------|
| **Software/Web** | SaaS, landing page, plataforma, API | Código, testes, deploy, infra | `visao/prd.md`, `arquitetura/stack.md` |
| **Design/Branding** | Logo, camisa, evento, identidade visual | Logo, mockups, artefatos para gráfica, banners | `visao/briefing.md` |

**Projetos de Design/Branding** usam a mesma estrutura de vault (`_contexto/`, `visao/`, `_compact/`, `arquivos/`) mas:
- `visao/briefing.md` substitui `visao/prd.md` como documento principal
- A pasta `arquivos/` guarda assets (gabaritos de gráfica, mockups, referências do cliente)
- Não há pastas `arquitetura/`, `modulos/` ou `infra/` — são irrelevantes para branding
- O fluxo do pipeline adapta-se: INCEPTION → DESIGN (entregáveis HTML) → entrega final

📖 [[references/whatsapp-project-intake.md]] — workflow completo de intake para projetos recebidos via WhatsApp.

## Fluxo de Orquestração (Hermes)

Quando iniciar um projeto com Hephaistos:

1. **Modo INCEPTION** — Hermes lê o vault, pesquisa mercado, define escopo, cria PRD ou briefing
2. **Modo DESIGN (3 fases + contexto Awwwards)** — Hermes orquestra:

   **Fase 0 — Carregar conhecimento de design Awwwards:**
   Antes de criar qualquer artefato visual, carregue o engrama Awwwards relevante ao tipo de projeto:
   - Paleta de cores → `engramas/referencias/awwwards-color.md`
   - Tipografia → `engramas/referencias/awwwards-typography.md`
   - Animações → `engramas/referencias/awwwards-animation.md`
   - Stack tech → `engramas/referencias/awwwards-technology.md`
   - UX/UI → `engramas/referencias/awwwards-ux.md`
   - Portfólio → `engramas/referencias/awwwards-portfolios.md`
   - Indústria → `engramas/referencias/awwwards-industries.md`
   - Storytelling → `engramas/referencias/awwwards-content.md`
   - Ferramentas → `engramas/referencias/awwwards-tools.md`
   Estes engramas contêm padrões extraídos de 100 coleções Awwwards (~13.000 sites) e garantem que o design do projeto siga tendências validadas.

   **Fase 1 — Pesquisa visual + Moodboards HTML:**
   ```python
   delegate_task(tasks=[{
       "goal": "Pesquisar referências visuais e criar 3 moodboards HTML para [projeto]",
       "context": "Briefing em [path]. Seguir padrão html-deliverables.md do skill design-research-moodboard para criar HTML auto-contido com Tailwind CDN + Google Fonts + tokens inline.",
       "toolsets": ["terminal", "file", "web"]
   }])
   ```
   Entregável: `design/research/moodboards/moodboard-[tema].html`

   **Fase 2 — Design System HTML:**
   ```python
   delegate_task(tasks=[{
       "goal": "Criar Design System completo em HTML para [projeto]",
       "context": "Moodboards aprovados em [path]. Seguir o padrão html-deliverables.md. Incluir tokens, componentes renderizados ao vivo, sidebar de navegação.",
       "toolsets": ["terminal", "file"]
   }])
   ```
   Entregável: `design/specs/design-system.html`

   **Fase 3 — Wireframes / Protótipo HTML funcional:**
   ```python
   delegate_task(tasks=[{
       "goal": "Criar protótipo funcional HTML com 6+ telas para [projeto]",
       "context": "Design system em [path]. Seguir o padrão html-deliverables.md. Preencher com conteúdo real do projeto. Garantir navegação entre telas.",
       "toolsets": ["terminal", "file"]
   }])
   ```
   Entregável: `design/wireframes/prototipo.html`

3. **Modo IMPLEMENTACAO** — Hermes delega para mimo CLI (MiMo Code):
   ```python
   delegate_task(tasks=[{
       "goal": "Implementar [feature] com TDD",
       "context": "Specs em [path], wireframes em [path], repositório em [path]",
       "toolsets": ["terminal", "file"]
   }])
   ```
   O subagente executa: `mimo run 'Implementar...'`
4. **Modo REVISAO** — agy revisa design visual, mimo revisa código
5. **Modo DEPLOY** — mimo executa scripts de CI/CD
6. **Modo ATUALIZACAO** — Hermes sincroniza vault, roda watchdog

**Regra de ouro:** `delegate_task` com `toolsets: ["terminal", "file"]` é o suficiente — o subagente Hermes invoca OpenCode/agy via `terminal()` internamente. Não precisa de ACP.

## Hierarquia por Custo de Modelo

| Camada | Ferramenta | Modelo | Custo | Uso |
|--------|-----------|--------|-------|-----|
| Orquestrador | Hermes | DeepSeek V4 Flash | Barato | Coordenação, contexto, modo |
| Codificação | OpenCode | DeepSeek V4 Flash | Barato | Implementação, testes |
| Estratégia | agy | Gemini 3.1 Pro | Caro | Design, revisão, pesquisa |
| Auxiliar | Hermes | DeepSeek V4 Flash | Barato | Docs, vault, contexto |

## Style Rules (user-enforced)

- **NUNCA usar emojis** — sempre Lucide icons (`<Star>`, `<AlertTriangle>`, `<Sparkles>`, `<Zap>`, etc.). Mapear glyphs/emojis para componentes Lucide importados. Em SVGs inline, usar `fill="currentColor"` e classes do design system.
- **Design visual SEMPRE delegado ao agy** — pesquisa visual, moodboards, revisão estética, auditoria visual, wireframes → `delegate_task` com subagente chamando `agy -p '...' --add-dir <path>`. Hermes NÃO faz design visual.
- **Copy em PT-BR** com o usuário. Código e commits em inglês.

## Distinção Fundamental: Trabalhar ON Hephaistos vs. WITH Hephaistos

**ON Hephaistos** = melhorar o framework em si. Adicionar engramas, atualizar a skill, refinar clusters, evoluir a arquitetura cognitiva.
**WITH Hephaistos** = usar o framework para construir projetos de clientes (jogo-da-solidariedade, sergipetec, desconsultor).

**REGRAS quando trabalhando ON Hephaistos:**
1. NUNCA crie um diretório separado em `projetos/` para melhorias do Hephaistos. O vault do Hephaistos E o projeto. Melhorias vao diretamente para `engramas/`, `_contexto/`, `modulos/` e a skill.
2. SEMPRE verifique `_contexto/arquitetura-cognitiva.md` (Fases 1-4) e `_contexto/estado-atual.md` antes de propor ou iniciar trabalho. O plano de evolucao ja existe.
3. Novos engramas vao para `engramas/<cluster>/` — nunca para `projetos/hephaistos-*/`.
4. Atualizacoes na skill vao para `~/.hermes/skills/autonomous-ai-agents/hephaistos/SKILL.md`.
5. Links associativos no `engramas/index.md` devem ser atualizados para referenciar novos engramas.
6. NUNCA invente sprints ou fases que nao existem no vault. Se o plano no vault nao cobre o que voce quer fazer, pergunte ao usuario antes de agir.
7. NUNCA crie artefatos visuais (design system HTML, prototipos) sem que o usuario tenha solicitado explicitamente. Verifique o que ja existe em `projetos-test/` antes de propor.

**Corrigido em 2026-06-16:** Agente criou `projetos/hephaistos-design-knowledge/` e sugeriu Design System HTML que ja existia em `projetos-test/componentes-design-system/design/html/`. Ambos os erros por nao ter verificado o vault primeiro.

## Regras

1. **Nunca misturar modos** — um modo por prompt, uma tarefa por sessao
2. **Hermes orquestra, nao executa codigo diretamente** — delega para mimo
3. **Hermes NUNCA faz design visual** — NUNCA. Qualquer decisao estetica (layout, cores, tipografia, icones, espacamento, posicionamento de elementos, hierarquia visual, selecao de icones, badges decorativos, glyphs) e delegada ao agy via `delegate_task`. Nem mesmo "pequenos ajustes" ou "badges decorativos" — o usuario detecta e rejeita. A unica excecao: patches cirurgicos de copy ou conteudo que nao alteram o layout.
4. **NUNCA usar emojis** — sempre icones Lucide (`lucide-react`). Emojis (sao proibidos em qualquer contexto: badges, headers, glyphs decorativos, placeholders, cards. Se um Lucide equivalente nao existir, use um icone proximo ou texto simples — mas nunca emoji.
5. **Atualizar `estado-atual.md` e `fio-do-projeto.md` a cada sessao**
6. **Nunca usar design generico de IA** (Inter padrao, gradientes roxo-azul, cards simetricos)
7. **Nunca hardcoded secrets** — sempre .env
8. **Nunca pular verificacao** — lint + typecheck + testes antes de concluir

## Sistema de Contexto em Camadas (economia de ~90% tokens)

- **Camada 1:** `estado-atual.md` (~300 tokens) — lido toda sessão
- **Camada 2:** `quick-projeto.md` + `quick-tech.md` (~800 tokens) — conforme modo
- **Camada 3:** Documentos completos (~2000 tokens) — só por demanda explícita
- **Compact:** `_compact/projeto.md` + `_compact/tech.md` (~200 tokens) — revisões rápidas

## Protocolo Vulcano — Busca Semântica de Conhecimento

Vulcano v3 é o **motor de busca primário** do vault Hephaistos. **SEMPRE usar `vulcano_search` antes de navegar manualmente** por `engramas/` ou usar `read_engram` direto.

### Início de Sessão (protocolo padrão)

```python
# 1. Contexto estrutural do modo ativo
ctx = get_mode_context("DESIGN")         # ou INCEPTION, IMPLEMENTACAO, etc.

# 2. Busca semântica — descobre engramas relevantes por significado
results = vulcano_search("glassmorphism UI blur componente", top_k=5)
# → engrama-glassmorphism-2026 (0.762) ← leia este

# 3. Lê apenas o que é relevante (não o vault inteiro)
detail = read_engram(results[0]["path"])

# 4. Contexto compacto para subagentes (economia de tokens)
context = vulcano_context("criar design system dark mode", max_tokens=500)
```

### Durante a Sessão

```python
# Encontrar engrama por conceito (substitui navegação manual)
vulcano_search("deploy Docker Coolify self-hosted", top_k=3)

# Ver engramas mais acessados (hot = mais relevantes para o projeto atual)
vulcano_hot(top_n=10)

# Seguir links associativos do engrama encontrado
follow_links("engramas/design/engrama-glassmorphism-2026.md", depth=1)
```

### Ao Criar Nova Skill Hermes → Indexar no Vulcano

```python
# Após criar ~/.hermes/skills/<dominio>/<nome>/SKILL.md:
create_engram(
    "engramas/orquestracao/engrama-skill-<nome>.md",
    "# Skill: <nome>\n\n**Quando:** <gatilho>\n**Ferramentas:** ...\n\n[[engrama-hermes-orquestracao]]"
)
# Garante que vulcano_search("<propósito da skill>") a encontre semanticamente
```

### Pitfall: Navegação Manual é Fallback, Não Protocolo

Usar `read_engram("engramas/design/engrama-glassmorphism-2026.md")` diretamente pressupõe que você já sabe o caminho. Use `vulcano_search` PRIMEIRO — mesmo que você ache que sabe o nome exato, a busca semântica frequentemente retorna engramas relacionados mais relevantes que você não consideraria.

## Estrutura do Vault

```
[projeto]/
├── _contexto/         → estado-atual, fio-do-projeto, decisoes, instrucoes-ai, quick-*
├── _compact/          → projeto.md + tech.md (visão rápida ~15 linhas)
├── visao/             → visao.md, publico.md, roadmap.md
├── arquitetura/       → stack.md, adr.md, api.md, dados.md, infra.md
├── modulos/           → bootstrap/, pipeline/, skills/, watchdog/
├── infra/             → Docker, CI/CD
├── notas-de-sessao/   → logs de sessão cronológicos
└── _auditoria/        → relatórios de watchdog e revisão
```

## Watchdog (Auto-Atualização)

Cron job que pesquisa 15 tópicos de vibe coding a cada 7 dias e gera relatório:

```bash
hermes cronjob run <job_id>
```

Tópicos: frameworks frontend, design systems, agentes CLI, segurança, deploy, custo de modelos, hype/depreciações.

## Comandos Úteis

```bash
# Iniciar projeto (quando hephaistos-init existir)
hephaistos-init "Meu Projeto" --tipo codigo

# Executar watchdog manualmente
hermes cronjob run 4286cfa9c55f

# Ver status do pipeline
cat /run/media/taciobrito/ARQUIVOS/[projeto]/_contexto/estado-atual.md

# Autenticar ferramentas
opencode auth list
agy -p "olá"  # primeira vez abre OAuth
```

## Verification

Verificar que as ferramentas estão prontas:

```bash
mimo --version     # >= 0.1.1
agy --version       # >= 1.0.8
hermes --version        # ≥ 0.16.0
ls "/run/media/taciobrito/ARQUIVOS/[projeto]/_contexto/estado-atual.md"
```

### Quality Gates — Projeto

Antes de concluir cada modo:

**Modo INCEPTION:**
- [ ] **Entrevista de discovery com usuário realizada?** — Contexto, dores, objetivos documentados
- [ ] **Escopo validado pelo usuário?** — OK explícito
- [ ] **Notas da entrevista salvas?** — Em `notas-de-sessao/` ou `visao/`

**Modo DESIGN:**
- [ ] **Entrevista de dores/necessidades com usuário realizada?** — Entender o problema antes de desenhar
- [ ] **Mapa de empatia gerado?** — Obrigatório antes de qualquer artefato visual
- [ ] **Direção visual validada pelo usuário?** — Moodboards, paleta, tipografia aprovadas
- [ ] **Design system validado pelo usuário?** — Tokens e componentes OK
- [ ] **Protótipo validado pelo usuário?** — Navegação e layout OK
- [ ] Moodboards HTML gerados (`design/research/moodboards/*.html`)
- [ ] Moodboards HTML abrem e exibem referências corretamente
- [ ] Design System HTML gerado (`design/specs/design-system.html`)
- [ ] Design System HTML navegável (sidebar funciona)
- [ ] Protótipo HTML funcional (`design/wireframes/prototipo.html`)
- [ ] Navegação entre telas do protótipo funciona
- [ ] Modais e interações do protótipo operacionais
- [ ] Consistência entre moodboard → design system → protótipo

**Modo IMPLEMENTACAO/REVISAO:**
- [ ] Lint passou? -- `npx biome ci .` ou equivalente
- [ ] Testes passaram? -- `npx vitest run` ou equivalente
- [ ] Typecheck passou? -- `npx tsc --noEmit` ou equivalente
- [ ] Anti-padrões verificados? -- Sem design genérico de IA

**Todos os modos:**
- [ ] **Gate de aprovação do usuário respeitado?** — Hephaistos perguntou, usuário respondeu SIM
- [ ] **Decisões registradas?** — `decisoes-tomadas.md` se houve decisão estrutural
- [ ] Vault atualizado? — `estado-atual.md` e `fio-do-projeto.md`

## Pitfalls

- **NUNCA use emojis — sempre ícones Lucide.** O usuário detecta e rejeita imediatamente. Emojis como ✦, ⚠, 🌿, 🧠, ✨, 🚀, 🔄, 🏛️ são proibidos em badges, headers, glyphs, placeholders, cards, CTAs. Use `lucide-react`: `Star`, `AlertTriangle`, `Leaf`, `Brain`, `Sparkles`, `Rocket`, `RefreshCcw`, `Landmark`, etc. Se não existir equivalente, use o ícone mais próximo ou texto simples. Verificado em Desconsultor 2026-06-16: o usuário explicitamente corrigiu uso de emojis na seção "Quem sou eu", headers de insights, e mapa de glyphs de arquétipos.
- **Design visual é SEMPRE delegado ao agy — NUNCA feito pelo Hermes diretamente.** Nem "só um badge", nem "só um card de bio", nem "só centralizar um CTA". Qualquer decisão estética (layout de nova seção, posicionamento de foto, escolha de ícone decorativo, hierarquia visual, espaçamento entre elementos) é delegada ao agy via `delegate_task`. O Hermes só faz patches cirúrgicos de copy/conteúdo que não alteram o layout. A regra #3 do Hephaistos é absoluta — se o usuário precisou corrigir, a delegação falhou.
- **NUNCA use imagens de placeholder (Picsum, placeholder.com, etc.) em moodboards ou protótipos.** O usuário detecta pesquisa simulada. Sempre extrair imagens REAIS de Behance, Dribbble ou Pinterest via `design-research-moodboard/references/research-extraction-methods.md`.
- **NUNCA invente descrições de referências de design** — as descrições devem refletir o conteúdo REAL do projeto referenciado. Visite a página do projeto para ler a descrição do autor.
- **Estudar referenciais visuais DE VERDADE antes de replicar** — quando o usuário envia um site de referência (ex: xnrgyclub.com), NÃO basta ler o DOM ou o accessibility tree. É obrigatório extrair a estrutura visual real via `browser_console`: (1) computed styles de cada seção (display, flexDirection, height, padding, backgroundColor), (2) tipografia (fontFamily, fontSize, fontWeight, lineHeight, letterSpacing, color, textTransform), (3) alternância de cores entre seções (dark/light pattern), (4) dimensões reais de imagens (width, height, objectFit, aspectRatio), (5) estrutura do grid (gridTemplateColumns, maxWidth, padding). Sem isso, você replica o CONTEÚDO do site mas não a ESTRUTURA VISUAL — e o usuário detecta imediatamente ("não tem a estrutura e quebras de conteúdo"). Validado no Jogo da Solidariedade 2026-06-17: primeira versão usou bento grids + glassmorphism quando o referencial era editorial magazine com seções alternando dark/light, tipografia 170px, colunas assimétricas e vertical letter labels.
- **Seguir o briefing do cliente sobre significados simbólicos** — quando o cliente corrigir a interpretação de um elemento (ex: "não mencione conexão com o divino, o cálice referencia a tradição simbólica e a caridade"), NUNCA reescrever com a interpretação anterior. O cliente é o dono do significado. Validado no Jogo da Solidariedade 2026-06-17: usuário corrigiu descrição do cálice para focar em tradição maçônica + Escada de Jacó + caridade, explicitamente removendo "conexão entre terreno e divino".
- **NUNCA pule a entrevista com o usuário no INCEPTION ou DESIGN.** O design sem entender as dores do usuário produz artefatos genéricos que não resolvem o problema real.

- **agy `research` falhou em ambiente container** — AGY CLI (antigravity-cli) requer TTY interativo (`bubbletea: could not open TTY`). Tentativas via `agy research --query ...` em subagentes falham com erro TTY. Fallback confirmado: subagente com knowledge base + `web_search` como compensação. Não é falha do AGY — é limitação de ambiente. Para research pesado em ambiente headless, usar `web_search` ou `browser_navigate`.
- **agy `--add-dir` é obrigatório** — sem ele, o agy escreve em `~/.gemini/antigravity-cli/scratch/` e os arquivos "desaparecem". Mesmo com `--add-dir`, o agy pode salvar em scratch e apenas referenciar — sempre verificar o output e copiar arquivos manualmente se necessário.
- **agy pode desviar de contexto quando chamado via terminal()** — se o AGY CLI tiver contexto residual de sessão anterior no workspace (pasta de outro projeto), ele pode ignorar completamente o prompt passado e executar no projeto errado. Ocorreu nesta sessão: ao passar `agy --print "pesquise Awwwards Collections..."`, o AGY foi para o projeto Desconsultor e começou a executar testes. **Prevenção:** (1) sempre prefixar com `--add-dir <path>` explícito para o vault de saída, (2) verificar o output do AGY antes de confiar nos resultados, (3) se o AGY desviar, usar navegação direta via browser_navigate como fallback imediato.
- **delegate_task com muitas URLs é frágil para pesquisa web** — batches de 25+ URLs via delegate_task com toolsets=[browser] podem ser interrompidos (exit_reason: "interrupted") pelo modelo orquestrador (DeepSeek Flash) quando o subagente consome muitos tokens visitando dezenas de páginas. **Prevenção:** (1) batches de 10-15 URLs máx por delegate_task, (2) para pesquisas grandes (100+ URLs), usar navegação direta sequencial com browser_navigate (mais lenta porém confiável), (3) compilar incrementalmente com write_file a cada 10 URLs visitadas para não perder progresso em caso de interrupção.
- **agy OAuth já configurado** — token salvo em `~/.gemini/antigravity-cli/antigravity-oauth-token`
- **OpenCode `run` timeout com prompts grandes** — prompts muito detalhados ou tarefas multi-step podem exceder o timeout de 180s. Soluções: (1) dividir em prompts menores e focados, (2) aumentar timeout com `terminal(timeout=300)`, (3) usar modo background (`background=true, pty=true`) para trabalho iterativo. Testado na Calculadora-CLI: prompt de implementação completo timeoutou.
- **delegate_task é síncrono** — o Hermes pai espera o subagente terminar. Para trabalho long-lived, use `cronjob` ou `terminal(background=true)`
- **Para projetos pequenos, Hermes pode fazer direto** — delegate_task tem overhead. Se a tarefa é simples (escrever um arquivo, rodar um teste), o Hermes pode executar sem delegar.
- **Não confundir agy com Gemini CLI** — agy (Antigravity CLI) é o sucessor. O binário `gemini` do pacote npm antigo será descontinuado em 18/06/2026
- **Arquivos no NTFS/exFAT** — partições montadas como fuseblk (ntfs-3g) ou exfat não suportam permissão `+x`. Shell wrappers em `node_modules/.bin/` falham com `EACCES`. Fix: bypassar via `node <caminho direto>`. Para binários nativos (Biome), copiar para `/tmp` e `chmod +x`. 📖 [[references/quality-gate-exfat.md]]
- **HTML deliverables: criar do zero com padrão, não copiar template** — os arquivos `moodboard.html`, `design-system.html` e `prototipo.html` são criados do zero seguindo o padrão [[design-research-moodboard/references/html-deliverables.md]] (self-contained HTML com Tailwind CDN + Google Fonts + tokens inline + Tailwind config inline). Não existem templates pré-prontos para copiar — cada projeto tem paleta, tipografia e componentes únicos substituir os placeholders `[Nome do Projeto]`, `[Nome do Tema]`, `#XXXXXX` resulta em páginas quebradas. Sempre preencher com dados reais do projeto. Verificar no navegador: zero erros JS.
- **Wireframes devem vir antes da implementação** — o protótipo HTML funcional (`prototipo.html`) não é opcional. Ele é o artefato que valida o fluxo de navegação e layout antes de escrever uma linha de código. Pular esta fase causa retrabalho.
- **Projetos existentes (Figma Make, V0, gerados)** — quando o usuário já tem um projeto gerado (ex: Figma Make → React + Tailwind + shadcn/ui), NÃO recriar do zero. O workflow correto: (1) ler `App.tsx` e componentes customizados para entender o design system (cores, tipografia, padrões de card, animações), (2) fazer patches cirúrgicos com `patch()` que respeitem exatamente o estilo existente — mesmas classes Tailwind, mesmos componentes wrapper (GlassCard, SectionTitle, etc.), mesmos padrões de animação (Framer Motion `initial`/`animate`/`whileInView`), (3) garantir que novas seções sigam a mesma estrutura de grid e hierarquia visual. Nunca trocar a stack ou refatorar o design system de um projeto existente sem aprovação explícita.
- **Awwwards-level design: qualidade mínima para HTML prototypes** — quando o usuário pede design "nível Awwwards", "cinematográfico", "tipo Lovable/Peach", ou sites premium com animações, o protótipo HTML (Fase 3 do DESIGN) deve obrigatoriamente incluir: **bento grids assimétricos** (cards de tamanhos variados), **glassmorphism** (`backdrop-blur`, `bg-white/5 border border-white/10`), **canvas particles ou waves** animados (simulando Three.js), **cursor glow** (radial-gradient tracking), **scroll-triggered reveals** (IntersectionObserver com fadeInUp/scaleIn), **tipografia dramática** (títulos enormes 7xl/8xl com gradient text, letter-spacing), **text reveal animations** no hero (linhas que entram sequencialmente), e **gradientes animados** no background. Protótipos com layout de grid simétrico simples, cards sem glassmorphism, sem animações, e tipografia padrão serão rejeitados como "extremamente simples". Validado no SergipeTec 2026-06-17: o primeiro protótipo foi rejeitado exatamente por isso. A iteração que adicionou bento grid, glassmorphism, canvas waves, cursor glow e typography reveal foi aprovada. 📖 Referência completa de técnicas Awwwards-level em [[design-research-moodboard/references/awwwards-level-html-prototypes.md]].

- **Canvas network graph interativo** — para protótipos HTML com canvas, implementar grafo de força direcionada (force-directed graph) que muda conforme navegação entre páginas. Cada página deve ter sua própria configuração de nós e arestas representando o ecossistema daquela seção. Técnica: simulação física com gravidade central, molas nas arestas (spring forces), repulsão entre nós, partícula de luz percorrendo as arestas animada via `Date.now()`. Nós com glow radial (RadialGradient) e labels. Atualizar o grafo via `updateGraphPage(page)` no mesmo evento de navegação SPA. Validado no SergipeTec 2026-06-17.

- **SVGs decorativos de arte clássica** — para projetos com tema tech/institucional que precisam de elementos decorativos sofisticados, usar SVGs inline de silhuetas de estátuas gregas, bustos, torsos com opacidade 5-10%, animação flutuante via CSS `@keyframes floatStatue`, e cores herdadas do design system (via classe CSS com `fill` e `stroke`). A opacidade baixa é essencial — o elemento deve ser sentido, não lido. Validado no SergipeTec 2026-06-17.

- **Next.js 16 SSR pitfall com Three.js** — `dynamic(() => import(...), { ssr: false })` é **bloqueado** no Next.js 16. O erro é `ssr: false is not allowed`. Fix: no componente Three.js/R3F, usar `useState(false)` + `useEffect(() => setMounted(true), [])` no topo, e retornar `null` se `!mounted`. Isso impede o SSR de tentar renderizar `@react-three/fiber Canvas` ou objetos `three` no servidor. Validado em Next.js 16.2.9, React 19.2.4, @react-three/fiber 9.6.1.
- **Branch rejeitada pelo cliente** — quando o trabalho de uma branch não for aprovado, confirmar com o usuário antes de deletar. Listar os commits que serão perdidos (ex: `git log --oneline main..branch`). Se a branch nunca foi pushada, os commits somem permanentemente — avisar explicitamente. Fluxo: `git checkout main && git branch -D branch`. O working directory pode conter alterações residuais dos commits deletados — verificar com `git status` após a exclusão.
- **Dados de pesquisa em PDFs locais** — quando `web_search` falha (Firecrawl offline, CAPTCHA) mas o projeto tem PDFs com dados críticos (TCC, pesquisa, artigos), extrair com `pdftotext` via `execute_code`. Ver [[references/pdf-extraction-fallback.md]].
- **Feedback do cliente em .doc** — extrair com `antiword` (preferencial) ou `catdoc` (fallback). Ambos disponíveis na maioria das distros Linux. Arquivos `.docx` podem ser lidos diretamente com `read_file` (Hermes suporta Office Open XML).
- **Deploy no Vercel via CLI (NTFS)** — `npx vercel` funciona em NTFS porque o CLI é Node.js puro (não depende de binários nativos com +x). Fluxo: (1) `npx vercel login` (abre browser OAuth), (2) `npx vercel --prod --yes --name <projeto-minusculo>` no diretório do projeto. ⚠️ O nome do projeto DEVE ser minúsculo (Vercel rejeita maiúsculas com erro 400). Se o projeto já existe no Vercel, o `--name` pode ser omitido — o CLI detecta automaticamente. O build é feito remotamente (não depende do NTFS local). Para projetos Vite, o CLI detecta `vite build` + `dist/` automaticamente. Validado em Propostadiagnstico, 2026-06-16.
- **GSAP `registerPlugin` duplicado entre componentes** — em projetos Next.js com múltiplos componentes usando GSAP + ScrollTrigger, cada `gsap.registerPlugin()` gera warnings. Centralizar em `src/lib/gsap.ts` que exporta `{ gsap, ScrollTrigger, useGSAP }`. Todos os componentes importam desse arquivo único. 📖 [[references/gsap-centralized-registration.md]]
- **Contraste WCAG AA em texto pequeno** — `text-slate-500` (#64748b) sobre fundo `#0a0d14` tem contraste ~3.8:1, abaixo do mínimo AA (4.5:1) para texto <14px. Substituir `text-slate-500` por `text-slate-400` (#94a3b8, ~5.3:1) em textos `xs`, `text-[10px]`, `text-[9px]`. Foco: labels, metadados, descrições secundárias. Texto `sm` ou maior não precisa (AA para large text é 3:1).

- **Vercel: redeploy SEMPRE após cada build aprovado** — o usuário exige deploy automático no Vercel após toda alteração. Comando: `cd /mnt/ARQUIVOS/Projetos/<projeto> && npx vercel --prod --yes`. Se reclamar de versão antiga, refazer o deploy — o alias de produção pode estar apontando para build anterior. Verificar hash do JS com curl. 📖 [[references/proposal-iteration.md#Vercel Redeploy OBRIGATÓRIO após cada build]]
- **Simplificação de página** — quando o usuário pede proposta "enxuta" ou diz "muita informação": cortar Pipeline, Entregáveis, Equipe e Vantagem Competitiva (seções de implementação, não de venda). Alvo: 7 seções ou menos. Separe visualmente Mensalidade (Bloco 1) de Participação de Resultado (Bloco 2) — NUNCA colocar Participação como pílula dentro do bloco de Mensalidade. 📖 [[references/proposal-iteration.md]]

- **Servidor local e cache HTTP** — Python `http.server` não envia headers de cache. Após rebuild, o navegador pode servir versão antiga mesmo em aba anônima. Se o usuário disser \"ainda aparece a versão anterior\", usar o script de servidor com `Cache-Control: no-store` (descrito em [[references/proposal-iteration.md#servidor-local-cache]]) ou fazer deploy no Vercel para build limpo remoto.

- **GitHub MCP Server: setup** — `hermes mcp add github --command npx --args -y @modelcontextprotocol/server-github` instala 26 ferramentas (create_issue, create_pull_request, push_files, etc.). O `--args` DEVE ser o último argumento. Autenticação via env var GITHUB_PERSONAL_ACCESS_TOKEN na config do servidor. ⚠️ `hermes config set mcp_servers.github.env` salva como string YAML, não como objeto — o MCP server quebra com erro \"dictionary update sequence element #0 has length 1\". Fix: editar `~/.hermes/config.yaml` diretamente e formatar como YAML mapping (com indentação e `KEY: value`). Usar `hermes mcp list` para verificar status; `/reload-mcp` em sessão ativa para recarregar.
- **Vulcano MCP Server: setup no Hermes** — Vulcano v3 expõe MCP via SSE HTTP (porta 8765) em Docker. Adicionar ao Hermes: `hermes mcp add vulcano --url http://localhost:8765/sse`. Recarregar com `/reload-mcp` em sessão ativa. Em Claude Code (stdio, local), já está configurado em `~/.claude.json`. HF_TOKEN warning ao iniciar é apenas aviso de rate limit — não bloqueia o engine. Se `VAULT_PATH` não estiver definido, o servidor não sobe. Referência: [[references/vulcano-v3-setup.md]] e `~/.hermes/skills/autonomous-ai-agents/vulcano/SKILL.md`.
- **Biome v2+ config migration** — ao criar `biome.json` novo, SEMPRE verificar a versão do CLI instalado (`biome --version`) e usar o schema correspondente. Biome v2 mudou: `organizeImports` → `assist.enabled`, `noConsoleLog` → `noConsole`, `recommended` → `preset: "recommended"`. Usar `biome migrate` quando disponível. Cuidado com `--write --unsafe` — pode quebrar sintaxe JSX em projetos React/Next.js. 📖 Referência: [[references/biome-v2-migration.md]]

- **Vitest + Next.js + jsdom** — setup completo de testes para Next.js: vitest.config.ts com react plugin, path alias, jsdom environment. matchMedia mock obrigário no test-setup.ts (GSAP/prefers-reduced-motion). Em exFAT, chamar `node ./node_modules/vitest/vitest.mjs run` diretamente. 📖 [[references/vitest-nextjs-setup.md]]

- **Clip-path + unlock gates** — quando sections têm clip-path circular (reveal cinematográfico) e estão por trás de um gate de blur/captura, NÃO aplicar `clip-path: circle(0%)` antes do unlock. O IntersectionObserver dispara imediatamente (usa bounding box, não visual clipping), causando conflito de transições. Aplicar clip-path apenas quando `isUnlocked === true`. 📖 Padrão validado no Desconsultor, 2026-06-16

- **Gate toggle para preview em desenvolvimento** — quando um projeto tem gates (blur-section, capture-gate, login wall), SEMPRE adicionar um botão flutuante de preview (`fixed bottom-4 right-4 z-[999]`) que permite ao desenvolvedor/usuário alternar entre bloqueado e desbloqueado sem preencher formulário. Implementar como `useState` toggle que bypassa o gate. Remover ou esconder em produção (env check ou feature flag). Padrão: botão com `Lock`/`LockOpen` do lucide-react, backdrop-blur, cores que indicam estado (laranja=blocked, teal=unlocked). Validado no Desconsultor, 2026-06-16.

- **Video lazy loading com IntersectionObserver** — vídeos de fundo (hero, contato) devem usar IntersectionObserver com `rootMargin: "200px"` para só carregar quando próximo do viewport. 📖 [[references/video-lazy-loading-pattern.md]]

- **Fraunces como fonte display** — Next.js: importar, variável CSS, @theme, classe `font-fraunces`. 📖 [[references/fraunces-display-font.md]]

- **GSAP ScrollTrigger.refresh() no resize** — adicionar useEffect com resize listener. 📖 [[references/gsap-scrolltrigger-refresh-resize.md]]

- **Focus-visible global CSS** — adicionar regra global em `globals.css` para `a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, [tabindex]:focus-visible` com `outline: 2px solid rgba(accent, 0.6); outline-offset: 2px; border-radius: 8px;`. Garante navegação por teclado acessível sem precisar adicionar focus styles em cada componente individualmente.

- **Supabase unreachable: .catch() + console.warn** — quando `.env.local` tem credenciais mas o projeto Supabase está inacessível (pausado/deletado), os inserts lançam `TypeError: Failed to fetch` como `console.error`. Fix: adicionar `.catch()` no chain e usar `console.warn` em vez de `console.error`. O app funciona normalmente com localStorage como fallback. Padrão: `db.from("x").insert([...]).then(({ error }) => { if (error) console.warn("skipped:", error.message); }).catch((err) => { console.warn("unreachable:", err.message); });`

- **Git backup antes de sprints** — NUNCA usar `git stash` como backup. stash salva mas limpa o working tree. Usar `git add -A && git commit -m "backup: descrição"` para criar checkpoint que mantém o código visível e navegável.
- **Supabase `PromiseLike` vs `Promise`** — o cliente Supabase retorna `PromiseLike<void>`, NÃO `Promise<void>`. O método `.then()` de `PromiseLike` retorna outro `PromiseLike`, que NÃO tem `.catch()`. Padrões que FALHAM: `db.from("x").insert([...]).then(...).catch(...)` → TS error "Property 'catch' does not exist on type 'PromiseLike<void>'". Fix: (1) usar `async/await` com `try/catch` (preferido), ou (2) usar `.then(onFulfilled, onRejected)` com dois argumentos. Para variáveis tipadas como `Promise<void>`, envolver em `new Promise<void>((resolve) => { insertResult.then(ok, fail) })`. 📖 [[references/supabase-async-patterns.md]]
- **SEMPRE verificar SPRINTS.md antes de propor trabalho** — o modelo anterior inventou sprints 9-11 que não existem e sugeriu "Design System HTML via agy" que não estava no plano. O usuário rejeitou como "loucura do modelo". SEMPRE consulte `~/vaults/hephaistos/SPRINTS.md` para saber o que realmente está planejado. NUNCA invente fases, sprints ou milestones que não existem no vault.
- **Obsidian engrama ≠ Hermes skill** — um engrama markdown no Obsidian vault documenta conhecimento. Uma Hermes skill (SKILL.md + frontmatter + templates) executa ações. A refatoração de um para o outro é um workflow explícito (ver Knowledge → Engrama-Skill Pipeline). NUNCA trate um engrama markdown como skill Hermes.
- **NUNCA misturar contexto entre projetos** — cada projeto tem seu próprio vault (`projetos/{nome}/`), design system, assets e entregáveis. Implementações de um projeto NUNCA devem ser aplicadas a outro. Exemplo concreto: elementos de apresentação do Hephaistos (deck) não pertencem ao site do SergipeTec. O usuário corrigiu isso em 2026-06-17: "você fez as implementações do deck do hephaistos no site do sergipetec, que não tem nada a ver".

- **SEMPRE verificar o tipo de entregável antes de criar** — antes de iniciar qualquer implementação, confirme com o usuário se o entregável é: site, landing page, deck de apresentação (slides), dashboard, aplicativo, protótipo HTML, brand showcase, ou outro formato. **NUNCA assuma o formato pelo nome.** "Deck" não é landing page — é apresentação estilo slides. "Apresentação" pode ser brand showcase (página de scroll) ou deck (slides navegáveis). O usuário corrigiu em 2026-06-17: "Hephaistos não é uma landing page é um deck que estamos fazendo, porra". Quando o entregável for um deck, a estrutura deve ser de slides navegáveis (slide anterior/próximo, transições, progressão linear), não de scrolling infinito ou SPA com páginas. Quando for brand showcase, é uma página de scroll com seções narrativas.

- **NUNCA adivinhe as cores da marca — extraia via PIL** — quando a marca já existe em PNG/AI/SVG, use `PIL.Image` para extrair as cores dominantes reais (com percentual de dominância). Adivinhar cores do briefing ou de descrições textuais produz paletas imprecisas que não batem com a marca real. O usuário forneceu os assets em `/4x/` com PNGs 6000x6000 — a extração via PIL revelou Navy #001030 (26% dominância) que não estava no briefing original. Sempre verificar se existem assets da marca antes de propor paleta.

- **WhatsApp Project Intake** — quando o briefing do projeto chega via WhatsApp (texto + áudios PTT .ogg), seguir o workflow: (1) transcrever áudios com ffmpeg + whisper, (2) extrair requisitos da conversa, (3) gerar briefing estruturado, (4) criar vault Hephaistos. Projetos de branding (logo, camisa, bola, banner) usam a mesma estrutura de vault mas com foco em `visao/briefing.md` como documento primário. 📖 [[references/whatsapp-project-intake.md]]
- **Sempre buscar nos insumos ANTES de perguntar** — quando o usuário disser "verifique nos insumos", "o PDF tem isso?", "isso não está nos arquivos?", fazer busca profunda em `INSUMOS_DATA/` (grep, pdftotext, search_files) antes de pedir esclarecimento. O usuário espera que o agente encontre o texto exato nos arquivos existentes. Só perguntar se realmente não encontrar após busca extensiva. Corrigido em 2026-06-16: pedi o texto do Próximo Passo PJ quando ele já existia no arquivo `Landing Page - Sedentarismo Cognitivo.md`.
- **Pesquisa visual: agy + navegador simultaneamente** — para projetos de design/branding, o fluxo de pesquisa visual esperado é: (1) agy pesquisa e gera conceitos/rascunhos via `generate_image`, (2) navegador pesquisa Pinterest/Dribbble com contas do usuário para coletar referências reais. Executar em paralelo quando possível. O usuário tem contas Pinterest/Dribbble configuradas para pesquisa via browser tool.
- **agy gera rascunhos visuais** — o agy (Antigravity CLI) tem ferramenta `generate_image` que pode criar mockups/drafts de logos, escudos, identidades visuais. Usar para gerar propostas visuais antes de refinar. Output salva em `~/.gemini/antigravity-cli/brain/<session>/` — copiar para o vault do projeto após geração. 📖 [[references/visual-research-browser-workflow.md]]
- **Processamento de feedback de cliente em projetos existentes** — workflow completo: extrair .doc/.pdf → mapear para código → gerar plano em blocos com severidades → identificar perguntas bloqueantes. 📖 [[references/client-feedback-workflow.md]]
- **Pesquisa visual em Awwwards para polimento de UI** — quando o projeto precisa de polimento visual, navegar Awwwards por categoria (dark-mode, microinteractions, data-visualization), extrair padroes de sites premiados (HM/SOTD), mapear gaps vs projeto atual, priorizar por impacto x esforco. NUNCA implementar visual diretamente — delegar ao agy. [[references/awwwards-research-workflow.md]]

- **Sprint execution: sempre delegar em paralelo (máx 3 subagentes por batch)** — quando o usuário autoriza rodar sprint, NÃO execute sequencialmente. Dividir tarefas em 2-3 frentes paralelas via `delegate_task(tasks=[...])`. Cada subagente pesquisa + cria arquivos. Ver [[references/sprint-execution-pattern.md]] para workflow completo.
- **Engramas de pesquisa devem ter profundidade completa, nao apenas padroes superficiais** — o usuario corrigiu explicitamente: "Nao e apenas extrair padroes de design e aprender eles, ter em contexto, as ferramentas, padroes, referencias, tudo." Cada engrama gerado de pesquisa precisa incluir: (1) ferramentas e tecnologias mencionadas, (2) exemplos reais com nomes de sites, (3) recursos tecnicos e bibliotecas, (4) principios de design extraidos, (5) contexto completo (colecoes relacionadas, curadores, tamanho, seguidores). Um engrama que lista apenas "pastel, gradient, dark mode" sem os detalhes falha o proposito.
  - **Workflow correto:** Parse pesquisa para JSON estruturado -> gere engramas em lote com script Python -> cada engrama contem dados completos -> atualize index. Ver [[references/awwwards-knowledge-embedding.md]] para exemplo praticado.
  - **Exemplo:** Pesquisa Awwwards (100 colecoes, 1013 linhas) gerou 9 engramas com ferramentas, exemplos, principios e contexto — nao apenas "padroes de cor XX e YY".
- **Perspectiva de aprendiz: cobertura completa, não resumos** — quando o usuário pede para documentar plataformas, ferramentas ou criadores com foco em "aprender", ele quer cobertura completa (ferramentas, como funcionam, metodologias, insights, dicas, formatos de trabalho), não resumos superficiais. Cada item documentado deve ter 5 categorias: (1) ferramentas que usa/recomenda, (2) como funciona (workflow prático), (3) metodologias que segue, (4) insights e dicas, (5) formatos de trabalho. Exemplo: "a finalidade é saber quais são as ferramentas que essas plataformas tem, como elas funcionam, as metodologias adotadas, os insights e dicas... agir como uma pessoa querendo aprender". Referência: [[references/sprint-execution-pattern.md#Preferência do Usuário: Perspectiva de Aprendiz]]
- **Subagentes criam wikilinks quebrados** — quando delegar criação de engramas para agy/mimo via delegate_task, os subagentes frequentemente inventam nomes de wikilinks que não existem no vault (ex: `[[engrama-injection-attacks]]` quando o arquivo correto é `[[engrama-security-injection]]`). **Sempre verificar e corrigir wikilinks após cada batch de criação.** Padrão: `find vault/engramas/ -name "engrama-*.md"` para listar arquivos existentes, depois `patch(replace_all=True)` para corrigir links quebrados. Incluir no context do delegate_task os nomes exatos dos wikilinks que devem ser usados.
- **Revisão de copy em propostas multi-seção** — quando atualizar uma proposta com múltiplas seções interligadas (cronograma, KPIs, pricing, participação de resultado), SEMPRE fazer uma busca reversa por referências aos termos antigos após todas as edições. Ex: após trocar "3 meses" → "12 semanas", rodar `search_files(pattern="3 meses")` no diretório para achar menções residuais. O mesmo para valores monetários antigos (R$ 1.924 → R$ 1.734), percentuais, labels desatualizados ("Early Adopter", "Take Rate"), e referências a conceitos removidos (Take Rate Parque). Uma única referência não atualizada gera contradição e mina a credibilidade da proposta. 📖 Padrões completos de proposta em [[references/proposal-iteration.md]].
- **Segurança front-end: auditoria padrão** — quando o usuário pedir auditoria de segurança ou antes de deploy em produção, seguir [[references/security-audit-frontend.md]]: npm audit (high/critical), search_files por hardcoded secrets e XSS vectors, CSP check. Criar kanban task de segurança com `hermes kanban create`.
- **Dados de pricing são irrelevantes no vault** — tabelas de preços, comparativos de custo, informações de assinatura e valores monetários NÃO devem ser armazenados nos engramas. O vault é repositório de conhecimento técnico, não catálogo de compras. Quando um engrama contém dados de pricing, removê-los antes de salvar. Exemplo prático: engrama-design-as-service.md tinha tabela de preços ($12-75/seat, $499/mes) que foi removida.
- **Condensar arquivos grandes em engramas atômicos** — quando encontrar um arquivo >200 linhas (como Pesquisa_lovable.md com 660 linhas ou pesquisa-exaustiva-orquestracao.md com 2198 linhas), NÃO mantê-lo como monólito. Dividir em engramas atômicos (max 100 linhas cada) cobrindo aspectos diferentes do tópico. Deletar o arquivo original após a condensação. Técnica: ler o arquivo completo, identificar seções temáticas, criar 3-5 engramas com frontmatter YAML, adicionar wikilinks entre eles, atualizar index.
- **Corrigir wikilinks quebrados via Python** — subagentes frequentemente criam wikilinks para engramas que não existem. Para corrigir em lote, usar script Python que percorre todos os .md files e substitui referências quebradas. Padrão: `import os; for root, dirs, files in os.walk(vault_path): for file in files: if file.endswith(".md"): content = open(...).read(); content = content.replace(old, new); open(...).write(content)`. 📖 [[references/vault-cleanup-pattern.md]] para workflow completo de limpeza.
