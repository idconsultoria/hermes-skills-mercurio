---
name: searxng-firecrawl-repair
description: "web_search empty? Diagnose and fix SearXNG→Firecrawl search engine chain.

Load this skill when web_search returns success with an empty web list — the search backend died silently. Covers the SearXNG→Firecrawl architecture, how to verify each link in the chain on the Oracle host, and repair steps. Not a Hermes bug: fix the backend."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web_search, firecrawl, searxng, search, infra, oracle]
    related_skills: [hermes-diagnostics, selfhost-service-deploy, oracle-host-access]
type: Research
timestamp: 2026-08-15T04:00:00Z
---

# SearXNG + Firecrawl Repair (web_search vazio)

## When to Use

- `web_search` (ou subagentes de pesquisa) retorna `{"success": true, "data": {"web": []}}` — sucesso com lista vazia, sem erro visível.
- Delegações antigas mostram `web_search ok Ns: { "success": true, "data": { "web": [] } }`.
- O Firecrawl self-hosted devolve `{"success":true,"data":[],"warning":"No search results found"}`.

**Sintoma enganoso**: a ferramenta "funciona" (success:true) mas sempre devolve vazio. Não é bug do Hermes — é o backend de busca morto silenciosamente.

## Arquitetura (cadeia do problema)

```
web_search (Hermes)
  → web.backend: firecrawl (config.yaml)
    → Firecrawl self-hosted (FIRECRAWL_API_URL=http://firecrawl_api:3002, key "local")
      → SEARXNG_ENDPOINT (http://searxng-core:8080)
        → SearXNG → engines upstream (bing, google, duckduckgo, brave...)
```

Qualquer elo devolvendo vazio quebra tudo. Na prática (Oracle Cloud, IP de datacenter), **a maioria das engines do SearXNG é bloqueada**: brave (too many requests), duckduckgo (timeout/CAPTCHA), startpage (CAPTCHA), google (vazio), mojeek/qwant (access denied), wikidata (403).

## Diagnóstico (em ordem)

### 1. Confirmar o sintoma
```bash
curl -s -m 30 "http://searxng-core:8080/search?q=OpenAI+GPT-5&format=json" | python3 -m json.tool | head -30
```
- `results: []` + `unresponsive_engines` listando brave/ddg/startpage = engines bloqueadas.

### 2. Testar engines individualmente (a que funciona)
```bash
for eng in bing google duckduckgo brave mojeek seznam gmx; do
  echo "--- $eng ---"
  curl -s -m 25 "http://searxng-core:8080/search?q=OpenAI+GPT-5&format=json&engines=$eng" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('  n=', len(d.get('results',[])), '| unresponsive=', d.get('unresponsive_engines'))"
done
```
No caso real (ago/2026): só `bing`, `gmx`, `seznam`, `mwmbl`, `boardreader` funcionam.

### 3. Bateria empírica completa (robusto, 2 rodadas)
Rodar `scripts/searxng_engine_test.py` (28 engines × 5 queries × 2 rodadas ≈ 15 min):
```bash
cd /opt/data && python3 scripts/searxng_engine_test.py > /tmp/searxng_test.log 2>&1
```
Critério de aprovação: ok≥4/5 nas DUAS rodadas. Descartar instáveis.

## Fix (settings.yml do SearXNG no host Oracle)

Arquivo: `/home/ubuntu/selfhost/searxng/core-config/settings.yml` (mount em `/etc/searxng` no container).

### ⚠️ PITFALL CRÍTICO: `disabled: true` no default
No settings.yml default do SearXNG, **as engines boas vêm com `disabled: true`** (bing, gmx, seznam, mwmbl, boardreader). O `keep_only` mantém esse estado — sem `disabled: false` explícito, o SearXNG fica com **0 engines ativas** e retorna vazio mesmo com config nova. SEMPRE adicionar `disabled: false` por engine no bloco `engines:`.

### Config validada (referência: scripts/searxng_settings_new.yml)
```yaml
use_default_settings:
  engines:
    keep_only:
      - bing
      - gmx
      - seznam
      - mwmbl
      - boardreader
# ... general/search/server/outgoing padrão ...
engines:
  - name: bing
    disabled: false
    weight: 2.0
  - name: gmx
    disabled: false
    weight: 1.5
  - name: seznam
    disabled: false
    weight: 1.5
  - name: mwmbl
    disabled: false
    weight: 1.0
  - name: boardreader
    disabled: false
    weight: 1.0
```

### Aplicar
```bash
scp /opt/data/scripts/searxng_settings_new.yml oracle-host:/tmp/searxng_settings_new.yml
ssh oracle-host "
  sudo cp /home/ubuntu/selfhost/searxng/core-config/settings.yml \
          /home/ubuntu/selfhost/searxng/core-config/settings.yml.bak-\$(date +%Y%m%d-%H%M%S)
  sudo cp /tmp/searxng_settings_new.yml /home/ubuntu/selfhost/searxng/core-config/settings.yml
  docker restart searxng-core
"
```
⚠️ Backup SEMPRE antes. ⚠️ Limpar cache do valkey se resultados velhos persistirem:
```bash
ssh oracle-host "docker exec searxng-valkey redis-cli FLUSHDB && docker restart searxng-core"
```

## Validação ponta a ponta (obrigatória)

| Camada | Comando | Esperado |
|---|---|---|
| SearXNG default | `curl .../search?q=X&format=json` | resultados > 0, unresponsive vazio |
| Firecrawl | `curl -X POST http://firecrawl_api:3002/v1/search -H "Authorization: Bearer \$FIRECRAWL_API_KEY" -d '{"query":"X","limit":3}'` | success:true, data não-vazio, sem warning |
| Hermes web_search | chamar tool `web_search` | data.web com resultados |
| Subagente | `delegate_task` pedindo web_search | resultados reais (2-3s) |

## Common Pitfalls

1. **Achar que é bug do Hermes.** O `success:true` + `web:[]` é o Firecrawl repassando o vazio do SearXNG. Investigar o backend antes de mexer no Hermes.
2. **`keep_only` sem `disabled: false`.** Resultado: 0 engines ativas, vazio mesmo com config "certa". Verificar com dump (abaixo).
3. **Esquecer o cache do valkey.** Após 5 semanas de dados, respostas vazias antigas podem persistir. `FLUSHDB` + restart.
4. **Testar só 1 engine.** Uma engine funcionando (bing) não prova que o default funciona — o default usa a categoria inteira. Testar o default SEM param `engines`.
5. **Config default do SearXNG muda entre versões.** Engines boas/bloqueadas mudam. Rodar a bateria empírica de novo se o comportamento regredir.

## Verificação rápida de engines ativas
```bash
# dentro do container searxng (copiar scripts/searxng_dump_active.py antes)
docker exec searxng-core /usr/local/searxng/.venv/bin/python /tmp/dump_active.py
# esperado: 5 engines, disabled: False
```

## Files

- `scripts/searxng_engine_test.py` — bateria empírica: 28 engines × 5 queries × 2 rodadas, mede n/latência/erros, ranking.
- `scripts/searxng_settings_new.yml` — config validada (keep_only + disabled:false + weights).
- `scripts/searxng_dump_active.py` — imprime engines ativas do runtime (debug).

## Related

- `hermes-diagnostics` — sintomas de session reset/fallback (não confundir com este caso).
- `selfhost-service-deploy` — deploy de serviços no Oracle ARM64 (contexto dos containers firecrawl/searxng).
- `oracle-host-access` — acesso SSH ao host Oracle.
