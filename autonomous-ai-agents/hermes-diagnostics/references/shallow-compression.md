# Shallow Compression ("comprimiu muito pouco") — worked case

Caso real (2026-08-12): continuação do caso de hygiene timeout — sessão Telegram
`20260810_221657_10d46263` (projeto CFP). Depois de fixar o timeout (Step 8), o
usuário reportou: "A compressão rodou agora, mas comprimiu muito pouco. Por quê?"
Corresponde ao Step 9 da SKILL.md.

## Evidência

```
INFO gateway.run: Session hygiene: 1025 messages, ~308,557 tokens (estimated) —
    auto-compressing (threshold: 85% of 1,000,000 = 850,000 tokens)
INFO agent.conversation_compression: context compression started:
    session=... messages=1047 tokens=~323,300 model=deepseek-v4-flash focus=None
INFO agent.conversation_compression: context compression done:
    session=... messages=1047->978 rough_tokens=~306,946 awaiting_real_usage=true
INFO agent.conversation_compression: context compression attempt telemetry:
    {"commit_status":"committed","split_status":"in_place_committed",
     "chunk_count":0,"total_duration_ms":37842}
```

69 mensagens removidas, ~5% de tokens. A compactação está saudável (committed),
mas raso. Por quê:

1. **Trigger foi contagem, não tokens**: 1047 >= `hygiene_hard_message_limit: 1000`
   enquanto ~308K tokens << 850K threshold. Sem pressão de tokens → corte raso.
2. **In-place é incremental**: `in_place_committed` absorve só o trecho entre o
   marker anterior e o novo corte. A sessão já tinha 29 markers de CONTEXT
   COMPACTION e 26.007 linhas arquivadas (`active=0, compacted=1`) — head já é
   resumo-de-resumo.
3. **Cauda protegida domina**: `protect_last_n: 15` + `_ensure_last_user_message_in_tail`
   + alinhamento de tool groups; tool outputs recentes de 10-12K chars esgotam o
   tail_token_budget (~130K = 650K×0.2) e o corte cai perto do head.

## Medições úteis (token_count costuma ser NULL/0 na state.db — estimar por length)

```python
c.execute('''SELECT COUNT(*), COALESCE(SUM(COALESCE(length(content),0)
             +COALESCE(length(tool_calls),0)+COALESCE(length(reasoning),0)),0)
             FROM messages WHERE session_id=? AND active=1''', (sid,))
# bucket por posição para ver onde os tokens estão:
# head(20%) / mid / tail(20%) / last100 — se o tail é pequeno mas o mid é enorme,
# o corte por tokens vai parar cedo.

# Duplicatas (patologia de sessão recompactada demais):
c.execute('''SELECT role, content, COUNT(*) cnt FROM messages
             WHERE session_id=? AND role IN ('assistant','user')
             GROUP BY role, content HAVING cnt > 1
             ORDER BY cnt DESC LIMIT 8''', (sid,))
# aqui: assistant "" x3756, e pares idênticos como 146415==146327

# Contagem de markers de compactação já ocorridos:
c.execute("""SELECT COUNT(*) FROM messages
             WHERE session_id=? AND content LIKE '%CONTEXT COMPACTION%'""", (sid,))
# → 29: a sessão já foi compactada in-place 29x; esperar cortes rasos é o normal.
```

## Conclusão para o usuário

Numa sessão com 29 compactações acumuladas, 5% de redução É o comportamento
projetado do in-place. A resposta honesta: `/reset` (histórico fica no
session_search), não há bug nem config que faça o corte ficar profundo — o
material denso já virou resumo. Subir `hygiene_hard_message_limit` só reduz a
frequência do trigger, não aprofunda o corte.

## Config-change mechanics (deste caso)

- `patch`/`write_file` direto no `/opt/data/config.yaml` → **recusado pelo
  Hermes** ("Refusing to write to Hermes config file... use 'hermes config'
  instead"). Sempre via CLI.
- Binário `hermes` pode não estar no PATH → `/opt/hermes/bin/hermes`.
- `hermes config set compression.hygiene_timeout_seconds 120` reescreve o
  arquivo; o gateway lê config de novo a cada execução do hygiene
  (`_load_gateway_config()` com cache por mtime) → **sem restart do gateway**.
- Verificar com `grep -n <key> config.yaml` após setar.
