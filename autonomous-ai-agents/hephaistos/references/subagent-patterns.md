# Subagent Patterns — Hephaistos Pipeline v2

> Padrões concretos de invocação de subagentes via delegate_task + OpenCode + agy.

## Princípio

Hermes **não executa código diretamente** nem **faz design visual**. Ele usa `delegate_task` para invocar subagentes que, por sua vez, chamam OpenCode CLI ou agy CLI via `terminal()`.

`delegate_task` não tem ACP bridge para OpenCode/agy (não são ACP-compatible). O padrão é:
- `delegate_task(toolsets=["terminal", "file"])` → o subagente recebe terminal + file tools
- O subagente chama `terminal(command="opencode run '...'")` ou `terminal(command="agy -p '...'")`

---

## 1. Subagente de Código (OpenCode)

**Contexto:** Modo IMPLEMENTACAO, modo DEPLOY

```python
delegate_task(tasks=[{
    "goal": "Implementar feature de autenticação JWT com TDD",
    "context": (
        "Repositório em /run/media/taciobrito/ARQUIVOS/meuprojeto\n"
        "Stack: Next.js 16 + Drizzle ORM + Supabase\n"
        "A feature: login com email/senha, refresh token, middleware de proteção\n"
        "Regras: TypeScript strict, Biome formatter, Vitest tests\n"
        "Comandos: npm run test:run para testes\n"
        "Use opencode run '...' para tarefas maiores que 2-3 arquivos"
    ),
    "toolsets": ["terminal", "file"]
}])
```

O subagente internamente faz:
```bash
opencode run 'Implementar auth JWT: login, refresh, middleware, testes' \
  --model openrouter/deepseek/deepseek-v4-flash
```

**Para tarefas pequenas** (< 3 arquivos), o subagente pode usar `patch()` e `terminal(npm run test)` diretamente sem OpenCode — economia de tokens.

---

## 2. Subagente de Design/Revisão (Antigravity CLI)

**Contexto:** Modo DESIGN, modo REVISAO

```python
delegate_task(tasks=[{
    "goal": "Criar design system para landing page SaaS",
    "context": (
        "Diretório alvo: /run/media/taciobrito/ARQUIVOS/meuprojeto\n"
        "Stack: Next.js 16 + Tailwind v4 + shadcn/ui\n"
        "O projeto é um SaaS de monitoramento financeiro\n"
        "Público: PMEs brasileiras, tom sóbrio profissional\n"
        "Usar agy CLI com --add-dir apontando para o diretório do projeto\n"
        "ANTI-PADRÕES: evitar gradientes roxo-azul, Inter font, cards simétricos, sombras pesadas"
    ),
    "toolsets": ["terminal", "file", "web"]
}])
```

O subagente internamente faz:
```bash
# agy PRECISA de --add-dir senão escreve em ~/.gemini/antigravity-cli/scratch/
agy -p 'Criar design system completo...' \
  --add-dir /run/media/taciobrito/ARQUIVOS/meuprojeto \
  --dangerously-skip-permissions
```

**⚠️ Flags obrigatórias do agy:**
- `--add-dir <path>` — sem isso os arquivos somem no scratch dir
- `--dangerously-skip-permissions` — para execução autônoma (use só em projetos controlados)

---

## 3. Subagente de Pesquisa/Docs (Hermes direto)

**Contexto:** Modo INCEPTION, modo ATUALIZACAO

```python
delegate_task(tasks=[{
    "goal": "Pesquisar concorrentes e tendências para SaaS de monitoramento financeiro",
    "context": "O projeto é focado em PMEs brasileiras. Precisa de análise de mercado.",
    "toolsets": ["web", "file"]
}])
```

Este subagente usa `web_search` e `web_extract` diretamente — sem OpenCode ou agy.

---

## 4. Fluxo Completo (Exemplo: Iniciar Projeto)

```python
# 1. Hermes lê o vault do projeto
contexto = read_file("_contexto/estado-atual.md")

# 2. Hermes decide modo e delega
if modo == "INCEPTION":
    # Pesquisa de mercado + definição de escopo
    pesquisa = delegate_task(tasks=[{
        "goal": "Pesquisar mercado de [setor] e concorrentes",
        "toolsets": ["web"]
    }])
    
    # O Hermes mesmo processa o resultado e escreve PRD
    write_file("_contexto/prd.md", prd_content)

elif modo == "DESIGN":
    # Delega design visual para agy
    delegate_task(tasks=[{
        "goal": f"Criar identidade visual e design system",
        "context": f"Path: {project_path}, Stack: Next.js + shadcn/ui",
        "toolsets": ["terminal", "file"]
    }])

elif modo == "IMPLEMENTACAO":
    # Quebra em sub-tarefas paralelas
    resultados = delegate_task(tasks=[
        {
            "goal": "Implementar backend: API + banco",
            "context": project_context,
            "toolsets": ["terminal", "file"]
        },
        {
            "goal": "Implementar frontend: páginas + componentes",
            "context": project_context,
            "toolsets": ["terminal", "file"]
        }
    ])
```

---

## 5. Tabela Rápida de Comandos

| Subagente | Ferramenta | Comando interno | toolsets |
|-----------|-----------|----------------|----------|
| Código | OpenCode | `opencode run '...'` | terminal, file |
| Design | agy | `agy -p '...' --add-dir <path>` | terminal, file, web |
| Pesquisa | Hermes | `web_search()` + `web_extract()` | web, file |
| Revisão | agy + OpenCode | `agy -p 'Review...'` + `opencode run 'Review...'` | terminal, file, web |

## 6. Resolução de Problemas

### agy não encontrado
```bash
export PATH="$HOME/.local/bin:$PATH"
which agy
```

### OpenCode não encontrado no subagente
```bash
export PATH="$HOME/.opencode/bin:$PATH"
which opencode
```
Ou use caminho absoluto: `~/.opencode/bin/opencode`

### agy "Illegal instruction"
CPU sem suporte AES. Configure CPU type `host` na VM e cold boot.

### agy escreve em scratch em vez do projeto
Sempre passar `--add-dir <caminho_absoluto>`.
