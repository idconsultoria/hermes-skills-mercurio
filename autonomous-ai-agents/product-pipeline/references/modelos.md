# Modelos do Pi — estado atual e histórico

## Hoje (out/2026)

| Papel | Provider | Model ID | Rótulo | Contexto |
|---|---|---|---|---|
| Pi best | `opencode-go` | `deepseek-flash` | DeepSeek V4.1 Flash | 200k, max output 32k |
| Pi cost | `opencode-go` | `deepseek-flash` | DeepSeek V4.1 Flash | idem |

**Os dois papéis usam o mesmo modelo.** "Best" e "cost" são papéis — contexto, tamanho de lote
e tipo de tarefa — não degraus de potência. Não existe escalada de modelo dentro de casa: se o
Pi errou, o conserto é contexto melhor (ler os arquivos certos) ou a revisão do agy.

## Invocação

```bash
source ~/.config/pi/opencode.env      # OPENCODE_GO_API_KEY
pi --provider opencode-go --model deepseek-flash -p "<prompt>"
```

Sem o `source`, a resposta é `401 Upstream request failed: Invalid credential` — a chave em
`~/.pi/agent/auth.json` **não** é usada para este provider no Pi 0.73.1. Verificado em 23/10/2026.

## Como conferir o que existe na máquina

```bash
python3 - <<'PY'
import json, os
d = json.load(open(os.path.expanduser('~/.pi/agent/models.json')))
for prov, cfg in d['providers'].items():
    print(prov, cfg.get('baseUrl'), [m['id'] for m in cfg.get('models', [])])
PY
```

Essa lista é a verdade do nó. Skill que cita modelo fora dela está mentindo.

## Quirk do reasoning

O V4.1 Flash raciocina antes de responder. Com `max_tokens` baixo (256) a resposta volta
**vazia** (`content: ""`), porque o orçamento inteiro foi para `reasoning_content`.
Sintoma no usage: `completion_tokens_details.reasoning_tokens ≈ max_tokens` com content vazio.
**Regra: `max_tokens ≥ 1024`** em chamada direta de API. Custo: ~380 tokens de raciocínio +
~130 de resposta por chamada, latência ~12s.

## Histórico (para não repetir a pesquisa)

| Época | Configuração | Por que saiu |
|---|---|---|
| até jul/2026 | `deepseek` API direta (v4-pro / v4-flash) | custo por token; sem cota fixa |
| ago/2026 | `opencode` Zen free (`opencode/deepseek-v4-flash-free`) | free tier restrito, rate-limit agressivo |
| ago/2026 | `opencode-go` v4-pro (best) + v4-flash (cost) | escada de custo; hoje unificada |
| out/2026 | `opencode-go` / `deepseek-flash` nos dois papéis | ordem do dono; provider com um único modelo |

Provedores mortos ou inacessíveis neste ambiente: `opencode` free tier (`403 can only be used
from within OpenCode`), `opencode-go` com header `x-opencode-session`, MiniMax M3 free.

## Quando trocar

Trocar modelo é decisão do dono, não do operador. Ao trocar:

1. Confirmar o model id real em `~/.pi/agent/models.json` (não no nome comercial).
2. Rodar o teste de vida: `pi --provider <p> --model <m> -p "responda apenas OK"`.
3. Atualizar esta tabela, o pré-voo da `product-pipeline` e a skill `pi-agent-coordination`.
4. Propagar para todas as cópias (ver §7 da proposta de reestruturação / script de sync).
