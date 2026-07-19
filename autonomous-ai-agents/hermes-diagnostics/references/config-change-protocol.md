# Protocolo de Mudança de Configuração do Hermes

> Capturado em 2026-07-15 — correção do usuário: "Quem mandou você trocar o provider? Responda sem fazer mudanças"

## Regra Fundamental

**NUNCA modificar config.yaml do Hermes (provider, model, compression, fallback) sem instrução explícita do usuário.**

Não inferir passos. Se o contexto de uma conversa anterior não for encontrado, perguntar — não adivinhar.

## Gatilho

Esta regra aplica-se a qualquer operação que altere:
- `model.provider`, `model.default`, `model.aliases`
- `providers.*` (qualquer entrada)
- `fallback_providers`, `fallback_model`
- `auxiliary.compression.*`, `auxiliary.vision.*`, `auxiliary.*`
- `compression.*`
- Qualquer seção de `config.yaml` que afete o comportamento da sessão

## Fluxo Correto

1. Usuário pede mudança → confirmar o valor exato antes de aplicar
2. Contexto de sessão anterior mencionado mas não encontrado → perguntar: "Não encontrei a conversa anterior. Pode me refrescar quais eram os passos?"
3. Mudança solicitada → executar apenas o que foi pedido, não extrapolar

## Pitfall

⚠️ **Inferência é pior que perguntar.** Trocar provider sem instrução gera retrabalho e perda de confiança. Mesmo que pareça óbvio (falha do provider A → trocar para provider B), confirmar primeiro. O usuário pode ter uma razão para manter o provider atual.
