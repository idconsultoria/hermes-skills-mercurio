# Pi Agent — Anatomia Interna do Harness (v0.78.1)

> Fonte: dissecação do código-fonte em 12/08/2026 (relatório "Funcionamento Interno").
> Pacote: `@earendil-works/pi-coding-agent` (pi.dev). Bin `pi` → `dist/cli.js`.
> Código instalado: `/opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent/dist/`
> Usar quando o usuário perguntar "como o Pi funciona por dentro" (tools, plugins, prompts base) ou ao estender/depurar o comportamento interno.

## Filosofia do upstream

- "Minimal terminal coding harness. Adapt pi to your workflows, not the other way around."
- **Deliberadamente SEM subagents e SEM plan mode** — a orquestração é externa (Hermes). Não tente fazer o Pi "planejar sozinho"; a product-pipeline já compensa.
- 4 modos: `interactive` (TUI), `print/json` (`-p`), `rpc` (integração de processo), `sdk` (embed).
- `DEFAULT_THINKING_LEVEL = "medium"` (constante em `dist/core/defaults.js`).

## Tools built-in (`dist/core/tools/`)

Default ativo: `read`, `bash`, `edit`, `write`. `grep`, `find`, `ls` existem mas só entram se selecionadas. `edit-diff` é módulo auxiliar do edit.

Cada tool registra `promptSnippet` (1 linha) + `promptGuidelines` (regras). Só tools com snippet aparecem em "Available tools" no system prompt.

| Tool | Snippet | Comportamentos-chave |
|------|---------|----------------------|
| `read` | "Read file contents" | Texto + imagens (jpg/png/gif/webp, auto-resize, enviadas como attachment); truncate 2000 linhas / 100 KB com `offset/limit` para continuar; compact read para SKILL.md/AGENTS.md/docs do pi; avisa quando o modelo não suporta imagem |
| `bash` | "Execute bash commands" | spawn via shell config, sem timeout default, `killProcessTree` em abort, output accumulator |
| `edit` | "Make precise file edits..." | multi-edits atômicos numa chamada (`edits[].oldText` exact match) |
| `write` | "Create or overwrite files" | só create/overwrite completo, nunca partial edit |
| `grep` | "Search file contents..." | respeita .gitignore |
| `find` | "Find files by glob..." | respeita .gitignore |
| `ls` | "List directory contents" | lista com limit |

Flags: `--no-tools` zera o registry; `--tools`/`--exclude-tools` filtram por nome. A pipeline nunca usa esses flags — roda default.

## System prompt (`dist/core/system-prompt.js` — `buildSystemPrompt`)

Estrutura do template default:

```
You are an expert coding assistant operating inside pi, a coding agent harness...
Available tools: [snippets de 1 linha]
In addition to the tools above, you may have access to other custom tools...
Guidelines: [dedup Set; sempre inclui "Be concise" e "Show file paths clearly"]
Pi documentation (read only when the user asks about pi itself...): [README/docs/examples]
[se appendSystemPrompt: texto extra]
[se contextFiles: <project_context> com AGENTS.md/CLAUDE.md]
[se skills && read disponível: <available_skills>]
Current date: ...
Current working directory: ...
```

Precedência de extensão:
1. `--system-prompt` / `SYSTEM.md` → **substitui** o prompt default inteiro. Discovery: `.pi/SYSTEM.md` (projeto) → `~/.pi/agent/SYSTEM.md` (global).
2. `--append-system-prompt` / `APPEND_SYSTEM.md` → **adiciona** antes do bloco final (data/cwd). Mesmo discovery.
3. Context files: `AGENTS.md`/`CLAUDE.md` no agentDir + subindo do cwd até a raiz → `<project_instructions path="...">` dentro de `<project_context>`.
4. Skills → catálogo `<available_skills>` (só se read disponível).
5. Prompt templates → `~/.pi/agent/prompts/` + `.pi/prompts/`.
6. Themes → `~/.pi/agent/themes/` + `.pi/themes/` (só visual do TUI, não afeta o LLM).

## Skills (`dist/core/skills.js`)

- `formatSkillsForPrompt()`: injeta `<available_skills>` com `name`/`description`/`location` (path absoluto do SKILL.md). Instrução ao modelo: "Use the read tool to load a skill's file when the task matches its description."
- Skills com `disableModelInvocation: true` ficam fora do catálogo.
- Discovery: diretório com `SKILL.md` é raiz de skill (não recursa); SKILL.md solto também conta; frontmatter `name`/`description` validados.
- **Frontmatter rico ajuda a seleção**: as 21 skills da raiz têm só name/description; as 19 do pm-skills têm `intent`, `best_for`, `scenarios`, `estimated_time`. Se o modelo escolhe skill errada, enriquecer o frontmatter antes de mexer no prompt.

## Extensões

- Instalação atual: **0 extensões** (`pi list` → "No packages installed"). 100% stock.
- Extensão pode registrar: tools custom, slash commands, flags CLI, interceptação de `user_bash` (wrappear/reescrever comandos).
- Carga: `--extension <path>` | `~/.pi/agent/extensions/` | `.pi/extensions/` | `pi install <source>` (npm/git).
- `detectExtensionConflicts()`: tool/flag com mesmo nome viram diagnostics; precedência por ordem de carga.
- Extensão pode declarar `skillPaths`/`promptPaths`/`themePaths` — recursos adicionais.
- Sem plan mode/subagents por design — só dá para adicionar escrevendo extensão TypeScript.

## Settings (`dist/core/settings-manager.js`)

- Dois arquivos: global `~/.pi/agent/settings.json` + projeto `.pi/settings.json` (no cwd). **Deep merge — projeto vence campo a campo.**
- Campos suportados: `defaultModel`, `theme`, `quietStartup`, `skills` (custom dirs), `themes`, `thinkingBudgets`, `httpIdleTimeoutMs`.
- **Estado atual da instalação**: settings.json = 39 bytes, só `lastChangelogVersion` → tudo default. `defaultModel` NÃO setado → invocação sem flags cai no primeiro provider com chave (deepseek v4-pro = tier caro). Mitigação: sempre `--provider` + `--model` explícitos (wrapper `pi-cost` já fixa o Zen free).
- Fix rápido do risco: `{"defaultModel": "deepseek/deepseek-v4-flash"}` no settings.json global.

## Auth (`~/.pi/agent/auth.json`)

- 4 providers, todos `type: "api_key"`: openrouter, deepseek, opencode, opencode-go.
- **opencode e opencode-go usam a MESMA chave** — dois endpoints do mesmo serviço (Zen free vs Go com cota 5h/mês). Por isso cota Go e rate-limit Zen são contabilizados na mesma conta e o fallback entre eles é transparente.

## Sessões

- JSONL em `~/.pi/agent/sessions/--<path-normalizado>--/*.jsonl`.
- Eventos `model_change` registram provider/model — base da auditoria `pi-session-audit`.
- `--session` = append no MESMO arquivo (nunca novo); `-c` continua a última; `-r` seletor interativo; `--fork` cria nova a partir de outra; `--export <file>` gera HTML legível.
- Compaction: `dist/core/compaction/` com branch-summarization.

## Inspeção rápida

```bash
/opt/data/pi-global/bin/pi --help        # flags completas (--system-prompt, --append-system-prompt, --no-extensions, --skill, --prompt-template, --theme, --export...)
/opt/data/pi-global/bin/pi list          # extensões instaladas
# Comportamento exato: ler dist/core/{system-prompt,resource-loader,settings-manager,skills}.js e dist/core/tools/*.js
```

## Estado da instalação (12/08/2026) — checklist

- SYSTEM.md / APPEND_SYSTEM.md: ausentes → prompt 100% stock
- AGENTS.md no agentDir: ausente (só os dos projetos; pm-skills tem o próprio)
- Prompt templates / themes: ausentes
- Extensões: 0
- `bin/fd` (3,5 MB) em ~/.pi/agent/bin/: helper não documentado, não referenciado — verificar antes de confiar
