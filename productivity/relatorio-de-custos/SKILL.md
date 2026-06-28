---
name: relatorio-de-custos
description: "Generate cost reports for multi-agent projects with real token data from Hermes and

Load this skill when the user asks for cost reports, spending breakdowns, or project expense analysis. Extracts real data from Hermes state.db and Pi Agent JSONL session logs, calculates costs based on model pricing per provider, and produces styled HTML reports via Antigravity with Hermes Style Guide design."

Load this skill when the user asks for cost reports, spending breakdowns, or project expense analysis. Extracts real data from Hermes state.db and Pi Agent JSONL session logs, calculates costs based on model pricing per provider, and produces styled HTML reports via Antigravity with Hermes Style Guide design."
category: productivity
related_skills: [html-report-hermes, product-pipeline]
type: Template
timestamp: 2026-06-19T19:47:50Z
---

# Relatório de Custos — Skill de Geração

> Gera relatórios técnicos de custos com dados reais de tokens de todos os agentes.

## Trigger

Usuário pede relatório de custos do projeto X, breakdown de gastos, quanto custou o MVP.

## Fluxo

### 1. Coletar Dados do Hermes

```bash
# state.db das sessões
sqlite3 /opt/data/state.db "
  SELECT id, title, source, model,
         input_tokens, output_tokens,
         cache_read_tokens, cache_write_tokens, reasoning_tokens,
         estimated_cost_usd, actual_cost_usd,
         datetime(started_at, 'unixepoch') as started,
         ended_at, message_count, tool_call_count
  FROM sessions
  WHERE title LIKE '%<projeto>%'
     OR title LIKE '%<tema>%'
  ORDER BY started_at
"
```

📘 **Reference completa:** `references/token-usage-breakdown.md` — queries para breakdown diário por fonte, hora, modelo, cache hit rate, e múltiplos dias.

**Schema real da tabela `sessions` (colunas de token/custo):**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `input_tokens` | INTEGER | Tokens de input (prompt) |
| `output_tokens` | INTEGER | Tokens de output (completion) |
| `cache_read_tokens` | INTEGER | Cache hit do provider (DeepSeek: contexto reutilizado) |
| `cache_write_tokens` | INTEGER | Cache write (escrita inicial no cache) |
| `reasoning_tokens` | INTEGER | Tokens de reasoning (chain-of-thought) |
| `estimated_cost_usd` | REAL | Custo estimado pelo Hermes (nem sempre preenchido) |
| `actual_cost_usd` | REAL | Custo real reportado pelo provider (raro) |
| `cost_status` | TEXT | "unknown", "estimated", ou "confirmed" |

**Filtrar por data (Unix epoch em segundos):**
```python
from datetime import datetime, timezone
start = datetime(2026, 6, 6, tzinfo=timezone.utc).timestamp()
end = datetime(2026, 6, 7, tzinfo=timezone.utc).timestamp()
```

### Sessões de Cron (Pipeline Automatizado)

```bash
sqlite3 /opt/data/state.db "
  SELECT id, started_at, input_tokens, output_tokens,
         cache_read_tokens, cache_write_tokens, reasoning_tokens
  FROM sessions
  WHERE source = 'cron'
    AND started_at >= <start_epoch>
    AND started_at < <end_epoch>
  ORDER BY started_at
"
```

O campo `source` diferencia tipos de sessão:
- `'cron'` — sessão de job agendado
- `'cli'` — terminal interativo
- `'telegram'`, `'discord'`, etc. — sessões de gateway

**Exemplo prático:** listar todos os 4 crons da IAF de um dia:

```bash
python3 -c "
import sqlite3
from datetime import datetime, timezone
conn = sqlite3.connect('/opt/data/state.db')
start = datetime(2026, 6, 6, tzinfo=timezone.utc).timestamp()
end = datetime(2026, 6, 7, tzinfo=timezone.utc).timestamp()
rows = conn.execute('''
    SELECT id, started_at, input_tokens, output_tokens,
           cache_read_tokens, reasoning_tokens, message_count
    FROM sessions
    WHERE source = 'cron' AND started_at >= ? AND started_at < ?
    ORDER BY started_at
''', (start, end)).fetchall()
for r in rows:
    dt = datetime.fromtimestamp(r[1], tz=timezone.utc)
    print(f'{dt.strftime(\"%H:%M\")} | in={r[2]:>6} out={r[3]:>6} cr={r[4]:>8} reas={r[5]:>6} msgs={r[6]}')
"
```

### Descobrir Schema ao Vivo (future-proof)

Sempre que a versão do Hermes mudar, descubra as colunas reais:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')
for col in conn.execute('PRAGMA table_info(sessions)').fetchall():
    print(f'{col[1]:30s} {col[2]:10s} nullable={not col[3]} default={col[4]}')
conn.close()
```

### 2. Coletar Dados do Pi Agent

```bash
# SSH no host Oracle e ler .jsonl do Pi
ssh oracle-host "cat /home/pi/.pi/agent/sessions/*.jsonl" | python3 -c "
import json, sys
for line in sys.stdin:
    data = json.loads(line)
    # Extrair tokens de cada call: input, output, cache_hit
    model = data.get('model', 'unknown')
    tokens_in = data.get('token_usage', {}).get('input', 0)
    tokens_out = data.get('token_usage', {}).get('output', 0)
    cache_hit = data.get('token_usage', {}).get('cache_read', 0)
    print(f'{model}\t{tokens_in}\t{tokens_out}\t{cache_hit}')
"
```

### 3. Calcular Custos

Preços de referência (DeepSeek — verificar preços atualizados na docs.deepseek.com):

| Modelo | Cache Hit (input) | Cache Miss (input) | Output |
|--------|-------------------|--------------------|--------|
| V4 Flash | $0,0028/M | $0,14/M | $0,28/M |
| V4 Pro | $0,003625/M | $0,435/M | $0,87/M |

Fórmula por call:
```
custo = (input * cache_hit_rate * preco_hit) +
        (input * cache_miss_rate * preco_miss) +
        (output * preco_output)
```

Cache hit rates: V4 Flash = 98%, V4 Pro ≈ 90% (estimado conservador).

### 4. Gerar o Relatório Completo via Agy (MÉTODO PREFERENCIAL)

**NUNCA escreva o HTML manualmente.** O usuário prefere o agy para output visual. Mesmo que o agy demore, o resultado visual é superior.

O agy gera o relatório COMPLETO (hero + sumário executivo + seções detalhadas) a partir de um único prompt — não é necessário criar um HTML base separado.

```bash
# 4a. Escrever prompt com dados reais (usar template em references/executive-summary-prompt.md)
#     Incluir: hero, 4 KPI cards, tabela de tokens, callout de total, insights, seções

# 4b. Copiar prompt para o host
scp -o StrictHostKeyChecking=no -i /opt/data/home/.ssh/id_rsa_oracle \
  prompt-exec.md ubuntu@172.19.0.1:/tmp/

# 4c. Executar agy com timeout generoso (300s) — NÃO usar 120s
#     timeout de 120s é INSUFICIENTE: agy começa a responder em ~30s
#     mas leva até 4min para completar a geração HTML multi-seção
ssh oracle-host 'export PATH="$HOME/.local/bin:$PATH" && \
  timeout 300 sh -c "cat /tmp/prompt-exec.md | agy 2>&1"'

# 4d. Descobrir o nome do arquivo gerado (agy nomeia conforme o prompt)
#     e copiar de volta
ssh oracle-host 'ls -t /home/ubuntu/*.html | head -3'
scp -o StrictHostKeyChecking=no -i /opt/data/home/.ssh/id_rsa_oracle \
  ubuntu@172.19.0.1:/home/ubuntu/<arquivo-gerado>.html \
  /opt/data/code/workstation/relatorio.html
```

### 4b. Fallback: Adicionar Sumário a HTML Existente

Quando já existe um HTML base e você só precisa adicionar o sumário executivo:

```bash
# 1. Copiar base HTML + prompt para o host
scp base.html ubuntu@172.19.0.1:/home/ubuntu/
scp prompt.md ubuntu@172.19.0.1:/tmp/

# 2. Prompt deve instruir agy a ler o base.html, inserir o bloco
#    do sumário executivo entre o hero e a seção 1
ssh oracle-host 'cat /tmp/prompt.md | timeout 300 agy'
```

### 6. Entregar

```bash
# Zip do HTML (Telegram não suporta .html diretamente)
python3 -c "import shutil, os; shutil.make_archive('relatorio', 'zip', '.', 'relatorio.html')"
```

Enviar via MEDIA: com resumo dos principais números.

## Estrutura do Relatório

```
1. HERO — gradiente azul, valor total em dourado
2. SUMÁRIO EXECUTIVO (inserido pelo agy):
   - 4 KPI cards (grid 4 colunas)
   - Tabela de tokens por modelo (cache hit / miss / output / total / hit rate / custo)
   - Callout: total geral de tokens em destaque
   - 4 Key Insights (grid 2×2, cards com borda colorida)
3. Metodologia de Coleta
4. Breakdown Hermes (por atividade)
5. Breakdown Pi Agent (por sessão/fase)
6. Agentes Gratuitos
7. Comparação v2 vs v3
8. Anexos Técnicos
```

## Dados Essenciais

Sempre incluir na tabela de tokens:

| Modelo | Cache Hit | Cache Miss | Output | Total | Hit Rate | Custo |
|--------|-----------|------------|--------|-------|----------|-------|
| Hermes V4 Flash | [N] | [N] | [N] | [N] | ~99% | $X.XX |
| Pi V4 Pro | [N] | [N] | [N] | [N] | ~97% | $X.XX |
| Pi V4 Flash | [N] | [N] | [N] | [N] | ~99% | $X.XX |
| Grátis | [N] | [N] | [N] | [N] | — | $0,00 |
| **Total** | **[N]** | **[N]** | **[N]** | **[N]** | **~99%** | **$X.XX** |

Callout de destaque:
```
📊 Total de Tokens Processados
Cache Hit:    [N] tokens  (98,98% do total)
Cache Miss:   [N] tokens  (1,02% do total)
Output:       [N] tokens
─────────────────────────────────
Total:        [N] tokens
```

## Pitfalls

⚠️ **Timeout do agy** — prompts de geração HTML multi-seção precisam de timeout ≥300s. O agy começa a responder em ~30s mas leva até 4min para concluir. `timeout 120` corta no meio. Usar `timeout 300 sh -c "cat prompt.md | agy"` no ssh.

⚠️ **Pi .jsonl** — arquivos em `/home/pi/.pi/agent/sessions/` no container Pi. Acessar via SSH no host Oracle e `docker exec pi-agent cat ...` ou configurar bind mount.

⚠️ **Entregar em .zip** — Telegram não suporta .html diretamente. Usar Python shutil:
   ```python
   python3 -c "import shutil, os; os.chdir('/opt/data/code/workstation'); shutil.make_archive('relatorio', 'zip', '.', 'relatorio.html')"
   ```

⚠️ **Cache hit rate** — o DeepSeek V4 Flash tem 98% garantido. Para V4 Pro, estimar 90% conservadoramente a menos que haja dados concretos.

⚠️ **Tabela de tokens no sumário executivo** — é a métrica mais importante. Sempre incluir: cache hit, cache miss, output, total, hit rate, e custo por modelo. O callout de total geral (279M+) em Space Mono dá o destaque visual.

⚠️ **Preços desatualizados** — verificar preços atuais em docs.deepseek.com antes de gerar. Os valores na skill são de referência (Jun 2026).

⚠️ **Idioma** — relatório inteiro em português. Números com vírgula decimal ($1,64, 279.866.333). Separador de milhar com ponto.

⚠️ **Porcentagem com vírgula** — usar formato brasileiro: `98,98%` (vírgula, não ponto).
