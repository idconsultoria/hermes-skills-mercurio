# Como sondar o endpoint LLM do Pi/opencode-go diretamente

## Contexto

Quando é preciso validar o LLM do produto (tom, latência, custo) antes de configurar produção, dá para sondar o MESMO endpoint que o Pi Agent usa, com a chave que o Pi já tem. Padrão validado no CFP IA (WS4-13, DeepSeek v4 Flash).

## Onde estão as chaves

`~/.pi/agent/auth.json` (no HOME do Hermes = `/opt/data/home/.pi/agent/auth.json`):

```json
{
  "openrouter": {"type": "api_key", "key": "sk-or-v1-..."},
  "deepseek":   {"type": "api_key", "key": "sk-..."},
  "opencode":   {"type": "api_key", "key": "sk-hgg5..."},
  "opencode-go":{"type": "api_key", "key": "sk-hgg5..."}
}
```

O usuário pode autorizar usar a chave `opencode-go` (mesma do `opencode`) para testes em vez de pedir uma chave OpenRouter nova.

## Endpoint e auth

- Base: `https://opencode.ai/zen/go/v1` (o mesmo base_url que o Hermes usa no provider `opencode-go`)
- Auth: `Authorization: Bearer <key>` — **NÃO** `x-api-key` (retorna 401 "Missing API key")
- Modelo: `deepseek-v4-flash`

## Armadilhas (todas encontradas na prática)

1. **urllib default User-Agent → 403 error 1010 (Cloudflare).** Curl funciona; urllib falha. Fix: setar `User-Agent: Mozilla/5.0 ...` no header.
2. **DeepSeek v4 Flash tem modo reasoning que come o budget.** Com `max_tokens: 256`, a resposta sai VAZIA (`completion_tokens` todo em `reasoning_tokens`). Com `max_tokens: 1024`, sobra ~500 tokens para a resposta real. **Sempre usar `max_tokens ≥ 1024`** ao sondar esse modelo.
3. **Latência real ~12s** (8–14s) para respostas com reasoning — acima do alvo de 3s de muitos PRDs. Reportar como ressalva, não como bloqueio; mitigar com streaming/cache/modelo sem reasoning.
4. `GET /models` pode dar 403 mesmo com auth ok — não confiar nesse endpoint para "testar conectividade"; ir direto no `POST /chat/completions`.

## Esqueleto de teste (5 cenários de tom + diagnóstico + latência)

- System prompt: identidade CFP/coach, palavras proibidas, "nunca exiba cálculos", "nunca recomende investimento específico".
- 5 mensagens: vergonha, falha (iFood), "quanto guardar?", rotativo, "você está me julgando?".
- Verificar cada resposta: palavras proibidas (errou/não devia/irresponsável/gastou demais/fracasso), tom julgador, exibição de cálculos, recomendação de investimento.
- Teste de diagnóstico: passar o resultado do motor (perfil + variáveis) e pedir para comunicar — verificar que NÃO vaza `IE=`, `SE=`, valores.
- Medir latência por chamada; reportar média.

**Falso positivo comum:** o detector de palavras proibidas acusa a palavra "fracasso" quando o USUÁRIO escreveu "me sinto um fracasso" na mensagem e a resposta ecoa o contexto. Re-verificar a resposta isolada antes de reportar falha.

## Veredito honesto

Se a chave não existe ou o endpoint está bloqueado, rodar `--dry-run` e reportar a pendência (ex.: "adicionar créditos no OpenRouter"). NUNCA inventar resultado de teste — se não rodou, dizer que não rodou.
