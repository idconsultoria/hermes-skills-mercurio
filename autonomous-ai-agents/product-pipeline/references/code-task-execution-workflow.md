# Code Task Execution Workflow

> Pattern validated in TaskFlow (72 tasks, 11 layers, ~7.500 linhas em ~2h)

## Visão Geral

```
code-tasks.md → [LER por layer] → [AGRUPAR em lote] → [Pi gera] → [VERIFICAR] → [COMMIT] → [todo() update] → próximo layer
```

Cada layer vira UM prompt para Pi, não 72 prompts individuais.

## ⚠️ Loop de Revisão agy — OBRIGATÓRIO (não pule)

A execução de code-tasks NUNCA termina em "Pi gera → VERIFICAR → COMMIT". O loop completo é:

```
Pi gera (lotes) → [SYNC local→shared volume] → agy revisa (Turno 1, feedbacks.md)
  → Pi corrige (MESMA sessão) → agy re-revisa (Turno 3) → ACORDO: <FASE> FINALIZADA
  → build/typecheck/verificação visual → commit
```

Mesmo para frontend/mock/demo (sem backend), o agy é o revisor de design e encontra issues reais
(ex.: seletores CSS quebrados, fórmula incorreta, hex estáticos quebrando dark theme, links sem
auto-foco). Correção real (CFP IA, ago/2026): Hermes executou 3 lotes de Pi e só lembrou do agy
depois — o usuário cobrou o fluxo padrão. Regra: NUNCA commitar demo/design sem o ACORDO do agy.
Ver `design-review-loop.md` para os comandos exatos dos turnos.

## Substituição Pi Best → Pi Cost (a pedido do usuário)

Quando o usuário pedir "Pi Cost sempre" (ex.: demo/mock sem decisões de arquitetura), usar
`--provider opencode-go --model deepseek-v4-flash` em TODOS os lotes — inclusive nos turnos de
correção do feedback do agy. Pi best/pro fica reservado para decisões de arquitetura/design.

## Ciclo com modelos especializados por papel (padrão Zera pré-checklist, ago/2026)

Correção do usuário (13/08/2026): para executar um checklist de tarefas de engenharia (ex.: as ondas
pré-alfa do Zera), o usuário especificou UM modelo por papel do ciclo de code-tasks — NÃO usar só Pi
cost e NÃO usar Pi best max para tudo:

```
┌────────────────────────────────────────────────────────────────────┐
│ 1. CODE-TASKS   Pi best        → gera/atualiza code-tasks.md da onda│
│ 2. EXECUÇÃO     Pi cost        → executa as code-tasks em lotes     │
│ 3. REVISÃO      agy (Turno 1)  → escreve feedbacks.md               │
│ 4. CORREÇÃO     Pi best max    → corrige (MESMA sessão, Turno 2)    │
│ 5. RE-REVISÃO   agy (Turno 3)  → até ACORDO: <ONDA> FINALIZADA      │
│ 6. VERIFICAÇÃO  Hermes         → tsc/pytest/dogfood                 │
│ 7. DOCUMENTAÇÃO Pi cost max    → atualiza docs (SAD, ERD, contratos)│
│ 8. COMMIT + CHECKLIST          → push + status na planilha          │
└────────────────────────────────────────────────────────────────────┘
```

- **Modelos:** Pi best = `deepseek-v4-pro` (opencode-go); Pi cost = `deepseek-v4-flash` (opencode-go);
  "max" = `--thinking xhigh`. Correção SEMPRE na MESMA sessão do executor (`pi --session`).
- **Execução em lotes sequenciais** (nunca paralelo): 3-5 tasks por lote; cada lote roda em background
  (`background=true` + `notify_on_complete=true`); Pi cost leva 5–25 min por lote.
- **Gap analysis é o primeiro passo do Pi best:** o checklist da planilha pode estar desatualizado vs
  código real (ex.: B06 "auth não iniciado" quando o auth JWT já existia da Task-004). O Pi best lê o
  código e reporta "já existe (arquivo:linha) vs falta" ANTES de especificar — evita reimplementar.
- **Cada onda = UM ciclo completo com ACORDO do agy** antes de avançar; nunca commitar código de uma
  onda sem o ACORDO (mesma regra do loop agy obrigatório acima).
- **Pi cost às vezes commita sozinho** (visto no Zera: Lotes 2-4 fizeram commit+push) e às vezes não
  (Lote 1). Verificar `git log`/`git status` após cada lote antes de commitar pelo orquestrador;
  commit atômico por lote é o padrão.

## Política de decisão — 🔴 revisão obrigatória vs 🟢 execução direta (padrão Zera, ago/2026)

O usuário exigiu uma política formal para o que para e pede aval dele vs o que executa direto
(documentada em `product/management/politica-decisao.md` no repo do projeto, vigente 13/08/2026):

- **🔴 PARAR e perguntar (checkpoints):** tecnologia crítica não especificada (lib/framework/serviço
  novo fora da Base Técnica/PRD/ADRs), princípios de design/arquitetura, forma de implementação de
  funcionalidade crítica (auth, motor, LLM, LGPD), custo recorrente, deploy produção, mudança de escopo.
  Formato do checkpoint: 3–5 linhas — decisão, 2–3 opções, recomendação com justificativa, impacto.
  Apresentar pendências 🔴 em lote, não uma a uma.
- **🟢 Executar direto (reportar no relatório final):** implementação dentro de decisão já tomada,
  correções mecânicas (lint, typo, imports), QA/verificação, documentação técnica, infra staging/CI
  seguindo padrões do repo, atualização de status na planilha, commits.
- **Regra de ouro:** reversível com esforço pequeno → executa; difícil de reverter ou afeta custo/
  usuário/contrato público → pergunta; dúvida genuína → pergunta (custo da pergunta < retrabalho).
- **O prompt de TODO agente (Pi best/cost/best max/cost max) DEVE incluir a política** e instruir o
  agente a (a) ler `politica-decisao.md`, (b) parar e reportar se encontrar um 🔴 (nunca codar por
  suposição), (c) declarar ao final: "Política de decisão: nenhuma decisão 🔴" OU listar as 🔴
  reportadas. Quando o Pi reporta um 🔴, o Hermes faz o relay ao usuário via `clarify` e só prossegue
  após o aval — registrar a decisão na política e nos docs (ex.: D12 cookie httpOnly, D13 frontend
  separado do protótipo → ADR).
- **Decisões do usuário viram ADR + entrada na tabela da política** (ex.: ADR-018 frontend real como
  base separada do protótipo `web/`, decidida 13/08) — para que as próximas ondas não reabram a
  discussão e os prompts carreguem a decisão como obrigatória ("não redecidir").

## Loop em DUAS fases: design specs → eng implementation (cada uma com agy)

Quando a mudança exige especificação + implementação (ex.: novo fluxo, novo componente), rodar DOIS
loops completos, cada um terminando em ACORDO do agy — NUNCA pular o loop de design e ir direto para
o código (validação real, CFP IA ago/2026: specs reprovadas no Turno 1 do agy com 8 itens — lista das
7 perguntas faltando, mapeamento campos/schemas, wireframes desatualizados):

```
FASE 1 — DESIGN: Pi escreve specs (fluxos, roteiro IA×web, wireframes) → agy revisa (Turno 1)
  → Pi corrige (MESMA sessão de design) → agy re-revisa (Turno 3) → ACORDO: <X> SPECS FINALIZADAS
FASE 2 — ENG:    Pi implementa no código (lê as specs como fonte de verdade) → agy revisa
  (Turno ENG 1) → Pi corrige (MESMA sessão de eng) → agy (Turno ENG 3) → ACORDO: <X> IMPLEMENTADO
```

- Prompt da FASE 1 pede `.md` apenas (specs); prompt da FASE 2 pede código, citando os arquivos de
  spec como fonte de verdade com seções exatas.
- Os turnos de correção registram-se no MESMO arquivo de feedback (feedbacks.md / feedbacks-<tema>.md),
  cada turno como `## 🗨️ Turno N — @Antigravity` / `## 🗨️ Turno N — @Pi`.
- **Pitfall — sessão certa para o turno de correção:** continuar a sessão que ESCREVEU o artefato.
  Correção de specs → sessão de design; correção de código → sessão de eng. (Hermes errou isso: usou a
  sessão de design para corrigir código e teve que matar/re-disparar na sessão de eng.) Localizar a
  sessão pelo nome: ler `session_info.name` no JSONL.

## Sincronização host ↔ container — NUNCA `git reset --hard` no host (regra do usuário)

Correção explícita do Gustavo (14/08/2026): ele **bloqueou** `git reset --hard origin/main` no host
Oracle durante o fluxo agy. Regra absoluta deste pipeline:

- **O volume É compartilhado** (`/home/ubuntu/selfhost/shared/...` no host = `/opt/data/...` no
  container) — quando o Hermes commita/pusha do container, o host já vê o estado. **Não existe
  "sincronização" a fazer via reset.**
- **Reset destrói trabalho não commitado** — o agy edita `product/engineering/feedbacks.md` na
  revisão; um reset na hora errada comeria o review.
- **Antes do agy:** só conferir `git log --oneline -1` no host (leitura, sem mutação). **Depois:**
  commitar o feedbacks.md direto do container. Se `git add` falhar por permissão (agy rodou como
  uid 1001/ubuntu e chownou o `.git`), corrigir owner PELO HOST:
  `sudo chown -R 10000:10000 <repo>/.git <repo>/prompts <repo>/product` — NUNCA reset.
- Detalhes e diagnóstico: `references/sincronizacao-host-volume.md`.

## Monitoramento — usar pi-session-audit, não só process wait

A skill `pi-session-audit` tem a técnica "Progress Classification (Pi)": ler o JSONL da sessão e
classificar a última entrada (LENDO git diff / LENDO codigo / ESCREVENDO arquivo / COMMIT / TRAVADO).
NÃO monitorar Pi só com `process wait`/poll — o wait estoura em 180s e o stdout fica vazio enquanto
o Pi trabalha. Combinar: classify_progress no JSONL + `find` de arquivos modificados no filesystem.

**Para o USUÁRIO ver a sessão ao vivo:** não abrir a TUI interativa sobre um JSONL que outro processo
está appendando (corrompe). Usar o Pi Live Viewer (`pi_follow.py` no terminal ou `pi_follow_web.py`
no browser com a interface real do Pi via `pi --export`) — ver `references/pi-live-viewer.md`.

## Continuar a MESMA sessão (requisito explícito do usuário)

Quando o usuário exigir "continue a mesma sessão" (ex.: auditorias em fases), usar
`pi --session /path/exato/sessao.jsonl` — `--name` cria sessão nova. Verificar a continuidade pelo
CRESCIMENTO do arquivo (append no mesmo JSONL, não arquivo novo) e pelo custo acumulado
(v1+v2 somam na mesma sessão). Passar o mesmo `--provider`/`--model` em cada continuação.

## Passo a Passo

### 1. Ler o escopo do layer

```bash
grep "^## LAYER\|^### Task-" product/engineering/code-tasks.md
```

Isso mostra a estrutura completa: quantas tasks, o que cada uma faz, dependências.

### 2. Construir o prompt do lote

Ler as tasks específicas do layer em code-tasks.md com `read_file` e construir um prompt único:

```
"Execute Tasks X-Y em batch:
Task-X: [descrição resumida + specs]
Task-Y: [descrição resumida + specs]
...
Crie TODOS os arquivos e confirme quando terminar."
```

Regras:
- Incluir a estrutura exata de diretórios e nomes de arquivo
- Incluir os critérios de aceitação como parte da descrição
- Para models: especificar SQLAlchemy 2.0 style (mapped_column, Mapped, relationship)
- Para schemas: especificar `model_config = ConfigDict(from_attributes=True)`
- Para routes: especificar padrão de injeção de dependência (Depends(get_current_user))

### 3. Invocar Pi

```bash
ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
LC_DIR=code/PROJETO pi-agent 'pi -c -p "<prompt completo do lote>" --provider deepseek --model deepseek/deepseek-v4-flash'
ENDSCRIPT
```

- Usar `pi -c` (continua sessão existente) — se não existir, criar com `pi --name "projeto-code"`
- v4-flash é suficiente para CODE (não precisa de v4-pro para implementação)
- timeout natural do SSH (~600s) é suficiente para lotes de até ~15 tasks

### 4. Verificar arquivos

```bash
# Listar arquivos criados
find /opt/data/code/workstation/PROJETO/<path> -type f | sort

# Checar linhas
wc -l /opt/data/code/workstation/PROJETO/<path>/*

# Chegar conteúdo crítico (se aplicável)
grep -c "keyword\|pattern" /opt/data/code/workstation/PROJETO/<path>/*
```

### 5. Commitar

```bash
ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
git add <path/glob> && git commit -m "feat: Tasks X-Y — descrição concisa"
ENDSCRIPT
```

Usar `git add` com path específico (não `-A`) para evitar mixed ownership issues.

### 6. Atualizar progresso

```bash
todo(todos=[{id: "layer-X", content: "descrição", status: "completed"}, ...])
```

## Tamanhos de lote (valores práticos)

| Tipo de task | Tasks por lote | Prompt size | Tempo Pi |
|---|---|---|---|
| Migrations (alembic) | 8-10 | ~2.000 chars | 2-3 min |
| Models (SQLAlchemy) | 6-8 | ~2.500 chars | 2-3 min |
| Repositories | 5-7 | ~2.500 chars | 2-3 min |
| Services | 8-10 | ~3.000 chars | 3-5 min |
| Schemas + Middleware + Routes | 15-20 | ~4.000 chars | 5-8 min |
| Infra (Docker, compose, nginx) | 3-5 | ~1.500 chars | 2-3 min |
| Frontend completo | 10-13 | ~4.000 chars | 5-10 min |
| Tests (unit + integration + CI) | 20-25 | ~3.000 chars | 5-10 min |

## Pipeline completo (TaskFlow)

```
Layer  | Tasks | Batch | Tempo
L1     | 001   | 1     | 2 min
L2     | 002-010 | 1   | 4 min
L3     | 011-018 | 1   | 3 min
L4     | 019-024 | 1   | 3 min
L5     | 025-033 | 1   | 4 min
L6-8   | 034-052 | 1   | 6 min
L9     | 053-056 | 1   | 3 min
L10    | 057-069 | 1   | 7 min
L11    | 070-072 | 1   | 6 min
Total  | 72      | 9   | ~40 min Pi + ~10 min verify/commit
```

## Servir e VERIFICAR a demo Next.js (validação visual real)

Após o loop (Pi → agy → ACORDO), o protótipo precisa de verificação visual ANTES do commit:

1. **Verificação visual = browser do Hermes no CONTAINER, não no host.** O browser do Hermes não
   alcança o servidor do host (redes separadas). Subir o Next.js no container em porta ALTERNATIVA
   (ex.: `npm start -- -p 3001`) e usar browser_navigate + browser_vision em `http://localhost:3001/...`.
2. **NUNCA confiar em screenshot do chromium snap do host** (`chromium-browser --headless --screenshot`):
   sob AppArmor o CSS não carrega → screenshot vem "quebrado" (ícones gigantes, sem header) — é artefato
   do sandbox, não bug do app. Usar apenas o browser do Hermes para julgar visual.
3. **EADDRINUSE na porta default**: o next-server do host é visível no namespace do container via rede
   Docker (mesmo após pkill no host). Se `npm start` der EADDRINUSE na 3000, subir em 3001; não insistir.
4. **Servidor do usuário (Android/SSH tunnel) fica no HOST porta 3000**: após validar, matar a instância
   do container e subir no host com `setsid nohup npm start > /tmp/cfp-web.log 2>&1 < /dev/null &`
   (o `nohup ... & disown` simples segura a sessão SSH e dá timeout — setsid desacopla de verdade).
   Usuário acessa com `ssh -L 3000:localhost:3000 ubuntu@IP` no Termux + `http://localhost:3000`.
5. **Verificar que o servidor serve o build NOVO**: conferir `cat web/.next/BUILD_ID` e testar a presença
   de classes novas no HTML servido (ex.: `curl -s localhost:3000/dashboard | grep -o "level-pill"`).
6. **Modo dev (hot reload) quando o usuário vai iterar no Android:** `npm run dev` no host recarrega
   automaticamente a cada edição — sem reiniciar. Comando que persiste além do SSH (testado CFP IA):
   `cd <projeto>/web && (setsid nohup npm run dev > /tmp/cfp-web-dev.log 2>&1 < /dev/null &)` — os
   parênteses extras são o que faz o setsid sobreviver ao fim da sessão SSH. Primeira carga de cada rota
   compila sob demanda (~6s), depois fica fluido. **EACCES em `.next/BUILD_ID` ao subir dev:** o `.next`
   foi criado pelo usuário do container (hermes); no host o processo roda como ubuntu sem escrita —
   corrigir com `sudo chown -R ubuntu:ubuntu <projeto>/web/.next` (ou chmod 777) antes de rodar dev.

## Pitfalls

- **Não usar create-vite**: scaffolding interativo não funciona no pi-agent. Criar package.json + configs manualmente.
- **Não esquecer `chmod -R 777`**: se Hermes precisar ler/escrever os arquivos depois, Pi cria com 755.
- **Sessão Pi morre se o container reiniciar**: verificar com `pi -r` antes de continuar.
- **v4-flash vs v4-pro**: flash gera código de qualidade equivalente para implementação. Reservar pro para decisões de arquitetura/design.
- **Prompt muito grande**: se Pi parar de responder sem erro, o prompt pode ter excedido o limite de contexto. Quebrar em 2 lotes menores.
