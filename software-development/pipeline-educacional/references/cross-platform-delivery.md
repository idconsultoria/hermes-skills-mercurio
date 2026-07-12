# Entrega de Arquivos Entre Plataformas (TUI → Telegram, etc.)

> Aprendizado da sessão: 2026-07-10

## Problema

Na TUI (terminal), `MEDIA:/path/arquivo` não entrega arquivos em canais de mensageria (Telegram, WhatsApp, Discord). O `MEDIA:` só funciona na mesma plataforma da sessão atual.

## Solução: Cronjob One-Shot

Use `cronjob` com `deliver` explícito para a plataforma destino:

```python
cronjob(
    action='create',
    schedule='<ISO timestamp>',  # ex: '2026-07-10T22:31:00' (2 min no futuro)
    prompt='Entregue MEDIA:/path/arquivo.ext',
    deliver='telegram'  # ou 'whatsapp', 'discord', 'all'
)
```

## Detalhes importantes

- `schedule` não aceita `'now'` — use timestamp ISO futuro (~2 min)
- `deliver='telegram'` envia para o chat privado do Telegram
- O job é one-shot por padrão (executa uma vez e é removido)
- Se `execution_success: false`, verifique `last_delivery_error`
- O `MEDIA:` no prompt do cronjob é processado pelo agente que roda o job, não pela sessão atual

## Alternativas testadas (não funcionam)

- `MEDIA:` inline na resposta da TUI — não atravessa plataformas
- `hermes chat -q --deliver telegram` — flag `--deliver` não existe
- Tool `messaging` — não disponível no toolset padrão da TUI
- `hermes gateway` com API direta — complexo demais para um arquivo
