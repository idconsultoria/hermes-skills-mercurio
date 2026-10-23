# Dependency Checklist — Product Pipeline

> **Última verificação:** 06 Jun 2026
> **Status geral:** ✅ Pipeline validado F1-F3 com TaskFlow. Pronto para F4.

## Infraestrutura

### Hermes
- [x] Acessível, terminal funcional
- [x] `delegate_task` operacional (usado em F2 para 5 pesquisas paralelas)
- [x] Skills carregadas: `product-pipeline`, `ideation-drilling`, `code-tasks`, `user-interview`, `deep-research`, `plan`, `pi-agent-coordination`

### Pi Agent
- [x] Acessível via `ssh oracle-host "pi-agent 'echo OK && pi --version'"`
- [x] 38 skills instaladas em `~/.pi/agent/skills/` (persistent volume)
- [~] Modelo best: `opencode-go/minimax-m3` — cota semanal estourada (reset ~7 Jun)
- [x] Modelo fallback: `deepseek/deepseek-v4-pro` — validado para PM work (F3), funcionou sem timeout
- [x] Modelo cost: `deepseek/deepseek-v4-flash` — funcional para escrita simples
- [x] Shared volume: `/opt/data/code/` = `/workspace/code/`

### Shared Volume — UID Mismatch (Fonte #1 de bugs)
- [x] Pi escreve como uid 1001, Hermes escreve como uid 10000
- [x] **Bidirecional**: nem Hermes chmoda arquivos do Pi, nem Pi chmoda arquivos do Hermes
- [x] Workaround: `delegate_task` → `chmod 666` (de quem criou) → `git add <path>` (por quem comita)
- [x] Workstation `/opt/data/code/workstation/` é 777 mas subdiretórios NÃO herdam

### Verificação Rápida (antes de cada fase)
- [x] Testar Hermes e Pi escrevem no projeto
- [x] Testar Pi acessível
- [x] Testar MiniMax M3 quota (se 429, usar v4-pro)
- [x] Testar arquivos da fase anterior legíveis

### Antigravity (agy)
- [x] `agy --version` → 1.0.5
- [x] OAuth configurado
- [ ] Ainda não usado no pipeline (previsto para F4a)

## Por Fase

### F1: Ideação — ✅ VALIDADO
- [x] `ideation-drilling` instalada no Pi
- [x] Sessão persistente com `--name` + `-c` funciona
- [x] Relay pattern: Pi pergunta → Hermes relay → usuário responde → Hermes reenvia
- [x] Scope discipline: manter conceitual, não listar features

### F2: Pesquisa — ✅ VALIDADO
- [x] `deep-research` via `delegate_task` funciona com toolsets `["web","terminal"]`
- [x] `user-interview` para produto pessoal: 3-4 perguntas focadas bastam
- [x] Arquivos de delegate_task precisam `chmod 666` antes de git commit
- [x] 7 pesquisas em paralelo funcionaram sem conflito

### F3: Conceito — ✅ VALIDADO
- [x] Pi carrega `/skill:prd-development`, `/skill:proto-persona`, etc.
- [x] 5 documentos PM gerados em 1 sessão v4-pro sem timeout
- [x] Git commit com path explícito: `git add product/management/`
- [x] Marcador `<!-- PHASE_COMPLETE: concept -->` implementado

### F4a: Design
- [ ] Skills de UX/UI instaladas no Pi (12 skills)
- [ ] agy funcional para revisão
- [ ] `feedbacks.md` em product/design/ criado
- [ ] Marcador `## ACORDO: PASSAR PARA ENGENHARIA` no feedbacks.md

### F4b: Engineering
- [ ] Skills de engenharia instaladas no Pi (7 skills)
- [ ] `code-tasks.md` gerado em `product/engineering/`
- [ ] Pi cost executa tasks do shared volume
- [ ] `feedbacks.md` em product/engineering/ criado

### F5: Iteração
- [x] Skill `backlog-and-sprint` criada e instalada (Hermes)
- [x] Skill `backlog-and-sprint` instalada no Pi (modelos: best para planning, cost para execução)
- [x] Formato de `feedbacks_sprint_i.md` implementado

## Observações

- **MiniMax M3**: cota semanal reset ~7 Jun. Fallback v4-pro validado para PM work.
- **UID mismatch**: Principal fonte de atrito. Regra de ouro: o dono do arquivo `chmod 666` para o outro lado.
- **git add**: Sempre com path explícito (`git add product/X/`), nunca `git add -A` em diretórios com mixed ownership.
- **Pre-flight check**: Executar antes de CADA fase. O usuário explicitamente pediu para não gastar tokens com debug de permissão.
- **Pi cost auditing**: Token data disponível por call nos arquivos `/home/pi/.pi/agent/sessions/*.jsonl` no Pi. Extração simples com Python (parse de cada line JSON, sum input_tokens + output_tokens por session_id/model). Critical para relatórios de custo pós-MVP.
- **Agy timeout com prompts longos**: `cat prompt | timeout 120 agy` via SSH timeouta para prompts >~2KB. Usar `agy -p "prompt inline"` para prompts curtos ou tmux interativo para prompts longos/complexos. Atualização capturada na skill `antigravity-design`.
