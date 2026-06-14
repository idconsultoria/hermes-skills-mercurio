---
name: product-pipeline
description: "Multi-agent product pipeline — da ideia bruta ao MVP com sprints iterativos. Orquestrado por Hermes, executado por Pi Agent + Antigravity.

Load this skill when building a product from scratch through the full pipeline — ideation, research, design, sprints, and delivery. Covers orchestrating a multi-agent team with Hermes as coordinator, Pi Agent for execution, and Antigravity for visual design review."
category: autonomous-ai-agents
---

# Product Development Pipeline

> **Orquestrador:** Hermes
> **Executores:** Pi Agent (local, v0.78.1) + Antigravity (revisor visual)
> **Shared volume:** `/opt/data/code/` ↔ `/workspace/code/`

## Preferências do Usuário (ID Consultoria / Gustavo)

Este bloco codifica o estilo de trabalho das pessoas que usam este pipeline.
**Carregar sempre que a skill for ativada — antes de qualquer ação.**

### Estilo de comunicação
- **Direto e pragmático:** Usuário quer ação, não explicação. "Mande aqui", "Faça", "Cheque" são comandos, não sugestões.
- **Correções são diretas:** "É para fazer o contrário", "Mova X para futuro" — aplicar a correção imediatamente em TODAS as seções afetadas, sem questionar.
- **Zero jargão corporativo:** "Prioridade máxima é funcionar para a ID" > "avaliaremos escalabilidade em V2".
- **Espera versão funcional, não especulação:** Se disser para construir algo, construir de verdade. Se não for possível, falar o obstáculo concreto.

### Estilo de entrega
- **Entregar arquivos, não descrições:** Usuário pediu um documento → salvar em disco e enviar via MEDIA. Não descrever o que faria.
- **Iteração é o padrão:** Primeira versão raramente é a final. Usuário vai pedir ajustes. Aplicar feedback SISTEMATICAMENTE em todas as seções (checklist PRD Revision Cycle).
- **Múltiplos canais:** Usuário alterna entre Telegram (DM), WhatsApp (grupos), Google Workspace (Docs/Agenda). Respeitar o canal onde a mensagem chegou.
- **Google Docs para revisão colaborativa:** Quando enviar PRD para Google Docs, NUNCA sobrescrever com markdown local. O doc é a fonte da verdade colaborativa. Sync-back é Google Docs → markdown local, nunca o contrário.

### Preferências técnicas
- **Responsividade mobile é requisito, não opcional:** HTML sem responsivo testado = não entregue.
- **Pi Agent em background:** Pi com MiniMax M3 gera output silencioso por minutos. Monitorar via `ls -la` nos arquivos de saída, não via stdout.
- **Pre-flight check antes de cada fase:** Usuário não quer gastar tokens debugando permissão.

### Preferências de documento
- **Formato limpo e enxuto:** Documentos de produto (personas, PRD, etc.) DEVEM ser focados no que importa — sem poluição de fontes inline, sem metadados de pesquisa no texto. Fontes são implícitas ou registradas no histórico, não no corpo. Exemplo real: user-personas foi reduzido de 265 linhas para 106 (60% mais enxuto) a pedido do usuário.
- **Template proto-persona do Pi Agent:** Usar o formato do Pi Agent (`~/.pi/agent/skills/pm-skills/skills/proto-persona/template.md`) como referência de estrutura: Bio & Demographics → Quotes (2-3) → Pains (2-3) → What/Goals → Attitudes & Influences. Sem tabelas enormes, sem fontes a cada linha.
- **Clone digital é insumo, não verdade absoluta:** Dados de clone digital alimentam a persona, mas NÃO substituem o que o usuário confirma sobre si mesmo. Se o usuário corrigir algo do clone, a correção vence — o clone pode ter alucinado características.

---

## Arquitetura de Agentes

```
┌───────────────────────────────────────────────────┐
│                     Hermes                         │
│  Orquestrador • valida • agenda • pesquisa • integra│
│  Tools: delegate_task, web, file, terminal, pi CLI  │
└──────┬──────────────────────────────┬──────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐        ┌──────────────────┐
│    Pi Agent      │        │   Antigravity    │
│   (local CLI)    │        │   (agy 1.0.6)    │
├──────────────────┤        ├──────────────────┤
│ F1: Ideação      │        │ Revisor visual   │
│ F3: PM docs      │        │ Autoridade final │
│ F4a: UX/UI       │        │ em design        │
│ F4b: Engenharia  │        │                  │
│ F5: Sprints      │        │                  │
└──────────────────┘        └──────────────────┘

### Hierarquia de uso

```
CARO/ESCASSO     agy --- Consultor externo especialista (design, UX, estrategia)
ESCASSO          Pi best -- Eng. senior interno (MiniMax M3 via Go)
BARATO/ABUNDANTE Pi cost -- Dev junior (DeepSeek V4 Flash Free)
GRATUITO         Pi cost -- Free tier Zen
```

Ver skill pi-agent-coordination para detalhes completos.

### Conexões

| Conexão | Como |
|---------|------|
| **Hermes ↔ Pi (one-shot)** | `pi -p "..." --provider deepseek --model deepseek-v4-flash` (local, sem SSH) |
| **Hermes ↔ Pi (persistent session)** | Primeiro: `pi --name "sessao" -p "..."`, depois: `pi -c -p "..."` |
| **Hermes ↔ Pi (sessão id)** | `pi --session /path/to/session.jsonl -p "..."` |
| **Hermes ↔ agy** | `ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && /home/ubuntu/.local/bin/agy -p "..."'` |
| **Pi → agy (design feedback)** | Pi salva protótipo → Hermes chama agy → agy escreve em `feedbacks.md` |

> **Sem limite de tempo:** Toda invocacao de Pi e agy no pipeline roda **sem timeout**. Pi pode gerar output por minutos sem streamar stdout — `timeout N` mata o processo silenciosamente (exit code 0 não indica erro). agy pode levar minutos analisando código. Nunca usar `timeout` com Pi ou agy. Para Pi: usar `terminal(background=true)` ou foreground sem flag de timeout. Para agy: usar tmux interativo.
> Pi e local — nao ha SSH, nao ha timeout de conexao, nao ha quoting hell.
> Para tarefas muito longas (>5min), Pi pode stallar — usar agy ou quebrar em partes.
> Ver skill pi-agent-coordination para detalhes de fallback entre modelos.

### Modelos

#### Pi Best (planejamento, design, docs complexos)

Priorizar MiniMax M3 via Go:

| Opção | Provider | Model ID | Custo | Notas |
|-------|----------|----------|-------|-------|
| **Pi best** | `opencode-go` | `minimax-m3` | $10/mês, cota semanal $30 | Preferido. Chave ativa |
| **Fallback 1 (via Go)** | `opencode-go` | `deepseek-v4-pro` | Cota semanal $30 | Mesmo provider, modelo diferente |
| **Fallback 2 (API direta)** | `deepseek` | `deepseek-v4-pro` | $0.14/M input, $0.42/M output | Último recurso |

#### Pi Cost (execução de code-tasks, fixes, docs)

| Prioridade | Provider | Model ID | Custo | Notas |
|-----------|----------|----------|-------|-------|
| 1 | `opencode` (Zen) | `opencode/deepseek-v4-flash-free` | **Gratuito** | Preferido. Chave OpenCode ativa |
| 2 | `opencode-go` (Go) | `deepseek-v4-flash` | Cota semanal $30 | Fallback se Zen rate-limited |
| 3 | `deepseek` (API direta) | `deepseek-v4-flash` | $0.14/M input | Último recurso |

**Teste de conectividade (sempre verificar antes de invocar):**
```bash
# Pi Cost — tentar 1, 2, 3 em ordem
pi -p "echo test" --provider opencode --model opencode/deepseek-v4-flash-free
pi -p "echo test" --provider opencode-go --model deepseek-v4-flash
pi -p "echo test" --provider deepseek --model deepseek-v4-flash

# Pi Best
pi -p "echo test" --provider opencode-go --model minimax-m3
```

---

## Estrutura do Projeto

```
<projeto>/
├── product/
│   ├── ideation/
│   │   └── ideation-result.md
│   ├── research/
│   │   ├── <topico-1>.md
│   │   ├── <topico-2>.md
│   │   ├── mercado.md
│   │   └── user-interview.md
│   ├── management/
│   │   ├── PRD.md
│   │   ├── user-personas.md
│   │   ├── opportunity-solution-tree.md
│   │   ├── user-stories.md
│   │   └── product-roadmap.md
│   ├── design/
│   │   ├── wireframes.md
│   │   ├── design-system.md
│   │   ├── empathy-map.md
│   │   ├── journey-map.md
│   │   ├── prototype.html
│   │   └── feedbacks.md
│   └── engineering/
│       ├── SAD.md
│       ├── tech-specs.md
│       ├── ERD.md
│       ├── api-contracts.yaml
│       ├── test-plan.md
│       ├── release-notes.md
│       ├── code-tasks.md
│       └── feedbacks.md
├── src/
├── tests/
├── .gitignore
└── README.md
```

---

## Fases do Pipeline

```
[Ideia] → F1: Ideação → F2: Pesquisa → F3: Conceito → F4: MVP → F5: Iteração
             ↑              ↑              ↑              ↑              ↑
           Hermes→Pi    Hermes+DR     Pi best PM      Pi+agy→Docker   Hermes sprints
                                                        ↓
                                                  4e: Agy valida
                                                   app rodando
```

---

## Pre-flight Check (Obrigatorio antes de CADA fase)

O usuario **explicitamente pediu** para nao gastar tokens debugando permissao. Executar antes de invocar qualquer agente:

```bash
# 1. Pi acessivel? (PATH pode não incluir /opt/data/pi-global/bin)
export PATH="/opt/data/pi-global/bin:$PATH"
pi --version

# 2. Skills do Pi carregadas?
pi -p "list your skills" --provider deepseek --model deepseek-v4-flash

# 3. Shared volume funcional?
ls /opt/data/code/workstation/PROJETO/product/ 2>/dev/null
touch /opt/data/code/workstation/PROJETO/.perm-check 2>/dev/null && rm $_ && echo "Hermes rw: OK" || echo "Hermes rw: BLOQUEADO"

# 4. Docs da fase anterior legiveis?
ls -la /opt/data/code/workstation/PROJETO/product/FASE_ANTERIOR/*.md 2>/dev/null | head -3

# 5. Agy funcional?
ssh oracle-host 'echo "n" | timeout 5 /home/ubuntu/.local/bin/agy 2>&1 | head -3'
```

Se qualquer check falhar, **corrigir antes de prosseguir** — não invocar Pi até estar verde.

---

## Fase 1: Ideação

**Agente:** Hermes → Pi (modelo best)

### Fluxo (padrão: Pi Agent síncrono)

1. Hermes cria a estrutura inicial. **Pi e Hermes compartilham o mesmo filesystem** — nao ha mais UID mismatch:

   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/ideation /opt/data/code/workstation/PROJETO/prompts
   cd /opt/data/code/workstation/PROJETO && git init -b main 2>/dev/null
   git add -A 2>/dev/null; git commit -m "chore: init" 2>/dev/null || true
   ```

2. Hermes cria **sessão Pi persistente com nome** e envia a ideia inicial:

   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/prompts
   cat > /opt/data/code/workstation/PROJETO/prompts/pi-ideation.md << 'PROMPT'
   IDEIA: [brief completa do usuário]
   Projeto: <projeto>
   Diretório: /workspace/code/<projeto>
   Sua missão: carregar /skill:ideation-drilling e conduzir a ideação.
   Quando terminar, escreva ideation-result.md em product/ideation/.
   Inclua <!-- PHASE_COMPLETE: ideation --> ao final.
   PROMPT

   pi --name "PROJETO-ideation" -p "$(cat prompts/pi-ideation.md)" --provider opencode-go --model minimax-m3
   ```

3. **Pi carrega `ideation-drilling`** e faz sequência longa de perguntas:
   - "Esse produto é realmente necessário?"
   - "Não há alternativa mais simples e barata?"
   - "Essa feature é essencial?"
   - "Se faltar X, o projeto ainda atinge o objetivo?"
   - "O que exatamente você quer dizer por Y?"
   - "Seria mais ou menos isso e isso?"

4. Quando agente e humano se dão por **plenamente satisfeitos**, Pi escreve **`product/ideation/ideation-result.md`** com:
   - Detalhamento completo da ideia final
   - Lista de racionais para cada decisão

> **Relay pattern:** Pi não usa `clarify`. Se fizer perguntas, Hermes relay: mostra pro usuário, coleta resposta, reenvia ao Pi com `pi -c`.

### Variante: Ideação Distribuída (AI Studio, múltiplos stakeholders)

> **Referência completa:** `skill_view(name='product-pipeline', file_path='references/distributed-ideation-ai-studio.md')`

Quando a ideação envolve **2+ pessoas** que não podem participar da mesma sessão síncrona (stakeholders em horários diferentes, equipe remota, sócios com agendas conflitantes), substitua o Pi Agent por:

1. **Hermes cria uma Instrução de Sistema auto-contida** para o Google AI Studio, que transforma o modelo num facilitador de ideação com:
   - Máx 6 turnos por participante (absoluto)
   - Uma pergunta por vez, com síntese antes de cada turno
   - Cardápio de perguntas: necessidade real, prioridade, definição, trade-off, diferenciação, público
   - Formato de saída: bloco markdown copiável

2. **Cada stakeholder roda no próprio AI Studio**, no seu ritmo. O agente faz perguntas, o stakeholder responde.

3. **Ao final**, o agente gera um relatório em bloco ````markdown` e instrui: *"Copie TODO o conteúdo e envie no grupo."*

4. **Hermes consolida** os relatórios em `product/ideation/ideation-result.md`:
   - Mapeia consensos entre participantes
   - Identifica divergências e tensões
   - Extrai o escopo do MVP validado
   - Preserva citações literais
   - Inclui seção "Tensões não resolvidas"

5. O documento consolidado segue para aprovação do usuário (mesmo fluxo abaixo).

> **Dica:** Incluir no prompt de sistema que o nome do projeto deve carregar o conceito (ex: Delfos = "lugar do oráculo"). Registrar o significado no relatório final.

### Saída

```
product/ideation/ideation-result.md
```

Com marcador `<!-- PHASE_COMPLETE: ideation -->`

> **Arquivos .MD entregues via MEDIA, nunca como texto inline.** Quando o usuário pede um arquivo .md, salvar em disco e entregar via `MEDIA:/path/to/file` no Telegram.

### Detecção de conclusão

```bash
grep "PHASE_COMPLETE" /opt/data/code/<projeto>/product/ideation/ideation-result.md
```

### Revisão pelo usuário

Após o Pi escrever `ideation-result.md`, Hermes:
1. Verifica se o arquivo existe e contém o marcador `PHASE_COMPLETE`
2. Envia o `.md` ao usuário **como arquivo anexado (MEDIA)** no Telegram
3. **Aguarda a aprovação explícita do usuário** antes de seguir para F2

> **Essa pausa é obrigatória.** O usuário precisa validar o entendimento mútuo antes de prosseguir.

### Git commit

```bash
cd /opt/data/code/workstation/PROJETO
git add product/ideation/ && git commit -m "feat: F1 ideation complete"
```

---

## Fase 2: Pesquisa

**Agente:** Hermes

### ⏱️ Tempo de pesquisa — AUMENTAR TIMEOUT, não aceitar timeout

O usuário quer que subagentes **sempre tenham tempo suficiente** para completar. O timeout
padrão de 600s do `delegate_task` frequentemente não basta para pesquisas com 15-25 chamadas
de API (cada web_search/web_extract/browser leva ~20-40s com modelos lentos).

**Regra:** Sempre que possível, configure o timeout máximo disponível. Se o `delegate_task`
não aceitar timeout por parâmetro, assegure que:
1. O contexto do subagente seja focado e auto-contido (menos chamadas = mais rápido)
2. Se houver risco de timeout (>8 tópicos), quebre em 2 rodadas de delegate_task
3. Em último caso, faça a pesquisa diretamente (fallback comprovado)

**Fluxo recomendado:**
1. Disparar 2-3 subagentes paralelos com contextos detalhados e auto-contidos
2. Instruir subagentes a **não insistir em fontes bloqueadas** — se Google/Reddit/bloqueio, trocar imediatamente por DuckDuckGo, Bing, ou URLs diretas
3. Se precisar de conteúdo do Reddit, carregar a skill `read-reddit` (RSS feeds, não bloq.)
4. Se timeoutarem, **não retentar subagentes** — ir para pesquisa direta com `web_search` + `web_extract`
5. A pesquisa direta é mais rápida porque pula overhead de contexto do subagente
6. Sintetizar findings em relatórios `.md` em `product/research/`

> 💡 **Nota técnica:** Os subagentes deixam sessões no state.db mesmo quando timeoutam.
> É possível extrair tool_results do banco via SQLite para recuperar dados parciais
> (ver `skill_view(name='product-pipeline', file_path='references/subagent-session-recovery.md')`),
> mas o conteúdo mais valioso está nos relatórios produzidos pela pesquisa direta.

### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/research
   ```

2. **Planejar pesquisa** — definir tópicos com base no ideation-result.md:
   - Referências explícitas (softwares mencionados, conceitos-chave)
   - Referências implícitas (domínios relacionados)
   - Mercado, concorrência, perfil de usuário

3. Disparar sub-agentes `deep-research` para cada tópico (conceder tempo máximo disponível):
   ```python
   delegate_task(
       goal="Pesquisar profundamente sobre [tópico]",
       context="Contexto do projeto + perguntas específicas",
       toolsets=["web", "browser"]
   )
   ```

4. **Fallback:** Se subagentes timeoutarem, pesquisar diretamente:
   ```python
   web_search(query="...", limit=10)
   web_extract(urls=["...", "..."])
   ```

5. **Entrevista de usuário:**
   - Carregar skill `user-interview`
   - **Produto pessoal:** Hermes entrevista o usuário diretamente
   - **Produto com outros perfis:** simular entrevista para cada perfil de usuário

6. Cada resultado de pesquisa armazenado como `.md` em `product/research/`.

   ```bash
   git add -A && git commit -m "feat: F2 research complete"
   ```

### Saída

```
product/research/
├── index.html            (opcional — página consolidada com visual Agy)
├── <topico-1>.md
├── <topico-2>.md
├── mercado.md
├── user-interview.md
└── <outros>.md
```

> **HTML responsivo (⚠️ comum quebrar no mobile):** Se o usuário pedir deploy de
> página HTML consolidando as pesquisas, garantir mobile responsiveness antes de
> publicar. Ver `skill_view(name='product-pipeline', file_path='references/mobile-responsive-html-deliverables.md')`
> para checklist e diagnóstico de overflow horizontal.

---

## Fase 3: Desenvolvimento de Conceito

**Agente:** Pi (modelo best)

### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/management
   ```

2. Hermes invoca **Pi com modelo best** em sessão persistente (background), carregando skills de PM:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/prompts
   cat > /opt/data/code/workstation/PROJETO/prompts/pi-pm-docs.md << 'PROMPT'
   [contexto completo com path dos arquivos, skills a carregar, docs a produzir]
   PROMPT

   pi --name "PROJETO-pm" -p "$(cat prompts/pi-pm-docs.md)" --provider opencode-go --model minimax-m3
   ```

3. **Monitorar progresso — verificar arquivos de saída, NÃO o stdout do processo:**
   ```bash
   # Pi gera output silencioso (sem stdout até o final). Monitorar assim:
   ls -la /opt/data/code/workstation/PROJETO/product/management/*.md
   # Ou polling periódico com process(action='poll')
   ```
   Pi com MiniMax M3 leva ~4-5 min por documento e não streama stdout intermediário.
   Não matar o processo achando que travou — verificar os arquivos primeiro.

4. Pi carrega skills instaladas e elabora:
   - **PRD** — `/skill:prd-development`
   - **User Personas** — (ver seção abaixo sobre estratégia de pesquisa)
   - **Opportunity Solution Tree** — `/skill:opportunity-solution-tree`
   - **User Stories** — `/skill:user-story`
   - **Product Roadmap** — `/skill:roadmap-planning`
   - (e outros que julgar necessários)

#### Persona Research Strategy: Proto vs. Pessoas Reais

O pipeline precisa decidir qual abordagem de persona usar com base no que se sabe sobre a equipe/usuários:

| Situação | Abordagem | Quem executa |
|----------|-----------|--------------|
| **Personas fictícias** — perfil genérico de usuário, sem nome/pessoa real conhecida | Pi gera proto-personas via `/skill:proto-persona` com base no PRD e entrevistas | Pi Agent (best) |
| **Pessoas reais da equipe** — membros conhecidos do time (sócios, colaboradores) | Pesquisa web profunda → clone digital → persona documentada. Seguir o protocolo em `skill_view(name='product-pipeline', file_path='references/persona-research-deep-dive.md')#7-montagem-do-clone-digital` | Hermes (pesquisa + montagem) |
| **Público externo** — usuários-alvo que não são da equipe | Entrevista simulada via `user-interview` + proto-personas | Hermes + Pi Agent |

**Fluxo para pessoas reais:**

1. **Antes** de invocar o Pi, Hermes pesquisa cada indivíduo real na web:
   - **Plataformas prioritárias:** LinkedIn, Instagram, Behance/Dribbble, Medium, GitHub, Escavador, site pessoal/empresa
   - **Técnica primária:** navegar diretamente via browser para plataformas específicas (não confiar só em web_search — buscadores podem retornar 0 resultados mesmo quando a pessoa tem presença digital rica)
   - **Se web_search retornar VAZIO (não timeout):** Tentar browser direto nas plataformas antes de reportar "não encontrado". O buscador pode estar bloqueado por CAPTCHA/rate-limit enquanto o browser funciona com navegação direta.
   - Se a busca no buscador retornar **zero resultados**, tentar navegação direta por URL (`linkedin.com/in/<username>`, `instagram.com/<user>`, `behance.net/<user>`)
   - Se ainda assim não achar, **pedir ao usuário um link direto** — não persistir tentando

2. **Técnicas avançadas após encontrar um perfil:**

   Uma vez que uma plataforma é encontrada (ex: GitHub), extrair dados complementares:

   a) **Análise de commits (GitHub API via terminal):**
      ```bash
      curl -sL "https://api.github.com/repos/<user>/<repo>/commits" | python3 -c "import json,sys; [print(c['sha'][:7],'|',c['commit']['message'].split(chr(10))[0]) for c in json.load(sys.stdin)]"
      ```
      Commits revelam vocabulário de trabalho ("cinematic composition", "premium gold gradients"), estilo, stack, autor (pode ser empresa, não username), e tipo de contribuição.

   b) **Análise de CSS em produção (se houver Vercel/Netlify deploy):**
      ```bash
      curl -sL "https://<projeto>.vercel.app/assets/<hash>.css" | head -200
      ```
      Extrair paleta de cores, tipografia, glassmorphism, animações — o sistema de design real da pessoa.

   c) **GitHub API para metadados do perfil:**
      ```bash
      curl -sL "https://api.github.com/users/<username>"
      ```
      Data de criação, número de repositórios, followers, bio (mesmo vazia), company (mesmo null — dados nulos são informativos).

   d) **Browser vision para páginas com antibot/accessibility tree truncada:**
      Quando Bing, Behance ou outras plataformas carregam visualmente mas o DOM snapshot vem truncado (Cloudflare, JS-rendered), usar `browser_vision(annotate=True)` para ler o conteúdo visual e identificar elementos clicáveis.

3. Seguir o protocolo completo em skill_view(name='product-pipeline', file_path='references/persona-research-deep-dive.md')
   (multi-plataforma recon → extrair → estruturar → consolidar clone digital)

4. A persona resultante (clone digital) alimenta o Pi para que os documentos (PRD, user stories, roadmap) reflitam **pessoas reais**, não arquétipos genéricos

5. **Referência viva:** A persona de cada membro real deve ser salva como `/opt/data/<nome>-digital-clone.md` para reúso em futuros projetos. O caminho pode ser consultado em memória ou passado ao Pi como contexto.

#### Formato de saída: user-personas.md

O documento final de personas DEVE seguir o formato proto-persona do Pi Agent, NÃO o formato verboso com fontes inline. Ver `references/persona-output-format.md` para template completo e regras.

```markdown
### Nome Real — "Persona Name"

> *Quote principal*

### Bio & Demographics
- Idade, localização, formação, cargo, empresas, perfil online
- Stack técnica / especialidades
- Perfil neurodivergente (se aplicável): 1 linha

### Quotes
- *"[Frase real 1]"*
- *"[Frase real 2]"*

### Pains
- **Dor nomeada:** Descrição em 1-2 linhas

### What is This Person Trying to Accomplish?
- 2-3 bullets concisos

### Goals
- **Alpha/X.X:** Meta específica para cada fase

### Attitudes & Influences
- Autoridade de decisão, influenciadores, crenças
```

**Regras:**
- **Sem fontes inline.** Nada de `[FONTE: pesquisa web]` no corpo. Fontes vão no histórico.
- **Sem tabela resumo gigante.** Máximo 8 itens no mapa de cobertura.
- **Sem linhas desnecessárias.** Cada seção tem 2-4 bullets, não 10.
- **Idades corretas.** Verificar com o usuário se houver dúvida.
- **Clone digital é rascunho.** O que o usuário confirmar é o documento final.

> **Prova do conceito:** Na prática, o Tácio Brito (sócio designer da ID) tem presença em GitHub (nosterviz), LinkedIn, Instagram e um Vercel deploy com CSS completo que revela seu sistema de design pessoal. O buscador padrão retornou 0 resultados — navegação direta + análise de commits/CSS foi essencial.

#### ⚠️ Pitfall Crítico — Clone Digital ≠ Pessoa Real

O clone digital é uma **hipótese**, não um retrato fiel. O LLM pode inferir características, crenças ou filosofias que a pessoa real não endossa. **Sempre**:

1. Separar o que é **dado verificável** (idade, formação, premiações, links, commit messages) do que é **inferência do LLM** (filosofia pessoal, crenças, citações inventadas)
2. Apresentar a persona ao usuário para validação explícita
3. Aplicar correções do usuário como verdade definitiva — NUNCA defender o que o clone disse contra o que o usuário afirma
4. Se o usuário disser "isso não é algo que Tácio se importa" sobre um traço do clone, remover imediatamente de TODAS as seções

**Exemplo real:** O clone digital do Tácio atribuiu a ele a crença "o método é a jaula" (schema fixo). O usuário corrigiu: "Isso não é algo que Tácio se importa não. Foi só algo que o clone digital dele disse." — a correção foi aplicada em 5 pontos do documento e o traço completamente removido.

> **Regra de ouro:** Clone digital gera hipóteses. Usuário confirma ou descarta. A correção do usuário é o documento final — o clone digital é só rascunho.

> ⚠️ **Não delegar a pesquisa de pessoas reais ao Pi Agent.** Hermes faz a pesquisa web diretamente. Pi gera o documento de persona estruturado a partir dos achados da pesquisa. (Pi não tem ferramentas de navegação web — pedir para ele pesquisar é ineficaz.)

5. **Hermes revisa o PRD antes de apresentar ao usuário** — análise de gaps práticos:

   > **PRD Review Checklist** — verificar antes de enviar para aprovação:
   >
   > - [ ] **Timeline / visualização no tempo**: Sistemas de gestão de projetos precisam de alguma forma de ver prazos e etapas no tempo. Se o PRD não menciona timeline, Gantt ou calendário, questionar se deve ir pro MVP.
   > - [ ] **Categorização de projetos**: Projetos internos vs. clientes é uma necessidade operacional básica em consultorias. Se o schema não prevê `type` ou `category`, adicionar.
   > - [ ] **O schema resolve o problema real?** Verificar se as entidades (Task, Project, etc.) cobrem o vocabulário do dia-a-dia da equipe, não só conceitos abstratos.
   > - [ ] **Consistência interna**: Resumo executivo, features MVP e critérios de aceite usam a mesma contagem de views? Números batem? Features mencionadas no resumo aparecem na tabela de escopo?
   > - [ ] **Nomes e versão**: Header do documento reflete versão atual com data. Histórico de atualizações presente.
   >
   > Se o PRD falhar em qualquer item acima, corrigir antes de enviar ao usuário.

> **PRD Revision Cycle (pós-primeira entrega):** Quando o usuário pedir ajustes no PRD,
> aplicar as mudanças SISTEMATICAMENTE em todas as seções impactadas — não apenas na tabela
> de features. O checklist abaixo garante consistência:
>
> - [ ] **Resumo Executivo** — reflete o novo conjunto de features? Números de views batem?
> - [ ] **Features MVP (5.1)** — features adicionadas/removidas na tabela?
> - [ ] **Fora do MVP (5.2)** — item movido para V2/futuro adicionado aqui?
> - [ ] **Critérios de aceite (5.3)** — novos critérios para as novas features?
> - [ ] **Features pós-MVP (6)** — V2/V3 movido, removido ou renumerado?
> - [ ] **Riscos (8)** — menções à contagem de views, features, escopo?
> - [ ] **Anexo — Decisões** — novas decisões adicionadas? Status de decisões antigas mudou?
> - [ ] **Cabeçalho** — versão bumpada (v1.0 → v1.1 → v1.2)?
> - [ ] **Histórico de atualizações** — entrada da revisão adicionada?
> - [ ] **Consistência numérica** — "4 views" vs "5 views" em TODO o documento?
>
> Esse padrão evita o erro comum de alterar só a tabela de features e deixar o resumo
> executivo, riscos e anexos inconsistentes.

> **PRD Sync-Back (Google Docs → Local):** Quando o PRD é compartilhado no Google Docs
> e a equipe faz edições diretamente lá, o fluxo reverso de sincronização exige atenção:
>
> 1. **Extrair texto do Google Doc** via Docs API (docs.documents.get → body.content →
>    paragraph.elements.textRun)
> 2. **Identificar mudanças significativas** comparando com o markdown local: seções
>    novas, renomeações, decisões registradas
> 3. **Aplicar no markdown local** preservando formatação (tabelas, negrito, listas)
> 4. **NÃO sobrescrever o Google Doc** — a equipe pode estar usando o doc como fonte
>    da verdade. Só atualizar se o usuário pedir explicitamente.
> 5. **Registrar no histórico** com autor "Equipe ID (edição no Google Docs)"
>
> Ver `skill_view(name='product-pipeline', file_path='references/google-docs-prd-delivery.md')`
> para detalhes completos do fluxo reverso, código Python e padrões comuns de edição.

#### Entrega do PRD

O usuário pode solicitar o PRD em diferentes formatos:

| Formato | Como entregar |
|---------|---------------|
| **Markdown (.md)** | Salvar em `product/management/PRD.md` e enviar via `MEDIA:/path` no Telegram |
| **Google Docs** | Ver `skill_view(name='product-pipeline', file_path='references/google-docs-prd-delivery.md')` |

Para Google Docs, o fluxo inclui verificação de token OAuth, re-autenticação PKCE (se necessário),
criação do doc, e compartilhamento com permissão "qualquer pessoa com o link pode comentar".

> ⚠️ **Regra crítica — direção do sync:** Uma vez que o Google Doc é compartilhado com a equipe
> para revisão, o doc passa a ser a **fonte da verdade colaborativa**. NUNCA sobrescrever o Google Doc
> com markdown local a menos que o usuário peça explicitamente. A direção correta é:
> **Google Docs (equipe) → markdown local (Hermes)**. Inserir markdown puro no doc destrói
> o trabalho de formatação da equipe — se o conteúdo já está no doc, leia de lá e atualize o
> markdown local, nunca o contrário.

### Saída

```
product/management/
├── PRD.md
├── user-personas.md
├── opportunity-solution-tree.md
├── user-stories.md
└── product-roadmap.md
```

---

## Fase 4: MVP

### 4a. Design (Pi modelo best + Antigravity + Stitch MCP)

> **Design System HTML é obrigatório desde o início.** Pi sempre produz `design-system.html` (todos os componentes renderizados visualmente) junto com os documentos de design. agy revisa em loop de 2+ iterações. O padrão: **Pi cria → agy revisa → Pi corrige → agy confirma**. Cada iteração registrada em `feedbacks.md` com `## Iteração N — Agente`. O loop termina com `## ACORDO: DESIGN SYSTEM FINALIZADO`.
>
> **Stitch MCP (último passo):** Google Stitch MCP é usado APÓS o design system estar aprovado, para gerar screens de UI finais a partir dos componentes já definidos. Stitch extrai DNA visual e acelera a prototipagem das telas finais. Ver `skill_view(name='product-pipeline', file_path='references/google-stitch-mcp.md')` para setup, tools disponíveis e fluxos de uso.

#### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/design
   ```

2. **Pi carrega skills de UX/UI design** (modelo best) e produz:
   - Wireframes (`/skill:ux-wireframing`)
   - Design System (`/skill:ux-design-system`)
   - Mapa de Empatia (`/skill:ux-empathy-map`)
   - Mapa de Jornada do Usuário (`/skill:ux-journey-map`)
   - User Flows (`/skill:ux-user-flow`)

3. **Pi implementa `design-system.html`** — HTML/CSS completo com todos os componentes do design system renderizados visualmente, usando dados mockados. Deve incluir paleta de cores, tipografia, botões, cards, formulários, navegação, modais, e grid system. Quebrar em lotes se necessário (v4-flash: ~2 docs/sessão, v4-pro: ~3 docs/sessão).

4. **Verificação de saída do Pi — NÃO confiar só no monitoramento de sessão:**
   ```bash
   # CERTO: verificar arquivos de output
   ls -la /opt/data/code/workstation/PROJETO/product/design/wireframes.md
   grep "PHASE_COMPLETE" /opt/data/code/workstation/PROJETO/product/design/wireframes.md
   ```
   Pi pode parecer travado mas já ter completado todo o output. Sempre verificar os arquivos no shared volume antes de matar ou reiniciar.

5. **Loop de revisão Antigravity:**
   ```bash
   agy -p "Review the design at /opt/data/code/<projeto>/product/design/.
   Evaluate: visual hierarchy, typography, color, spacing, interaction design.
   Write your feedback in product/design/feedbacks.md"
   ```
   - **Pi cria → agy revisa → Pi corrige → agy confirma**
   - Cada iteração registrada em `feedbacks.md`
   - Loop termina com `## ACORDO: DESIGN SYSTEM FINALIZADO`
   - **Agy executa do HOST, não do container**

6. **Stitch MCP — geração de telas finais (último passo):**
   Com o design system aprovado, usar Stitch MCP para gerar cada tela.

   **Pré-requisitos:**
   - Stitch MCP configurado como HTTP direto no `/opt/data/config.yaml` (NÃO no `.hermes/config.yaml`)
   - Design system verificado e atualizado ANTES de gerar — conferir: `colorMode` (DARK/LIGHT), fontes, cores primárias
   - `/reload-mcp` feito para ativar as tools

   **Workflow:**
   a) **Verificar design system existente** no projeto Stitch via `list_design_systems`
   b) **Atualizar/criar** design system com tokens corretos antes de gerar screens
      - Atenção: `UpdateDesignSystem` não aceita todas as fontes (BRICOLAGE_GROTESQUE falha, usar SPACE_GROTESK)
      - `CreateDesignSystem` aceita mais fontes mas pode dropá-las silenciosamente
   c) **Gerar mobile primeiro** (`deviceType=MOBILE`), depois desktop (`deviceType=DESKTOP`)
      - Usar `generate_screen_from_text` com prompts detalhados (mencionar tokens exatos: hex colors, font names, radius)
      - Incluir sempre `designSystem: assets/<id>` para consistência visual
   d) **Baixar screenshots** full-res: URL + `=s0` → salvar em `/opt/data/delfos-screens/`
   e) **Enviar via MEDIA** para o usuário
   f) **Gerar protótipo HTML** via agy após Stitch screens aprovadas:
      ```bash
      ssh oracle-host "cat prompt.txt | /home/ubuntu/.local/bin/agy --print --model gemini-3.1-pro --print-timeout 5m"
      ```
   g) Iterar com `edit_screens` + `generate_variants` se necessário
   - Stitch é o passo final da F4a — só depois que agy aprovou o design system

### Saída

```
product/design/
├── wireframes.md
├── design-system.md
├── design-system.html    (obrigatório — componentes renderizados)
├── empathy-map.md
├── journey-map.md
├── feedbacks.md
└── stitch-screens/       (telas geradas pelo Stitch MCP, última etapa)
```

---

### 4b. Engineering (Pi modelo best + cost + Antigravity)

> Na prática, `delegate_task` timeoutou ao orquestrar Pi via SSH de dentro de um subagente. Executar Pi diretamente do Hermes pai. v4-flash é suficiente para documentação técnica; v4-pro reservado para decisões arquiteturais complexas.

#### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/engineering
   ```

2. **Pi carrega skills de engenharia** (modelo best) e produz:
   - SAD, TechSpecs, ERD, API contracts, Test Plan, Release Notes

3. Pi gera lista de tarefas em **`product/engineering/code-tasks.md`**

4. **Execução — Hermes instancia Pi (modelo cost) em LOTES por layer:**
   - Agrupa tasks relacionadas em um único prompt
   - Invoca Pi UMA vez com todas as tasks do lote
   - Pi escreve todos os arquivos do lote
   - Hermes verifica e commita
   - Avança para o próximo layer (continua mesma sessão Pi com `-c`)

5. **Build final — Pi modelo best faz revisão final**

6. **Antigravity revisa código e testes**

7. Feedbacks trocados via `product/engineering/feedbacks.md`

8. Quando código e testes forem aprovados → avançar para **4d. Docker Build & Deploy**

### Saída

```
product/engineering/
├── SAD.md
├── tech-specs.md
├── ERD.md
├── api-contracts.yaml
├── test-plan.md
├── release-notes.md
├── code-tasks.md
└── feedbacks.md
```

---

### 4c. Post-Code: Test Execution & Debug Loop

> **Referência:** `skill_view(name='product-pipeline', file_path='references/first-test-run-pipeline.md')`

Após executar todas as code-tasks, Pi gera código funcional mas com incompatibilidades de ambiente. Padrão que resolveu ~95% dos erros:

```
1. INSTALAR deps: uv venv + uv pip install -e ".[dev]"
2. CRIAR pytest.ini: asyncio_mode = auto
3. RODAR tests unitários primeiro
4. RODAR tests de integração
5. PI BEST revisa falhas e CORRIGE DIRETAMENTE
6. HERMES valida os fixes
7. COMMIT + AGY re-avalia
```

#### Ordem de prioridade para fixes

| Prioridade | Fix | Impacto típico |
|-----------|-----|----------------|
| 1 | ForeignKey nos models | ~55 erros |
| 2 | bcrypt==4.0.1 | ~10 erros |
| 3 | aiosqlite nas deps | ~2 erros |
| 4 | `from __future__ import annotations` | ~13 erros |
| 5 | pytest.ini com asyncio_mode=auto | ~68 erros |
| 6 | Conftest de integração | ~39 erros |
| 7 | MissingGreenlet | ~25 erros |
| 8 | Trailing slash 307 | ~12 erros |
| 9 | `_task_to_response` sem relationships | ~16 erros |
| 10 | SQLite Date/Time | ~5 erros |
| 11 | Deprecations (utcnow, class Config) | warnings |

---

### 4d. Docker Build & Deploy

> **Referência:** `skill_view(name='product-pipeline', file_path='references/docker-build-deploy.md')`

1. Garantir Dockerfiles (frontend + backend)
2. `docker compose build 2>&1`
3. Corrigir falhas no build
4. Gerar `.env`
5. `docker compose up -d`
6. Verificar com checklist
7. Avançar para **4e. Validação Final**

#### Pitfalls comuns na Oracle VM

| Problema | Solução |
|----------|---------|
| ghcr.io inacessivel | `pip install uv` |
| Porta 80 ocupada | Remapear para `8080:80` |
| Boolean default `0`/`1` no PostgreSQL | Trocar para `sa.text("false")` / `sa.text("true")` |
| Healthcheck 401 | Verificar prefixo do router |

## Deploy: GitHub + Systemd + Nginx

Após o Antigravity aprovar (4e), estruturar o deploy final.

### Oracle Cloud: apenas portas 80/443 abertas externamente

A Oracle Cloud Application Firewall só expõe as portas 80 e 443. Usar Nginx Proxy Manager na porta 80 para expor o app.

**Passos:**

1. **Criar repositório GitHub privado e fazer push**
2. **Clonar para selfhost/** no host
3. **Systemd service** (auto-start no boot)
4. **Conectar à rede do Nginx Proxy Manager**
5. **Proxy reverso** via NPM ou nginx do host

> **Trailing slash bug:** FastAPI gera redirects 307. `$http_host` vs `$host` no proxy_set_header. Solução real: middleware FastAPI com redirect relativo + `redirect_slashes=False`.

---

### 4e. Validação Final pelo Antigravity

> Carrega a skill `dogfood` para QA exploratório antes do veredito.

#### Fluxo

0. **Dogfood QA** — teste exploratório sistemático
1. **Hermes coleta evidências** via browser (7 screenshots padrão)
2. **Entrega prints ao usuário** via MEDIA
3. **Salva prompt do agy** como `.md` em `product/engineering/dogfood/prompt-para-antigravity.md`
4. **Invocar agy via tmux interativo** (não `agy -p`)
5. **Verificar o veredito** no `feedbacks.md`
6. Se aprovado → Deploy
7. Se rejeitado → Loop de correção

> **Hermes NÃO diagnóstica bugs.** Apenas coleta evidência. A análise é do Antigravity.

#### Decisão final

| Resultado | Próximo passo |
|-----------|---------------|
| **APROVADO** | MVP concluído. Avançar para F5 |
| **REJEITADO** | Loop de correção (Pi best → rebuild → re-valida) |

---

## Fase 5: Iteração e Melhoria

> **Skill principal:** `backlog-and-sprint`

1. Usuário testa o MVP
2. Backlog não-estruturada
3. Melhorias pontuais rápidas
4. Sprints (quando solicitado)

---

## Formato do feedbacks.md

Estruturados como **conversas multi-turno entre agentes**:

```markdown
## Turno N — @AgenteRemetente

**Para:** @AgenteDestinatário
**Em resposta ao:** Turno N-1

### Conteúdo

Com status ( / / ), citações, código.

### O que espero de você, @AgenteDestinatário:
- [ ] Ação concreta
```

- **Turno 1** não tem "Em resposta ao"
- **Turno final**: `**Decisão final:** ACORDO: ...`
- Menções a `@Pi`, `@Antigravity`, `@Hermes` são permitidas

---

## Phase Completion Audit

Após cada fase, auditar entregáveis:

```bash
echo "=== FASE [N]: [Nome] ==="
ls -la product/[fase]/*.md 2>/dev/null
grep "PHASE_COMPLETE: [fase]" product/[fase]/PRD.md
```

Itens a verificar:
- [ ] Todos os arquivos da `## Saída` existem?
- [ ] Marcador `<!-- PHASE_COMPLETE: ... -->` presente?
- [ ] F4e: Dogfood QA report gerado?
- [ ] F4e: Antigravity aprovou?
- [ ] Tudo commitado?
- [ ] Usuário revisou e aprovou (F1)?

---

## Pitfalls

⚠️ **agy via SSH pode quebrar permissões do container** — agy (SSH host, uid 1001) pode executar `sudo chown -R ubuntu:ubuntu` no diretório do projeto, e o container Hermes (uid 10000) perde escrita. **Fix:** rodar `ssh oracle-host 'sudo chmod -R 777 ...'`. Verificar permissões após agy executar.

⚠️ **Stitch MCP — config no `/opt/data/config.yaml`, NÃO no `.hermes/config.yaml`** — O override (`~/.hermes/config.yaml`) funciona para desenvolvimento rápido, mas o config principal (`/opt/data/config.yaml`) é o repositório oficial. Stitch MCP HTTP não funciona via npx proxy — usar `url:` + `headers:` + `transport: http`. A API key vai no header `X-Goog-Api-Key`. Editar via SSH no host com Python (não sed) para evitar YAML malformado.

⚠️ **Stitch MCP — design system ANTES das screens** — Sempre verificar/atualizar o design system no Stitch antes de gerar screens. Screens geradas com tokens errados (LIGHT em vez de DARK, fonte errada) precisam ser descartadas e regeneradas.

⚠️ **Stitch UpdateDesignSystem — fontes limitadas** — BRICOLAGE_GROTESQUE não funciona no UpdateDesignSystem. Usar SPACE_GROTESK como alternativa. Testar fontes no Update antes de tentar no Create.

⚠️ **Stitch MCP — usar o mesmo design system id em todas as telas** — Para consistência visual, passar `designSystem: assets/<id>` em toda chamada de `generate_screen_from_text`.

⚠️ **agy prototype — executar no host, não no container** — agy está em `/home/ubuntu/.local/bin/agy` no host Oracle. Usar `ssh oracle-host` com `--print` para geração não-interativa. O modelo `gemini-3.1-pro` funciona bem para protótipos complexos. `--print-timeout 5m` evita timeout prematuro.

⚠️ **Stitch MCP — usar HTTP direto, não stdio proxy** — A API key funciona no header `X-Goog-Api-Key` quando usada via HTTP MCP direto (`url:` + `headers:`). O `@_davideast/stitch-mcp` package tem um subcomando `tool` que NÃO funciona com API key. Usar `transport: http` com headers no config do Hermes. Ver `skill_view(name='product-pipeline', file_path='references/google-stitch-mcp.md')`.

⚠️ **Pi best não streama stdout intermediário** — Com MiniMax M3, Pi pode levar 4-5 min por documento sem produzir stdout. Monitorar pelos arquivos de saída, não pelo output do processo. Usar `terminal(background=true)` + `ls -la` periódico.

⚠️ **Pi PATH pode não estar definido** — Pi está em `/opt/data/pi-global/bin/pi`. Se `which pi` falhar, exportar PATH ou usar caminho absoluto.

⚠️ **batch-splitting para tarefas grandes do Pi** — Quebrar em lotes de 2-3 docs. v4-pro aguenta ~3 docs/sessão; v4-flash ~2.

⚠️ **Pi parece travado mas output já está completo** — Verificar arquivos no shared volume antes de matar.

⚠️ **Async Pi execution** — Executar em background, monitorar via shared volume, não via SSH.

⚠️ **Commit + tag ANTES de invocar Pi para fixes** — Criar checkpoint antes de Pi modificar código.

⚠️ **Tests fora do Docker build context** — `docker cp` obrigatório.

⚠️ **Oracle Cloud: portas** — Apenas 80/443 externas. Usar NPM.

⚠️ **SQLite `func.now()`** — Precisão de segundos. Usar `default=datetime.now(timezone.utc)` em vez de `server_default`.

⚠️ **delegate_task timeout (600s)** — Executar Pi diretamente do Hermes, não delegar.

⚠️ **v4-flash para docs de engenharia** — Suficiente. v4-pro reservado para decisões arquiteturais.

⚠️ **`agy -p` stallou em Docker commands** — Usar tmux interativo.

⚠️ **`agy design` NÃO valida código existente** — Gera novo design hipotético. Usar browser tools.

⚠️ **Hermes coleta evidência, NÃO diagnóstica bugs na 4e** — Só reportar o que viu.

⚠️ **Permissão do container — agy pode quebrar com chown** — evitar. Ver pitfall "agy via SSH" acima.

⚠️ **agy output token limit (>70KB)** — Quebrar em CSS/HTML/JS separados.

⚠️ **UID mismatch** — Hermes (10000) vs Pi (1001). Verificar permissões antes de cada fase.

⚠️ **Pre-flight check** — Verificar antes de cada fase. O usuário não quer gastar tokens debugando permissão.

⚠️ **Workstation 777 não herda** — Rodar `chmod -R 777` após criar pastas.

⚠️ **Git add com path explícito** — `git add product/management/` em vez de `-A`.

⚠️ **Pi skills não existem por padrão** — Instalar manualmente.

⚠️ **MiniMax M3 free encerrado** — Usar `opencode-go/minimax-m3`.

⚠️ **DeepSeek v4-Pro timeout** — Usar v4-flash ou `/compact preserve:context`.

⚠️ **F1 scope: manter conceitual** — Feature matrix, schema de dados, entidades e arquitetura são materiais de F3 em diante. A ideação deve ficar em nível de promessa, persona, nome/conceito e delimitação de escopo. **Não fixar entidades, schemas ou campos durante a consolidação da F1** — o que importa são as regras (ex: "IA não altera o schema"), não a estrutura em si. O nome do projeto carrega o conceito — registrar no `ideation-result.md`.

⚠️ **Mirror `<projeto>.old/`** — Verificar e remover lixo após corrigir permissões.

⚠️ **Frontend scaffolding** — Criar arquivos manualmente, não usar `create-vite`.

⚠️ **Pi adora "***" como placeholder de senha** — Substituir por `"secret123"`.

⚠️ **Backend restart: ConnectionResetError** — Aguardar health check 200.

⚠️ **UUID no PostgreSQL vs String(36)** — Usar `UUID` do dialect PostgreSQL.

⚠️ **Pi best overshoot em conftest** — Não aceitar mudança no `event_loop` sem testar.

⚠️ **Prompt files no shared volume** — UID mismatch bloqueia leitura do Pi.

⚠️ **bcrypt pin** — `bcrypt==4.0.1` no Dockerfile.

⚠️ **patch/write_file falha com UID 1001** — `chmod o+w` no diretório pai ou usar SSH.

⚠️ **Google OAuth PKCE — setup.py não persiste code_verifier** — O script `setup.py` do google-workspace gera URLs de auth sem salvar o PKCE verifier. A troca falha com `Missing code verifier`. Usar `google_oauth_gen.py` + `google_oauth_exchange.py`. Ver `skill_view(name='product-pipeline', file_path='references/google-oauth-pkce-workaround.md')`.

⚠️ **Google token expira após ~7 dias** — Refresh falha com `invalid_grant`. Re-autenticação completa PKCE necessária.

⚠️ **Google Docs: token não autoriza escopo de documentos** — O token existente pode ter sido criado sem o escopo `https://www.googleapis.com/auth/documents`. Re-autenticar com escopos explícitos.

## Verificacao Rapida

```bash
# Antes de iniciar o pipeline ou cada fase
pi --version
pi -p "list skills" --provider deepseek --model deepseek-v4-flash
ls /opt/data/code/workstation/PROJETO/product/ 2>/dev/null
ssh oracle-host 'echo "n" | timeout 5 /home/ubuntu/.local/bin/agy 2>&1 | head -3'
git config user.name && git config user.email
touch /opt/data/code/workstation/PROJETO/.perm-check 2>/dev/null && rm $_ && echo "OK" || echo "BLOQUEADO"
```
