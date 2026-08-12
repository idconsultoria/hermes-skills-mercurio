# Continuar a MESMA Sessão do Pi (requisito do usuário)

> Usuário exige explicitamente: "continue a mesma sessão do Pi Cost (não gere uma sessão nova)".
> Padrão validado no CFP IA (ago/2026) — auditoria em 2 passos na mesma sessão.

## Como continuar

```bash
pi --session /caminho/para/sessao.jsonl -p "$(cat prompts/pi-continuacao.md)" --provider opencode-go --model deepseek-v4-flash
```

- `pi --session <path>` usa o arquivo JSONL exato e faz **append** — NÃO cria sessão nova.
- Alternativas: `pi -c` (continua a última sessão) ou `pi -r` (menu para escolher).
- Usar `--session <path>` quando a sessão-alvo NÃO for a última (ex.: projeto com várias sessões).

## Verificação de continuidade (obrigatória)

Depois de disparar, confirmar que é a MESMA sessão antes de prosseguir:

```bash
# 1. Tamanho do JSONL cresceu (append)?
ls -la ~/.pi/agent/sessions/--<projeto>--/<timestamp>_<uuid>.jsonl

# 2. Nenhuma sessão NOVA criada na pasta?
ls -la ~/.pi/agent/sessions/--<projeto>--/ | grep jsonl
```

Se o tamanho cresceu E não há `.jsonl` novo → continuidade confirmada.

## ⚠️ Pitfall: sessão errada com `--name` parecido

Com várias sessões do mesmo projeto (ex.: `cfp-design-onboarding` vs `cfp-eng-onboarding`), é fácil
pegar o path da sessão ERRADA ao montar `--session` — o Pi então continua um contexto que não tem
o código novo (ex.: retomar a sessão de design quando o turno pede editar código de engenharia).

Sintomas: o Pi responde como se nunca tivesse visto os arquivos recentes, ou começa re-lendo o
projeto do zero.

Prevenção: ao achar a sessão-alvo, CONFIRMAR o `--name` no header do JSONL antes de disparar:

```bash
grep -l "cfp-eng-onboarding" ~/.pi/agent/sessions/--<projeto>--/*.jsonl
```

Se já disparou com a sessão errada: `process(kill)` no processo errado e relançar imediatamente
com o path certo — o custo é só o início do turno (o Pi ainda não fez trabalho útil).

## Custo da sessão acumulada

Auditar a sessão completa (v1 + v2) pelo MESMO arquivo:

```python
import json
entries = [json.loads(l) for l in open(session_path) if l.strip()]
total = {"input":0,"output":0,"cacheRead":0,"totalTokens":0}
cost = 0.0
for e in entries:
    if e.get("type")=="message" and e.get("message",{}).get("role")=="assistant":
        u = e["message"].get("usage",{})
        if u:
            for k in total: total[k] += u.get(k,0)
            cost += u.get("cost",{}).get("total",0)
print(f"{len(entries)} entries | ${cost:.4f} | {total['totalTokens']:,} tokens")
```

Observado: auditoria completa em 2 passos custa ~$0.03 (v4-flash, 94% cache hit, 2.4M tokens).
