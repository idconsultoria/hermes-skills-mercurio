# Humanizing Design Docs with agy + Skill References

> Workflow validado em 2026-07-09 humanizando 7 arquivos de design do projeto Delfos.
> Removeu 1.444 linhas de "cara de IA" de uma só vez.

## Quando usar

O usuário tem documentos de design (design system, wireframes, user flows, journey/empathy maps, HTML visual catalog) que soam como "escritos por IA" — vocabulário inflado, tom de press release, gerúndio de falsa profundidade, tabelas onde listas bastariam. A paleta de cores e tokens de design estão bons; só o texto editorial precisa de cirurgia.

## Pré-requisitos

- agy autenticado (OAuth no host, não no container)
- Acesso SSH ao host onde agy roda
- Design files acessíveis pelo usuário que roda agy

## Workflow

### 1. Preparar os arquivos no host

agy roda no **host** (Oracle VM, Ubuntu). Os arquivos de design podem estar num volume compartilhado Docker (`bind mount`) com permissões restritas. Copie para um diretório sob o `$HOME` do usuário que roda agy:

```bash
# Se os arquivos originais estão num bind mount Docker (uid 10000):
ssh oracle-host 'sudo mkdir -p /home/ubuntu/delfos-design'
ssh oracle-host 'sudo cp /path/to/originals/*.md /home/ubuntu/delfos-design/'
ssh oracle-host 'sudo cp /path/to/originals/*.html /home/ubuntu/delfos-design/'
ssh oracle-host 'sudo chown -R ubuntu:ubuntu /home/ubuntu/delfos-design/'
```

**SEMPRE `chown` para o usuário que executa agy** — agy precisa ler e escrever os arquivos in-place.

### 2. Copiar skills de referência como contexto

As skills de humanização (`humanizer`, `brand-studio-forge`, `ui-ux-design-principles`) contêm os padrões anti-IA e regras de design. Copie os SKILL.md delas para o mesmo diretório:

```bash
ssh oracle-host 'sudo cp /home/ubuntu/selfhost/hermes/data/skills/creative/humanizer/SKILL.md \
  /home/ubuntu/delfos-design/reference-humanizer.md'
ssh oracle-host 'sudo cp /home/ubuntu/selfhost/hermes/data/skills/creative/brand-studio-forge/SKILL.md \
  /home/ubuntu/delfos-design/reference-brand-studio-forge.md'
ssh oracle-host 'sudo chown ubuntu:ubuntu /home/ubuntu/delfos-design/reference-*.md'
```

Observação: o bind mount do Hermes mapeia `/opt/data` (container) → `/home/ubuntu/selfhost/hermes/data` (host). Skills vivem em `/opt/data/skills/` dentro do container. O caminho equivalente no host é `/home/ubuntu/selfhost/hermes/data/skills/`.

### 3. Construir o prompt

O prompt deve listar:

- **Arquivos para editar** — caminhos absolutos no host (ex: `/home/ubuntu/delfos-design/design-system.md`)
- **O que NÃO mudar** — CSS tokens, cores hex, variáveis :root, classes HTML, dados factuais (citações, nomes, datas, personas)
- **O que mudar** — padrões de IA específicos (vocabulário inflado, tom promocional, estrutura excessiva, gerúndio de falsa profundidade, copula avoidance)
- **Tom alvo** — direto, de quem construiu; sem jargão de marketing; primeira pessoa quando apropriado
- **Formato de saída** — editar in-place; no HTML, editar APENAS texto dentro de tags de conteúdo (`<p>`, `<h1-6>`, `<title>`, etc.), NUNCA CSS

Escreva o prompt localmente e copie via SCP:

```bash
cat > /tmp/prompt.md << 'PROMPTEND'
[... prompt completo ...]
PROMPTEND
scp -i /path/to/key /tmp/prompt.md ubuntu@host-ip:/home/ubuntu/prompt.md
```

### 4. Executar agy com --add-dir

`--add-dir` adiciona um diretório ao workspace do agy (permitindo que ele leia arquivos de lá). Múltiplos `--add-dir` são aceitos. `--dangerously-skip-permissions` evita pedidos de confirmação para cada arquivo lido/escrito.

```bash
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  /home/ubuntu/.local/bin/agy \
  --add-dir /home/ubuntu/delfos-design \
  --dangerously-skip-permissions \
  --print "$(cat /home/ubuntu/prompt.md)"'
```

**Flags explicadas:**
| Flag | Função |
|------|--------|
| `--add-dir /path` | Adiciona diretório ao workspace (agy pode ler/escrever arquivos lá) |
| `--dangerously-skip-permissions` | Auto-aprova todas as requisições de file I/O |
| `--print "prompt"` | Modo não-interativo (one-shot) — string, não pipe |

### 5. Copiar arquivos editados de volta

Após agy terminar, os arquivos em `/home/ubuntu/delfos-design/` foram editados in-place. Copie de volta ao local original:

```bash
ssh oracle-host 'sudo cp /home/ubuntu/delfos-design/design-system.md /path/to/original/'
# ... etc para cada arquivo
```

### 6. Verificar o diff

```bash
cd /path/to/repo && git diff --stat product/design/
```

Confira que os CSS tokens não foram alterados, que citações foram preservadas, e que o tom melhorou. Se agy fez mudanças estruturais demais ou de menos, ajuste o prompt e re-execute.

## Prompt patterns que funcionaram

### Preservar CSS tokens
```
## O que NÃO mudar
- Paleta de cores (naval-* gold-* state-* --surface-* --text-* etc.)
- Design tokens CSS (:root vars)
- Nomes de classes, componentes, ou estrutura HTML
```

### Focar em texto editorial no HTML
```
No HTML, edite APENAS o texto dentro de <p>, <h1-6>, <title>, 
<meta description>, <figcaption>, <li> — não mexa em classes, 
ids, ou valores CSS.
```

### Targets de vocabulário
```
- "serve como" / "representa" / "constitui" → "é"
- "valiosa", "crucial", "essencial", "fundamental" → cortar
- Gerúndio de falsa profundidade → cortar
- Tom de branding agency → conversa de quem construiu
- Primeira pessoa quando apropriado
```

## Second Pass: Remove ALL Emojis from Design Artifacts

After humanizing the editorial voice, do a **separate pass** to strip emojis from design documents and HTML prototypes. The user requires **zero emojis** in any design-system output — icons should use inline SVGs or CSS pseudo-elements, not Unicode emoji characters.

### Emoji scan

```python
import re
emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\uFE00-\uFE0F]')

for f in arquivos:
    with open(f, 'r') as fh:
        content = fh.read()
    emojis = emoji_pattern.findall(content)
    if emojis:
        print(f'{f}: {len(emojis)} total — {" ".join(sorted(set(emojis)))}')
```

### Emoji-to-text mapping table (validated in Delfos project)

| Emoji | Context | Replace with |
|-------|---------|-------------|
| ⚡ | Energy indicator, quick-action | `"Energia"` or CSS icon class |
| 🧠 | AI, brain | `"Coach"` / `"IA"` |
| 🔇 | Mute/sound-off | `"Mudo"` |
| 🔊 | Speaker/sound-on | `"Som"` / `"Audível"` |
| 🔔 | Notifications | `"Notificações"` |
| ✓ | Checkmark on cards/badges | `"Done"` / `"Feito"` (texto) |
| 🔒 | Internal/locked | `"Internal"` / `"Interno"` |
| 🤝 | Client/external | `"Client"` / `"Cliente"` |
| 📂 | Folder in sidebars/ASCII | Remove, keep project name |
| 🤖 | Bot/agent | `"Agente"` / `"Hermes"` |
| 🚀 | Rocket in copy examples | Remove |
| 😊 | Smiley in journey maps | `"Alívio"` or keep axis label |
| 👤 | Person/profile | `"[Perfil]"` |
| ⏰ | Alarm clock in wireframes | Remove emoji, keep time text |
| ⏱ | Timer in wireframes | Remove emoji, keep time text |
| ⏸ | Pause in filters | `"Em pausa"` / `"Pausado"` |

### Prompt pattern for emoji removal in design docs

Include this in the agy prompt for the emoji pass:

```
## REGRA ABSOLUTA: NÃO usar emojis em lugar nenhum.
- ⚡ → "Energia" / CSS icon
- 🧠 → "Coach"  
- 🔇/🔊 → "Mudo" / "Som"
- 🔔 → "Notificações"
- ✓ → "Done" / "Feito" (texto simples, não Unicode checkmark)
- 🔒/🤝 → "Internal" / "Client"
- 📂 → remover, manter nome do projeto
- 🤖 → "Agente"
- 🚀/😊/👤/⏰/⏱/⏸ → remover ou substituir por texto sem emoji

NÃO usar emojis substitutos. Zero. Nada de ✅❌⭐🎯🔥💡 ou qualquer outro.
```

### Handling JS-rendered content in HTML prototypes

For high-fidelity HTML prototypes where emojis appear in JavaScript template literals or DOM updates:

1. agy edits JS strings like `` `⚡ ${energy}` `` → `` `${energy}` ``
2. JS event listeners that inject emoji-spans (e.g., `<span>⚡</span>`) → remove the span entirely or keep empty span with CSS-only indicator
3. Filter chips and badges rendered by JS → update the string templates
4. After agy finishes, verify with the emoji scan script above

### Multi-file execution

Same pattern as humanization — sync files to host → agy with `--add-dir` → copy back:

```bash
# One-shot for both humanization AND emoji removal:
agy --add-dir /home/ubuntu/target-dir \
  --dangerously-skip-permissions \
  --print "$(cat /home/ubuntu/prompt.md)"
```

For large prototypes (>3K lines) with emoji in JS strings, a single agy pass can handle both humanization and emoji removal — just combine instructions in one prompt. If the prompt grows beyond ~25KB, split into two passes (humanize first, then emoji-strip).

## Pitfalls

⚠️ **`--print` recebe STRING, não pipe.** `cat prompt.md | agy --print` NÃO funciona. Use `agy --print "$(cat prompt.md)"`.

⚠️ **Prompt grande demais (>25KB) pode travar agy.** Para editar muitos arquivos de uma vez, o prompt deve ficar abaixo de ~25KB. Se precisar de mais contexto, fatie: primeiro um agy para humanizar os .md, outro para o .html.

⚠️ **Verificar permissões do diretório no host.** agy roda como o usuário SSH (ubuntu). O diretório de trabalho deve ser legível/gravável por esse usuário. Use `sudo chown -R ubuntu:ubuntu /path/to/workdir/` antes de executar.

⚠️ **HTML pode ser muito grande para uma única execução.** O arquivo `design-system.html` do Delfos tem 80KB/2035 linhas. agy conseguiu processá-lo inteiro, mas se o HTML for maior, considere editar apenas seções específicas ou usar múltiplas execuções.

⚠️ **agy pode perder contexto sobre o que NÃO mudar.** No Delfos, agy respeitou a instrução de não alterar CSS, mas verificações manuais são recomendadas. Sempre `git diff` antes de commitar.
