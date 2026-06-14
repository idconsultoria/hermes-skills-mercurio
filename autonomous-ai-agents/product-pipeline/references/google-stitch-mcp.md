# Google Stitch MCP — Official HTTP Setup

> **Skill:** product-pipeline — F4a (Design)
> **Data:** 14 Jun 2026
> **Tipo:** HTTP MCP direto (oficial) com API key via header

---

## Visão Geral

Google Stitch expõe um servidor MCP HTTP oficial em `https://stitch.googleapis.com/mcp`. A autenticação é feita via **API key** enviada como header HTTP `X-Goog-Api-Key`.

---

## Configuração no Hermes

Formato oficial (stitch.withgoogle.com/docs/mcp):

```yaml
mcp_servers:
  stitch:
    url: https://stitch.googleapis.com/mcp
    headers:
      X-Goog-Api-Key: "AQ.sua-chave-aqui"
    transport: http
```

**Onde colocar:**
- Principal: `/opt/data/config.yaml`
- User override: `/opt/data/.hermes/config.yaml`

---

## Como usar

Após `/reload-mcp`, as tools do Stitch ficam disponíveis:

- `create_project` / `list_projects` / `get_project`
- `generate_screen_from_text` — gerar tela por prompt
- `get_screen` / `list_screens`
- `edit_screens` / `generate_variants`
- `create_design_system` / `list_design_systems` / `apply_design_system`
- `build_site` — site HTML a partir de telas
- `get_screen_code` / `get_screen_image`

### Fluxo típico

1. `create_project(title="Delfos")` → `projectId`
2. `generate_screen_from_text(projectId, prompt, "DESKTOP")` para cada view
3. `get_screen(projectId, screenId)` → screenshot + HTML URLs

---

## API Key: funciona SIM (quando usada corretamente)

| Método | Funciona? |
|--------|-----------|
| HTTP MCP com `X-Goog-Api-Key` header | ✅ tools/list, initialize, tools/call |
| `@_davideast/stitch-mcp` `tool` subcommand | ❌ (usa OAuth2, ignora API key) |
| `@google/stitch-sdk` `StitchToolClient` | ❌ (usa MCP transport, rejeita key) |

---\n\n## Dicas\n\n- Seja específico no prompt: cores Navy/Teal/Gold, glassmorphism, dark mode\n- Mobile UIs têm qualidade superior que Desktop\n- Screenshots: adicionar `=s0` à URL para resolução máxima\n- Para consistência, gere a primeira tela e re-use o designSystem retornado\n\n### Fluxo de geração de telas\n\n1. **Verificar/atualizar o design system ANTES** de gerar telas — o projeto Stitch pode existir com parâmetros errados (ex: LIGHT mode em vez de DARK, fonte errada)\n2. **Aplicar design system** via `update_design_system` ou `create_design_system` com os tokens corretos\n3. **Gerar mobile primeiro** (`deviceType=MOBILE`), depois desktop (`deviceType=DESKTOP`)\n4. **Download full-res**: pegar a URL do `screenshot.downloadUrl` e adicionar `=s0` no final\n5. **Salvar em `/opt/data/delfos-screens/`** com nomes descritivos\n6. **Enviar via MEDIA** no Telegram para o usuário\n7. **Após Stitch screens finalizadas**, chamar agy para gerar protótipo HTML de alta fidelidade\n\n### Design system — fontes compatíveis com UpdateDesignSystem\n\nO Stitch suporta fontes na criação, mas **UpdateDesignSystem aceita apenas um subconjunto**. Fontes testadas:\n\n| Fonte | CreateDesignSystem | UpdateDesignSystem |\n|-------|:-:|:-:|\n| `BRICOLAGE_GROTESQUE` | ✅ (silenciosamente dropada) | ❌ (invalid argument) |\n| `SPACE_GROTESK` | ✅ | ✅ |\n| `NUNITO_SANS` | ✅ | ✅ |\n| `MANROPE` | ✅ | ✅ |\n| `INTER` | ✅ | ✅ |\n| `PUBLIC_SANS` | ✅ | ✅ |\n\n**Workaround:** Usar `SPACE_GROTESK` como alternativa ao `BRICOLAGE_GROTESQUE` — mesma família grotesca, suportada pelo UpdateDesignSystem.\n\n---\n\n## Pitfalls

⚠️ **Config no `.hermes/config.yaml`** — Sobrescreve a config principal.

⚠️ **tools/list funciona, tools/call falha** → você está usando o transport errado (stdio proxy em vez de HTTP direto). Configure como `url:` + `headers:` + `transport: http`.

⚠️ **`@_davideast/stitch-mcp`** é um pacote comunidade que tem seu próprio `tool` subcomando. Esse subcomando NÃO funciona com API key. Use apenas a config HTTP MCP direta no Hermes.

---

## Referências

- Config oficial: `{"mcpServers": {"stitch": {"url": "https://stitch.googleapis.com/mcp", "headers": {"X-Goog-Api-Key": "..."}}}}`
- stitch.withgoogle.com/docs/mcp
