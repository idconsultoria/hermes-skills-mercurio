# OpenCode / LLM diagnostic map (validado 22/08/2026)

Como validar uma chave de API do OpenCode e interpretar cada resposta do endpoint,
quando a IA de um backend (chat/análise) está "sempre caindo num fallback" ou
"dando erro de conexão".

## Regra rápida de diagnóstico

Se a UI mostra um **fallback genérico** (ex.: uma "análise SWOT" com textos óbvios e
vazios) + erro de conexão no chat → **toda chamada LLM falhou** (401/403/saldo), não é
"feature incompleta" nem "o mock é a feature". Atacar config/chave.

## Como validar uma chave sem o app

```bash
BASE="https://opencode.ai/zen/go/v1"; KEY="sk-..."; MOD="deepseek-v4-flash"
curl -s -w "\nHTTP %{http_code}\n" --max-time 60 -X POST "$BASE/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KEY" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36" \
  -d "{\"model\":\"$MOD\",\"messages\":[{\"role\":\"user\",\"content\":\"Responda apenas: OK\"}],\"temperature\":0.3,\"max_tokens\":20}"
```

⚠️ O `User-Agent` de navegador no header é **obrigatório** — o OpenCode rejeita o
default do `urllib`.

## Mapa de respostas dos providers OpenCode

| Endpoint | Resposta | Significado |
|---|---|---|
| `https://opencode.ai/zen/go/v1` | **HTTP 200** `chat.completion` | Chave OK, modelo respondendo. Principal. |
| `https://opencode.ai/zen/go/v1` | **HTTP 403 `RegionError`** "only available hosted in China and requires explicit opt in" | Modelo DeepSeek hospedado na **região China**; conta sem opt-in. Link: `opencode.ai/workspace/<wrk>/go` (config: Provedores → "Ativar modelos hospedados na China"). |
| `https://opencode.ai/zen/v1` | **HTTP 401 `CreditsError`** "Insufficient balance" | Conta **sem saldo** (billing). Link: `.../billing`. |
| `https://opencode.ai/go/v1` | **HTTP 404** | Endpoint inexistente — não conta como provider válido. |
| qualquer | **HTTP 401** "invalid api key" | Chave errada/expirada. |
| qualquer | content vazio / `{"ok":false}` | Modelo respondeu vazio — checar opt-in/saldo ou prompt. |

- 403/401 de opt-in/saldo **não** indicam chave errada — são estado da **conta**.
- Backends com fallback de providers (`zen → go → zen-go`) tentam em ordem; o primeiro
  que responder resolve. Basta o principal estar ok (mesmo com os demais sem saldo).

## Pitfall: chave salva como valor MASCARADO

Backends que mascararão segredos ao listar (ex.: `listar_config` →
`valor_mascarado = f"{v[:7]}...{v[-4:]}"`, dando `sk-fh4...GOcN`) podem receber o
**texto mascarado** de volta no "novo valor" se o usuário copiar o que a UI mostra.
Sintoma: chave "salva", todas as chamadas 401.
- **Detectar:** valor com `...` literal no meio, ~13–14 chars, em vez de >50 chars
  de um sk- real.
- **Corrigir:** colar a chave REAL (nunca a versão pontilhada que a UI mostra).

## Rate limit vira 500 (FastAPI/Starlette recente)

Endpoints com `@limiter.limit("10/hour")` (testar-config é um exemplo típico)
estouram o limite ao clicar repetidamente. Se o handler do slowapi faz
`raise HTTPException(429)` DENTRO de um exception handler, Starlette recente
(fastapi 0.133 / uvicorn 0.41) converte em **500** — o front mostra "API 500:
Internal Server Error".
- **NÃO é** problema de autenticação: se fosse, o endpoint pegaria no `except` e
  retornaria `{"ok":false, "erro":"HTTP..."}` — jamais 500. Um 500 num handler de
  config = rate limit atingido.
- **Correção:** exception handler deve **retornar** `JSONResponse(status_code=429)`,
  nunca `raise`.
- **Desbloqueio imediato:** reiniciar o backend zera o contador em memória (ou aguardar
  a janela, ex. `10/hour`).

## Dica de segurança

Não gravar chave de API real em **dump versionado** de banco — vaza em backup/fork.
Previews devem receber a chave por env, não por seed.