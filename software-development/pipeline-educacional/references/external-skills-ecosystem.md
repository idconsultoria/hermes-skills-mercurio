# Busca de Skills no Ecossistema Mais Amplo

> Aprendizado da sessão: 2026-07-10 — Jornada de IA ID Consultoria

## Contexto

O hub de skills do Hermes (`hermes skills search`) é enxuto. A maioria das skills públicas está em repositórios de outros agentes (Claude Code, OpenCode, Codex, Cursor), mas segue o padrão Agent Skills 1.0 — compatível com Hermes.

## Como buscar

1. **Web search por repositórios de skills:**
   - `"agent-skills" <domínio> github` (ex: `"agent-skills" education github`)
   - `"SKILL.md" <domínio> claude code` (ex: `"SKILL.md" "curriculum design"`)
   - Buscar no GitHub diretamente: `github.com search "SKILL.md" education`

2. **Plataformas de skills conhecidas:**
   - `agentskills.io` — diretório do padrão Agent Skills
   - `code.claude.com/docs/en/skills` — docs oficiais Claude Code
   - `opencode.ai/docs/rules/` — compatibilidade OpenCode
   - `cursorrules.org` — comunidade Cursor

3. **Repositórios de referência encontrados:**
   - `github.com/GarethManning/education-agent-skills` — 165 skills pedagógicas (395★)
   - `github.com/deanpeters/Product-Manager-Skills` — 47 skills de PM
   - `github.com/inbharatai/claude-skills` — 183+ skills para Claude Code

## Como instalar no Hermes

```bash
# Opção 1: git clone + cópia manual (mais confiável)
git clone --depth 1 <repo-url> /tmp/skills-temp
cp -r /tmp/skills-temp/skills/<skill-name> /opt/data/skills/<category>/<skill-name>

# Opção 2: hermes skills tap add (se suportado)
hermes skills tap add <repo-url>
```

## Filtro: nem toda skill externa é útil

- Analise o `registry.json` ou `README.md` do repositório
- Filtre apenas skills diretamente aplicáveis à tarefa atual
- Exemplo: das 165 skills do education-agent-skills, apenas 7 (4,2%) eram relevantes para produto educacional. As outras 158 eram para K-12, educação infantil, ou tutoria 1:1.
- Skills de PM (deanpeters) eram redundantes com as que já tínhamos (`product-pipeline`, `ideation-drilling`) — foram removidas após instalação.
