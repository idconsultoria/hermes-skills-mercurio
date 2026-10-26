---
name: product-pipeline
description: "Use when construindo um produto do zero — da ideação ao MVP em produção.

Orquestra Hermes (coordena), Pi Agent (gera código e documentos) e agy (revisa) em cinco fases com portões de aprovação."
category: autonomous-ai-agents
type: Orchestrator
timestamp: 2026-10-23T12:00:00Z
---

# Product Pipeline — do requisito ao deploy

> **Hermes orquestra. Pi gera. agy revisa.**
> Cinco fases, cada uma com artefato e portão. Nada avança sem o portão.

Este arquivo é o **contrato**. O procedimento detalhado de cada fase está nas skills
`pipeline-fase1..4`; o catálogo de falhas em `pipeline-pitfalls` e `references/pitfalls.md`;
o material de apoio em `references/`. Se o corpo desta skill repetir o que já está lá,
uma das duas cópias está errada — e não se sabe qual.

---

## 1. Quando usar

- Produto novo, do zero, atravessando ideação → pesquisa → conceito → MVP → iteração.
- Retomada de um produto já em pipeline, em qualquer fase.
- Correção estrutural pós-gap-review (ver §19).

**Não usar para:** tarefa isolada de código sem produto por trás (use `pi-agent-coordination`),
ou ajuste de uma linha em projeto existente.

---

## 2. O contrato

1. **Hermes nunca escreve código.** Nem HTML, nem CSS, nem JS, nem Python. Se o Pi entregou
   incompleto, o Pi corrige com o feedback do agy. (`P-PROC-04`)
2. **Hermes não diagnóstica bug na F4e.** Coleta evidência — print, console, log — e entrega
   ao agy, que é a autoridade. (`P-PROC-01`)
3. **Execução sequencial estrita.** Não se abre a fase seguinte com a anterior aberta.
   `process(action='wait')` antes de disparar o próximo passo. (`P-PROC-03`)
4. **Todo portão é real.** F1 termina com aprovação explícita do usuário; F4a e F4b terminam
   com `ACORDO` escrito pelo agy no `feedbacks.md`; F4e termina com veredito do agy + browser.
5. **O resumo do Pi não é evidência.** "Implementei tudo" é aspiração; o agy verifica arquivo
   por arquivo. (`P-AGY-08`)
6. **Pedido de velocidade não encurta a pipeline.** "Rápido", "direto ao deploy", "pula essa
   parte" — ignorar e seguir o contrato. O usuário já corrigiu isso duas vezes.
7. **Entrega é arquivo, não descrição.** Documento pedido = arquivo em disco + `MEDIA:/caminho`.
8. **Não se apaga trabalho do usuário.** `git reset --hard` no shared volume é proibido;
   checkpoint (commit + tag) antes de qualquer correção em lote.

### Estilo de trabalho (herdado do usuário)

- **Direto e pragmático.** "Mande aqui", "faça", "cheque" são comandos, não sugestões.
- **Recap antes de nova rodada.** Quando pedirem "roda outra vez", listar primeiro as fases
  que serão executadas: Pi → agy → fixes → dogfood → deploy → relatório.
- **Correção é para ser aplicada**, em todas as seções afetadas, sem debate.
- **Zero emoji na interface entregue.** Ícones SVG do design system; se faltar, adicionar ao
  `svg-icons.js`. Verificação: `grep -r '&#x1F\|🚧\|📊\|⚠️' public/` deve voltar vazio.
- **Documento limpo.** Sem fonte inline, sem metadado de pesquisa no corpo, sem tabela gigante.
- **Canal da mensagem manda.** Telegram, WhatsApp, Docs — responder onde a pergunta chegou.

---

## 3. Papéis e modelos

| Papel | Quem | O que faz | Modelo |
|---|---|---|---|
| **Orquestrador** | Hermes | decide, pesquisa, valida, entrega, mantém o estado | — |
| **Pi best** | Pi Agent | planejamento, design, documentos, correções | `opencode-go` / `deepseek-flash` |
| **Pi cost** | Pi Agent | execução em lote de code-tasks, docs | `opencode-go` / `deepseek-flash` |
| **Revisor** | agy (Antigravity) | revisão visual e de completude; autoridade final | modelo próprio do agy |

**Os dois Pi usam o mesmo modelo.** A diferença entre best e cost é **papel, contexto e
tamanho de lote** — não potência. Best conduz raciocínio longo (design, arquitetura,
correção de issues); cost executa lote fechado de tarefas. Sessões separadas, para não
misturar contexto.

Consequência prática: não existe "escalar para um modelo mais forte" dentro de casa. Se o
Pi errou, a correção é **contexto melhor** (ler os arquivos certos) ou **revisão do agy** —
o agy é o único olho com modelo diferente. Por isso o `ACORDO` não é formalidade.

### Invocação

```bash
source ~/.config/pi/opencode.env     # exporta OPENCODE_GO_API_KEY (sem isso: 401)
$PI --provider opencode-go --model deepseek-flash -p "<prompt>"
```

- **Retomar sessão:** sempre a mesma sessão, nunca uma nova —
  `$PI --session <arquivo>.jsonl -p "..."`. O JSONL cresce por append; verificar que
  cresceu e que o Pi lembra do contexto anterior.
- **Sem timeout em Pi e agy.** `timeout N` mata o processo silenciosamente e o exit code 0
  mente. Pi pode ficar minutos sem escrever stdout.
- **`max_tokens ≥ 1024`** em chamada direta de API: o modelo raciocina antes de responder
  e devolve `content: ""` com orçamento baixo.
- **Lote:** 2–3 documentos por sessão. Mais que isso, dividir.

Histórico de provider/modelo e como trocar: `references/modelos.md`.

---

## 4. Ambiente e pré-voo

Nenhum path absoluto no corpo desta skill. Os três ambientes reais:

| Nó | `$WS` (raiz dos projetos) | `$PI` | agy |
|---|---|---|---|
| **Capitolium / Termux** (Hermes local) | `~/capitolium/code` | `pi` (PATH) | `ssh oracle-host '...agy...'` |
| **Olimpo / Oracle** (Hermes no host) | `/opt/data/code/workstation` | `/opt/data/pi-global/bin/pi` | local: `/home/ubuntu/.local/bin/agy` |
| **Clone local** (ex.: hefesto) | `~/<projeto>` | `pi` (PATH) | `ssh oracle-host '...agy...'` |

Variáveis derivadas: `$LOCAL` é o clone local do projeto quando o Pi trabalha fora do shared
volume (ex.: `~/metricas-nas-nuvens`); `$HERMES_HOME` é o diretório do perfil em uso.

Onde houver divergência entre nó e conteúdo, **o nó perde**: ajusta-se a variável, não a skill.

### Pré-voo — antes de CADA fase

O usuário não quer gastar tokens debugando permissão. Seis checagens, todas verdes antes
de invocar qualquer agente:

```bash
# 1. Pi acessível e autenticado
source ~/.config/pi/opencode.env
$PI --version && $PI --provider opencode-go --model deepseek-flash -p "responda apenas OK"

# 2. Workspace existe e é gravável
mkdir -p $WS/<projeto>/product && touch $WS/<projeto>/.perm-check && rm $WS/<projeto>/.perm-check \
  && echo "escrita: OK" || echo "escrita: BLOQUEADA"

# 3. Permissões do projeto (dono correto)
ls -ld $WS/<projeto>        # dono deve ser o uid que o Pi usa

# 4. Documentos da fase anterior existem e são legíveis
ls -la $WS/<projeto>/product/<fase-anterior>/*.md | head -3

# 5. agy responde
ssh oracle-host 'echo n | /home/ubuntu/.local/bin/agy 2>&1 | head -3'

# 6. Git limpo ou com checkpoint
git -C $WS/<projeto> status -sb
```

Falhou alguma? Corrige antes de prosseguir. O pré-voo não é cerimônia: é o que impede a
fase inteira de morrer no meio por permissão. (`P-ENV-06`)

### Munição de design (obrigatória em fase de UI)

Antes de projetar ou julgar qualquer interface, carregar `references/design-ammo.md`.
As 23 skills vendorizadas ficam em `~/forja/ammo/hub/` (Termux) e
`/home/ubuntu/forja/ammo/hub/` (Oracle). O Pi lê as skills; o agy julga contra elas.
Sem a munição, o gate visual não é válido.

---

## 5. Estrutura do projeto

```
<projeto>/
├── product/
│   ├── ideation/          ideation-result.md
│   ├── research/          <topico>.md · mercado.md · user-interview.md · sintese-executiva.html
│   ├── management/        PRD.md · user-personas.md · opportunity-solution-tree.md
│   │                      user-stories.md · product-roadmap.md
│   ├── design/            wireframes.md · design-system.md · design-system.html
│   │                      empathy-map.md · journey-map.md · feedbacks.md
│   └── engineering/       SAD.md · tech-specs.md · ERD.md · api-contracts.yaml
│                          test-plan.md · release-notes.md · code-tasks.md · feedbacks.md
├── src/  tests/  prompts/
├── AGENTS.md              governança de documentos (quando existir)
└── README.md
```

Cada fase escreve só na sua pasta. Prompts do Pi ficam em `prompts/` — nunca no corpo de
um comando longo.

---

## 6. A espinha

| Fase | Dono | Artefato | Portão de saída |
|---|---|---|---|
| **F1 Ideação** | Pi best | `ideation-result.md` | **aprovação explícita do usuário** |
| **F2 Pesquisa** | Hermes | relatórios em `research/` | findings cobrem os tópicos do F1 |
| **F3 Conceito** | Pi best | PRD, personas, OST, stories, roadmap | checklist de PRD + revisão do usuário |
| **F4a Design** | Pi best + agy | `design-system.html` + docs de UX | `ACORDO: DESIGN SYSTEM FINALIZADO` |
| **F4b Engenharia** | Pi best/cost + agy | código + docs técnicos | `ACORDO: ENGENHARIA FINALIZADA` |
| **F4c Testes** | Pi best | suíte verde | testes unitários e de integração passando |
| **F4d Deploy** | Pi + Hermes | container no ar | checklist de deploy |
| **F4e Validação** | Hermes + agy | evidências + veredito | dogfood + browser + `ACORDO` |
| **F5 Iteração** | Hermes + Pi | backlog, sprints | — |

```
[Ideia] → F1 → F2 → F3 → F4a → F4b → F4c → F4d → F4e → F5
            ↑     ↑     ↑      ↑      ↑      ↑      ↑
         usuário  —  checklist  ACORDO ACORDO testes deploy  veredito
```

---

## 7. F1 — Ideação

**Dono:** Pi best · **Portão:** aprovação do usuário.

1. Hermes cria a estrutura e o repositório:

   ```bash
   mkdir -p $WS/<projeto>/product/ideation $WS/<projeto>/prompts
   cd $WS/<projeto> && git init -b main && git add -A && git commit -m "chore: init"
   ```

2. Escreve o prompt em `prompts/pi-ideation.md` e abre a sessão:

   ```bash
   $PI --name "<projeto>-ideation" -p "$(cat prompts/pi-ideation.md)" \
       --provider opencode-go --model deepseek-flash
   ```

   O prompt manda carregar `/skill:ideation-drilling`, conduzir a ideação e escrever
   `product/ideation/ideation-result.md` terminando com `<!-- PHASE_COMPLETE: ideation -->`.

3. **Perfuração:** a ideação não aceita a primeira resposta. As perguntas que importam são
   "isso precisa existir?", "qual a alternativa mais simples?", "se faltar X, ainda vale?",
   "o que exatamente você quer dizer com Y?".

4. **Relay pattern:** o Pi não tem `clarify`. Se ele perguntar, o Hermes mostra ao usuário,
   coleta a resposta e devolve na mesma sessão com `$PI --session ... -p "<resposta>"`.

5. **Escopo:** F1 é conceitual. Promessa, persona, nome/conceito, delimitação. **Não fixar
   entidades, schema ou campos** — isso é F3. O nome do projeto carrega o conceito; registrar
   o significado no resultado. (`P-PROC-02`)

6. **Detecção de conclusão** — sempre pelo arquivo, nunca pelo stdout:

   ```bash
   grep "PHASE_COMPLETE: ideation" $WS/<projeto>/product/ideation/ideation-result.md
   ```

7. **Portão:** enviar o `.md` via `MEDIA:` e **parar**. Não existe F2 sem "aprovado".

**Variante distribuída** (2+ stakeholders que não podem estar na mesma sessão síncrona):
`references/distributed-ideation-ai-studio.md`. O Hermes vira facilitador no AI Studio,
cada pessoa roda no próprio ritmo, e o Hermes consolida consensos, tensões e escopo do MVP.

---

## 8. F2 — Pesquisa

**Dono:** Hermes · **Portão:** cobertura dos tópicos.

1. **Decompor** o `ideation-result.md` em tópicos: referências explícitas, implícitas,
   mercado, concorrência, perfil de usuário.
2. **Disparar 2–3 subagentes em paralelo**, cada um com contexto auto-contido — contexto
   grande é o que faz o subagente estourar o tempo. Acima de 8 tópicos, quebrar em duas rodadas.
3. **Instruir o fallback no próprio contexto do subagente:** "se `web_search` voltar vazio
   duas vezes seguidas, abandone e use só `web_extract` + navegação direta; não reformule a
   query". O `web_search` rate-limita por sessão e o subagente não sabe disso sozinho.
   (`P-RESEARCH-01`)
4. **Se der timeout, não retentar o subagente.** Ir para pesquisa direta — é mais rápida,
   porque pula o overhead de contexto. Sessões órfãs podem ser mineradas depois
   (`references/subagent-session-recovery.md`).
5. **Entrevista de usuário:** produto pessoal → Hermes entrevista o usuário; produto com
   outros perfis → simulação paralela por perfil, com persona detalhada, e síntese cruzada
   (temas citados por 2+ perfis viram P0).
6. **Saída** em `product/research/*.md`; relatórios premium, design system compartilhado e
   síntese executiva quando o usuário pedir "base de referências":
   `references/research-suite.md` + `references/mbb-executive-summary-standards.md`.
7. Commit com path explícito: `git add product/research/ && git commit -m "feat: F2 research"`.

---

## 9. F3 — Conceito

**Dono:** Pi best · **Portão:** checklist de PRD + revisão do usuário.

1. Sessão persistente com `/skill:prd-development`, `/skill:opportunity-solution-tree`,
   `/skill:user-story`, `/skill:roadmap-planning`.
2. Documentos: **PRD**, **user-personas**, **opportunity-solution-tree**, **user-stories**,
   **product-roadmap**. Se existir roadmap anterior no Drive, o novo é superset — preserva
   as quinzenas e expande.

### Estratégia de persona

| Situação | Abordagem | Quem faz |
|---|---|---|
| Persona fictícia, perfil genérico | proto-persona a partir do PRD e entrevistas | Pi best |
| Pessoa real da equipe | pesquisa web → clone digital → persona documentada | **Hermes pesquisa**, Pi escreve |
| Público externo | entrevista simulada + proto-personas | Hermes + Pi |

Pessoa real: o Hermes pesquisa (LinkedIn, Instagram, GitHub, site, CSS de deploy), o Pi
estrutura. **Nunca delegar a pesquisa ao Pi** — ele não navega. Protocolo completo em
`references/persona-research-deep-dive.md`; formato de saída em
`references/persona-output-format.md`.

**Clone digital é hipótese, não retrato.** Separar dado verificável de inferência do modelo,
apresentar ao usuário, e tratar a correção dele como verdade final. (`P-DSN-11`)

### PRD — antes de enviar

Checklist de gaps práticos (timeline, categorização, schema, consistência numérica, versão)
e o ciclo de revisão que aplica cada ajuste em **todas** as seções — não só na tabela de
features: `references/prd-review-checklist.md`.

### Entrega

`.md` via `MEDIA:`; Google Docs quando o usuário pedir. **Direção do sync é uma só:**
Google Docs (equipe) → markdown local. Nunca sobrescrever o doc com o markdown —
`references/google-docs-prd-delivery.md`.

---

## 10. F4a — Design

**Donos:** Pi best + agy · **Portão:** `ACORDO: DESIGN SYSTEM FINALIZADO`.

1. Pi produz wireframes, design system, mapa de empatia, jornada, user flows.
2. **`design-system.html` é obrigatório** — todos os componentes renderizados, com dados
   mockados: cores, tipografia, botões, cards, formulários, navegação, modais, grid.
3. **Loop de revisão — no mínimo 2 iterações:**

   ```
   ITERAÇÃO 1:  Pi cria    → agy revisa → feedbacks.md
   ITERAÇÃO 2:  Pi corrige → agy re-revisa → feedbacks.md
   ITERAÇÃO N:  ... até o agy escrever ACORDO
   ```

   O loop não é opcional. Pi não acerta tudo na primeira tentativa, e o agy é quem diz
   quando está pronto — não o Pi. (`P-DSN-09`)
4. **agy roda no host, não no container.** Prompt longo vai por arquivo copiado para o host;
   `--dangerously-skip-permissions` é obrigatório no modo `--print`.
5. **Stitch MCP** só depois do design system aprovado, para gerar as telas finais —
   `references/google-stitch-mcp.md`.
6. Commit e seguir para F4b.

---

## 11. F4b — Engenharia

**Donos:** Pi best (docs e correções) + Pi cost (lotes) + agy · **Portão:** `ACORDO: ENGENHARIA FINALIZADA`.

1. Pi best produz SAD, tech specs, ERD, contratos de API, plano de testes, release notes
   e `code-tasks.md`.
2. **Execução em lotes por camada:** agrupar tasks relacionadas, uma invocação do Pi por lote,
   verificar arquivos, commitar, avançar. Mesma sessão entre lotes (`-c`).
3. **Frontend só nasce depois de ler o design.** O prompt lista `design-system.html`,
   `design-system.md` e o protótipo como leitura obrigatória; tokens colados no prompt não
   substituem o layout renderizado. (`P-DSN-06`)
4. **Auditar a sessão JSONL** depois do lote de frontend: confirmar que o Pi *leu* os arquivos
   (`cat`/`read_file`), não apenas os viu num `ls`. (`P-DSN-07`)
5. **agy revisa código e testes** e escreve `review-report.md`. Pi best corrige — incluindo os
   documentos técnicos, no mesmo loop. (`P-PROC-05`)
6. **Checkpoint antes de cada rodada de correção:** commit + tag. (`P-ENV-03`)
7. Verificar **todas** as issues 🔴 antes de seguir; "o Pi corrigiu tudo" não é verificação.
   (`P-AGY-07`)

---

## 12. F4c — Testes

**Dono:** Pi best · **Portão:** suíte verde.

```
1. uv venv + uv pip install -e ".[dev]"
2. pytest.ini com asyncio_mode = auto
3. testes unitários
4. testes de integração
5. Pi best corrige as falhas diretamente
6. Hermes valida os fixes
7. commit + agy reavalia
```

Ordem de prioridade dos fixes (a que resolveu ~95% dos erros):

| # | Fix | Impacto típico |
|---|---|---|
| 1 | ForeignKey nos models | ~55 erros |
| 2 | `bcrypt==4.0.1` | ~10 |
| 3 | `aiosqlite` nas deps | ~2 |
| 4 | `from __future__ import annotations` | ~13 |
| 5 | `pytest.ini` com `asyncio_mode=auto` | ~68 |
| 6 | conftest de integração | ~39 |
| 7 | MissingGreenlet | ~25 |
| 8 | Trailing slash 307 | ~12 |
| 9 | `_task_to_response` sem relationships | ~16 |
| 10 | SQLite Date/Time | ~5 |
| 11 | Deprecations (utcnow, class Config) | warnings |

Detalhe: `references/first-test-run-pipeline.md`.

---

## 13. F4d — Docker e deploy

**Donos:** Pi + Hermes · **Portão:** checklist de deploy.

1. Dockerfiles de frontend e backend.
2. `chmod 644` em todo arquivo novo — permissão 600 vira arquivo de 0 byte na imagem. (`P-DEP-01`)
3. `docker compose build` → corrigir falhas → `.env` → `docker compose up -d`.
4. Checklist de saúde: container de pé, health check 200, porta respondendo, log sem erro.

**Oracle Cloud:** só 80 e 443 são expostas externamente — o resto passa pelo Nginx Proxy
Manager. Portas ocupadas se resolvem com `expose:` e nginx como única porta externa.
(`P-DEP-02`)

**Frontend separado (Vercel/Netlify):** `config.js` com `API_BASE` como primeiro script,
CORS atualizado, `vercel build --prod` + `vercel deploy --prebuilt`, e **`rm -rf .vercel/output`
antes de cada build** — cache velho faz o deploy ficar eternamente em "Building".
Detalhe: `references/docker-build-deploy.md`.

---

## 14. F4e — Validação final

**Donos:** Hermes (evidência) + agy (veredito) · **Portão:** `ACORDO` + browser verde.

1. **Dogfood QA** — teste exploratório sistemático antes do veredito (skill `dogfood`).
2. **Hermes coleta as 7 evidências padrão** e entrega os prints ao usuário. Não diagnostica.
3. **Sincronizar local → shared volume ANTES de chamar o agy.** Se o agy lê a versão antiga,
   ele reprova correção que já foi feita e queima uma iteração inteira. (`P-DSN-08`)
4. **agy revisa** e escreve o veredito no `feedbacks.md`.
5. **Reforço obrigatório no browser:** agy lendo código não pega erro de runtime — `fmt is not
   defined` só aparece quando a página executa. Navegar 3–4 views checando o console; se o
   console acusar, não há ACORDO. (`P-AGY-09`)
6. **Decisão:** aprovado → F5 ou deploy; rejeitado → volta para o loop de correção.

---

## 15. F5 — Iteração

Usuário testa → backlog não estruturada → melhorias pontuais → sprints quando solicitado
(skill `backlog-and-sprint`). Auditoria de status periódica em `references/quinzenal-status-audit.md`.

---

## 16. `feedbacks.md` e o `ACORDO`

Conversa multi-turno entre agentes, um arquivo por fase:

```markdown
## Turno N — @AgenteRemetente

**Para:** @AgenteDestinatário
**Em resposta ao:** Turno N-1

### Conteúdo
[status, citações, código]

### O que espero de você, @AgenteDestinatário:
- [ ] ação concreta
```

- Turno 1 não tem "em resposta ao".
- Turno final: `**Decisão final:** ACORDO: <FASE> FINALIZADA`.
- Menções a `@Pi`, `@Antigravity`, `@Hermes` são permitidas.
- **Sem ACORDO não há avanço.** É a condição de parada do loop, e só o agy a escreve.

---

## 17. As doze regras que não se quebram

1. Hermes não escreve código. (`P-PROC-04`)
2. Não se avança fase com a anterior aberta. (`P-PROC-03`)
3. Toda entrega de fase tem arquivo e marcador de conclusão.
4. F1 só termina com aprovação explícita do usuário.
5. F4a e F4b só terminam com `ACORDO` do agy — mínimo 2 iterações de revisão.
6. O resumo do Pi não é evidência; o agy verifica arquivo por arquivo. (`P-AGY-08`)
7. Sincronizar local → shared volume antes de qualquer revisão. (`P-DSN-08`)
8. Pi e agy rodam sem timeout.
9. Checkpoint (commit + tag) antes de correção em lote; `reset --hard` no shared volume é proibido.
10. Toda issue 🔴 do review precisa estar resolvida e verificada antes do deploy. (`P-AGY-07`)
11. Entrega é arquivo via `MEDIA:`, não descrição.
12. O ambiente se adapta à skill — não o contrário.

---

## 18. Checklists

**Fim de fase**

- [ ] Todos os arquivos da fase existem (ver §5 e a fase correspondente)?
- [ ] Marcador `<!-- PHASE_COMPLETE: <fase> -->` presente?
- [ ] Portão cumprido (aprovação, checklist ou `ACORDO`)?
- [ ] Commit com path explícito?
- [ ] Próxima fase só começa depois do pré-voo?

**Pós-pull / rebrand**

- [ ] `git pull` e comparação de tamanho dos arquivos-chave
- [ ] Pi best faz code-review + dogfood e gera `gap-report.md`
- [ ] Decisão: deploy direto ou plano de correção por fases
  (`references/gap-review-post-pull.md`)

---

## 19. Situações especiais — onde ir

| Situação | Onde |
|---|---|
| Execução simultânea de frentes (workstreams) | `references/execucao-autonoma-ondas-politica-decisao.md` |
| Auditoria de rastreabilidade (produto ↔ design ↔ código) | `references/traceability-audit.md` |
| Entregável para parceiro não-técnico (Docs/Sheets/PDF) | `references/partner-drive-deliverable-package.md` |
| Flowcharts Mermaid em Google Docs | `references/mermaid-to-docs-images.md` |
| Casos completos com artefatos brutos simulados | `references/casos-completos-artefatos-brutos.md` |
| Governança de documentos no repo (`AGENTS.md`) | `references/agents-md-governanca.md` |
| Gap review pós-pull / rebrand | `references/gap-review-post-pull.md` |
| Status audit quinzenal | `references/quinzenal-status-audit.md` |
| HTML responsivo para entrega | `references/mobile-responsive-html-deliverables.md` |
| Recuperar sessão de subagente que deu timeout | `references/subagent-session-recovery.md` |
| Render local (PDF, print, Mermaid) vs navegação web | Chromium ARM64 do nó para render; `browser_exec` para site externo — nunca o contrário |

---

## 20. Mapa das referências

As 60+ referências estão organizadas por situação. As mais usadas:

| Quando você precisa de… | Arquivo |
|---|---|
| Continuar a sessão do Pi corretamente | `references/pi-session-continuation.md` |
| Papéis e política 🔴/🟢 em code-tasks | `references/code-task-model-roles.md` |
| Fluxo de execução em código por papel | `references/code-task-execution-workflow.md` |
| Padrão de pesquisa com HTML premium | `references/research-suite.md` |
| Formato de persona (proto-persona) | `references/persona-output-format.md` |
| Pesquisa profunda de pessoa real | `references/persona-research-deep-dive.md` |
| Stitch MCP (setup e fluxo) | `references/google-stitch-mcp.md` |
| Loop de revisão de design | `references/design-review-loop.md` |
| Primeira execução de testes | `references/first-test-run-pipeline.md` |
| Docker build e deploy | `references/docker-build-deploy.md` |
| Sync antes da revisão da F4e | `references/f4e-review-loop-sync.md` |
| Gap report (template) | `references/gap-report-template.md` |
| Direção do sync com Google Docs | `references/google-docs-prd-delivery.md` |
| Munição de design (23 skills) | `references/design-ammo.md` |
| Histórico de provider e modelo | `references/modelos.md` |
| Catálogo de armadilhas por sintoma | `references/pitfalls.md` |

Para o índice completo: `ls references/`.

---

## 21. Quando algo quebra

1. Procure o **sintoma** em `references/pitfalls.md` (catálogo com ID, por área).
2. Não achou? Vá para a fase correspondente em `pipeline-fase*`.
3. Ainda não achou? `grep -ril "<sintoma>" references/`.
4. Resolveu algo novo? Registre como `P-<área>-<n>` no catálogo — o próximo não paga o
   mesmo preço. Regra: um item por armadilha, com o conserto junto.

