# MiniMax M3 — Opções de Acesso

> Atualizado: 06 Jun 2026. MiniMax M3 lançado em 1 Jun 2026 (open-weight, pesos prometidos em ~10 dias).

## Via Pi Agent

### 1. OpenCode Zen (FREE) — Preferido
| Campo | Valor |
|-------|-------|
| Provider | `opencode` |
| Model ID | `opencode/minimax-m3-free` |
| Chave | `OPENCODE_API_KEY` (mesma do Go) |
| Base URL | `https://opencode.ai/zen/v1/chat/completions` |

Comando:
```bash
ssh oracle-host "LC_DIR=code/PROJETO pi-agent 'pi -p \"prompt\" --provider opencode --model opencode/minimax-m3-free'"
```

### 2. OpenCode Go (Subscription) — Fallback pago
| Campo | Valor |
|-------|-------|
| Provider | `opencode-go` |
| Model ID | `minimax-m3` |
| Custo | $5 1º mês, $10/mês |
| Limites | 5h $12, Semanal $30, Mensal $60 |
| Requests/semana | ≈3.500 (MiniMax M3) |

### 3. DeepSeek V4 Pro (API Key) — Fallback geral
| Campo | Valor |
|-------|-------|
| Provider | `deepseek` |
| Model ID | `deepseek/deepseek-v4-pro` |
| Chave | `DEEPSEEK_API_KEY` |

## Detecção de Disponibilidade

```bash
# Testar Zen free
ssh oracle-host "pi-agent 'pi -p \"echo test\" --provider opencode --model opencode/minimax-m3-free'" 2>&1 | head -3

# Testar Go (se free falhar)
ssh oracle-host "pi-agent 'pi -p \"echo test\" --provider opencode-go --model minimax-m3'" 2>&1 | head -3

# Se 429 em ambos → fallback DeepSeek
```

## Configuração Inicial — Provider `opencode`

O provider `opencode` (Zen) **não vem no Pi por padrão** — só `opencode-go` (Go). Para adicionar:

```bash
# Injetar com node (mesma chave do opencode-go)
ssh oracle-host "pi-shell 'node -e \"let f=require(\\\"fs\\\"); \
let d=JSON.parse(f.readFileSync(\\\"/home/pi/.pi/agent/auth.json\\\",\\\"utf8\\\")); \
d[\\\"opencode\\\"]=d[\\\"opencode-go\\\"]; \
f.writeFileSync(\\\"/home/pi/.pi/agent/auth.json\\\",JSON.stringify(d,null,2));\"'"

# Verificar
ssh oracle-host "pi-agent 'pi -p \"show config\"'" | grep -E "Provider|OpenCode"
# Output esperado: OpenRouter, DeepSeek, OpenCode, OpenCode-Go
```

> 💡 `OPENCODE_API_KEY` é compartilhada — mesma chave serve para Zen e Go.

## Via OpenCode Zen Direto (sem Pi)

API endpoint: `https://opencode.ai/zen/v1/chat/completions`
Model ID: `minimax-m3-free`

```bash
curl https://opencode.ai/zen/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax-m3-free","messages":[{"role":"user","content":"hello"}]}'
```

## Modelos Gratuitos no OpenCode Zen

Confirmados via API `GET https://opencode.ai/zen/v1/models`:

| Model ID | Tipo |
|----------|------|
| `minimax-m3-free` | Chat/Code |
| `deepseek-v4-flash-free` | Chat/Code |
| `mimo-v2.5-free` | Chat |
| `qwen3.6-plus-free` | Chat/Code |
| `nemotron-3-ultra-free` | Chat |
| `nemotron-3-super-free` | Chat |

> ⚠️ A documentação do OpenCode Zen em `opencode.ai/docs/zen/` NÃO lista `minimax-m3-free` (desatualizada). A API `/zen/v1/models` é a fonte da verdade.

## Lista completa de modelos gratuitos (API)

```bash
curl -s https://opencode.ai/zen/v1/models \
  -H "Authorization: Bearer $OPENCODE_API_KEY" \
  | python3 -m json.tool
```

## Via MiniMax Direto (PAYG)

| Campo | Valor |
|-------|-------|
| Provider no Pi | `minimax` |
| Chave | `MINIMAX_API_KEY` |
| API Key | PAYG de `platform.minimax.io` (NÃO subscription key) |
| Base URL (OpenAI compat) | `https://api.minimax.io/v1` |
| Base URL (Anthropic compat) | `https://api.minimax.io/anthropic` |
| Preço | $0.30/M input, $1.20/M output (50% off lançamento, ≤512k) |

## Pi Providers — Mapeamento

| Provider Key (auth.json) | ENV var | Pi Provider Name | Model ID prefix |
|--------------------------|---------|------------------|-----------------|
| `opencode` | `OPENCODE_API_KEY` | OpenCode Zen | `opencode/` |
| `opencode-go` | `OPENCODE_API_KEY` | OpenCode Go | (direto) |
| `deepseek` | `DEEPSEEK_API_KEY` | DeepSeek | `deepseek/` |
| `minimax` | `MINIMAX_API_KEY` | MiniMax | (direto) |
| `openrouter` | `OPENROUTER_API_KEY` | OpenRouter | (direto) |
