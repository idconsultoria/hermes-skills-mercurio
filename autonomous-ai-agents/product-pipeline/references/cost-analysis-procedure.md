# Cost Analysis — Pós-MVP

> **Quando:** Após MVP concluído (Fase 4e) ou quando o usuário solicitar.
> **Quem executa:** Hermes (coleta + relatório direto) ou Hermes → Antigravity (HTML via agy)
> **Propósito:** Relatar ao usuário o custo real de desenvolvimento.

## Fontes de Dados

| Agente | Fonte | Formato | Localização |
|--------|-------|---------|-------------|
| **Hermes** | state.db (SQLite) | `sessions` table | `/opt/data/state.db` |
| **Pi Agent** | Session .jsonl files | `message.usage` objects | `/home/pi/.pi/agent/sessions/{workspace}/*.jsonl` |
| **Antigravity** | Plano Google One | Free tier | — |
| **MiniMax M3** | OpenRouter free | Free tier | — |

## 1. Coletar tokens do Hermes (state.db)

### Identificar a cadeia de sessões do projeto

O state.db registra cada sessão com `parent_session_id`. A cadeia do projeto começa na sessão raiz (a que executou `/product-pipeline` pela primeira vez):

```python
import sqlite3
conn = sqlite3.connect('state.db')
cur = conn.cursor()
root_id = 'ID_DA_SESSAO_RAIZ'

# Pegar TODAS as sessões da cadeia (raiz + filhas)
cur.execute('''
SELECT id, parent_session_id, started_at, input_tokens, output_tokens, 
       cache_read_tokens, message_count, tool_call_count, model
FROM sessions 
WHERE id = ? OR parent_session_id = ?
ORDER BY started_at
''', (root_id, root_id))
rows = cur.fetchall()
```

**Campos úteis do sessions table:**
| Campo | Descrição |
|-------|-----------|
| `input_tokens` | Cache miss input (tokens enviados ao modelo) |
| `output_tokens` | Tokens gerados pelo modelo |
| `cache_read_tokens` | Cache hit input (lidos do cache) |
| `model` | Modelo usado (ex: `deepseek-v4-flash`) |
| `source` | Origem (telegram, cron, tui, cli, whatsapp) |
| `parent_session_id` | Sessão pai (para encadeamento) |

### Descobrir a sessão raiz

Use `session_search` para encontrar quando a skill `/product-pipeline` foi executada pela primeira vez:

```python
cur.execute('''
SELECT id, started_at FROM sessions 
WHERE source='telegram'
ORDER BY started_at ASC
LIMIT 20
''')
for r in cur.fetchall():
    # Verificar primeira mensagem de cada sessão
    cur.execute('SELECT content FROM messages WHERE session_id=? AND role="user" ORDER BY id LIMIT 1', (r[0],))
    msg = cur.fetchone()
    if msg and "product-pipeline" in (msg[0] or ""):
        print(f"Found root: {r[0]} at {r[1]}")
```

### Ratio real de cache

Calcular a proporção Cache Hit : Cache Miss : Output das sessões do projeto:

```python
total_cr = sum(r[5] for r in rows)  # cache_read_tokens
total_in = sum(r[3] for r in rows)  # input_tokens  
total_out = sum(r[4] for r in rows) # output_tokens

ratio_hit = total_cr / total_out
ratio_miss = total_in / total_out
# Exemplo real: 306 : 2.5 : 1 (Hermes) / 207 : 2.1 : 1 (Hermes + Pi combinado)
```

## 2. Coletar tokens do Pi Agent (.jsonl)

### Localização e estrutura

Pi salva sessões em arquivos JSONL no contêiner Docker. Estrutura:

```
/home/pi/.pi/agent/sessions/
├── --workspace-code-workstation-PROJETO--/
│   ├── 2026-06-06T20-39-36-077Z_*.jsonl
│   └── ... (demais sessões do projeto)
└── --workspace-code-other--/
    └── ...
```

Cada arquivo contém linhas JSON com `type`:
- `{"type":"model_change","modelId":"deepseek-v4-pro","provider":"deepseek"}` → modelo usado
- `{"type":"message","message":{"role":"assistant",...},"usage":{"input":2512,"output":1159,"cacheRead":132224,"cost":{"total":0.00113}}}` → dados de uso

**⚠️ Crucial:** o campo `usage` está dentro de `message` no nível da linha JSON, NÃO no topo. Ou seja: `obj["message"]["usage"]`, não `obj["usage"]`.

### Script de extração

Pi container não tem Python (só Node.js). Copiar os arquivos para o host e parsear:

```bash
# 1. Copiar session files do container para o host
ssh oracle-host 'docker cp pi_agent:/home/pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO-- /tmp/pi-sessions-taskflow'

# 2. Parsear com Python no host
python3 << 'HERMESEOF'
import json, os, glob

for fpath in sorted(glob.glob("/tmp/pi-sessions-taskflow/*.jsonl")):
    with open(fpath) as f:
        for line in f:
            try: obj = json.loads(line.strip())
            except: continue
            if obj.get("type") == "message":
                usage = obj.get("message", {}).get("usage")
                if usage:
                    inp = usage.get("input", 0)
                    out = usage.get("output", 0)
                    cr = usage.get("cacheRead", 0)
                    cost = usage.get("cost", {}).get("total", 0)
                    # Acumular por modelo
HERMESEOF
```

### Modelos que podem aparecer

| modelId | Provider | Custo |
|---------|----------|-------|
| `deepseek-v4-pro` | `deepseek` | Pago ($0.435/$0.87 + cache $0.003625) |
| `deepseek-v4-flash` | `deepseek` | Pago ($0.14/$0.28 + cache $0.0028) |
| `minimax-m3` | `opencode-go` | Free (cota semanal) |
| `minimax-m3-free` | `opencode` | Free (limites por request) |
| `deepseek/deepseek-v4-pro` | `openrouter` | OpenRouter routing (raro) |

### Verificar outras fontes do Pi

Além dos .jsonl do Pi, verificar:

```bash
# DeepSeek API - saldo atual (não mostra consumo histórico)
curl -s https://api.deepseek.com/v1/user/balance -H "Authorization: Bearer $KEY"

# OpenRouter - consumo total  
curl -s -H "Authorization: Bearer $KEY" https://openrouter.ai/api/v1/auth/key
```

## 3. Preços por modelo (DeepSeek direto — verificado Jun/2026)

### DeepSeek V4 Flash
| Tipo | Preço / 1M tokens | Desconto |
|------|-------------------|----------|
| Cache Hit (input) | $0,0028 | 98% |
| Cache Miss (input) | $0,14 | — |
| Output | $0,28 | — |

### DeepSeek V4 Pro
| Tipo | Preço / 1M tokens | Desconto |
|------|-------------------|----------|
| Cache Hit (input) | $0,003625 | 99,2% |
| Cache Miss (input) | $0,435 | — |
| Output | $0,87 | — |

### MiniMax M3 + Gemini Flash 3.5
Free tier / incluso no plano Google One.

> ⚠️ **Cache hit OpenRouter ≠ DeepSeek direto:** OpenRouter oferece 75% de desconto em cache hit. DeepSeek direto oferece 98% (V4 Flash) e 99,2% (V4 Pro). Confirmar qual provedor cada agente usou antes de calcular.

## 4. Calcular custos

```python
# Hermes (V4 Flash)
hermes_cost = (cr/1e6)*0.0028 + (inp/1e6)*0.14 + (out/1e6)*0.28

# Pi (V4 Pro)
pi_cost = (cr/1e6)*0.003625 + (inp/1e6)*0.435 + (out/1e6)*0.87

# Pi (V4 Flash) 
pi_flash_cost = (cr/1e6)*0.0028 + (inp/1e6)*0.14 + (out/1e6)*0.28
```

## 5. Geração do relatório

### Hermes gera HTML diretamente (preferido)

O Hermes pode gerar o HTML final usando o Hermes Agent Design Style Guide (azul #0000FF, Inter/Space Mono/Spectral). Incluir no CSS:

```css
:root {
  --primary: #0000FF;       /* azul royal */
  --blue-bg: #F0F5FF;       /* fundo gelo */
  --blue-border: #CCD9FF;   /* bordas */
  --text-muted: #666680;     /* texto secundário */
  --code-bg: #F5F5F7;       /* fundo código */
}
```

**Regras para o relatório (preferências do usuário):**
1. ✅ **100% português brasileiro** — todo texto, inclusive labels de tabelas
2. ❌ **NUNCA usar gráficos de pizza/donut** — terminantemente proibidos
3. ✅ **Barras horizontais** CSS são aceitas (cache hit vs miss vs output)
4. ✅ **Muito texto corrido** — não apenas tabelas. Explicar a matemática
5. ✅ **Fórmulas explícitas** — mostrar o cálculo: `242M × $0,0028 = $0,68`
6. ✅ **Tabela linha a linha** das sessões com tokens individuais
7. ✅ **Comparativo humano** com múltiplos cenários (BR otimista, US realista, conservador)
8. ✅ **Seção "O que $X compraria?"** — perspectiva lúdica (café, chope, etc.)
9. ✅ **Incluir projeção de manutenção** futura

### Antigravity gera HTML (alternativa — via tmux)

Se o usuário pedir agy para gerar o HTML:

```bash
# 1. Salvar prompt completo em arquivo no host
ssh oracle-host 'cat > /home/ubuntu/tmp_cost_prompt.md << "PROMPT"
# Prompt para agy — geração de relatório de custos
[...dados completos...]
PROMPT

# 2. Iniciar tmux
tmux new-session -d -s agy "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"

# 3. Aguardar TUI
sleep 8

# 4. Enviar prompt — NÃO usar paste-buffer (agy interpreta como comando bash)
tmux send-keys -t agy "Leia /home/ubuntu/tmp_cost_prompt.md e gere um HTML..." Enter

# 5. Aguardar processamento (30-90s)
sleep 60
tmux capture-pane -t agy -p -S -15

# 6. Copiar resultado
cat /home/ubuntu/taskflow-cost-report-agy.html
```

> ⚠️ `tmux paste-buffer` não funciona com agy — o agy pede permissão bash e nunca processa o prompt colado. Enviar texto diretamente via send-keys.

## Dados reais de referência (TaskFlow MVP, Jun/2026)

### Hermes (17 sessões encadeadas, DS V4 Flash)
| Métrica | Valor |
|---------|-------|
| Cache miss input | 1.985.561 tokens |
| Cache hit input | 242.225.664 tokens |
| Output | 791.049 tokens |
| Custo | $1,18 |
| Cache : Miss : Out | 306 : 2,5 : 1 |

### Pi Agent (11 sessões, extraído dos .jsonl)
| Modelo | Sessões | Calls | Cache Miss | Output | Cache Hit | Custo |
|--------|---------|-------|-----------|--------|-----------|-------|
| DS V4 Pro | 8 | 398 | 756.764 | 408.314 | 27.302.656 | $0,78 |
| DS V4 Flash | 2 | 79 | 87.265 | 128.155 | 6.113.664 | $0,07 |
| MiniMax M3 | 5 | 6 | 10.142 | 90 | 5.423 | $0,00 |
| **Total Pi** | **11** | **486** | **858.813** | **538.063** | **33.467.183** | **$0,85** |

### Consolidado
| Agente | Custo | % |
|--------|-------|---|
| Hermes (DS V4 Flash) | $1,18 | 58% |
| Pi Agent (DS V4 Pro + Flash) | $0,85 | 42% |
| Gemini Flash 3.5 (Antigravity) | $0,00 | 0% |
| MiniMax M3 | $0,00 | 0% |
| **Total** | **$2,03** | **100%** |

## Pitfalls

⚠️ **Identificar sessões corretas:** Nem toda sessão no state.db é do projeto. Sessões de news digest, IAF newsletter, conversas gerais também aparecem. Filtrar pela cadeia de `parent_session_id` da raiz que executou a skill `/product-pipeline`.

⚠️ **Pi .jsonl: usage está dentro de message:** `obj["message"]["usage"]`, NÃO `obj["usage"]`. Erro comum que retorna zero.

⚠️ **Pi container não tem Python:** Para parsear os .jsonl, copiar para o host primeiro com `docker cp`, depois parsear no host.

⚠️ **DeepSeek balance API não mostra consumo histórico:** O endpoint `/v1/user/balance` só retorna o saldo atual. Para saber quanto foi consumido, subtrair do saldo inicial conhecido ou usar os .jsonl.

⚠️ **OpenRouter key vs DeepSeek key:** Pi pode ter ambas configuradas. Verificar no container qual foi usada (`env | grep KEY`). Cada key tem provedor diferente e preços diferentes.

⚠️ **MiniMax M3 free vs Go:** `opencode/minimax-m3-free` (Zen, gratuito) vs `opencode-go/minimax-m3` (Go, assinatura paga). Ambos podem aparecer nos .jsonl com providers diferentes.

⚠️ **Gemini Flash 3.5, não 3.1 Flash Lite:** O Antigravity usa Gemini Flash 3.5 (configurado como "Gemini 3.1 Pro (High)" na UI do agy). Não confundir com Gemini 3.1 Flash Lite (que NÃO foi usado no projeto).

⚠️ **Agy via tmux = frágil:** A TUI do agy é interativa e requer aprovação para cada comando. Preferir que o Hermes gere o HTML diretamente quando possível.
