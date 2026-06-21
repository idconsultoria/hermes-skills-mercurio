---
name: pi-agent-coordination
description: "Invoke Pi Agent locally from Hermes — provider/model hierarchy and session recovery. Covers the three-tier hierarchy (agy for strategy, Pi best via MiniMax M3 for planning, Pi cost via DeepSeek V4 Flash for code), provider/model selection with fallback chains, session recovery from interrupted runs, stall detection and diagnosis, parallel execution patterns, tmux-based monitoring, and the absolute rule: always use terminal background, never delegate_task.

Load this skill for running Pi Coder Agent as a local npm binary — no Docker, no SSH."
category: autonomous-ai-agents
metadata:
  hermes:
    related_skills: [autonomous-ai-agents/pi-session-audit]
---

# Pi Agent (Local)

> Pi Coder Agent v0.78.1 instalado como npm global LOCALMENTE no Hermes.
> Nada de Docker, SSH hops, split filesystem ou quoting hell.
>
> **Hierarquia:** agy (consultor externo) → Pi best (eng. sênior) → Pi cost (dev júnior)

## Hierarquia de Uso

```
CARO/ESCASSO     agy ─── Consultor externo especialista (design, UX, estratégia)
                     │   Usar em momentos estratégicos. Pouco e certeiro.
                     │   Prompt complexo, leitura de arquivos.
                     │
ESCASSO          Pi best ── Eng. sênior interno (MiniMax M3 via Go)
                     │   Planejamento, user stories, docs conceituais.
                     │   Tempo precioso, qualidade acima de velocidade.
                     │
BARATO/ABUNDANTE Pi cost ─ Dev júnior (DeepSeek V4 Flash)
                         Code tasks, fixes, revisões. Escopo restrito,
                         tarefas bem definidas previamente.
```

### Regra prática

| Tipo de tarefa | Quem |
|----------------|------|
| Design, UX, estratégia, pesquisa | **agy** (SSH host) |
| Planejamento, user stories, docs conceituais | **Pi best** (`opencode-go/minimax-m3`) |
| Code tasks, fixes, testes, revisões | **Pi cost** (`deepseek/deepseek-v4-flash`) |
| Tarefa muito simples (< 3 linhas) | Qualquer, preferir Pi cost |

## Localização

```
Binário:  /opt/data/pi-global/bin/pi
Config:   ~/.pi/agent/  (= /opt/data/home/.pi/agent/)
├── auth.json      — 4 providers
├── settings.json  — v0.78.1
└── skills/        — 21 skills (PM + UX + UI + Eng)
Dotfiles: gh:[username]/pi-dotfiles
```

## Providers e Modelos

| Provider | Model ID | Chave | Custo | Papel |
|----------|----------|-------|-------|-------|
| `opencode` (Zen) | `opencode/deepseek-v4-flash-free` | `OPENCODE_API_KEY` | **Gratuito** | **Pi cost** 🥇 |
| `opencode-go` (Go) | `deepseek-v4-flash` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi cost** 🥈 |
| `deepseek` (API direta) | `deepseek-v4-flash` | `DEEPSEEK_API_KEY` | $0.14/M input | **Pi cost** 🥉 |
| `opencode-go` (Go) | `minimax-m3` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi best** 🥇 |
| `opencode-go` (Go) | `deepseek-v4-pro` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi best** fallback 1 🥈 |
| `opencode-go` (Go) | `glm-5.2` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi best** alt — criativo, sites, design |
| `opencode-go` (Go) | `kimi-k2.6` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi best** alt — raciocínio longo |
| `opencode-go` (Go) | `qwen3.7-max` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi best** alt — contextos extensos |
| `deepseek` (API direta) | `deepseek-v4-pro` | `DEEPSEEK_API_KEY` | $0.14/M + $0.42/M | **Pi best** fallback 2 🥉 |
| `openrouter` | `openrouter/<model-id>` | `OPENROUTER_API_KEY` | Variável | Reserva |

### ⚠️ Modelos não registrados no Pi (Custom Model ID)

O Pi Agent tem um registry interno de modelos. Modelos que existem na API do provider
mas NÃO estão nesse registry ainda funcionam — o Pi emite um warning e os trata como
"custom model id". O warning é cosmético, não afeta a execução:

```
Warning: Model "glm-5.2" not found for provider "opencode-go". Using custom model id.
```

Para confirmar se um modelo funciona: `pi --provider opencode-go --model <id> --print "OK"`

Para listar modelos disponíveis na API: `curl -s https://opencode.ai/zen/go/v1/models -H "Authorization: Bearer $OPENCODE_API_KEY" | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"`

### ⚠️ GoUsageLimitError — Cota do OpenCode Go

O provider `opencode-go` (usado para Pi best e Pi cost 🥈) tem um limite mensal
de **5 horas de uso**. Quando estoura, retorna:

```
429 {"type":"error","error":{"type":"GoUsageLimitError",
     "message":"5-hour usage limit reached. Resets in Xh Ymin."}}
```

**Sintomas:**
- Pi termina imediatamente com exit code 1 e sem output
- Nenhum token consumido (a chamada é rejeitada antes de processar)
- A sessão `.jsonl` fica com 1 única entrada de erro

**Ação imediata — fallback automático:**

1. **Se Pi best (`opencode-go/minimax-m3`) estourou cota:**
   ```bash
   # Fallback via deepseek direto (V4 Pro é mais caro mas melhor que nada)
   pi --session ~/caminho/da/sessao.jsonl --provider deepseek --model deepseek-v4-pro
   ```

2. **Se Pi cost (`opencode-go/deepseek-v4-flash`) estourou cota:**
   ```bash
   # Fallback via deepseek direct (V4 Flash, $0.14/M input)
   pi --session ~/caminho/da/sessao.jsonl --provider deepseek --model deepseek-v4-flash
   # Ou via Zen gratuito (mais lento, sem custo)
   pi --session ~/caminho/da/sessao.jsonl --provider opencode --model opencode/deepseek-v4-flash-free
   ```

**Regra de fallback na tabela de providers:**
| Provider principal | Quando falha | Fallback |
|-------------------|--------------|----------|
| `opencode-go/minimax-m3` (Pi best 🥇) | Quota 5h/mês | `opencode-go/deepseek-v4-pro` (🥈, via Go) → `deepseek/deepseek-v4-pro` (🥉, API direta) |
| `opencode-go/deepseek-v4-flash` (Pi cost 🥈) | Quota 5h/mês | `deepseek/deepseek-v4-flash` (🥉) ou `opencode/deepseek-v4-flash-free` (🥇) |

**NUNCA relance o prompt do zero** quando o erro for só de cota — a sessão
existente tem contexto valioso. Use `pi --session ...` com o fallback provider.

## ⚠️ Pi CLI ≠ Providers

`opencode`, `opencode-go`, `deepseek` são **nomes de providers** no auth.json, não CLIs.

| Correto | Errado |
|---------|--------|
| `pi -p "msg" --provider deepseek --model deepseek-v4-flash` | `deepseek -p "msg"` |

## ⚠️ Recuperar Sessão Interrompida (--session)

**SEMPRE** antes de relançar um Pi best que morreu, verificar se a sessão
original pode ser retomada. Relançar do zero = perder 5-10 min de leitura +
centenas de milhares de tokens já gastos.

Pi best (MiniMax M3) leva 5-10+ min só lendo arquivos antes de começar a
escrever. Se o processo morrer (timeout Hermes, kill, crash), **NÃO reinicie
do zero** — a sessão morta tem todo o contexto acumulado queimado.

Use `--session /path/to/session.jsonl` para continuar exatamente de onde parou:

```bash
# 1. IDENTIFICAR a sessão morta — buscar pelo --name usado
ls -lt ~/.pi/agent/sessions/--*/ | grep "sprint1-pr"

# 2. VERIFICAR se a sessão tem progresso real
python3 -c "
import json
with open('CAMINHO_DO_JSONL') as f:
    entries = [l for l in f if l.strip()]
print(f'{len(entries)} entradas')
last = json.loads(entries[-1])
print(f'Ultimo tipo: {last.get(\"type\",\"?\")}')
"

# 3. RETOMAR (Pi carrega o histórico e continua)
pi --session ~/.pi/agent/sessions/--<dir>--/<timestamp>_<uuid>.jsonl \
  --provider opencode-go --model minimax-m3
```

**Identificação correta:** entre sessões com o mesmo `--name`, o arquivo com
mais entradas é o que morreu mais tarde (mais progresso). Pi append ao mesmo
arquivo quando retomado — não cria um novo.

**Combinando `--session` + `-p`:** Embora documentados como exclusivos, na prática
funcionam juntos. Pi carrega o histórico da sessão E processa o novo prompt,
adicionando-o como entrada adicional. Útil para dar instruções de continuação
sem precisar editar o JSONL manualmente. Exemplo real funcionou com Pi v0.78.1.

## OpenCode Go — Cota Mensal de 5h

O provider `opencode-go` (MiniMax M3 e DeepSeek V4 Flash) tem **limite de
5 horas mensais de uso** por workspace. Quando estoura:

```
429 GoUsageLimitError: "5-hour usage limit reached. Resets in 3hr 22min."
```

**Fallback providers por prioridade:**
| Situação | Provider | Modelo | Custo |
|----------|----------|--------|-------|
| Pi best (Go exaurido) — 1º | `opencode-go` | `deepseek-v4-pro` | Cota semanal $30 |
| Pi best (Go exaurido) — 2º | `deepseek` | `deepseek-v4-pro` | $0.14/M input |
| Pi cost (Go exaurido) | `deepseek` | `deepseek-v4-flash` | $0.14/M input |
| Último recurso | `openrouter` | Varia | Variável |

**Comandos de fallback:**
```bash
# Pi best sem Go — 1° tentativa (via Go, mesmo provider)
pi -p "prompt" --provider opencode-go --model deepseek-v4-pro

# Pi best sem Go — 2° tentativa (API direta)
pi -p "prompt" --provider deepseek --model deepseek-v4-pro

# Pi cost sem Go
pi -p "prompt" --provider deepseek --model deepseek-v4-flash
```

⚠️ **NUNCA omitir `--provider` e `--model` ao invocar Pi.** O default do `pi` é `google` (built-in), mas não há provider "google" no auth.json. Pi cai em fallback para o primeiro provider disponível com key (`deepseek`) e o modelo padrão do deepseek é `deepseek-v4-pro` (não `v4-flash`). Consequência: toda sessão roda no tier mais caro sem você perceber. **Sempre explicitamente passar `--provider opencode --model opencode/deepseek-v4-flash-free` (gratuito) ou `--provider deepseek --model deepseek-v4-flash` (barato) ao lançar Pi Cost.** Verificar via `model_change` event no session `.jsonl` se o provider/model esperado foi usado.

⚠️ **Wrapper `pi-cost` disponível** em `[pi-bin-dir]/pi-cost` que já fixa `--provider opencode --model opencode/deepseek-v4-flash-free`. Use `pi-cost` no lugar de `pi` quando quiser garantir o tier gratuito.

⚠️ **NÃO prefixar com `opencode-go/`** quando usando fallback.
`opencode-go/deepseek-v4-pro` tenta o provider Go (sem cota).
Use só `deepseek` como provider.

## Acessar Pi do Host via Docker Exec

As chaves do Pi vivem dentro do container Hermes em `/opt/data/home/.pi/agent/auth.json`.
Para usar o Pi via `docker exec` do host:

```bash
# ❌ ERRO: docker exec como root → ~ = /root/, sem chaves
docker exec -it hermes_agent pi ...  # "no API keys configured"

# ✅ CERTO: --user hermes + caminho absoluto
docker exec -it --user hermes hermes_agent \
  /opt/data/pi-global/bin/pi \
  --session /opt/data/home/.pi/agent/.../file.jsonl \
  --provider deepseek --model deepseek-v4-pro

# ✅ Se HOME não for herdado, passar explicitamente
docker exec -it --user hermes \
  -e HOME=/opt/data/home \
  -e DEEPSEEK_API_KEY=$(docker exec --user hermes hermes_agent \
    python3 -c "import json; print(json.load(open('/opt/data/home/.pi/agent/auth.json'))['deepseek']['key'])") \
  hermes_agent \
  /opt/data/pi-global/bin/pi \
  --session ...jsonl
```

O binário `pi` não está no PATH do user hermes — **sempre usar caminho completo**
`/opt/data/pi-global/bin/pi`. O `--user hermes` é obrigatório para acessar
as chaves em `/opt/data/home/.pi/agent/auth.json`.

## ⚠️ REGRA ABSOLUTA: Pi Agent = Terminal Background, NUNCA Delegate

Pi Agents são **sempre** invocados como processo de terminal em background — `terminal(background=true, notify_on_complete=true)`. **Nunca** usar `delegate_task` para Pi Agents. `delegate_task` cria subagentes isolados sem acesso ao filesystem real do projeto, cancelados se o turno do orquestrador terminar. Pi Agents precisam de acesso direto aos arquivos e podem rodar por 10-30 minutos — `terminal(background=true)` é o único modo seguro. Esta regra vale para Pi best e Pi cost, qualquer provider.

## Como Invocar

### Padrão A — Prompt inline (curto, sem `$`, `` ` ``, `'`)
```bash
pi -p "seu prompt" --provider deepseek --model deepseek-v4-flash
```

### Padrão B — Prompt file (multi-linha, caracteres especiais)
```bash
pi -p "$(cat prompts/task.md)" --provider deepseek --model deepseek-v4-flash \
  --name "sprint-N-tarefa"
```

⚠️ **Sempre usar `--name "sprint-N-descricao"`.** O nome aparece no header do `.jsonl` de sessão e permite:
- Identificar qual sessão corresponde a qual tarefa na auditoria
- Resumir sessão pelo nome via `pi -r` (seletor interativo)
- Extrair tokens/custo depois via `skill_view(name='pi-session-audit')`

### Padrão B2 — Batch paralelo (features independentes)
Para features independentes dentro de uma Sprint (ex: F1 GCal e F5 MCP), rodar Pi em paralelo. Cada feature recebe seu próprio prompt e escreve em arquivos diferentes:

```bash
# Terminal 1: F1 GCal
pi -p "$(cat prompts/f1-gcal.md)" --provider deepseek --model deepseek-v4-flash --name "sprint1-f1"

# Terminal 2: F5 MCP (simultâneo)
pi -p "$(cat prompts/f5-mcp.md)" --provider deepseek --model deepseek-v4-flash --name "sprint1-f5"
```

Features são paralelizáveis quando não compartilham os mesmos arquivos de output (schema → model → service → api → ui → test de cada feature é isolado).

**⚠️ Zen gratuito é lento demais para execução paralela.** O provider `opencode/deepseek-v4-flash-free` tem rate-limit — 4 Pi paralelos com esse provider demoraram >10 min. Para paralelismo real, usar `deepseek/deepseek-v4-flash` (API direta, ~2-4 min cada) ou agrupar em 1-2 batches por vez com o Zen.

**Regra prática para paralelismo:**
| Cenário | Provider | Pi calls paralelas |
|---------|----------|-------------------|
| Features independentes (< 5 tasks cada) | `deepseek/deepseek-v4-flash` | Até 4 |
| Features independentes (> 5 tasks cada) | `deepseek/deepseek-v4-flash` | Até 2 |
| Qualquer tarefa com Zen free | `opencode/deepseek-v4-flash-free` | 1-2 (sequencial é mais rápido) |

### Padrão C — agy (design, UX, pesquisa estratégica)
```bash
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
  /home/ubuntu/.local/bin/agy -p "prompt complexo"'
```

### Padrão D — Pi via tmux (tarefas longas, preferido do usuário)
Para tarefas que podem levar minutos (code tasks, geração de docs), usar tmux em vez de `terminal(background=true)`. Dá visibilidade em tempo real e evita stall silencioso sem diagnóstico:

```bash
cat > /tmp/pi-prompt.md << 'EOF'
prompt aqui...
EOF
tmux kill-session -t pi-sessao 2>/dev/null; true
tmux new-session -d -s pi-sessao \
  "pi -p \"$(cat /tmp/pi-prompt.md)\" --provider deepseek --model deepseek-v4-flash"
sleep 30
tmux capture-pane -t pi-sessao -p -S -10  # ver progresso
```

### Sessões interativas (Termux)
```bash
# Instalar Pi (qualquer máquina)
bash <(curl -fsSL https://raw.githubusercontent.com/[username]/pi-dotfiles/main/scripts/bootstrap.sh)

# Rodar
cd ~/projetos/taskflow && pi
```

## ⚠️ Pre-Launch Check — Reuse Existing Pi Sessions

**Antes de lançar qualquer Pi novo, SEMPRE verificar:**

1. **Pi já está rodando?** `ps aux | grep " pi " | grep -v grep`
2. **Sessão ativa no JSONL?** A última sessão tem entries crescendo?
3. **Se estiver progredindo** (entries > 10, custo > $0.05, último toolCall é `read`/`bash`/`write`), **deixe terminar** — não reinicie do zero.
4. **Se stalled** (entries paradas por >120s), verificar o que Pi estava fazendo (últimas entries) e decidir: retomar com `--session` vs relançar.
5. **Se já gerou o arquivo esperado** mas não adicionou `PHASE_COMPLETE` (por EACCES), adicionar manualmente via `patch` em vez de relançar.

### Regra

```bash
# 1. Verificar processos
ps aux | grep " pi " | grep -v grep

# 2. Verificar última sessão
ls -lt ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl | head -3
python3 -c "
import json, glob
p = sorted(glob.glob('/opt/data/home/.pi/agent/sessions/--*/--*.jsonl'))[-1]
entries = [json.loads(l) for l in open(p) if l.strip()]
last = entries[-1]
print(f'{len(entries)} entries')
print(f'Ultimo tipo: {last.get(\"type\",\"?\")}')
if last.get('type')=='message':
    for c in last['message'].get('content',[]):
        if isinstance(c,dict) and c.get('type')=='toolCall':
            print(f'Ultima acao: {c.get(\"name\")}: {str(c.get(\"arguments\",{}))[:200]}')
"

# 3. Só lançar novo Pi se:
#    - Nenhum Pi rodando
#    - Última sessão completou (PHASE_COMPLETE presente ou >5min idle)
#    - Arquivo esperado não existe
```

**NUNCA faça isso** — recomeçar do zero queima tokens e perde contexto:
- ❌ `pkill -f "pi$" && pi -p "..."` (mata sessão produtiva)
- ❌ Relançar sem verificar se já existe arquivo de output
- ❌ Ignorar sessão `--session` viável e criar nova do zero

## ⚠️ Image Input Crash — OpenCode Go Rejects Images from ALL Models

OpenCode Go NÃO suporta image inputs em NENHUM modelo — nem GLM 5.2 (text-only),
nem MiniMax M3 (nativamente multimodal). Qualquer tentativa de ler screenshot,
PNG, ou enviar imagem via `read` resultará em:

```
400 Error from provider: This model does not support image inputs
```

### Como acontece

Pi pode tentar ler screenshots que ele mesmo gerou com Playwright (`read /tmp/site-shot.png`).
O `read` tool retorna a imagem como blob, o provider tenta processar e rejeita.

### Recuperação — Editar o JSONL

NÃO relance do zero — a sessão tem contexto valioso. Edite o JSONL para remover
as entradas de imagem:

```python
import json

session_path = 'caminho/da/sessao.jsonl'
with open(session_path) as f:
    entries = [json.loads(l) for l in f if l.strip()]

# Encontrar entradas com imagem
for i, e in enumerate(entries):
    content = e.get('message',{}).get('content','')
    if isinstance(content, list):
        has_image = any(isinstance(c, dict) and c.get('type') == 'image' for c in content)
        if has_image:
            print(f'Entry {i}: IMAGE — cortando aqui')

# Truncar antes da primeira imagem
safe = entries[:cut_idx]
with open(session_path, 'w') as f:
    for e in safe:
        f.write(json.dumps(e) + '\n')
```

Depois relance com `--session` e o mesmo modelo (ou MiniMax M3 se preferir).

### ⚠️ Prevenção

Ao dar prompts que mencionam Playwright ou screenshots, INSTRUA o Pi:
> "Do NOT use Playwright, Chromium, or read any image/screenshot files.
> This provider does NOT support image inputs. Use only text-based verification."

### ⚠️ Pi best (MiniMax M3) é LENTO — não confunda com stall

Pi best (`opencode-go/minimax-m3`) rotineiramente leva **5-10+ minutos só lendo**
arquivos antes de gerar o primeiro output. Numa sessão real de 181 entradas,
Pi passou 100+ entradas (~7 min) lendo código, docs, git diffs e schemas
antes de começar a escrever. **Não é stall — é o modelo montando contexto.**

Pi cost (`deepseek/deepseek-v4-flash`) é mais rápido nessa fase de leitura
(~30-60s), mas também pode passar 2-3 min em contexto grande.

**Sinal de stall real:** >120s sem que a contagem de entradas do JSONL cresça.
Verificar:
```bash
wc -l ~/.pi/agent/sessions/--*/$(ls -t ~/.pi/agent/sessions/--*/ | head -1)
```

**Progress-check rápido para múltiplos Pi Agents paralelos** (executar do container Hermes):

```bash
python3 -c "
import json, glob
for path in sorted(glob.glob('/opt/data/home/.pi/agent/sessions/--opt-data-*--/202*.jsonl')):
    name = path.split('setor-')[1].split('--')[0] if 'setor-' in path else path.split('--')[-2][:30]
    entries = sum(1 for _ in open(path))
    writes = 0; last_read = '?'
    with open(path) as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                if e.get('type') == 'message':
                    for c in e.get('message', {}).get('content', []):
                        if isinstance(c, dict) and c.get('type') == 'toolCall':
                            if c.get('name') == 'read' and last_read == '?':
                                last_read = c.get('arguments', {}).get('path', '')[-50:]
                            if c.get('name') == 'write':
                                writes += 1
    print(f'{name:10s} | {entries:3d}e | reads→{last_read} | writes={writes}')
"
```

Isso mostra entradas crescendo, último arquivo lido, e se já começou a escrever output.

**Sinal de leitura normal:** entradas crescendo, custo acumulando, última
entrada contendo snippets de código, diffs, ou schemas.

### Execução de Pi best sem timeout

Pi best (MiniMax M3) NUNCA deve rodar em foreground do Hermes — o timeout
padrão de 180s mata a sessão antes de Pi começar a escrever, mesmo que Pi
esteja progredindo normalmente na fase de leitura.

**Sempre usar background para Pi best:**
```bash
terminal(
  command="cd /opt/data/code/workstation/PROJETO && pi -p \"$(cat prompts/tarefa.md)\" --provider opencode-go --model minimax-m3 --name \"sprint-N-tarefa\"",
  background=true,
  notify_on_complete=true
)
```

Para Pi cost (DeepSeek V4 Flash), foreground com timeout=300 geralmente é
suficiente, mas background é mais seguro para prompts >30 linhas.

Pi pode stallar com prompts muito complexos (> 15 linhas). Sintoma: > 60s sem output.

### Diagnóstico

Verificar se Pi está realmente stallado VS apenas lento:

```bash
# 1. Verificar session files — se entries crescem, NÃO está stallado
wc -l ~/.pi/agent/sessions/--*/$(ls -t ~/.pi/agent/sessions/--*/ | head -1)
# 2. Verificar se há output visível via tmux (se usando tmux)
tmux capture-pane -t pi-sessao -p -S -5 2>/dev/null
```

### Execução paralela (features independentes)

Features de uma Sprint que tocam arquivos diferentes (ex: F1 GCal + F5 MCP) podem rodar **simultaneamente** em múltiplos Pi processes. Pi é leve o bastante para 4 processos paralelos sem competição de memória.

```bash
# Terminal 1: F1 GCal
pi -p "$(cat prompts/f1.md)" --provider opencode --model opencode/deepseek-v4-flash-free --name "sprint1-f1"
# Terminal 2: F5 MCP (lançar simultaneamente)
pi -p "$(cat prompts/f5.md)" --provider opencode --model opencode/deepseek-v4-flash-free --name "sprint1-f5"
```

⚠️ **NÃO usar `pkill` quando executando Pi em paralelo.** O padrão `pkill -f \"^pi$\"` mata todos os processos Pi, incluindo features independentes rodando em paralelo. Só matar zumbis específicos por PID ou session name.

### Quando stallar de verdade

```bash
pkill -f "pi --name.*sprint1-"   # matar APENAS um session específico
# migrar para agy (se tarefa for estratégica/design)
```

### ⚠️ Stall Silencioso

Pi pode **sair com exit code 0 sem produzir output**. O processo termina normalmente mas o arquivo esperado não é gerado. Acontece especialmente com:
- **DeepSeek V4 Pro** (modelo mais lento, maior chance de stall)
- Prompts que exigem ler + escrever múltiplos arquivos (> 3 simultâneos)
- Pi rodando em **foreground com timeout** (morre antes de escrever o output)

Exit code 0 **não é garantia** de sucesso. Sempre verificar o arquivo de output (ex: `ls -la`, `grep PHASE_COMPLETE`) independente do exit code.

### 🔍 Monitoramento via tmux (preferido)

O usuário prefere o **padrão tmux** (mesmo usado com agy) para tarefas longas do Pi, em vez de `terminal(background=true, notify_on_complete=true)`:

```bash
# 1. Escrever prompt como arquivo
cat > /tmp/pi-prompt.md << 'EOF'
prompt completo aqui...
EOF

# 2. Rodar Pi em tmux (mesmo container, sem SSH)
tmux kill-session -t pi-sessao 2>/dev/null; true
tmux new-session -d -s pi-sessao \
  "pi -p \"$(cat /tmp/pi-prompt.md)\" --provider deepseek --model deepseek-v4-flash"

# 3. Monitorar a cada 30s (visibilidade em tempo real)
for i in $(seq 1 40); do
  sleep 30
  echo "--- Poll $i ---"
  tmux capture-pane -t pi-sessao -p -S -5 2>/dev/null
  if [ -f "product/sprint_N/engineering/Sprint-N-code-tasks.md" ]; then
    echo "✅ Arquivo gerado!"
    break
  fi
done

# 4. Limpar
tmux kill-session -t pi-sessao 2>/dev/null; true
```

**Vantagem:** visibilidade em tempo real do que Pi está gerando, mesmo quando não crasha mas também não produz output.

### 🔍 Monitoramento via Cron (tarefas muito longas, 30min+)

Para tarefas que podem levar 30+ minutos (sites completos, codebases), o tmux
não escala — o agente precisa continuar trabalhando em outras coisas. Use cron
jobs para verificação periódica:

```bash
# Criar cronjob que checa a cada 5 minutos
cronjob(
  action='create',
  schedule='5m',
  repeat=20,
  name='check-pi-progress',
  enabled_toolsets=['terminal'],
  deliver='origin',
  prompt='Verifique o progresso do Pi Agent ... e relate APENAS formato conciso.'
)
```

Referência completa de monitoramento: `skill_view(name='pi-agent-coordination', file_path='references/cron-progress-monitor.md')`

### Modelos: V4 Flash > V4 Pro para code tasks

DeepSeek **V4 Flash é mais confiável** que V4 Pro para code tasks. V4 Pro stallou mais vezes com prompts equivalentes no mesmo setup. Usar V4 Pro APENAS para:
- Decisões arquiteturais complexas (ADR, escolha de stack, trade-offs)
- Documentos com análise de riscos/custos
- Prompts curtos (< 10 linhas) onde a profundidade do raciocínio importa


## ⚠️ Prompt Quality for Complex Creative Tasks

When Pi Agent is tasked with **creative output** (sites, visual design, multi-file
projects, generative art, complex UIs), the prompt MUST be specification-grade — not
a loose description. A basic prompt ("build a site with Three.js and 4 screens")
produces low-quality, monolithic output that the user will reject.

### Antipattern (REJECTED by user)

```
Build a single-page site with Three.js, GSAP, and 4 screens: Hero, Map, Report, Projects.
```

### Required Structure for Complex Prompts

Every high-quality prompt for creative Pi tasks must include:

1. **Project architecture** — exact file tree, module responsibilities, CDN versions
2. **Design tokens** — exact CSS custom properties (colors, fonts, radii, glows)
3. **Technical specifications** — renderer config, light setup, material parameters,
   shader requirements. Give exact values for NON-NEGOTIABLES (tone mapping, shadow
   maps, dark mode, no-gradients rule). Describe INTENT for creative choices (animation
   timing, audio design, camera movement) — let the model exercise judgment
4. **Screen-by-screen breakdown** — for each screen: 3D scene CONCEPT + HTML overlay
   CONCEPT + interaction INTENT. Do NOT prescribe exact pixel sizes or animation
   durations unless they define visual identity
5. **Data sources** — exact file paths within the repo that contain the data to render
6. **Asset pipeline** — how procedural fallbacks work, where external assets would
   plug in, structure of `assets-requisitados.md`
7. **Audio specification** — Web Audio API approach, emotional direction (e.g. "drone
   em tonalidade menor, contemplativo"), not exact frequencies
8. **Responsive breakpoints** — exact px values with behavior INTENT per tier
9. **Performance budget** — FCP, TTI, framerate, page weight targets
10. **Verification checklist** — 20+ specific, testable items

### ⚠️ The Line Between Spec and Creative Freedom

The user REJECTED a prompt that was too rigid — exact light intensities, exact
font sizes in px, exact animation durations in seconds, exact audio frequencies
in Hz. These micro-decisions belong to the model, not the spec.

**Specify as exact values:** colors (hex), non-negotiable constraints (no gradients,
no emojis, dark mode), design tokens, data sources (file paths), performance budgets,
CDN URLs, shadow map type, tone mapping algorithm, responsive breakpoints.

**Specify as intent/direction:** animation style, timing feel, audio mood, camera
angles, particle density, font sizes beyond the token system, exact Three.js light
positions, shader parameter values.

> Regra: se o valor exato define a IDENTIDADE VISUAL, vá no hex. Se define
> implementação, deixe o modelo decidir.

### Rule of Thumb

If the prompt is under 400 lines, it's too vague. A complex creative Pi task
(site, dashboard, generative experience) needs **400-600 lines** of specification.
The Pi Agent has context capacity — use it. Specificity reduces drift, prevents
monolithic output, and produces artifacts the user accepts on first delivery.

### User Preference

The user reviews prompts before agents execute. Send the `.md` prompt file for
approval BEFORE launching the Pi process. Do not launch and ask for forgiveness.

| Categoria | Skills | Qtd |
|-----------|--------|-----|
| 🌀 Ideação | `ideation-drilling` | 1 |
| 📋 PM (19) | `opportunity-solution-tree`, `prd-development`, `proto-persona`, `user-story`, etc. | 19 |
| 🧠 UX | `ux-design-principles`, `ux-empathy-map`, `ux-journey-map`, etc. | 7 |
| 🎨 UI | `ui-design-principles`, `ui-interaction-design`, `ui-form-design`, etc. | 5 |
| ⚙️ Eng | `software-architecture`, `tech-specs`, `entity-relationship-diagram`, etc. | 6 |

## Manutenção de Dotfiles

Configuração versionada em `gh:[username]/pi-dotfiles`:

```bash
# Máquina nova: instalar Pi + restaurar tudo
bash <(curl -fsSL https://raw.githubusercontent.com/[username]/pi-dotfiles/main/scripts/bootstrap.sh)

# Sincronizar skills (qualquer máquina)
cd ~/.pi-dotfiles && bash scripts/sync.sh pull   # repo → local
cd ~/.pi-dotfiles && bash scripts/sync.sh push   # local → repo
```

## Auditoria Pós-Execução

Após Pi completar uma tarefa, extrair métricas de uso da sessão `.jsonl`:

```bash
# Auditar última sessão
skill_view(name='pi-session-audit')
# ou comando direto
ls -lt ~/.pi/agent/sessions/--*/ | head -3
```

Carregar `pi-session-audit` para script completo de extração de tokens, custo e duração.

## ⚠️ OpenCode Go NÃO Suporta Image Inputs (Nenhum Modelo)

**Causa:** o provider `opencode-go` rejeita image inputs em TODOS os modelos —
GLM-5.2, MiniMax M3, DeepSeek V4 Pro, todos. Não é limitação do modelo, é do
provider. A API do OpenCode Go simplesmente não implementa o tipo `image` no
schema de mensagens.

**Sintoma:** Pi tenta ler um arquivo de imagem (screenshot, PNG de diagrama) e o
provider retorna:

```
400 Error from provider: This model does not support image inputs
```

Pi termina com `exit code 1`. A sessão fica com a entrada da imagem travada no
JSONL — qualquer tentativa de retomar com `--session` falha igual.

**Modelos afetados (via OpenCode Go):** todos — `glm-5.2`, `minimax-m3`,
`deepseek-v4-pro`, `deepseek-v4-flash`, `kimi-k2.6`, `qwen3.7-max`.

**Modelos NÃO afetados:** `deepseek` (API direta), `opencode` (Zen), `openrouter`.

⚠️ GLM-5.2 e MiniMax M3 são nativamente multimodais, mas a capacidade de visão
não é exposta pelo provider OpenCode Go. Se precisar de visão, use outro provider.

**Prevenção (no prompt):** sempre que o Pi for gerar código que possa envolver
screenshots, Playwright, Puppeteer, ou leitura de imagens, incluir explicitamente:

```
Do NOT use Playwright, Chromium, or read any image/screenshot files.
This provider (OpenCode Go) does NOT support image inputs.
Any attempt to read images will crash the session.
Use only text-based verification.
```

**Recuperação:** editar o JSONL para remover as entradas problemáticas. Ver
`### ⚠️ Cirurgia de JSONL — Remover Entradas Problemáticas` abaixo.

## ⚠️ GLM-5.2 é Texto Puro (Modelo de Visão é GLM-5V-Turbo)

A família GLM tem dois ramos separados:

| Modelo | Tipo | Provider |
|--------|------|----------|
| `glm-5.2` | Texto puro, 1M contexto | `opencode-go` |
| `glm-5v-turbo` | Multimodal (visão) | Não disponível no OpenCode Go |

Mesmo que o modelo base suporte visão, o provider OpenCode Go só expõe o modo
texto. Para tarefas que exigem visão, usar `minimax-m3` via `deepseek` provider
(API direta) ou `openrouter`.

## ⚠️ Cirurgia de JSONL — Remover Entradas Problemáticas

Quando uma sessão Pi trava por entrada inválida (imagem, token excedido, formato
quebrado), é possível EDITAR o JSONL para remover as entradas problemáticas e
relançar com `--session`. Isso preserva TODO o contexto anterior — horas de
leitura e raciocínio não são perdidas.

**Procedimento:**

```bash
# 1. Identificar entradas problemáticas
python3 -c "
import json
with open('session.jsonl') as f:
    entries = [json.loads(l) for l in f if l.strip()]
for i, e in enumerate(entries):
    content = e.get('message',{}).get('content','')
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get('type') == 'image':
                print(f'Entry {i}: IMAGE — cortar aqui')
"

# 2. Truncar o JSONL antes da primeira entrada problemática
python3 -c "
import json
with open('session.jsonl') as f:
    entries = [json.loads(l) for l in f if l.strip()]
# Manter entradas 0 até safe_idx-1
safe = entries[:SAFE_IDX]
with open('session.jsonl', 'w') as f:
    for e in safe:
        f.write(json.dumps(e) + '\n')
print(f'Cortado: {len(entries)} -> {len(safe)} entries')
"

# 3. Relançar com --session
pi --session session.jsonl --provider opencode-go --model minimax-m3
```

**Cenário típico:** Pi construiu todo o código (24 arquivos, site completo),
verificou que funciona, tirou screenshot para auto-verificação, e travou ao
tentar processar a imagem. Solução: cortar as últimas 5-8 entradas (Playwright +
screenshot + resposta travada) e relançar. O trabalho NÃO é perdido — os
arquivos já estão no disco.

## ⚠️ Model Drift — Pi Best (MiniMax M3) Refatora Sem Aviso

Pi best (`opencode-go/minimax-m3`) tem **alta propensão a drift**: pode refatorar
APIs de serviços existentes, renomear arquivos e deletar arquivos não relacionados
sem instrução explícita. É um efeito da capacidade do modelo — ele "melhora" o que vê.

**Problemas observados:**
- **Renomeia arquivos:** `mcp_tokens.py` → `mcp.py` (sem ser instruído)
- **Refatora APIs:** Muda assinatura de métodos do service (`issue_token` retorno,
  `validate_token` parâmetros), quebra compatibilidade com testes e routes existentes
- **Deleta arquivos:** Remove `test_mcp_action_token_service.py` como efeito colateral
  de `rm` durante debugging
- **Muda schemas de rota:** Altera estrutura de request/response esperada pela API

**⚠️ PITFALL CRÍTICO — Não assuma alucinação em docs**

Pi best modifica `product/engineering/` durante sprint execution (release-notes,
tech-specs, ERD, SAD, api-contracts) como parte do fluxo normal de trabalho.
**Isso não é alucinação, é documentação do que foi implementado.**

Caso real: Pi incluiu "7-state GTD model", "Morning Report" e "GTD Tutorial" no
release-notes — features que realmente existiam no código. O agente que reverteu
esses docs sem verificar perdeu horas de trabalho e queimou tokens desnecessários.

**Regra:** antes de reverter qualquer alteração do Pi nos docs de engenharia:

```bash
# 1. Verificar se as features mencionadas existem no código
grep -n "feature_name\|new_field" backend/taskflow/models/*.py 2>/dev/null
grep -rn "endpoint_name" backend/taskflow/api/routes/ 2>/dev/null
ls frontend/src/components/NovoComponente* 2>/dev/null

# 2. Confirmar com git diff o que mudou — se as features existem, o doc está correto
git diff product/engineering/
```

Se a feature existir no código, o doc está correto — não reverta.

**Checklist pós-Pi best (drift detection):**

```bash
# 1. Checar arquivos deletados ou renomeados
cd /opt/data/code/workstation/PROJETO
git diff --name-status HEAD
echo "=== Arquivos esperados ==="
ls backend/taskflow/api/routes/mcp*.py 2>/dev/null
ls tests/unit/test_mcp*.py 2>/dev/null

# 2. Checar se API do service mudou (diff de assinatura)
grep -n "^    async def " backend/taskflow/services/*.py

# 3. Rodar testes que Pi best pode ter quebrado
pytest tests/unit/test_mcp* tests/integration/test_mcp* -v --tb=short

# 4. Se drift for detectado, restaurar do git e re-aplicar só o necessário
git checkout -- backend/taskflow/services/mcp_action_token_service.py
# depois aplicar correção seletiva em vez de reescrever o arquivo todo
```

## ⚠️ UID Mismatch & Deploy

Pi escreve em staging (`_sprint1_F*_staging/`, `/tmp/`, `staging/`) quando o diretório
alvo é owned por uid 1001 (projetos do container Pi antigo). Para implantar:

```
skill_view(name='pi-agent-coordination', file_path='references/deploy-host-ssh.md')
```

**⚠️ Cuidado com o path correto.** O volume montado no container é:
```
host:/home/ubuntu/selfhost/shared/code/ → container:/opt/data/code/
host:/home/ubuntu/selfhost/hermes/data/ → container:/opt/data/
```

Portanto:
- **Working tree (Pi escreve):** `host:/home/ubuntu/selfhost/shared/code/workstation/taskflow/`
- **CI deploy:** `host:/home/ubuntu/selfhost/taskflow/` (clone separado)

Sempre aplicar `chmod` no path correto — o `shared/code/` é o volume ativo.

### ⚡ Git Permission Fix (UID 1001 ↔ 10000)

`git add` falha com `"insufficient permission for adding an object"` quando `.git/objects/`
e `.git/refs/` têm permissão restritiva e o dono é UID 1001 (host) mas o agente roda como
UID 10000 (container).

**⚠️ `sudo chown -R` NÃO funciona em arquivos do `.git/`** — o Docker overlay filesystem
retém o UID original mesmo após chown. O Hermes não tem sudo. A correção é via SSH no host:

```bash
# Via SSH no host — tornar .git/ world-writable
ssh oracle-host 'sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type d -exec chmod 777 {} \; && sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type f -exec chmod 666 {} \;'
```

**Verificação:** após o comando, testar `git add` localmente.

**Aplicação no setup atual:**
```bash
ssh oracle-host 'sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type d -exec chmod 777 {} \; && sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type f -exec chmod 666 {} \;'
```

### 🔄 Arquivos Novos Deletados pelo `git checkout`

`git checkout <branch>` deleta **arquivos untracked** que não existem na branch de
destino. Com UID 1001, o `Permission denied` impede a deleção — mas o arquivo some
mesmo assim (git tenta unlink e, falhando, o arquivo fica em estado inconsistente).

**Recuperação:** se existe um clone (`/opt/data/taskflow-pr/`) com os commits, copiar
de lá:

```bash
cd /opt/data/taskflow-pr
git diff --name-only origin/master HEAD --diff-filter=A | \
  while IFS= read -r f; do
    ssh oracle-host "mkdir -p /home/ubuntu/selfhost/taskflow/\$(dirname \"$f\")" 2>/dev/null
    ssh oracle-host "cat > /home/ubuntu/selfhost/taskflow/\$f" < "\$f"
  done
```

Se o clone não existe, o arquivo está perdido — só recuperável da sessão `.jsonl` do Pi.

**Prevenção:** antes de mudar de branch numa working tree com untracked files,
verificar com `git status --short | grep '^??'` e fazer stash ou commit primeiro.

## ⚠️ Monitoramento Manual com Sleep (Preferido do Usuário)

O usuário rejeitou cron jobs para monitoramento de Pi Agent. Prefere controle
manual: o agente dorme (`sleep 300`) com `notify_on_complete=true`, acorda,
checa o progresso, relata, e dorme de novo. Isso mantém o agente no loop e
evita automação desnecessária.

```bash
# Padrão: loop manual de sleep + check + relato
terminal(
  command="sleep 300 && echo 'ACORDEI'",
  background=true,
  notify_on_complete=true,
  timeout=320
)
```

A cada despertar, executar o script de progresso (ver `pi-session-audit`),
relatar no formato:

```
⏱️ Progresso — X min
- Entradas: N  |  Reads: N | Writes: N | Bash: N
- Arquivos criados: N
- Última ação: [descrição]
- Fase: [LENDO | PLANEJANDO | ESCREVENDO | FINALIZANDO]
```

Se o Pi terminar (exit code != null no processo), relatar o resultado final
## ⚠️ Pre-Flight Verification de Sites Estáticos

Após Pi gerar um site, fazer verificação antes do deploy:

```bash
# 1. Sintaxe JS (todos os arquivos)
cd etapa-4-site && for f in js/*.js; do node -c "$f" 2>&1 || echo "FAIL: $f"; done

# 2. Imports resolvem (checar main.js)
grep -rn "from '" js/main.js

# 3. Servir localmente e testar
python3 -m http.server 8765 &
sleep 2
curl -sI http://localhost:8765/index.html  # esperado: 200
for f in css/*.css js/*.js; do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/$f)
  [ "$code" != "200" ] && echo "FAIL: $f ($code)"
done
kill %1

# 4. Deploy
npx vercel --prod --yes
```

Verificação visual: `browser_navigate(url)` + `browser_vision` para confirmar
que elementos 3D renderizam e textos aparecem.

## Referências

- `references/fastmcp-testability-pattern.md` — Como testar MCP tools com FastMCP (impl/wrapper pattern para contornar `'FunctionTool' object is not callable`)
