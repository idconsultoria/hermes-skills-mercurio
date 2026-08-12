---
name: agy
description: "Versatile skill for coordinating Google Antigravity CLI for any design project type.

Load this skill when you need to generate any visual output via Antigravity CLI — from simple HTML reports and brand visuals to full interactive websites with Three.js, GSAP, and cinematic effects. Covers install, OAuth auth, and multiple design workflows: image generation, prototyping, parallel subagents, full site generation with iterative strategy, and HTML report generation. Always invoke agy as a background terminal process — never with timeout."
category: software-development
type: ToolIntegration
timestamp: 2026-06-21T05:11:49Z
---

# agy — Antigravity CLI (Consultor Externo)

> ⚡ **Stitch MCP:** Se esta tarefa envolver prototipagem de telas, mockups interativos ou UI design que exija ferramenta visual, ative o Stitch MCP primeiro: edite `/opt/data/config.yaml` mudando `stitch.enabled` para `true` e execute `/reload-mcp`.

> **Papel na hierarquia:** Consultor externo especialista. Usar em momentos estratégicos.
> Prompt complexo, leitura de arquivos, design/UX → agy. Tarefa simples, code task → Pi cost.
> Pouco e certeiro. Nao usar para tarefas operacionais rotineiras.
>
> Ver pi-agent-coordination para a hierarquia completa (agy > Pi best > Pi cost).

**PRIMARY design tool** — agy (Gemini Flash 3.5 via `--print` mode) é o DEFAULT para qualquer output visual. Use FIRST, não como fallback.

**⚠️ REGRA DE INVOCAÇÃO:** agy é **sempre** invocado como processo de terminal em background — `terminal(background=true, notify_on_complete=true)`. **Nunca** usar `timeout` no comando. Acompanhar progresso com `process(action='poll')` e coletar resultado com `process(action='wait')`.

## Trigger

- User asks for any visual design output — HTML pages, brand presentations, UI mockups, SVGs, prototypes
- User says "make an HTML", "create a visual", "apresente em HTML"
- User asks for charts, graphs, dashboards, or data visualization — use CSS puro (sem Chart.js, sem CDN) no HTML. Ver `data-report-prompt-pattern.md`.
- User asks for full interactive websites — with Three.js, GSAP ScrollTrigger, Web Audio API, 3D scenes, cinematic scrolling, or complex visual effects. Use iterative strategy (see Full Site Generation below).
- Tarefa complexa/estratégica que requer file I/O ou design/UX
- User asks to use agy for design tasks
- **Video layout audit** — user asks agy to review a HyperFrames HTML composition before render. See `hyperframes-video-production` skill for the workflow.
- User asks for "consulting style", "padrão McKinsey", "clean chart sem branding" — use agy with the consulting-style data visualization workflow below

For user Gustavo Mello: agy is the primary design tool. Não use HTML manual quando agy está disponível.

## Install

### On Host (Oracle VM / Ubuntu)
```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

### On Hermes Container (if needed)
```bash
# Download script first (pipe-to-bash blocked by smart approval)
curl -fsSL -o /tmp/agy-install.sh https://antigravity.google/cli/install.sh
bash /tmp/agy-install.sh
```

Installed to `~/.local/bin/agy` (version: 1.0.6, Go binary ~158MB).

Add to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Authentication (Critical — OAuth Requires Interactive TTY)

agy uses Google OAuth with PKCE. In remote/SSH environments (no browser), use tmux:

```bash
# 1. Install tmux if missing
ssh oracle-host 'sudo apt-get install -y tmux'

# 2. Create a tmux session
ssh oracle-host 'tmux new-session -d -s agy-auth \
  "env HOME=/home/ubuntu TERM=xterm-256color /home/ubuntu/.local/bin/agy"'

# 3. Wait, then select Google OAuth
sleep 3
ssh oracle-host 'tmux send-keys -t agy-auth "1" Enter'

# 4. Extract auth URL
ssh oracle-host 'tmux capture-pane -t agy-auth -p -S -30'

# 5. User visits URL, authenticates, gets a code
# 6. Send code back
ssh oracle-host 'tmux send-keys -t agy-auth "<THE_CODE>" Enter'

# 7. Verify
ssh oracle-host 'tmux capture-pane -t agy-auth -p -S -10'
```

**Important:** Each agy invocation generates a fresh PKCE `code_challenge`.

### Detecting auth state
```bash
ssh oracle-host 'echo "n" | timeout 12 env HOME=/home/ubuntu /home/ubuntu/.local/bin/agy 2>&1 | head -10'
```

## Prompt Design — Size & Base64

### Keep prompts under ~25KB

Quando o prompt (incluindo base64 do logo) ultrapassa ~25KB, agy pode travar sem produzir output por minutos — o shell argument fica pesado e o Gemini demora a responder.

**Regra prática:** o prompt final (após substituir placeholders) deve ficar abaixo de 25KB.

### Base64 logo: tamanho e formato

Use um logo **redimensionado para ~150px de largura** antes de converter para base64. Isso gera ~14KB de base64 em vez de 59KB (para um logo 400px).

```bash
# Redimensionar com Pillow antes de converter
uv run python3 -c "
from PIL import Image
img = Image.open('logo.png').convert('RGBA')
w = 150
h = int(img.size[1] * w / img.size[0])
img = img.resize((w, h), Image.LANCZOS)
img.save('logo_small.png')
"
base64 -w 0 logo_small.png > /tmp/logo_b64.txt
# Juntar com o prefixo data URI
echo -n "data:image/png;base64," > /tmp/logo_uri.txt
cat /tmp/logo_b64.txt >> /tmp/logo_uri.txt
```

**CUIDADO com prefixo duplicado:** se o template do prompt já contém `data:image/png;base64,` e o arquivo base64 também começa com esse prefixo, o resultado será `data:image/png;base64,data:image/png:base64,...`. Verifique com `grep -c "data:image" prompt.md` — deve aparecer exatamente 1 vez no contexto da data URI real.

### Monitoramento de execução

agy pode levar 2-3 minutos (ou mais para sites complexos). **Sempre executar como `terminal(background=true, notify_on_complete=true)`** — nunca com `timeout` no comando:

```bash
# Exemplo de invocação via Hermes (não executar diretamente no shell):
terminal(
  command="ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && agy --dangerously-skip-permissions --print \"$(cat /tmp/prompt.txt)\"'",
  background=true,
  notify_on_complete=true
)

# Acompanhar com poll
process(action='poll', session_id='...')
# Coletar resultado final
process(action='wait', session_id='...')
# Copiar resultado para entrega
ssh oracle-host 'sudo cp /home/ubuntu/arquivo.html /home/ubuntu/selfhost/hermes/data/'
```

## Design Workflows

### 1. Image & Visual Generation

Generate logos, banners, brand kits, illustrations using Gemini Flash 3.5's built-in image generation.

```bash
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  agy --dangerously-skip-permissions --print \
  "Generate a [logo/banner/brand-kit/image] for [subject]. \
   Style: [description]. Colors: [exact hexes]."'
```

**Image retrieval:** agy saves to `~/.gemini/antigravity-cli/brain/<uuid>/<name>.png`.
```bash
ssh oracle-host 'find ~/.gemini/antigravity-cli/brain/ -name "*.png" -mmin -5 2>/dev/null | head -3'
ssh oracle-host 'sudo cp ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png /home/ubuntu/selfhost/hermes/data/'
```

### 2. HTML Generation (brand presentations, landing pages)

Use agy's `--print` mode with Gemini Flash 3.5 for standalone HTML.

**CRITICAL: `--print` syntax.** `--print` takes a STRING argument. Piping/redirecting stdin does NOT work:
```bash
# ✅ CORRECT:
agy --print "your prompt here"
agy --print "$(cat /tmp/prompt.txt)"

# ❌ WRONG:
cat prompt.txt | agy --print
agy --print < prompt.txt
```

**Two modes — prefer Mode B when a file already exists:**

**Mode A — Generate from scratch:**
```bash
cat > /tmp/prompt.md << 'PROMPT'
[detailed prompt with ALL data, colors, specs inline]
PROMPT
scp -F ~/.ssh/config /tmp/prompt.md oracle-host:/tmp/prompt.txt
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && agy --print "$(cat /tmp/prompt.txt)"'
```

**Mode B — Edit existing file (preferred when user provides one):**
```bash
scp -F ~/.ssh/config /path/to/original.html oracle-host:/home/ubuntu/file.html
# Write focused prompt describing exact edits
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && agy --print "$(cat /tmp/prompt.txt)"'
ssh oracle-host 'sudo cp /home/ubuntu/file.html /home/ubuntu/selfhost/hermes/data/'
```

### 3. Autonomous Prototyping (/goal)
```bash
agy /goal "Build a single-page landing page for [product]"
```
Generates: `implementation_plan.md`, code output, `walkthrough.md`.

### 4. Requirements Gathering (/grill-me)
```bash
agy /grill-me "Design a dashboard UI for [purpose]"
```

### 5. Subagents (Parallel Design Work)
Three subagent types: `research` (read-only), `self` (full clone), custom.

### 6. Image Generation & File Retrieval
agy has native `GenerateImage()` — no external tools needed.

When agy generates an image, it saves to:
```
~/.gemini/antigravity-cli/brain/<uuid>/<descriptive-name>.png
```

Fallback delivery when bind mount has permission issues:
```bash
ssh oracle-host 'sudo cat ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png | base64' 2>/dev/null | \
  base64 -d > /opt/data/<filename>.png
```

### 7. Full Site Generation (Iterative Strategy)

**agy é a ferramenta primária para sites completos** — incluindo projetos com Three.js, GSAP ScrollTrigger, Web Audio API, animações 3D e múltiplas seções cinematográficas.

**Estratégia iterativa para projetos grandes (500KB+):**

```
1. GERAR ESQUELETO: agy --print com prompt descrevendo estrutura completa (seções, layout, design tokens)
   → ~50KB HTML+CSS base, executar em background sem timeout

2. GERAR SEÇÕES: agy --print para cada seção complexa individualmente
   → Cada chamada gera HTML parcial que é montado no esqueleto via script Python

3. GERAR JAVASCRIPT: agy --print para lógica complexa (Three.js, GSAP, áudio)
   → Arquivos .js separados, linkados no HTML principal

4. MONTAR: script Python que junta as peças no HTML final
   → Substitui placeholders, resolve paths, minifica se necessário
```

**Alternativa: `/goal` mode** para projetos que precisam de múltiplos arquivos com estrutura de diretórios:

```bash
agy /goal "Build a complete interactive website with [specs]. 
Output as multiple files in a directory structure."
```

O `/goal` gera: `implementation_plan.md` + estrutura de diretórios + arquivos individuais + `walkthrough.md`.

**Regra:** nunca abandone o agy por causa de tamanho. Adapte o workflow — quebre em iterações, use `/goal` para multi-arquivo, monte com script. O agy entrega altíssima qualidade visual; o trabalho de montagem compensa.

### 8. Humanizing Design Documents (de-AI-ing voice)

Use agy com `--add-dir` para passar skills de referência (`humanizer`, `brand-studio-forge`) como contexto, editando múltiplos arquivos de design in-place — removendo vocabulário inflado, tom de press release, e gerúndio de falsa profundidade sem tocar em CSS tokens ou dados factuais.

> **Reference:** See `references/humanize-design-docs.md` for the complete workflow — file sync, `--add-dir` usage, prompt patterns for preserving CSS while editing text, and verification.

## Hermes Style Guide (for agy prompts)

Default to this design system for visual outputs. **Sempre carregar o guia completo** (`/opt/data/referencias/hermes-agent/hermes-agent-style-guide.html`) como contexto no prompt do agy — não apenas os tokens resumidos abaixo. O guia HTML contém 15 componentes com previews visuais que servem como referência de layout.

```css
--blue-royal: #0000F2;
--white: #FFFFFF;
--charcoal: #171717;
--paper: #F5F5F7;
--amber: #FFBD38;
--red: #FF0000;
```

- **Giant titles:** 'Cormorant Garamond', serif (700, uppercase, -0.02em tracking)
- **Section headers:** 'Syncopate', sans-serif (uppercase, 0.08em tracking)
- **Body/Code:** 'Space Mono', monospace
- **UI labels/Badges:** 'VT323', monospace (pixel font)
- **Report structure:** Hero (blue #0000F2 bg, white text, giant serif title), Cards (white bg, blue border, chamfered corner), Tables (dashed dividers, hover rows), Footer (blue top border)
- **Components disponíveis no guia:** CRT overlay, cursor terminal, tech grid, terminal showcase, install block, botão isométrico, platform tabs, retro header, card chanfrado, status tags, tech table, scroll logs, meta list, tech footer

## Key Commands Reference

| Command | Purpose |
|---------|---------|
| `agy` | Launch interactive TUI session |
| `agy --print "prompt"` | One-shot execution |
| `agy --print "$(cat prompt.txt)"` | One-shot from file |
| `agy /goal "..."` | Autonomous hands-free build |
| `agy /grill-me` | Interactive requirements interview |
| `agy doctor` | Verify setup and auth |
| `agy -p` | Print mode (non-interactive) |
| `agy --dangerously-skip-permissions` | Skip approval prompts (file writes) |

## Auditoria de Sessões — Extração de Tokens via Protobuf

Diferente do Pi Agent (JSONL com `usage` explícito) e do Hermes (state.db SQLite), o agy armazena dados de sessão em **85+ SQLite DBs com blobs protobuf do Google Cloud Code**. É possível extrair tokens com engenharia reversa usando schemas do GitHub.

### Localização

```bash
~/.gemini/antigravity-cli/conversations/<uuid>.db   # 85+ DBs (~35 MB total)
~/.gemini/antigravity-cli/log/cli-<timestamp>.log   # Logs do language server
```

### Schemas Protobuf

Os schemas foram extraídos e estão disponíveis em:

- **`jkfujinami/antigravity-grpc-schemas`** — Schemas gRPC/Protobuf completos do Antigravity v2.0 (MIT)
- **`ag-donald/Antigravity-Database-Manager`** — Schema da trajectory no `state.vscdb`

### Hierarquia de Mensagens para Tokens

```
Trajectory (field numbers do DB são auto-increment)
  └── gen_metadata (table) = CortexStepGeneratorMetadata[]
       └── field 1 → ChatModelMetadata (oneof: chat_model)
            ├── field 3 → model (enum)
            └── field 4 → ModelUsageStats
                 ├── field 2 → input_tokens (uint64)
                 ├── field 3 → output_tokens (uint64)
                 ├── field 4 → cache_write_tokens (uint64)
                 ├── field 5 → cache_read_tokens (uint64)
                 ├── field 9 → thinking_output_tokens (uint64)
                 └── field 10 → response_output_tokens (uint64)
```

### Modelos Disponíveis (via `agy models`)

Os modelos reais são obtidos rodando `agy models` no host, não dos enums do schema proto:

| Display Name (agy models) | Modelo | Sessões típicas |
|---------------------------|--------|:---------------:|
| Gemini 3.5 Flash | gemini-3.5-flash | ~32 (rápidas, baratas) |
| Gemini 3.1 Pro | gemini-3.1-pro | ~52 (complexas, pesadas) |

O enum interno do proto (1016, 1020) **não corresponde** aos modelos 2.5 do schema público — na prática são Gemini 3.x.

### Script de Extração

Veja `references/session-audit-proto.md` para o script completo de extração de tokens de todas as 84+ sessões, geração de CSV, e mapeamento de modelos.

## Pitfalls

⚠️ **`--print` syntax non-obvious.** `--print` takes a STRING argument. Pipe/redirect do NOT work.

⚠️ **TUI requires real TTY.** Cannot pipe commands for interactive use. Always use tmux on host.

⚠️ **30s auth timeout.** agy waits 30s for user to authenticate. tmux session stays alive indefinitely.

⚠️ **PKCE one-time use.** Auth code invalidated if agy restarts.

⚠️ **Output token limit** em arquivos grandes. agy pode truncar se >75KB em uma única chamada. Para sites completos, gerar em múltiplas iterações (esqueleto → seções → JS → montagem) ou usar `/goal` mode.

⚠️ **$HOME must be set.** agy crashes without it.

⚠️ **Keyring only on host.** OAuth tokens cached on host keyring, NOT inside containers. Always run agy on host via SSH.

⚠️ **Nunca usar `timeout` com agy.** Invocar **sempre** como `terminal(background=true, notify_on_complete=true)`. O timeout pode matar o processo antes da conclusão, especialmente em sites complexos. Acompanhar com `process(action='poll')` e `process(action='wait')`.

⚠️ **Prefira editar existente a regenerar:** Editar preserva ajustes manuais.

⚠️ **No emojis em outputs visuais.** Substitua por SVGs inline (stroke, viewBox="0 0 24 24").

⚠️ **agy CAN read AND write files from the host filesystem** via its own tools (not just stdout). When told to edit existing files, agy may write changes directly to disk instead of outputting the diff to stdout — check the target files after execution rather than relying solely on captured output. Put files on host first (SCP or ensure they exist on the target path).

⚠️ **`DOMContentLoaded` timing** em slides HTML interativos. Usar padrão `readyState === 'loading'` para init.

⚠️ **Base64 images inline** inflam o HTML, mas o formato importa: usar `data:image/png;base64,...` para logos com transparência, nunca `data:image/jpeg;base64,...` (JPEG achata canal alfa em fundo branco). Usar uma única variável JS `const LOGO_URI = "data:..."`. Converter PNG para base64: `base64 -w 0 logo.png > /tmp/b64.txt`.

⚠️ **Path confusion.** Sempre usar caminho absoluto completo nos prompts.

⚠️ **First-run color scheme picker.** Cached after first use.

⚠️ **Telegram NÃO aceita .html — descartado silenciosamente pelo servidor.** Enviar .html com MEDIA: resulta em 200 OK mas o arquivo nunca chega. ZIPAR primeiro.\n\n⚠️ **Quota exhaustion — fallback estruturado.** agy compartilha quota do Google Cloud (Gemini API). Sintoma: `agy --print` retorna imediatamente sem output (exit 0, nada em stdout) ou o processo fica vivo 3-5 min com 0% CPU e depois morre sem produzir nada. Nao confunda com lentidao normal -- agy leva 2-3 min em prompts complexos MAS o stdout cresce. Se stdout estiver vazio apos 30s, e cota exaurida.

**Fallback quando agy esta sem cota (3 opcoes em ordem de preferencia):**

1. **Prompt fracionado** — Se o prompt original tem ~6KB+, tente fatiar: esqueleto (800B) + conteudo interativo (2-3KB) + complementos. Cada chamada individual tem mais chance de passar.
2. **HTML manual com os tokens visuais do agy** — Use os mesmos tokens de design (cores, tipografia, glassmorphism) para gerar HTML/CSS/JS manualmente. O agy skill documenta todos os tokens; replique o estilo sem a ferramenta.
3. **Pi best (GLM 5.2) para geracao de HTML/CSS** — `pi -p "prompt" --provider opencode-go --model glm-5.2`. Limitado: GLM 5.2 tende a entrar em loop de pensamento infinito em prompts >3KB ou com multiplos arquivos. Prefira prompts muito focados (1 arquivo, 1 secao por vez). Ver pitfalls do `pi-agent-coordination` para diagnostico de stall vs pensamento lento.

⚠️ **Prompt grande com expansão de shell pode travar o agy.** Na execução real do pipeline Sergipetec (Etapa 4), um prompt de ~6.6KB passado via `$(cat /tmp/prompt.txt)` no SSH fez o agy travar por >3 min sem produzir output — o processo ficou vivo no host (PID, RAM alocada) mas sem stdout. A solução foi fatiar: (1) gerar esqueleto HTML+CSS com prompt curto (~800 bytes), (2) editar o arquivo existente para adicionar conteúdo com segundo prompt (~4.7KB). Se um prompt full-site travar, **não insista** — mate o processo e reduza o escopo para esqueleto primeiro, conteúdo depois.

⚠️ **Chart.js CDN não renderiza em ambientes restritos.** O agy gera o HTML, mas Chart.js via CDN falha quando o usuário abre offline. Sempre especificar CSS puro no prompt. Mais seguro que depender de CDN.

⚠️ **Gráfico de pizza/donut = rejeição imediata do usuário.** Explicitamente proibir no prompt. Sempre pedir "barras horizontais".

⚠️ **Verificar diff após humanização de design docs.** agy pode editar texto editorial corretamente mas às vezes toca em CSS ou formatação estrutural. Sempre rode `git diff --stat` e uma inspeção visual nos tokens CSS após uma execução de humanização multi-arquivo.

⚠️ **Verificar CSS após edições JS multi-file.** agy pode gerar JS que referencia classes CSS, IDs de elementos DOM, ou seletores que ele mesmo não criou no CSS — por exemplo, adicionar `element.classList.add('timeline-popover')` no JS sem o correspondente `.timeline-popover {}` no CSS. O JS roda sem erro mas o componente fica invisível/sem estilo. **Após cada execução do agy que edita múltiplos arquivos:** (1) capture o stdout ou inspecione os arquivos alterados, (2) extraia classes/IDs novos do JS com `grep -oP "(?<=className|classList\.add\(['\"])[^'\"]+" js/`, (3) verifique se cada um tem estilos correspondentes no CSS. Se faltarem, injete manualmente.

⚠️ **PDF renderizado destoa do navegador? Quase sempre é FONTES.** O Chromium do host é um **snap com fontconfig ISOLADO** — não enxerga `~/.local/share/fonts` nem `/usr/share/fonts` custom. Instalar fontes no sistema NÃO resolve para o snap. Solução validada: injetar no HTML `@font-face { font-family: "X"; src: url("file:///home/ubuntu/fonts/X.ttf"); }` (o snap lê `/home/ubuntu`) com as fontes do design baixadas do Google Fonts — EB Garamond (corpo), Playfair Display (nome/drop cap), Cinzel (display), variáveis `[wght]` cobrem todos os pesos, pegue regular + itálico. Fundo/chips sem cor no PDF = falta `-webkit-print-color-adjust: exact; print-color-adjust: exact` (Chromium não imprime backgrounds sem isso). Verificar fontes reais no PDF: pymupdf `page.get_fonts()` (embutidas via @font-face aparecem como `Type3`/nome vazio; `DejaVu*` = fallback) e `get_text('dict')` → `span['font']` por trecho. Estudo completo (debug passo a passo, bugs do WeasyPrint): `references/rendering-fidelity.md`.

⚠️ **`background-clip: text` + `-webkit-text-fill-color: transparent` = Chromium render bug.** Esse padrão CSS para texto gradiente faz o texto desaparecer (torna-se invisível) após re-render de layout no Chromium — especialmente quando um elemento pai tem `display` togglado via JS (ex: `sidebar.style.display = ''` ao navegar entre rotas SPA). O bug é conhecido e não tem previsão de conserto no Chrome/Edge. **Soluções testadas (em ordem de confiabilidade):** (1) Substitua por `color: <solid>` + `text-shadow` glow — a perda do gradiente é menor que o bug de invisibilidade. (2) Use `will-change: background; transform: translateZ(0)` no elemento — funciona para casos leves mas falha em toggles repetidos. (3) Force repaint via `requestAnimationFrame()` no handler de rota — safety net, não cura a causa. **Preferir (1) sempre que o gradiente não for requisito de contrato.** Verificado em Chromium 128+.



## Data Visualization (CSS Puro — SEM Chart.js)

agy pode gerar HTML com gráficos em CSS puro para visualização de dados tabulares. **NÃO use Chart.js ou CDNs** — o ambiente pode bloquear requisições externas e os gráficos não renderizam.

For cost-comparison charts specifically, see `references/cost-comparison-chart-pattern.md` (absorbed from former `cost-comparison-chart` skill) — covers CSS-only horizontal bars, honest linear scale, mobile-first layout, storytelling structure, and color coding by model family.

### Preferências do usuário (Gustavo Mello)

- **Foco em melhorias de processos e fluxos de trabalho, não em showcase de software** (validado em sessão 18/jun/2026). Quando o conteúdo do relatório é sobre uma ferramenta, enquadre como **case de augmentação aplicado em um processo real** — a ferramenta é meio, o processo é o fim. Se o user pedir explicitamente um relatório sobre uma categoria de ferramenta, aí software-por-software vale.
- **100% PT-BR na interface.** Zero inglês em qualquer string visível ao usuário — botões, labels, placeholders, badges, tooltips, empty states, mensagens de erro, nomes de dias/meses. Campos de status/prioridade/tipo vindos do backend em inglês devem ser traduzidos via mapa (Utils.translate() ou equivalente). Revisão manual após cada geração de UI.
- **SEM Chart.js, SEM CDN** — gráficos em CSS puro (divs com width percentual, `@keyframes slideIn`)
- **SEM pizza/donut/rosca** — só barras horizontais
- **Texto CONCISO** — descrições de uma frase no máximo
- **Relações de dados explícitas** — se X alimenta Y, mostre a conexão
- **Fontes do sistema** (Georgia, Courier New, system-ui) se Google Fonts falhar
- **Tabela de apoio abaixo de CADA gráfico** com dados completos

### Workflow

```bash
# 1. Escrever prompt com dados inline e especificações de design
cat > /tmp/chart-prompt.md << 'PROMPT'
Gere um HTML autônomo com gráficos em CSS puro (SEM Chart.js, SEM CDN).

## Dados
| Categoria | Metrica A | Metrica B | Metrica C |
|---|---|---|---|
| Item 1 | 10.5 | 20.3 | 30.1 |
| Item 2 | 15.2 | 25.1 | 35.0 |

## Estilo
- Design system Hermes Agent (ver tokens no guia)
- Barras horizontais (divs com width percentual, @keyframes slideIn)
- SEM Chart.js, SEM CDN, SEM Google Fonts
- Tabela de apoio abaixo de cada gráfico
- Texto conciso (descrições de 1 frase)

## Layout
1. Hero + Título
2. Gráficos CSS + tabelas de apoio
3. Footer
PROMPT

# 2. Enviar e executar
scp -F ~/.ssh/config /tmp/chart-prompt.md oracle-host:/tmp/chart-prompt.md
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  agy --dangerously-skip-permissions --print "$(cat /tmp/chart-prompt.md)"'

# 3. Copiar resultado
ssh oracle-host 'sudo cp /home/ubuntu/arquivo.html /home/ubuntu/selfhost/hermes/data/'
```

### Estilo Consultoria (Alto Nível, Sem Branding)

Quando o usuário pedir "padrão consultoria" ou "estilo McKinsey/BCG":

- **Fundo:** off-white suave (#F8F9FA), NUNCA escuro
- **Card:** branco (#FFFFFF) com sombra quase imperceptível (`0 4px 24px rgba(0,0,0,0.03)`)
- **Cores:** sóbrias e profissionais — verde escuro, azul acinzentado, âmbar
- **Tipografia:** Inter (corpo, títulos finos), Space Mono (dados)
- **Grid:** linhas quase invisíveis (#E8ECF0), sem bordas chamativas
- **Nada decorativo:** sem gradientes, sem ícones decorativos, sem logotipos, sem badges coloridos
- **Tooltip:** fundo branco, borda sutil, padding generoso
- **Nada de Chart.js em escala logarítmica:** Chart.js v4 tem bug com `type: 'logarithmic'` + `indexAxis: 'y'` — as barras não renderizam. Usar escala linear OU CSS puro (divs com width percentual). **CSS puro é o padrão preferido** — sem dependência de CDN.
- **Dados:** exatos nos labels das barras, tabela de apoio sempre presente
- **Proporção:** espaçamento amplo, ar arejado

### Tipos de Gráfico por Contexto

| Tipo | Quando usar | Notas |
|------|-------------|-------|
| Barras horizontais | **PADRÃO** — rankings, comparativos, distribuição de custos | Ordem decrescente, label à esquerda, valor à direita |
| Barras agrupadas | Comparar categorias com múltiplas métricas (ex: hit/miss/output) | 3-4 barras por grupo |
| Barras empilhadas | Mostrar proporção/composição | Melhor para percentuais que somam 100% |
| Linha | Séries temporais | Raro em relatórios de consumo |

**⚠️ NUNCA use pizza/donut/rosca — rejeitado pelo usuário.**

### Relatório Multi-Sessão (Padrão Data-Report)

Para relatórios completos de consultoria com **múltiplas tabelas + gráficos + análise textual** (ex: análise de custos, KPI mensais, comparativos), use o padrão documentado em `references/data-report-prompt-pattern.md`.

**Essência do padrão:**
1. Estruture você mesmo os dados crus do usuário em markdown limpo
2. Pré-calcule todas as análises e percentuais (agy não é bom em contas)
3. Embeba os tokens de design system completos no prompt
4. Especifique exatamente a ordem e conteúdo de cada seção
5. Envie como prompt único autossuficiente via SCP → agy --print

## Verification
```bash
agy --version        # → 1.0.5+
agy doctor           # → "All checks passed" (requires auth)
```

## Histórico de Atualizações

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-07-09 | Hermes (Delfos F4) | Adicionado workflow 8 (Humanizing Design Docs) com `--add-dir` para passar skills como contexto. Referência `humanize-design-docs.md` com padrões de prompt, file sync, e verificação pós-edição. |
| 2026-07-10 | Hermes (Delfos F4b hotfix) | Adicionado pitfall de verificação CSS após edições JS multi-file. Adicionado user preference "100% PT-BR na interface" — zero inglês visível. Atualizada descrição de file I/O (agy lê E escreve). |
