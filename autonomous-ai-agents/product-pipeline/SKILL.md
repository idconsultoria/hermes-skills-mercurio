---
name: product-pipeline
description: Multi-agent product pipeline from raw idea to MVP with iterative sprints. Orchestrated by Hermes, executed by Pi Agent + Antigravity.
category: autonomous-ai-agents
---

# Product Development Pipeline

> **Orquestrador:** Hermes
> **Executores:** Pi Agent (local, v0.78.1) + Antigravity (revisor visual)
> **Shared volume:** `/opt/data/code/` ↔ `/workspace/code/`

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

### 🔗 Hierarquia de uso

```
CARO/ESCASSO     agy ─── Consultor externo especialista (design, UX, estrategia)
ESCASSO          Pi best ── Eng. senior interno (MiniMax M3 via Go)
BARATO/ABUNDANTE Pi cost ─ Dev junior (DeepSeek V4 Flash Free)
GRATUITO         Pi cost ── Free tier Zen
```
```

Ver skill pi-agent-coordination para detalhes completos.
```

### Conexões

| Conexão | Como |
|---------|------|
| **Hermes ↔ Pi (one-shot)** | `pi -p "..." --provider deepseek --model deepseek-v4-flash` (local, sem SSH) |
| **Hermes ↔ Pi (persistent session)** | Primeiro: `pi --name "sessao" -p "..."`, depois: `pi -c -p "..."` |
| **Hermes ↔ Pi (sessão id)** | `pi --session /path/to/session.jsonl -p "..."` |
| **Hermes ↔ agy** | `ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && /home/ubuntu/.local/bin/agy -p "..."'` |
| **Pi → agy (design feedback)** | Pi salva protótipo → Hermes chama agy → agy escreve em `feedbacks.md` |

> 🔄 **Sem limite de tempo:** Toda invocacao de Pi e agy no pipeline roda **sem timeout**. Pi pode gerar output por minutos sem streamar stdout — `timeout N` mata o processo silenciosamente (exit code 0 não indica erro). agy pode levar minutos analisando código. Nunca usar `timeout` com Pi ou agy. Para Pi: usar `terminal(background=true)` ou foreground sem flag de timeout. Para agy: usar tmux interativo.
> Pi e local — nao ha SSH, nao ha timeout de conexao, nao ha quoting hell.
> Para tarefas muito longas (>5min), Pi pode stallar — usar agy ou quebrar em partes.
> Ver skill pi-agent-coordination para detalhes de fallback entre modelos.

### Modelos

#### Pi Best (planejamento, design, docs complexos)

Priorizar MiniMax M3 via Go:

| Opção | Provider | Model ID | Custo | Notas |
|-------|----------|----------|-------|-------|
| 🥇 **Pi best** | `opencode-go` | `minimax-m3` | $10/mês, cota semanal $30 | Preferido. Chave ativa |
| 🥈 **Fallback 1 (via Go)** | `opencode-go` | `deepseek-v4-pro` | Cota semanal $30 | Mesmo provider, modelo diferente |
| 🥉 **Fallback 2 (API direta)** | `deepseek` | `deepseek-v4-pro` | $0.14/M input, $0.42/M output | Último recurso |

#### Pi Cost (execução de code-tasks, fixes, docs)

| Prioridade | Provider | Model ID | Custo | Notas |
|-----------|----------|----------|-------|-------|
| 1° 🥇 | `opencode` (Zen) | `opencode/deepseek-v4-flash-free` | **Gratuito** | Preferido. Chave OpenCode ativa |
| 2° 🥈 | `opencode-go` (Go) | `deepseek-v4-flash` | Cota semanal $30 | Fallback se Zen rate-limited |
| 3° 🥉 | `deepseek` (API direta) | `deepseek-v4-flash` | $0.14/M input | Último recurso |

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
# 1. Pi acessivel?
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

### Fluxo

1. Hermes cria a estrutura inicial. **Pi e Hermes compartilham o mesmo filesystem** — nao ha mais UID mismatch:

   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/ideation /opt/data/code/workstation/PROJETO/prompts
   cd /opt/data/code/workstation/PROJETO && git init -b main 2>/dev/null
   git add -A 2>/dev/null; git commit -m "chore: init" 2>/dev/null || true
   ```

   > ⚠️ Antes o Pi rodava em container separado (uid 1001) e Hermes (uid 10000) sofria EACCES.
   > Agora Pi é local (mesmo container), uid unico — sem split filesystem, sem permissao.
   > O shared volume workstation/ (777) ainda existe mas nao e mais necessario para
   > contornar UID mismatch — e mantido por compatibilidade com scripts existentes.

2. Hermes cria **sessão Pi persistente com nome** e envia a ideia inicial. Pi roda em **background sem timeout** (ver Conexões):

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

   scp /opt/data/code/workstation/PROJETO/prompts/pi-ideation.md \
     oracle-host:/home/ubuntu/selfhost/shared/code/workstation/PROJETO/prompts/pi-ideation.md

   ssh oracle-host 'bash -s' << 'ENDSCRIPT'
   cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
   LC_DIR=code/PROJETO \
     nohup pi-agent 'pi --name "PROJETO-ideation" \
     -p "$(cat prompts/pi-ideation.md)" \
     --provider opencode-go --model minimax-m3' \
     > /tmp/pi-ideation.log 2>&1 &
   ENDSCRIPT

   for i in $(seq 1 40); do
     sleep 30
     ssh oracle-host 'SESS=$(ls -dt ~pi/.pi/agent/sessions/--workspace-* 2>/dev/null | head -1); [ -n "$SESS" ] && wc -l "$SESS"/*.jsonl 2>/dev/null'
     if grep -q "PHASE_COMPLETE" /opt/data/code/workstation/PROJETO/product/ideation/ideation-result.md 2>/dev/null; then
       echo "Ideação concluída!"; break
     fi
   done
   ```

   ⚠️ **Relay pattern — relay de perguntas do Pi:** Pi como sub-agente não usa clarify. Se o Pi fizer perguntas durante a ideação, Hermes relay: mostra pro usuário, coleta resposta, reenvia ao Pi continuando a sessão em background:

   ```bash
   ssh oracle-host 'bash -s' << 'ENDSCRIPT'
   cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
   LC_DIR=code/PROJETO \
     nohup pi-agent 'pi -c -p "Resposta do usuário com histórico completo..." \
     --provider opencode-go --model minimax-m3' \
     > /tmp/pi-ideation.log 2>&1 &
   ENDSCRIPT
   ```

3. **Pi carrega `ideation-drilling`** e faz sequência longa de perguntas via pty output:
   - "Esse produto é realmente necessário?"
   - "Não há alternativa mais simples e barata?"
   - "Essa feature é essencial?"
   - "Se faltar X, o projeto ainda atinge o objetivo?"
   - "O que exatamente você quer dizer por Y?"
   - "Seria mais ou menos isso e isso?"

   ⚠️ **Relay pattern — Pi não usa `clarify`:** Pi como sub-agente não faz perguntas. Toda pergunta chega via pty output. Hermes precisa:
   a) Relatar ao usuário em formato limpo
   b) Coletar a resposta
   c) Reenviar ao Pi com `CONTEXT` contendo histórico completo das perguntas e respostas

4. Quando agente e humano se dão por **plenamente satisfeitos**, Pi escreve **`product/ideation/ideation-result.md`** com:
   - Detalhamento completo da ideia final
   - Lista de racionais para cada decisão

### Saída
```
product/ideation/ideation-result.md
```
Com marcador `<!-- PHASE_COMPLETE: ideation -->`

⚠️ **Arquivos .MD entregues via MEDIA, nunca como texto inline.** Quando o usuário pede um arquivo .md (ideation-result.md, relatório de fase, documento de produto), salvar o conteúdo em disco e entregar via `MEDIA:/path/to/file` no Telegram. Texto inline de .md longo é truncado, perde formatação, e o usuário não consegue baixar. Esta regra cobre F1 e TODAS as fases do pipeline — o usuário explicitamente prefere baixar arquivos.

### Detecção de conclusão
```bash
grep "PHASE_COMPLETE" /opt/data/code/<projeto>/product/ideation/ideation-result.md
```

### Revisão pelo usuário

Após o Pi escrever `ideation-result.md`, Hermes:
1. Verifica se o arquivo existe e contém o marcador `PHASE_COMPLETE`
2. Envia o `.md` ao usuário **como arquivo anexado (MEDIA)** no Telegram, nunca como texto inline — o usuário explicitamente prefere baixar o arquivo
3. **Aguarda a aprovação explícita do usuário** antes de seguir para F2

> ⚠️ **Essa pausa é obrigatória.** O usuário precisa validar o entendimento mútuo antes de prosseguir.

### Variante: Ideação assíncrona com múltiplos participantes (AI Studio)

Quando a ideação precisa envolver **2+ pessoas que não podem participar da mesma sessão síncrona** com o Pi (stakeholders em horários diferentes, equipe remota, sócios com agendas conflitantes):

#### Quando usar

- Equipe com 3+ pessoas que precisam contribuir individualmente
- Os participantes não têm acesso ao Pi Agent / Hermes
- Precisa-se de respostas independentes, sem influência entre participantes
- O briefing inicial já é rico o suficiente para não precisar de drilling síncrono

#### Fluxo

1. **Hermes cria** um prompt de sistema auto-contido para o Google AI Studio, que incorpora a metodologia de `/skill:ideation-drilling`:
   - Máximo de 6 turnos por participante (critério absoluto de parada)
   - Cardápio de perguntas: necessidade real, prioridade, definição, trade-off, diferenciação, público
   - Uma pergunta por vez, com síntese antes de cada novo turno
   - Formato de saída: bloco ````markdown` copiável com relatório completo

2. **Cada participante** roda a conversa no AI Studio individualmente, no seu próprio ritmo

3. **Ao final** (6º turno ou entendimento satisfatório), o agente:
   - Agradece o participante
   - Gera um bloco markdown com o relatório completo da entrevista
   - Instrui enfaticamente: *"Copie TODO o conteúdo deste bloco e envie no grupo da equipe"*

4. **Hermes compila** os relatórios na Fase 2 (Pesquisa) — cada um vira `product/research/user-interview-<nome>.md`

#### Template

O template completo do prompt de sistema está em `skill_view(name='ideation-drilling', file_path='references/ai-studio-ideation-system-instruction.md')`.

### Git commit (via pi-shell)

Após aprovação do usuário:
```bash
ssh oracle-host 'pi-shell "cd /workspace/code/workstation/PROJETO && \
  git config user.email \"email@projeto\" && \
  git config user.name \"Nome\" && \
  git add -A && git commit -m \"feat: F1 ideation complete\""'
```

> ⚠️ **Git no workstation:** Apesar de Hermes poder criar diretórios em `workstation/` (777), `git init` cria `.git/` com ownership herdado (uid 1001). Commits de Hermes falham com `Permission denied`. Sempre delegar `git commit` ao pi-shell.

---

## Fase 2: Pesquisa

**Agente:** Hermes

### Fluxo

1. Criar subpasta (via pi-shell — Hermes não escreve no shared volume):
   ```bash
   ssh oracle-host 'pi-shell "mkdir -p /workspace/code/PROJETO/product/research"'
   ```

2. **Planejar pesquisa** com recurso `/plan` — revisado pelo usuário antes de iniciar.

3. Disparar sub-agentes `deep-research` para cada tópico:
   - **Referências explícitas:** softwares usados como inspiração, conceitos-chave
   - **Referências implícitas:** domínios relacionados que Hermes julgue relevantes
   - **Mercado e perfil de usuário:** concorrência, tendências, perfil demográfico

   ```python
   delegate_task(
       goal="Pesquisar profundamente sobre [tópico]",
       context="Contexto do projeto + perguntas específicas",
       toolsets=["web", "browser"]
   )
   ```

4. **Entrevista de usuário:**
   - Carregar skill `user-interview`
   - **Produto pessoal:** Hermes entrevista o usuário diretamente
   - **Produto com outros perfis:** simular entrevista para cada perfil de usuário
   - **Agentes de IA como usuários:** simular entrevista com agente(s) de IA

5. Cada resultado de pesquisa e entrevista armazenado como `.md` em `product/research/`.

   ⚠️ **Nao ha mais UID mismatch entre Hermes e Pi** — Pi roda localmente no mesmo container.
   Arquivos criados por Hermes sao visiveis e editaveis pelo Pi diretamente, sem `chmod` adicional.

   ```bash
   git add -A && git commit -m "feat: F2 research complete"
   ```

### Saída
```
product/research/
├── referencias-explicitas.md
├── referencias-implicitas.md
├── mercado.md
├── user-interview.md
└── <outros>.md
```

---

## Fase 3: Desenvolvimento de Conceito

**Agente:** Pi (modelo best)

### Fluxo

1. Criar subpasta (via pi-shell):
   ```bash
   ssh oracle-host 'pi-shell "mkdir -p /workspace/code/PROJETO/product/management"'
   ```

2. Hermes invoca **Pi com modelo best** em sessão persistente, carregando skills de PM:
   ```bash
   CONTEXT="A partir dos arquivos em:
   - product/ideation/ideation-result.md
   - product/research/*.md

   Carregue as skills de product management e produza os documentos
   de PM na pasta product/management/."

   ssh oracle-host "LC_DIR=code/<projeto> pi-agent \
     'pi --name \"<projeto>-pm\" -p \"$CONTEXT\" --provider opencode-go --model minimax-m3'"
   ```

3. Pi carrega skills instaladas e elabora:
   - **PRD** — `/skill:prd-development`
   - **User Personas** — `/skill:proto-persona`
   - **Opportunity Solution Tree** — `/skill:opportunity-solution-tree`
   - **User Stories** — `/skill:user-story`
   - **Product Roadmap** — `/skill:roadmap-planning`
   - (e outros que julgar necessários)

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

### 4a. Design (Pi modelo best + Antigravity)

> **Design System HTML + Loop de Revisão:** Esta fase pode incluir uma sub-fase opcional onde Pi implementa um `design-system.html` completo (todos os componentes renderizados visualmente) e agy revisa em loop de 2+ iterações. O padrão: **Pi cria → agy revisa → Pi corrige → agy confirma**. Cada iteração registrada em `feedbacks.md` com `## Iteração N — Agente`. O loop termina com `## ACORDO: DESIGN SYSTEM FINALIZADO`.

#### Fluxo

1. Criar subpasta (via pi-shell):
   ```bash
   ssh oracle-host 'pi-shell "mkdir -p /workspace/code/PROJETO/product/design"'
   ```

2. **Pi carrega skills de UX/UI design** (modelo best) e produz:
   - Wireframes (`/skill:ux-wireframing`)
   - Design System (`/skill:ux-design-system`)
   - Mapa de Empatia (`/skill:ux-empathy-map`)
   - Mapa de Jornada do Usuário (`/skill:ux-journey-map`)
   - User Flows (`/skill:ux-user-flow`)
   - Protótipo de alta fidelidade (HTML/CSS interativo com dados mockados)

3. **Verificação de saída do Pi — NÃO confiar só no monitoramento de sessão:**
   O Pi salva session logs em `~pi/.pi/agent/sessions/*.jsonl` que são **efêmeros** — vivem dentro do container Pi e somem quando o container morre. Os arquivos de output, porém, persistem no shared volume. Para verificar se Pi concluiu:
   ```bash
   # ✅ CERTO: verificar arquivos de output no shared volume
   ls -la /opt/data/code/workstation/PROJETO/product/design/wireframes.md
   ls -la /opt/data/code/workstation/PROJETO/product/design/user-flows.md
   ls -la /opt/data/code/workstation/PROJETO/product/design/prototype.html
   grep "PHASE_COMPLETE" /opt/data/code/workstation/PROJETO/product/design/wireframes.md

   # ❌ ERRADO: session files podem sumir se o tmux morrer
   ssh oracle-host 'wc -l ~pi/.pi/agent/sessions/*.jsonl'  # EFÊMERO
   ```

   ⚠️ **Pi pode parecer travado** (idle longo, CPU próximo de 0%) mas já ter completado todo o output. Sempre verificar os arquivos no shared volume antes de matar ou reiniciar o processo.

3. **Antigravity é invocado como crítico e revisor**:
   ```bash
   # Do container (se token OAuth estiver ativo):
   agy -p "Review the design at /opt/data/code/<projeto>/product/design/.
   Evaluate: visual hierarchy, typography, color, spacing, interaction design.
   Write your feedback in product/design/feedbacks.md"

   # Do host (se token no keyring, mais confiável):
   ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
     /home/ubuntu/.local/bin/agy -p "Review the design at product/design/. ..."'
   ```

4. Toda conversa entre Pi e Antigravity acontece em **`product/design/feedbacks.md`** no formato **conversa multi-turno** (ver `## Formato do feedbacks.md`):
   - Cada turno é uma mensagem `## 🗨️ Turno N — @Agente` com conteúdo estruturado
   - Cada turno explicita **o que espera do outro agente** ao final
   - Antigravity tem **palavra final** sobre aspectos visuais
   - Pi sabe disso, ainda assim defende suas ideias

5. **Fase concluída quando ambos concordam explicitamente** em passar o design para engenharia:
   ```markdown
   **✅ Decisão final:** ACORDO: PASSAR PARA ENGENHARIA
   ```

#### Sub-fase: Design System HTML (+ Loop de Revisão)

Quando o usuário solicitar implementação visual do design system:

1. Pi cria `design-system.html` com base no `design-system.md`, renderizando todos os componentes (paleta, tipografia, sidebar, task list, botões, etc.)

2. Para tarefas grandes de Pi (design system HTML com 12+ componentes), **quebrar em lotes**:
   - **Lote 1** (v4-flash, timeout 300s): wireframes.md + empathy-map.md + journey-map.md
   - **Lote 2** (v4-flash, timeout 300s): design-system.md + user-flows.md
   - **Lote 3** (v4-pro, timeout 600s): prototype.html
   - **Lote 4** (v4-flash, timeout 300s): design-system.html
   - **Lote 5+**: Loop de revisão

3. Loop de revisão (formato conversa multi-turno — ver `## Formato do feedbacks.md`):
   ```bash
   # Turno 1: agy revisa
   ssh oracle-host 'agy -p "Review design-system.html at [path]. \
     Evaluate all 12 components. Append under ## 🗨️ Turno 1 — @Antigravity \
     with explicit ⬆️ O que espero de @Pi"

   # Turno 2: Pi responde e corrige o HTML
   ssh oracle-host "LC_DIR=code/PROJETO pi-agent 'pi -c -p \
     \"Leia feedbacks.md ## 🗨️ Turno 1 — @Antigravity. \
     Responda em ## 🗨️ Turno 2 — @Pi no formato conversa. \
     Aplique correções no design-system.html.\"'"

   # Turno 3: agy re-review + acordo
   ssh oracle-host 'agy -p "Re-review design-system.html. Verify corrections. \
     If satisfied, append as ## 🗨️ Turno 3 — @Antigravity \
     com **✅ Decisão final:** ACORDO: DESIGN SYSTEM FINALIZADO"'
   ```

4. **Agy executa do HOST, não do container** — ver referência nos Pitfalls.

### Saída
```
product/design/
├── wireframes.md
├── design-system.md
├── empathy-map.md
├── journey-map.md
├── prototype.html
├── design-system.html    ← implementação visual dos componentes (opcional)
└── feedbacks.md
```

---

### 4b. Engineering (Pi modelo best + cost + Antigravity)

> ⚡ **Na prática (F4b):** `delegate_task` timeoutou (600s) ao tentar orquestrar Pi via SSH de dentro de um subagente — Pi é lento o suficiente pra consumir todo o budget de tempo do subagente antes de terminar. Solução: executar Pi diretamente do Hermes pai via SSH heredoc, sem delegar. As 7 documentações de engenharia e as 58 code-tasks (~5.990 linhas) foram geradas com **v4-flash**, não v4-pro — resultado de alta qualidade sem timeout. v4-pro é desnecessário para documentação técnica; reserve-o para decisões arquiteturais complexas (escolha de stack, ADRs).

#### Fluxo

1. Criar subpasta (via pi-shell):
   ```bash
   ssh oracle-host 'pi-shell "mkdir -p /workspace/code/PROJETO/product/engineering"'
   ```

2. **Pi carrega skills de engenharia** (modelo best) e produz:
   - SAD — Software Architecture Document (`/skill:software-architecture`)
   - TechSpecs (`/skill:tech-specs`)
   - Diagrama Entidade-Relacionamento (`/skill:entity-relationship-diagram`)
   - Contratos de API (`/skill:api-contracts`)
   - Test Plan (`/skill:test-plan`)
   - Release Notes (`/skill:release-notes`)

3. Pi gera lista de tarefas em **`product/engineering/code-tasks.md`**:
   ```bash
   # Pi carrega /skill:code-tasks (versão Pi)
   # Lê os docs de engenharia, quebra em tasks de 2-15 min
   # Escreve em product/engineering/code-tasks.md
   ```

4. **Execução — Hermes instancia Pi (modelo cost) em LOTES por layer:**

   Na prática (72 tasks executadas em um projeto real), o padrão **um-Pi-call-por-task** é ineficiente — cada chamada SSH + carregamento de modelo custa ~15-30s de overhead. O padrão que funciona:

   ```
   LOOP POR LAYER:
     1. Hermes lê TODAS as tasks pendentes daquele layer em code-tasks.md
     2. Agrupa tasks relacionadas em um único prompt para Pi
     3. Invoca Pi UMA vez com todas as tasks do lote
     4. Pi escreve todos os arquivos do lote
     5. Hermes VERIFICA os arquivos (find + wc -l)
     6. COMMITA via pi-shell (git add <path> && git commit -m "...")
     7. Atualiza progresso com todo() — um item por layer
     8. Avança para o próximo layer (continua mesma sessão Pi com -c)
   ```

   **Exemplo prático (Layer 2 — 9 migrations em 1 chamada):**
   ```bash
   ssh oracle-host 'bash -s' << 'ENDSCRIPT'
   cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
   LC_DIR=code/PROJETO pi-agent 'pi -c -p "Crie TODAS as migrations:
   - Task-002: migration base (extensions)
   - Task-003: migration users
   - Task-004: migration projects
   ... (lista completa no prompt)
   Confirme cada migration criada." --provider opencode --model opencode/deepseek-v4-flash-free'
   ENDSCRIPT
   ```

   **Verificação + commit entre lotes:**
   ```bash
   # Verificar arquivos
   find /opt/data/code/workstation/PROJETO/backend/<path> -type f | sort
   wc -l /opt/data/code/workstation/PROJETO/backend/<path>/*

   # Commitar
   ssh oracle-host 'bash -s' << 'ENDSCRIPT'
   cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
   git add <path/glob> && git commit -m "feat: Tasks X-Y — descrição"
   ENDSCRIPT
   ```

   **Rastreio de progresso:**
   Um item `todo()` por layer (11 no total), não um por task. Marcar como in_progress antes, completed depois.

   **Sessão Pi contínua entre lotes:**
   - Primeiro lote: `pi --name "projeto-code" -p "..."` (cria sessão)
   - Lotes seguintes: `pi -c -p "..."` (continua mesma sessão)
   - Pi mantém contexto do projeto entre chamadas, não precisa reexplicar estrutura

5. **Build final — Pi modelo best faz revisão final + primeiro build:**
   - **Build OK** → avança para 4c (testes)
   - **Ajustes pequenos** → Pi mesmo corrige e tenta de novo
   - **Ajustes grandes** → novas tasks em `code-tasks.md`, volta ao passo 4

6. **Antigravity revisa código e testes** (feedback técnico):
   ```bash
   agy -p "Run tests and review the application at /opt/data/code/<projeto>.
   Give technical feedback in product/engineering/feedbacks.md"
   ```

   **Variante: Antigravity para bug-fixing (não só review)**
   Quando agy já reviewou e identificou bugs, invocar agy com um **prompt estruturado listando bugs específicos** com paths de arquivo e abordagens de fix. agy então tenta corrigir os arquivos diretamente.

   Padrão de prompt:
   ```
   You are Antigravity, final validator. Fix ALL remaining bugs.
   
   ## Bugs (prioridade)
   
   ### P0 - [nomedobug] ([N] tests)
   Location: tests/unit/test_X.py
   Error: [mensagem de erro exata]
   Fix: [abordagem sugerida]
   Steps: 1. Read file 2. Fix Y 3. Run test Z
   
   ## Your process
   1. Read relevant files first
   2. Run failing tests individually
   3. Fix each bug one at a time
   4. Run full suite when done
   5. Write findings to feedbacks.md as Turno N
   ```

   > agy -p funciona para bug-fixing quando o prompt é completo (paths reais, erros exatos, fix approach) e o ambiente está pronto (venv criado, deps instaladas). Para ambientes complexos (Docker, permissões), usar tmux interativo.

7. Feedbacks trocados entre **Pi modelo best e Antigravity** via `product/engineering/feedbacks.md`.

8. Pi modelo best usa feedbacks para criar **novas Code-Tasks**. Quando concluídas, retorna no `feedbacks.md` solicitando nova revisão ao Antigravity.

9. Quando código e testes forem aprovados por Antigravity → avançar para **4d. Docker Build & Deploy**.

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

> **Referência completa:** `skill_view(name='product-pipeline', file_path='references/first-test-run-pipeline.md')` — catálogo com 11 bugs, fixes, template de conftest e métricas.

Após executar todas as code-tasks, Pi gera código funcional mas com incompatibilidades de ambiente que só aparecem na execução. O padrão abaixo resolveu ~95% dos erros em 2 iterações (ex: 0 → 104/133 testes passando em um projeto real).

#### Fluxo

```
1. INSTALAR deps no host (Pi container não tem Python)
   → ssh oracle-host + uv venv + uv pip install -e ".[dev]"
   → Pinar bcrypt==4.0.1 para compatibilidade com passlib

2. CRIAR pytest.ini na raiz do projeto
   → asyncio_mode = auto (OBRIGATÓRIO)

3. RODAR tests unitários primeiro
   → Identificar causas raiz (não sintomas)
   → Verificar: ForeignKey, async def list, aiosqlite, bcrypt

4. RODAR tests de integração (após unitários verdes)
   → Conftest: setup_db function-scoped, password real (nunca "***")

5. **PI BEST revisa falhas e CORRIGE DIRETAMENTE** (não criar code-tasks a menos que o fix seja muito grande para uma chamada só):
   → Invocar Pi best com o diagnóstico e pedir que ele mesmo corrija os arquivos
   → Só criar FIX tasks formais em code-tasks.md se o fix exigir múltiplas chamadas ou coordenação complexa
   → Exemplo: "Pi, corrija as 3 falhas: abc na rota X, def no serviço Y, ghi no teste Z"

6. HERMES coordena execução ou valida os fixes do Pi best
7. COMMIT + AGY re-avalia → decide se libera Docker build (alvo: 90%+)
```

#### Ordem de prioridade para fixes

| Prioridade | Fix | Impacto típico |
|-----------|-----|----------------|
| 1 | ForeignKey nos models | ~55 erros |
| 2 | bcrypt==4.0.1 | ~10 erros |
| 3 | aiosqlite nas deps | ~2 erros |
| 4 | from __future__ import annotations (se `async def list(` existe) | ~13 erros |
| 5 | pytest.ini com asyncio_mode=auto | ~68 erros |
| 6 | Conftest de integração (autouse, escopo, password, drop_all) | ~39 erros |
| 7 | MissingGreenlet: lazy="selectin" + session.refresh() (ver Fase 5 da ref) | ~25 erros |
| 8 | Trailing slash 307: alinhar URLs de teste com rotas (ver Fase 6 da ref) | ~12 erros |
| 9 | _task_to_response sem relationships | ~16 erros |
| 10 | SQLite Date/Time: func.date() + server_default (ver Fase 7 da ref) | ~5 erros |
| 11 | Deprecations (utcnow, class Config) | warnings |

---

### 4d. Docker Build & Deploy

> **Referência completa:** `skill_view(name='product-pipeline', file_path='references/docker-build-deploy.md')` — catalogo de 10 bloqueios com causas, fixes e verification checklist.

Após os testes passarem (4c) e Antigravity liberar o build, o proximo passo e gerar as imagens Docker e subir a stack.

#### Fluxo

1. **Garantir que ambos os Dockerfiles existem** — frontend/Dockerfile e backend/Dockerfile
2. **Rodar build:** `docker compose build 2>&1` (ou servico por servico para debug)
3. **Corrigir falhas no build** seguindo o catalogo de blocoeios (referencia acima)
4. **Gerar `.env`** com `SECRET_KEY` (hex de 32 bytes) e `DATABASE_URL` apontando para o container PostgreSQL
5. **Subir:** `docker compose up -d`
6. **Verificar** com o checklist (referencia acima)
7. **Stack rodando** → avançar para **4e. Validação Final pelo Antigravity**

#### Pitfalls comuns na Oracle VM

| Problema | Por que acontece | Solucao |
|----------|-----------------|---------|
| ghcr.io inacessivel | Oracle VM bloqueia o registry | `pip install uv` |
| Porta 80 ocupada | Nginx Proxy Manager ja esta usando | Remapear para `8080:80` |
| asyncpg nao encontrado | Nao esta em pyproject.toml | Adicionar as deps e rebuildar |
| @tailwindcss/postcss faltando | package.json desalinhado com postcss.config.js | Adicionar ou remover o plugin |
| Container restartando em loop | Migration falhou no PostgreSQL (ex: Boolean default `0`) | Resetar DB, rebuildar sem cache |
| Healthcheck 401 | Caminho /health nao corresponde a rota real (ex: /api/v1/health) | Verificar prefixo do router no Dockerfile |
| **Migration PostgreSQL: Boolean default `0`/`1`** | Migrations escritas para SQLite aceitam `0`/`1` como Boolean, PostgreSQL rejeita | Trocar `server_default=sa.text("0")` por `sa.text("false")` e `sa.text("1")` por `sa.text("true")` em TODAS as colunas Boolean |
| **Migration PostgreSQL: import path errado** | Alembic env.py importa de `<projeto>.db.base` mas o módulo é `<projeto>.models.base` | Corrigir import no `alembic/env.py` |

## Deploy: GitHub + Systemd + Nginx

Após o Antigravity aprovar (4e), estruturar o deploy final. O padrão é: GitHub → clonar para `selfhost/<projeto>/` → docker compose → systemd → reverse proxy.

### ⚠️ Oracle Cloud: apenas portas 80/443 abertas externamente

A Oracle Cloud Application Firewall só expõe as portas 80 e 443. Qualquer outra porta (8080, 8081, 3000, etc.) é **acessível apenas internamente** (localhost, docker networks). Nunca assumir que uma porta está acessível externamente só porque funcionou em `curl localhost:PORTA` — testar com `curl http://<ip-publico>:PORTA` do container Hermes (que faz HTTP externo via bridge).

Fluxo de deploy correto:
1. App roda em Docker na porta interna (ex: 8080)
2. **Nginx Proxy Manager** (porta 80/443) faz o proxy reverso
3. Usuário acessa via `http://<ip>/` (porta 80), explícita

Caminhos de deploy ordenados por preferência:

| Método | Porta | Externo? | Quando usar |
|--------|-------|----------|-------------|
| **NPM proxy host** | 80/443 | ✅ Sim | Preferido. Configurar via UI (porta 81) ou DB direto (ver reference) |
| **Docker nginx direto** | 8080 | ❌ Não | Apenas interno (localhost/docker) |
| **Host nginx adicional** | 8081 | ❌ Não | Apenas interno — redundante se docker nginx já existe |

### NPM proxy host via DB (quando UI não está acessível)

O Nginx Proxy Manager armazena proxy hosts no SQLite em `data/database.sqlite` e gera nginx configs em `data/nginx/proxy_host/`. Para adicionar um proxy host sem usar a UI (porta 81):

```bash
# 1. Inserir no banco
ssh oracle-host "sudo python3 << 'PYEOF'
import sqlite3, json
from datetime import datetime, timezone
DB = '/home/ubuntu/selfhost/nginx-proxy-manager/data/database.sqlite'
now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
conn = sqlite3.connect(DB)
domains = json.dumps(['<ip-publico>'])
conn.execute('''INSERT INTO proxy_host (created_on, modified_on, owner_user_id,
    is_deleted, domain_names, forward_host, forward_port, access_list_id,
    certificate_id, ssl_forced, caching_enabled, block_exploits, advanced_config,
    meta, allow_websocket_upgrade, http2_support, forward_scheme, enabled,
    locations, hsts_enabled, hsts_subdomains, trust_forwarded_proto)
    VALUES (?, ?, 1, 0, ?, ?, 80, 0, 0, 0, 0, 1, '',
            '{}', 1, 0, 'http', 1, '[]', 0, 0, 1)''',
    (now, now, domains, '<container-name>'))
conn.commit()
conn.close()
PYEOF"

# 2. Escrever nginx config no formato NPM
sudo tee /data/nginx/proxy_host/1.conf << "CONFEOF"
server {
    set $forward_scheme http;
    set $server         "<container-name>";
    set $port           80;

    listen 80;
    listen [::]:80;

    server_name <ip-publico>;

    access_log /data/logs/proxy-host-1_access.log proxy;
    error_log /data/logs/proxy-host-1_error.log warn;

    location / {
        include conf.d/include/proxy.conf;
        proxy_http_version 1.1;
        proxy_buffering off;
    }

    include /data/nginx/custom/server_proxy[.]conf;
}
CONFEOF

# 3. Recarregar nginx no container NPM
docker exec nginx_proxy_manager nginx -t && docker exec nginx_proxy_manager nginx -s reload

# 4. Testar (Host header deve corresponder ao server_name)
curl -s -H "Host: <ip-publico>" http://localhost:80/ | head -5
# Deve mostrar o app, não "Default Site"
```

> ⚠️ O config file NPM usa `$forward_scheme`, `$server`, `$port` como variáveis NPM-internas e inclui `conf.d/include/proxy.conf` — não copiar template de nginx comum que usa `$connection_upgrade` (variável não definida no NPM).

**Ordem final no filesystem:**
```
/home/ubuntu/selfhost/
├── <projeto>/          ← projeto 1
├── proximo-projeto/   ← projeto 2 (etc)
├── hermes/
├── pi-agent/
├── nginx-proxy-manager/
├── firecrawl/
└── shared/
```

**Passo 1 — Criar repositório GitHub privado e clonar para selfhost/**

O deploy final vai para `selfhost/<projeto>/`, seguindo o padrão dos demais serviços (hermes, pi-agent, nginx-proxy-manager, firecrawl).

```bash
# No Hermes container (cria repo e faz push)
cd /opt/data/code/workstation/PROJETO

# Criar .gitignore (excluir __pycache__, .env, node_modules, *.db, *.bak, etc.)
echo "# Python
__pycache__/
*.py[cod]
*.egg-info/
.env
venv/
.venv/
*.db
*.sqlite3

# Node
node_modules/
dist/
.next/

# Docker
docker-data/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Generated / Temp
*.bak
*.log
tmp_*.py
.perm-check" > .gitignore

# Inicializar git e criar repo
git init
export PATH="/opt/data/bin:$PATH"
gh repo create PROJETO --private --source . --push --description "Descrição"
```

Após push, **clonar para selfhost/** no host:

```bash
# Extrair token do Hermes para usar no clone
GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" /opt/data/.env | head -1 | cut -d= -f2)

# Clonar direto pra selfhost/
ssh oracle-host "cd /home/ubuntu/selfhost && \\
  git clone https://SEU_USER:${GITHUB_TOKEN}@github.com/SEU_USER/PROJETO.git PROJETO"

# Corrigir permissões (clone cria arquivos com uid do token owner)
ssh oracle-host "sudo chown -R ubuntu:ubuntu /home/ubuntu/selfhost/PROJETO"
```

> ⚠️ O clone do GitHub cria arquivos com ownership do usuário que fez o push (uid 10000 no container). No host (uid 1001), `chown` é necessário para que docker compose e git add funcionem.

> ⚠️ `chown -R` no host também corrige arquivos de pesquisa criados por `delegate_task` (que roda como Hermes, uid 10000). Sempre rodar após clone e sempre que Hermes criar arquivos no volume compartilhado.

**Passo 2 — Systemd service (auto-start no boot)**

```bash
ssh oracle-host 'sudo tee /etc/systemd/system/PROJETO.service << "EOF"
[Unit]
Description=PROJETO Stack
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/caminho/PROJETO
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable PROJETO.service'
```

**Passo 3 — Conectar à rede do Nginx Proxy Manager**

Para que o NPM (porta 81) possa rotear tráfego para o app:

```yaml
# No docker-compose.yml do projeto:
nginx:
  # ...
  networks:
    - projeto-net
    - proxy_network    # <-- adicionar esta (externa)

networks:
  projeto-net:
    driver: bridge
  proxy_network:       # <-- declarar como externa
    external: true
```

```bash
# Recreate o container nginx
ssh oracle-host 'cd /caminho && docker compose up -d nginx --force-recreate'
```

**Passo 4 — Nginx do host (opcional, sem NPM)**

Se não usar Nginx Proxy Manager, instalar nginx no host e configurar como proxy reverso:

```bash
# Instalar
ssh oracle-host 'sudo apt-get install -y nginx'

# Configurar
ssh oracle-host 'sudo tee /etc/nginx/sites-available/PROJETO << "EOF"
server {
    listen 8081;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
sudo ln -sf /etc/nginx/sites-available/PROJETO /etc/nginx/sites-enabled/
sudo systemctl restart nginx'
```

A stack Docker geralmente usa NGINX como proxy reverso. Configuração funcional validada:

```nginx
server {
    listen 80;
    location /api/ {
        proxy_pass http://<backend-service>:8000;
        proxy_set_header Host $http_host;        # CRÍTICO: inclui porta
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
}
```

**`$http_host` vs `$host` — um bug sutil que quebra o frontend:**

FastAPI gera redirects 307 quando recebe request sem trailing slash (ex: `/api/v1/tasks` → `/api/v1/tasks/`). O Location header do redirect é montado a partir do `Host` header recebido.

- `proxy_set_header Host $host;` → Host = `localhost` (sem porta) → redirect vai pra `http://localhost/...` (porta 80, inalcançável de fora)
- `proxy_set_header Host $http_host;` → Host = `localhost:8080` → redirect vai pra `http://localhost:8080/...` ✅

**Na prática, `$http_host` NÃO resolveu o problema.** O backend FastAPI/Starlette gerou `http://localhost/...` mesmo com `$http_host` configurado — a porta foi perdida durante o proxy, resultando em redirect para porta 80. O `proxy_redirect http://localhost/ /;` no NGINX também não funcionou (não afetou 307 redirects).

**Solução que realmente funciona: middleware FastAPI com redirect relativo.** Desabilitar o redirect automático de slashes do FastAPI e implementar um middleware manual que retorna 307 com URL relativa (starts with `/`). O cliente (Axios/browser) resolve a URL relativa contra sua própria origin, que inclui a porta correta:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
import re

class TrailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        # Só redirecionar rotas que precisam de trailing slash
        if re.match(r"^/api/v1/tasks$", path):
            qs = ("?" + request.url.query) if request.url.query else ""
            return RedirectResponse(url=path + "/" + qs, status_code=307)
        return await call_next(request)

# No FastAPI app:
app = FastAPI(..., redirect_slashes=False)
app.add_middleware(TrailingSlashMiddleware)
```

Isso também requer alterar as rotas em `__init__.py` para garantir que `@router.post("")` (sem barra) funcione sem o redirect automático.

**Alternativa mais limpa (se puder modificar as rotas):** usar `redirect_slashes=False` e reescrever as rotas para usar o padrão sem barra (`@router.get("")` em vez de `@router.get("/")`), ajustando todos os clientes (frontend + testes) para não usarem trailing slash.

Sintoma: frontend loga "Network Error" no carregamento de tasks, mas o mesmo endpoint funciona via curl com auth header. Backend logs mostram 307 (não 500).

**Frontend Axios baseURL relativo:** O Vite bundle geralmente usa `baseURL: "/api/v1"` (relativo), não `http://localhost:8000`. Se o build incluir URL absoluta, o frontend faz requests direto pro backend, ignorando NGINX e sofrendo CORS. Verificar no bundle JS compilado:

```bash
grep -o 'baseURL[^,}]*' path/to/assets/index-*.js | head -5
# Esperado: baseURL:"/api/v1"  (relativo)
# Perigoso: baseURL:"http://localhost:8000"  (ignora proxy)
```

**NGINX proxy location deve existir sempre:** Por padrão, o Dockerfile do frontend Vite gera um NGINX que só serve static files (sem `location /api/`). O frontend faz requests pra mesma origin → NGINX tenta servir arquivo estático para `/api/v1/...` → 404 → Axios reporta "Network Error". Adicionar o `location /api/` proxy é um passo obrigatório pós-build fácil de esquecer.

**Verificação do proxy:**
```bash
# Testar via NGINX (exatamente como o frontend faz)
curl -s -X POST "http://localhost:8080/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"test123"}' \
  | python3 -c "import sys,json; print('OK' if json.load(sys.stdin).get('access_token') else 'FAIL')"

# Verificar se redirects usam a porta correta
curl -sv "http://localhost:8080/api/v1/tasks?status=pending&limit=20" \
  -H "Authorization: Bearer *** 2>&1 | grep -i location
# Esperado: location: http://localhost:8080/api/v1/tasks/?status=pending&limit=20
```

---

### 4e. Validação Final pelo Antigravity

**Critério de conclusão do MVP.** Só após a aplicação em execução ser testada e aprovada, o MVP é dado como concluído.

#### Fluxo da Validação Final (4e)

> **Integração dogfood:** Esta fase carrega a skill `dogfood` para produzir um relatório de QA exploratório sistemático, que é passado como contexto para o Antigravity dar o veredito final.

##### 0. Dogfood QA — teste exploratório sistemático

Antes de coletar screenshots e invocar o Antigravity, rodar a skill `dogfood` na aplicação rodando para gerar um relatório de bugs estruturado.

**Pré-requisitos:** A aplicação precisa estar rodando e acessível via browser.

**Passos:**

1. Carregar a skill `dogfood` e seguir seu workflow de 5 fases (Plan → Explore → Collect Evidence → Categorize → Report)

2. **Scope sugerido para MVP:** testar todos os fluxos críticos definidos no PRD:
   - Fluxo de autenticação (login, registro, logout)
   - CRUD das entidades principais
   - Navegação entre telas
   - Busca/filtros
   - Tratamento de erros (403, 404, 422)
   - Estados vazios (zero items, primeira vez)
   - Form validation

3. Salvar o relatório gerado em:
   ```
   product/engineering/dogfood/report.md
   ```
   Com os screenshots em:
   ```
   product/engineering/dogfood/screenshots/
   ```

4. O relatório do dogfood serve como **entrada factual** para o Antigravity — ele não precisa redescobrir bugs que o QA já catalogou.

##### 1. Hermes coleta evidências via browser

Navegar pelo app rodando e capturar **7 screenshots padrão**:

| # | Tela | O que verificar |
|---|------|----------------|
| 1 | **Login** | Campos email/senha, botão entrar |
| 2 | **Inbox** | Dashboard pós-login, sidebar |
| 3 | **Hoje** | Visão do dia |
| 4 | **Projetos** | Lista de projetos |
| 5 | **Contextos** | Lista de contextos |
| 6 | **Relatórios** | Stats / gerar |
| 7 | **Erro (se houver)** | Bug encontrado durante navegação |

```bash
# 1. Capturar
browser_navigate url="http://host:porta/"
browser_vision question="Login"
# ... navegar e printar cada tela

# 2. Mover para pasta de prints
mkdir -p /opt/data/code/workstation/PROJETO/product/engineering/dogfood/screenshots
cp browser_screenshot_*.png .../dogfood/screenshots/01-login.png
cp browser_screenshot_*.png .../dogfood/screenshots/02-inbox.png
# ... etc
```

> ⚠️ **Hermes NÃO diagnóstica bugs.** Se encontrar erro (ex: 500 ao criar tarefa), apenas printa a tela de erro e move o print — não analisa causa, não lê logs do backend, não escreve diagnóstico. A análise é responsabilidade exclusiva do Antigravity. Usuário corrigiu explicitamente: "Só relate o que você viu na aplicação, deixe que o Antigravity reporte esse erro da API".

##### 2. Entregar prints ao usuário via MEDIA

```text
MEDIA:.../dogfood/screenshots/01-login.png
MEDIA:.../dogfood/screenshots/02-inbox.png
MEDIA:.../dogfood/screenshots/03-hoje.png
MEDIA:.../dogfood/screenshots/04-projetos.png
MEDIA:.../dogfood/screenshots/05-contextos.png
MEDIA:.../dogfood/screenshots/06-relatorios.png
MEDIA:.../dogfood/screenshots/07-erro-criar-tarefa.png
```

##### 3. Salvar prompt do agy como `.md`

> 🎯 **REQUERIDO pelo usuário.** Não pular este passo.

O prompt enviado ao agy DEVE ser salvo como `.md` em `product/engineering/dogfood/prompt-para-antigravity.md` ANTES de invocar o agy:

\```markdown
# Prompt enviado ao Antigravity (agy)

> **Data:** DD/MM/AAAA
> **Pipeline:** product-pipeline — PROJETO
> **Fase:** Validação Final (Antigravity)

---

**Contexto fornecido:**

1. **Dogfood QA Report:** `product/engineering/dogfood/report.md` — bugs catalogados com severidade, steps to reproduce, screenshots
2. **Screenshots do app:** `product/engineering/dogfood/screenshots/` — prints de cada tela funcional
3. **Feedbacks anteriores:** `product/engineering/feedbacks.md` — histórico de revisões de código
4. **App rodando em:** http://localhost:PORT

**Sua missão:**

1. Leia o **Dogfood QA Report** — os bugs já estão catalogados, não precisa redescobri-los
2. Acesse a aplicação rodando e **corrija os bugs encontrados** (se possível)
3. Verifique os endpoints críticos (autenticação, CRUD, busca)
4. Dê o **VEREDITO FINAL** em `product/engineering/feedbacks.md`:
   - ✅ APROVADO — se todos os bugs críticos foram corrigidos
   - ❌ REJEITADO — se houver bloqueadores, com lista do que precisa ser corrigido
\```
---

**Status:** Prompt enviado ao agy.
```

> ⚠️ Incluir o prompt EXATO que foi enviado — o usuário pode querer conferir o que foi pedido.

##### 4. Invocar agy via tmux interativo

> 🔴 `agy -p` (print mode) é **NÃO-interativo** — o agy processa o prompt e sai sem conseguir responder a prompts de permissão (docker, pytest, curl...). Para validação que precisa de múltiplas ferramentas, usar tmux interativo com agy puro (sem flags).

```bash
# 4a. Iniciar tmux com agy (sem flags — TUI interativa)
ssh oracle-host 'tmux kill-session -t agy-review 2>/dev/null'
ssh oracle-host 'tmux new-session -d -s agy-review \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'

# 4b. Aguardar TUI carregar (sleep 5-8s)
sleep 8

# 4c. Enviar prompt — linha por linha (prompts multi-linha)
ssh oracle-host 'tmux send-keys -t agy-review "Review the MVP at [path]" Enter'
ssh oracle-host 'tmux send-keys -t agy-review "Your mission:" Enter'
# ... etc

# 4d. Loop de monitoramento + aprovação de permissões
# agy pede confirmação para CADA comando (docker, pytest, curl...).
# Enviar "2" (yes + always allow nesta conversa) ou "1" (yes only).
ssh oracle-host 'tmux send-keys -t agy-review "2" Enter'

# 4e. Ler resultado final
ssh oracle-host 'tmux capture-pane -t agy-review -p -S -50'
```

O prompt deve pedir EXPRESSAMENTE que o agy escreva o veredito em `product/engineering/feedbacks.md` na seção `## Veredito Antigravity`, com: bugs encontrados, correções feitas, status de cada endpoint, e decisão final.

> ⚠️ **`agy -p` (--print)**: modo one-shot que processa o prompt e sai. Não serve para validação que exige múltiplos comandos.

> ⚠️ **`--dangerously-skip-permissions`**: flag que pula todas as confirmações. Usar com cautela — agy executará comandos destrutivos (ex: `docker compose down -v`) sem aviso.

##### 5. Verificar o veredito no feedbacks.md

```bash
grep "Veredito Antigravity" /opt/data/code/workstation/PROJETO/product/engineering/feedbacks.md
grep "Sim (Yes)\|APROVADO\|REJEITADO" /opt/data/code/workstation/PROJETO/product/engineering/feedbacks.md
```

##### 6. (Se aprovado) Deploy final

Seguir seção de Deploy abaixo.

#### Decisão final

| Resultado | Próximo passo |
|-----------|---------------|
| ✅ **APROVADO** | MVP concluído. Commitar tudo. Relatar ao usuário. Avançar para **Fase 5: Iteração e Melhoria** |
| ❌ **REJEITADO** | **Loop de correção:** Hermes analisa cada ❌ e decide: <br>1. **BLOQUEANTE** → Pi best corrige, retorna ao passo de testes (4c)<br>2. **ALTA** → Pi best corrige, rebuilda Docker (4d), re-valida (4e)<br>3. **MÉDIA/BAIXA** → Documentar como débito técnico. Avançar para V2 |

#### Loop de correção

Se Antigravity rejeitar:

```bash
# 1. Hermes analisa o feedback e cria prompt de correção
PROMPT_CORRECAO="Antigravity rejeitou a validacao final.
Corrigir: [lista de BLOQUEANTES e ALTAS de product/engineering/feedbacks.md]"

# 2. Invoca Pi best com as correções
ssh oracle-host "LC_DIR=code/PROJETO pi-agent \
  'pi -c -p \"$PROMPT_CORRECAO\" --provider opencode-go --model minimax-m3'"

# 3. Após Pi corrigir, rebuilda stack e re-invoca Antigravity
ssh oracle-host "cd /home/ubuntu/selfhost/shared/code/PROJETO && docker compose build --no-cache && docker compose up -d"

# 4. Antigravity re-valida (volta ao inicio de 4e, usa tmux — sem timeout)
ssh oracle-host 'tmux kill-session -t agy-reval 2>/dev/null; true'
ssh oracle-host 'tmux new-session -d -s agy-reval \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'
sleep 8
ssh oracle-host 'tmux send-keys -t agy-reval \
  "Re-valide a aplicacao em http://localhost:PORTA." Enter'
ssh oracle-host 'tmux send-keys -t agy-reval \
  "Verifique se as correcoes foram aplicadas. Decida: APROVADO ou REJEITADO novamente." Enter'
```

> ⚠️ O loop termina **apenas** quando Antigravity der ✅ APROVADO. Não pular esta etapa mesmo que os testes unitários estejam verdes — a validação funcional da aplicação rodando é insubstituível.

#### Saída

```
product/engineering/feedbacks.md       ← atualizado com veredito do Antigravity
product/engineering/dogfood/           ← novo — relatório de QA exploratório
├── report.md                           ← bugs catalogados com taxonomia
└── screenshots/                        ← prints de cada bug encontrado
```

Com marcador `<!-- PHASE_COMPLETE: mvp -->` no final do feedbacks.md quando aprovado.

---

## Fase 5: Iteração e Melhoria

> **Skill principal:** `backlog-and-sprint` — contém o fluxo completo: backlog, brief, planning, design, engineering (com execução paralela), review e close.
> Abaixo apenas o resumo. Carregar `skill_view(name='backlog-and-sprint')` para detalhes operacionais.

**Agente:** Hermes (+ Pi + Antigravity)

### Fluxo

1. **Usuário testa o MVP** e usa para casos concretos

2. **Backlog não-estruturada:** Hermes cria e mantém itens de melhoria conforme feedback do usuário

3. **Melhorias pontuais rápidas:** Hermes implementa diretamente (ou invoca Pi best se for complexa)

4. **Sprints** (quando o usuário solicitar implementação das melhorias pendentes):
   ```\n   SPRINT i:\n     0. Hermes conduz brief de clarificação com o usuário\n        → Perguntas objetivas sobre itens ambíguos da backlog\n        → Respostas registradas em product/sprint_i/brief-notes.md\n\n     1. Pi best com skills de PM
        → Revisa backlog e roadmap
        → Define novas user stories para a Sprint

     2. Pi best com skills de UX/UI
        → Revisa documentos diante dos feedbacks
        → Cria wireframes/user flows para cumprir as stories
        → Antigravity revisa (como na Fase 4a)
        → feedbacks_sprint_i.md

     3. Pi best revisa/atualiza docs de engenharia
        → PRIMEIRO: atualiza SAD, TechSpecs, ERD, API contracts,
          test-plan e release-notes em product/engineering/
          para acomodar as mudancas de design da Sprint
        → DEPOIS: gera code-tasks em product/sprint_N/engineering/
          Sprint-N-code-tasks.md
        → Antigravity revisa (como na Fase 4b)

     4. Hermes relata tudo que aconteceu na Sprint
        → Pede para usuário testar

     5. Feedbacks e ajustes incorporados
        → Sprint concluída quando usuário se dá por satisfeito
   ```

---

## Formato do feedbacks.md

Os feedbacks.md devem ser estruturados como **conversas multi-turno entre agentes** — cada turno é uma mensagem estilizada como se fosse de um chat, com markdown estruturado que já explicita o que o destinatário deve responder.

### Padrão de cada turno

```markdown
## 🗨️ Turno N — @<AgenteRemetente>

**Para:** @<AgenteDestinatário>  
**Data:** ...  
**Em resposta ao:** Turno N-1  
**Contexto:** (opcional — resumo do estado atual)

---

### <seção 1>

Conteúdo estruturado com:
- Listas de pontos com status `✅ / ⚠️ / ❌`
- Tabelas comparativas, código, referências a arquivos
- Citações do turno anterior com `> bloco`

### <seção 2>

...

---

### ⬆️ O que espero de você, @<AgenteDestinatário>:
- [ ] Ação concreta 1
- [ ] Ação concreta 2
- Decisão esperada: aprovar / corrigir / re-avaliar
```

Regras:
- **Turno 1** não tem `Em resposta ao` (é o turno inicial que abre o ciclo)
- **Turno final** substitui a lista de ações por `**✅ Decisão final:** ACORDO: ...`
- **Cada turno deixa EXPLÍCITO o que espera do outro agente** — não apenas feedback, mas qual resposta se espera
- Menções a agentes `@Pi`, `@Antigravity`, `@Hermes` são permitidas como identificadores
- Ciclo se encerra quando um turno contém `**✅ Decisão final:** ACORDO: ...` sem ações pendentes

### Exemplo

```markdown
## 🗨️ Turno 1 — @Antigravity

**Para:** @Pi  
**Data:** 06 Jun 2026  
**Contexto:** Revisão inicial dos documentos de engenharia (F4b)

---

**1. SAD.md — Modelo de Processo do MCP Server**
⚠️ Inconsistência entre C2 e C3...

**2. api-contracts.yaml — Gestão de Usuários**
⚠️ Ausência de endpoints para registro e troca de senha...

---

### ⬆️ O que espero de você, @Pi:
- [ ] Corrigir a inconsistência no C2/C3 do SAD.md
- [ ] Adicionar 3 endpoints de user management
- [ ] Revisar os demais 5 pontos
```

```markdown
## 🗨️ Turno 2 — @Pi

**Para:** @Antigravity  
**Data:** 06 Jun 2026  
**Em resposta ao:** Turno 1

---

**1. ✅ SAD.md — MCP Server Process Model**
Corrigido. ...

**2. ✅ api-contracts.yaml — Gestão de Usuários**
Adicionados: `POST /auth/register`, `PUT /auth/me`, `PUT /auth/me/password`

---

### ⬆️ O que espero de você, @Antigravity:
- Re-avaliar os 7 pontos corrigidos
- Confirmar aprovação ou apontar ressalvas
```

### Onde aplicar

| Fase | Arquivo |
|------|---------|
| F4a (Design) | `product/design/feedbacks.md` |
| F4b (Engineering) | `product/engineering/feedbacks.md` |
| F5 (Sprints) | `product/feedbacks_sprint_<i>.md` |

> ⚠️ **Conversa viva, não ata de reunião.** Cada turno deve soar como uma fala de um agente para outro — com opinião, decisões e expectativas explícitas. Não escrever como se fosse uma ata do que aconteceu; escrever como a mensagem que o agente está enviando *naquele momento*.

Para sprints: `feedbacks_sprint_i.md`

---

## Phase Completion Audit

Após cada fase, auditar entregáveis contra o checklist da skill ANTES de relatar ao usuário:

```bash
# Template de auditoria
echo "=== FASE [N]: [Nome] ==="
# Listar arquivos esperados
ls -la product/[fase]/*.md 2>/dev/null
echo "---"
# Verificar marcador de conclusão
grep "PHASE_COMPLETE: [fase]" product/[fase]/PRD.md # ou arquivo principal
echo "---"
# 4e: Dogfood QA report
ls product/engineering/dogfood/report.md 2>/dev/null && echo "Dogfood report: OK" || echo "Dogfood report: AUSENTE"
echo "---"
# 4e: Verificar aprovação de Antigravity
grep "APROVADO" product/engineering/feedbacks.md 2>/dev/null || echo "Agy approval: PENDENTE"
echo "---"
# Verificar git status limpo
git status --short
```

Itens a verificar:
- [ ] Todos os arquivos da `## Saída` existem?
- [ ] O marcador `<!-- PHASE_COMPLETE: ... -->` está presente no arquivo principal?
- [ ] F4e: Dogfood QA report gerado? (`ls product/engineering/dogfood/report.md`)
- [ ] F4e: Antigravity aprovou a aplicação rodando? (`grep "APROVADO" product/engineering/feedbacks.md`)
- [ ] F4e: Loop de correção encerrado (se aplicável)?
- [ ] As permissões permitem leitura/escrita de ambos (Hermes + Pi)?
- [ ] Tudo commitado?
- [ ] Usuário revisou e aprovou (F1: arquivo .md enviado)?

> ⚠️ O usuário explicitamente pediu auditoria: "Verifique se você fez tudo que compete à fase 2". Não confiar na memória — checklist contra a skill a cada fase.

Cada `pi -p "..."` isolado inicia uma **nova sessão** — o Pi não tem memória entre chamadas. Para tópicos que exigem continuidade, use **sessão nomeada**:

```bash
# 1ª chamada: cria a sessão
pi --name "projeto-fase" -p "prompt inicial..."

# Chamadas seguintes: continua a mesma sessão
pi --session <id> -p "próximo prompt..."

# Ou pelo atalho: continua a mais recente
pi -c -p "próximo prompt..."
```

As sessões ficam em `~/.pi/agent/sessions/`, organizadas por diretório de trabalho. Use `pi -r` para navegar. `/session` mostra o ID e arquivo atual.

> ⚠️ **Sessões são scoped por diretório** — o nome da pasta de sessão é derivado do diretório de trabalho. Entre no diretório correto antes de `pi -c` ou `pi -r`.

## Pitfalls

⚠️ **batch-splitting para tarefas grandes do Pi** — Quando uma tarefa do Pi timeouta (600s), não tentar de novo com o mesmo escopo. Quebrar em lotes de 2-3 documentos conceituais primeiro (wireframes, empathy-map, journey-map), depois os detalhados (design-system, user-flows), depois o protótipo (prototype.html). v4-pro aguenta ~3 documentos por sessão; v4-flash aguenta ~2 com descrições concisas.

⚠️ **Pi parece travado mas output já está completo** — Após o Pi completar a última tarefa (ex: escrever prototype.html), o processo fica em idle (0.6% CPU, zero conexões de rede) esperando novo input ou timeout. O marcador `PHASE_COMPLETE` pode estar presente. **Não matar o processo sem primeiro verificar os arquivos de output no shared volume.** Session logs no container são efêmeros — os arquivos `.jsonl` somem quando o container morre. A única fonte confiável é o shared volume.

⚠️ **Async Pi execution + session monitoring** — Quando Pi precisa rodar por tempo indeterminado (fixes pós-MVP, refactors grandes), executar em background com `terminal(background=true, notify_on_complete=true)`. O Pi não emite logs progressivos via SSH — o progresso é monitorado pelo shared volume:

   ```bash
   # Acompanhar via session file (Pi salva cada turno):
   ssh oracle-host 'ls -lt ~pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--/*.jsonl | head -3'
   wc -l ~pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--/*.jsonl

   # Verificar se arquivos foram criados/modificados:
   grep "Turno 11\|Turno 12\|APROVADO\|REJEITADO" product/engineering/feedbacks.md
   ls -la backend/<projeto>/repositories/

   # Ver output parcial do processo (pode estar vazio até o fim):
   process action=log session_id=proc_XXXXX
   ```

   **Padrão de prompt para Pi async:** escrever o prompt num arquivo no shared volume (`prompts/pi-prompt.md`), invocar Pi com `pi --name "sessao" -p "$(cat /tmp/pi-prompt.md)"`. Assim o prompt chega limpo sem quoting hell.

⚠️ **Commit + tag ANTES de invocar Pi para fixes** — Sempre criar um ponto de restauro antes de Pi modificar código:
   ```bash
   # 1. Commit estado atual
   git add -A && git commit -m "feat: pre-Pi fix round checkpoint"

   # 2. Tag versionada
   TAG="mvp-validated-$(date +%Y%m%d-%H%M)"
   git tag -a "$TAG" -m "MVP validated - pre Pi best fixes"

   # 3. Rollback se precisar:
   git checkout tags/$TAG
   ```
   Isso evita perder o estado funcional se Pi quebrar algo.

⚠️ **Tests fora do Docker build context — `docker cp` obrigatório** — O build context do backend (`context: ./backend`) só copia arquivos dentro de `backend/`. Testes em `tests/` na raiz do projeto NÃO entram na imagem. Após rebuildar:
   ```bash
   rm -rf /app/tests && docker cp /caminho/no/host/tests container-name:/app/tests
   ```
   Sempre remover a pasta antiga antes para evitar cache de arquivos velhos.

⚠️ **Oracle Cloud: apenas portas 80/443 externas** — A Oracle Cloud Application Firewall só expõe portas 80 e 443. Por padrão, `curl localhost:8080` funciona (Interno) mas `curl http://IP:8080` não (Externo). Se a porta estiver aberta no Security List mas ainda assim bloquear, verificar o host nftables: o `reject` rule no `INPUT` chain pode estar ANTES das regras de `accept`. Adicionar rules na posição correta com `sudo nft add rule ip filter INPUT tcp dport <port> accept` — elas precisam vir ANTES do `reject with icmp type host-prohibited`. Verificar posição com `sudo nft list chain ip filter INPUT`. Sempre testar com port checker externo (ex: portchecker.co). Usar Nginx Proxy Manager na porta 80 para expor o app. Ver seção `Deploy > Oracle Cloud: apenas portas 80/443 abertas externamente`.

⚠️ **SQLite `func.now()` tem precisão de SEGUNDOS** — `server_default=func.now()` em SQLite retorna apenas `YYYY-MM-DD HH:MM:SS`, sem milissegundos. Tasks criadas no mesmo segundo compartilham `created_at`. Isso quebra testes de cursor pagination que usam `created_at` como chave de ordenação. Fixes possíveis:
   - **No teste:** adicionar `await asyncio.sleep(1.5)` entre criações para garantir timestamps distintos
   - **Na assertion:** substituir `assert page1_ids.isdisjoint(page2_ids)` (frágil com ties) por `assert cursor not in {t.id for t in page2}` (verifica que o cursor não repete na próxima página)
   - **No model:** usar `default=datetime.now(timezone.utc)` (Python-side, precisão de microssegundos) em vez de `server_default=func.now()`, com ressalva que perde o server-side default

⚠️ **delegate_task timeout para orquestração Pi (600s)** — Subagentes que orquestram Pi (SSH → pi-agent → pi) timeoutam porque Pi é lento o bastante pra consumir todo o budget. Preferir executar Pi diretamente do Hermes pai via SSH heredoc (`<< 'ENDSSH'`) em vez de delegar. Se precisar delegar, quebrar em chunks menores (ex: 2-3 docs por delegate_task).

⚠️ **v4-flash é suficiente para documentação de engenharia** — A skill diz "modelo best" para SAD/TechSpecs/etc., mas na prática v4-flash gera documentação de alta qualidade (~5.990 linhas, 58 code-tasks) sem timeout. Reservar v4-pro apenas para decisões arquiteturais complexas (escolha de stack, ADRs, trade-offs).

⚠️ **`agy -p` para engineering review stallou em Docker commands.** agy -p tenta executar comandos (pytest, docker, curl) e pede permissão para cada um. No engineering review, agy inevitavelmente tenta rodar os testes — e o Docker exec timeouta. Em vez disso: usar tmux interativo pré-aprovando permissões, ou rodar testes manualmente e escrever feedback combinando análise do agy + resultados reais dos testes.

⚠️ **`agy design` NÃO valida código existente** — `agy design "validate minha app"` gera um NOVO design/projeto hipotético, ignorando a aplicação rodando. Para validação, usar browser tools do Hermes, curl, ou `agy "prompt"` via pipe. Ver seção 4e.

⚠️ **Hermes coleta evidência, NÃO diagnóstica bugs na 4e** — Durante a validação final, Hermes navega pelo app e captura prints. Se encontrar um erro (ex: 500 ao criar tarefa), o papel de Hermes é: (1) fazer print da tela de erro, (2) mover o print para `dogfood/screenshots/`, (3) incluir o fato no relatório factual do dogfood. Hermes NÃO deve investigar causa, ler logs do backend, ou escrever diagnóstico. Essa análise é responsabilidade exclusiva do Antigravity, guiada pelo relatório do dogfood. Usuário corrigiu explicitamente: "deixe que o Antigravity reporte esse erro".

⚠️ **agy -p timeout com prompts longos (>2KB via SSH pipe):** cat prompt.md | timeout 120 agy e agy -p "prompt longo..." timeoutam para prompts que exigem raciocínio multi-etapas ou chamadas de ferramentas. Para longos: usar tmux interativo. Ver antigravity-design skill para detalhes. — O token OAuth do agy fica no keyring do host. No container não tem dbus/keyring. Sempre invocar agy via SSH com paths do host

⚠️ **agy atinge output token limit ao gerar prototypes grandes (>70KB):** agy (Gemini 3.5 Flash) estoura o limite de tokens de saída ao escrever prototypes HTML ou arquivos grandes. Sintoma no tmux: "models generation exceeded the maximum output token limit". agy tenta retry automático com versão compacta. Após retry, verificar se o arquivo foi escrito e se o conteúdo está completo. Para mitigar: quebrar tarefas grandes em CSS isolado, HTML estrutural, JS separado em prompts distintos.
```bash
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && /home/ubuntu/.local/bin/agy -p "prompt"'
```
Os paths diferem: container vê `/opt/data/code/workstation/`, host vê `/home/ubuntu/selfhost/shared/code/workstation/`.

> 📘 **GUID TypeDecorator (PostgreSQL + SQLite):** `skill_view(name='product-pipeline', file_path='references/guid-type-decorator.md')` — padrão para rodar tests SQLite e produção PostgreSQL com o mesmo model code, sem quebra de `.hex`.

> 📘 **Persistir patches do container na fonte:** `skill_view(name='product-pipeline', file_path='references/container-patch-persistence.md')` — quando correções são aplicadas dentro do container running (nano, docker cp), copiar de volta para a fonte no shared volume antes de rebuildar.

> 📘 **Execução prática de code-tasks:** `skill_view(name='product-pipeline', file_path='references/code-task-execution-workflow.md')` — workflow validado em 72 tasks, com tamanhos de lote, comandos exatos e pitfalls.
> 📘 **Design Review Loop detalhado:** `skill_view(name='product-pipeline', file_path='references/design-review-loop.md')` — roteiro completo do loop de revisão com correções comuns.
> 📘 **Primeira execução de testes:** `skill_view(name='product-pipeline', file_path='references/first-test-run-pipeline.md')` — 11 bugs catalogados, ordem de prioridade de fixes, template de conftest.
> 📘 **Testes em Docker:** `skill_view(name='product-pipeline', file_path='references/docker-integration-testing.md')` — module cache clearing, trailing slash fixes, rate limit bypass, SQLite datetime.
> 📘 **MiniMax M3 acesso:** `skill_view(name='product-pipeline', file_path='references/minimax-m3-access.md')` — Zen free vs Go pago, model IDs, providers, comandos de teste.
> 📘 **NGINX proxy template:** `skill_view(name='product-pipeline', file_path='templates/nginx-fastapi-proxy.conf')` — config funcional com `$http_host`.
> 📘 **Cost Analysis (pós-MVP):** `skill_view(name='product-pipeline', file_path='references/cost-analysis-procedure.md')` — coleta de tokens do Hermes (state.db) e Pi (OpenRouter API), cálculo de cache ratio, pesquisa de preços, e template de relatório HTML.
>
> 📘 **Pi Agent Cost Auditing via .jsonl:** `skill_view(name='product-pipeline', file_path='references/pi-jsonl-cost-audit.md')` — extração de tokens reais dos logs de sessão do Pi, com script de agregação e função de cálculo de custo por modelo.

⚠️ **UID mismatch: Hermes (10000) vs Pi (1001)** — **BIDIRECIONAL.** Não é só Hermes que não escreve onde Pi criou — Pi também não escreve onde Hermes criou. `delegate_task` roda como Hermes (uid 10000), então arquivos de pesquisa criados por subagentes também bloqueiam Pi. Toda operação de escrita no shared volume precisa de verificação de permissão. Regra de ouro: se um lado criou, o outro lado toma EACCES. O dono precisa `chmod 666` ou `chmod o+rwX`.

⚠️ **Pre-flight check antes de qualquer fase** — O usuário explicitamente pediu para não gastar tokens debugando permissão. Verificar Hermes e Pi escrevem no projeto antes de invocar qualquer comando.

⚠️ **Workstation 777 não herda** — A raiz `/opt/data/code/workstation/` é 777, mas `mkdir -p` (mesmo via pi-shell) cria subpastas com 755. Rodar `chmod -R 777` imediatamente após criar a estrutura.

⚠️ **Git add com path explícito** — `git add -A` pode falhar com mixed ownership no diretório (uid 10000 + uid 1001). Sempre adicionar pelo path específico: `git add product/management/`. Para arquivos de `delegate_task` (criados por Hermes/uid 10000), rodar `chmod 666` antes do git add. Para arquivos criados por Pi (uid 1001), git add funciona direto.

⚠️ **Git no workstation requer pi-shell** — `git init` cria `.git/` com ownership do uid do bind mount. Commits de Hermes (uid 10000) falham com "Unable to create index.lock: Permission denied". Commits precisam ser via `ssh oracle-host 'pi-shell \"git add -A && git commit -m \\\"msg\\\"\"'`.

⚠️ **Pi skills não existem por padrão** — 38 skills instaladas manualmente em `~/.pi/agent/skills/`. Pi v0.78.1 vem sem skills.

⚠️ **MiniMax M3 free encerrado — usar Go:** O tier free do MiniMax M3 (`opencode/minimax-m3-free`) encerrou. Usar `opencode-go/minimax-m3` (Go, cota semanal $30). Fallback: `deepseek/deepseek-v4-pro`. Para Pi cost (execução), usar `opencode/deepseek-v4-flash-free` (gratuito).

⚠️ **DeepSeek v4-Pro timeout em sessões longas** — Sintoma: SSH retorna exit 124 sem output. Soluções:
   - Usar v4-flash para tarefas simples
   - Usar `/compact preserve:context` no Pi
   - Iniciar sessão nova referenciando arquivos das fases anteriores

⚠️ **F1 scope: manter conceitual** — Feature matrix detalhada, especificações de funcionalidades e arquitetura são materiais de F3 (PRD). A ideação deve ficar em nível de promessa, persona, diferenciais e delimitação de escopo.

⚠️ **Mirror `<projeto>.old/`** — Quando Pi não consegue escrever, ele faz `mv projeto projeto.old && mkdir projeto && cp -r`. O `.old/` fica como lixo. Verificar e remover após corrigir permissões.

⚠️ **Pi sessão por diretório** — Ao entrar no container via `docker exec`, o diretório padrão é `/workspace`. As sessões do Pi ficam em `/workspace/code/workstation/<projeto>/`. Use `cd` para o diretório correto antes de `pi -c` ou `pi --session`. Ou use o caminho completo ou UUID do session file.

⚠️ **Injeção de chaves no auth.json** — para adicionar chaves sem restart:
```bash
ssh oracle-host "pi-shell 'node -e \"let f=require(\\\"fs\\\"); \
let d=JSON.parse(f.readFileSync(\\\"/home/pi/.pi/agent/auth.json\\\",\\\"utf8\\\")); \
d[\\\"provider\\\"]={\\\"type\\\":\\\"api_key\\\",\\\"key\\\":\\\"sk-...\\\"}; \
f.writeFileSync(\\\"/home/pi/.pi/agent/auth.json\\\",JSON.stringify(d,null,2));\"'"
```

⚠️ **Docker compose para recarregar .env** — `docker restart` não recarrega env vars. Usar `docker compose up -d pi-agent --force-recreate`.

⚠️ **Frontend scaffolding: criar arquivos manualmente, não usar create-vite** — `create-vite` (e qualquer scaffolding interativo) não funciona via pi-agent porque exige stdin/pty. Criar todos os arquivos do frontend manualmente no prompt do Pi: `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.tsx`, etc. O Pi (v4-flash) gera ~38 arquivos de frontend em um único prompt sem timeout se bem especificado. Incluir `vite.config.ts` com proxy `/api → localhost:8000` e `tailwind.config.js` com as cores do design system no mesmo prompt.

⚠️ **Pi adora "***" como placeholder de senha** — Em fixtures de teste, Pi frequentemente usa `"password": "***"`. Isso quebra o register endpoint (422 validation error ou 401). Sempre verificar e substituir por `"secret123"` antes de rodar integração.

⚠️ **Backend restart: ConnectionResetError nos primeiros 3-6s** — Após `docker restart`, o backend demora pra subir (migrations + startup). Chamadas imediatas dão `ConnectionResetError: [Errno 104]`. Aguardar health check 200 antes de testar.

⚠️ **Docker cp de arquivo local** — Primeiro scp pro host, depois `docker cp`. Não tentar `docker cp` direto de um path que é local (ex: `/tmp/script.py` do Hermes container não existe no host).

⚠️ **Pi não tem flag -m para mensagens diretas** — `pi -m "msg"` não existe. Usar `pi -p "prompt"` ou `pi -c -p "continue"`. Comunicação entre agentes via `feedbacks.md` no shared volume.

⚠️ **UUID no PostgreSQL vs String(36) nos models** — Pi scaffolda models com `String(36)` para PKs (compatível com SQLite), mas as migrations geram colunas `uuid` no PostgreSQL. O INSERT quebra com `column "id" is of type uuid but expression is of type character varying`. Fix: trocar os models para `from sqlalchemy.dialects.postgresql import UUID`. Depois disso, Pydantic precisa de `BeforeValidator(str)` nos schemas de resposta. Catálogo completo no `references/docker-build-deploy.md` (entradas 11-15).

⚠️ **UUID em campos ForeignKey no TaskResponse quebra serialização Pydantic** — Mesmo com `IdStr` nos campos `id` e `user_id`, os campos `project_id`, `context_id`, `parent_task_id` em schemas de resposta usam `Optional[str]` simples. Quando o banco retorna um valor UUID não-nulo, Pydantic valida como `string_type` e joga 500. Fix: usar `Optional[IdStr]` (onde `IdStr = Annotated[str, BeforeValidator(str)]`) em TODOS os campos que podem conter UUID estrangeiros nos schemas de resposta. Isso converte automaticamente UUID do ORM para string na serialização.

⚠️ **Duplicate fixture definitions no conftest.py** — Quando Pi gera conftest.py, às vezes define `setup_db` duas vezes...

⚠️ **Pi best overshoot em fixes de conftest** — Quando pedir pro Pi best corrigir testes flaky, ele tende a mudar `event_loop` de `scope="session"` para `scope="function"`, o que quebra 100+ testes async. Nunca aceitar mudança no `event_loop` sem testar exaustivamente. O fix correto para testes flaky é mudar APENAS `setup_db` para function scope, mantendo `event_loop` como session scope. Verificar se o fix do Pi não incluiu alterações no `event_loop` antes de aplicar.

⚠️ **Prompt files no shared volume: UID mismatch bloqueia leitura do Pi** — Quando Hermes escreve um prompt file via `write_file` no shared volume (`/opt/data/code/workstation/PROJETO/prompts/`), o arquivo nasce com owner 10000 e permissão 600. Pi (uid 1001) não consegue ler. Escrever prompts via pi-shell no host:

```bash
ssh oracle-host 'pi-shell "cat > /workspace/code/workstation/PROJETO/prompts/pi-prompt.md << '"'"'PROMPTEOF'"'"'
Conteúdo do prompt...
PROMPTEOF"'
```

Ou escrever diretamente no filesystem do host (`/tmp/`) via SSH:

```bash
ssh oracle-host 'cat > /tmp/pi-prompt.md << "EOF"
Conteúdo...
EOF'
```

E referenciar no pi-agent com `cat /tmp/pi-prompt.md`.

⚠️ **Pi session timeout com progresso parcial (só se estiver em foreground):**** Quando Pi roda em foreground e timeouta, NÃO assuma que nada foi feito. Pi frequentemente completa 60-80% do trabalho antes do timeout. Sempre verificar: `ls -la` nos diretórios alvo, `grep` nos arquivos. Se rodou em background (padrão atual), simplesmente aguarde — não há timeout.

⚠️ **bcrypt pin deve estar no Dockerfile, não só no container running** — `passlib[bcrypt]` instala bcrypt 5.x que quebra a compatibilidade. Pinar `bcrypt==4.0.1` no Dockerfile (build stage). Rebuild sem cache (`--no-cache`) para garantir. Se a imagem for rebuildada sem o pin, volta pra bcrypt 5.x.

⚠️ **patch/write_file falha mesmo com chmod 666 no alvo** — Hermes precisa criar `.hermes-tmp.N` no mesmo diretório que o arquivo alvo. Se o diretório pai for 755 e owned por uid 1001, Hermes (uid 10000) toma EACCES. Fix: `chmod o+w /caminho/do/diretorio/` antes de tentar patch. Usar `pi-shell` para aplicar `chmod` no diretório, ou delegar o patch inteiro via `pi-shell`. Para escrita de arquivos owned por uid 1001, o método mais confiável é:
   ```bash
   ssh oracle-host "python3 -c \"with open('/path/to/file', 'w') as f: f.write('''conteudo''') \"" 
   ```
   Ou via SSH heredoc: `ssh oracle-host 'cat > /path/to/file << EOF\n...\nEOF'`

## Verificacao Rapida

Comandos de referencia avulsos:

Antes de iniciar o pipeline ou cada fase, verificar (o usuario explicitamente pede para nao gastar tokens debugando permissao):

```bash
# 1. Pi acessivel?
pi --version

# 2. Skills do Pi carregadas?
pi -p "list skills" --provider deepseek --model deepseek-v4-flash

# 3. Shared volume funcional?
ls /opt/data/code/workstation/PROJETO/product/ 2>/dev/null

# 4. Agy funcional?
ssh oracle-host 'echo "n" | timeout 5 /home/ubuntu/.local/bin/agy 2>&1 | head -3'

# 5. Git configurado?
git config user.name && git config user.email

# 6. Permissoes do projeto OK?
ls -la /opt/data/code/workstation/PROJETO/product/ 2>/dev/null
touch /opt/data/code/workstation/PROJETO/.perm-check 2>/dev/null && rm $_ && echo "OK" || echo "BLOQUEADO"
```
