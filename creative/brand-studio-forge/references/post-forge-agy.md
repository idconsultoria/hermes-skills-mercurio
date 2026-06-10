# Pós-Forge: Materialização Visual com agy

Após gerar o identity kit (paleta, tipografia, voz, símbolo), use **agy (Gemini Flash 3.5)** para materializar os assets visuais. agy produz resultados superiores a HTML/CSS manual — é o DEFAULT para qualquer saída visual.

## Quando usar

- Após completar `forge_forge` com todos os 4 pilares (cores, fontes, voz, logo)
- Usuário pediu "apresente em HTML", "quero ver", "faça um visual"
- Precisa de logo/imagem do símbolo/mascote

## Workflow 1: HTML Presentation

Crie um prompt inline com TODOS os dados do identity kit (agy não lê arquivos).

```bash
# 1. Write the complete prompt to a file
cat > /tmp/agy-prompt.txt << 'PROMPT'
[complete brand data — all hex codes, font names with Google Fonts URLs,
 spacing values, component specs, voice examples, anti-slop checklist]
PROMPT

# 2. SCP to host
scp -F ~/.ssh/config /tmp/agy-prompt.txt oracle-host:/tmp/agy-prompt.txt

# 3. Run agy with 300s timeout
# NOTE: --print takes a STRING argument. Pipe (|) does NOT work with --print.
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --print "$(cat /tmp/agy-prompt.txt)"'

# 4. Copy result back
ssh oracle-host 'sudo cp /home/ubuntu/output.html /home/ubuntu/selfhost/hermes/data/'
```

**Regras do prompt:**
- Inclua TODOS os hex codes e nomes de fonte com URLs do Google Fonts
- Especifique ordem das seções e regras de design (anti-slop bans)
- Defina CSS custom properties com a paleta exata
- Inclua SVG inline do mascote/símbolo com descrição detalhada

**Atualizando HTML existente (preservando logos):**
Quando o HTML já foi gerado com logos embutidas como base64 e você só precisa atualizar textos:
- NÃO regenere do zero — isso perde as imagens embutidas
- Use o `patch` tool para fazer substituições nos textos
- As imagens base64 permanecem intactas

## Workflow 2: Logo / Símbolo (Image Generation)

agy pode gerar imagens PNG/JPEG do mascote.

```bash
# 1. Run agy with --dangerously-skip-permissions for file writes
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --dangerously-skip-permissions --print \
  "Generate a logo image for [brand]. 
   Symbol: [description of mascote]. 
   Pose/position: [details].
   Style: [cartoon/technical/geometric].
   Colors: [exact hex codes].
   Background: [dark/transparent]..."'

# 2. Find the generated image
ssh oracle-host 'ls -lt ~/.gemini/antigravity-cli/brain/*/*.png 2>/dev/null | head -3'

# 3. Copy to Hermes bind mount
ssh oracle-host 'sudo cp ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png \
  /home/ubuntu/selfhost/hermes/data/'
```

**Dicas para prompts de logo:**
- Seja explícido sobre a pose (perfil, sentado, andando)
- Defina o nível de detalhe técnico (engrenagens, circuitos, parafusos)
- Especifique o estilo emocional (amigável, sério, lúdico)
- Inclua cores EXATAS em hex — agy respeita paletas fornecidas

## Prompt que funcionou (Mascot Logo Example)

```
Generate a logo image for a community.

The symbol is a MECHANICAL CAPYBARA in side profile, walking calmly to the left.
Style: mix of friendly cartoon and subtle technical/engineering details,
clean vector style, professional logo quality.
The capybara should have: a small gear on the shoulder, subtle circuit board
patterns on its flank, a gentle glowing LED eye, visible screw details on the paws.
The expression should be WARM, GREGARIOUS, FRIENDLY.
Colors: petroleum blue (#006c98 primary, #0088bb for highlights),
dark navy (#010407) background, details in muted teal (#034963).
The logo should feel: Brazilian, technically competent, warm,
professional enough for a website header.
Output as a clean PNG image. Simple, memorable, scalable.
```

## Entrega dos Arquivos

```bash
# Para Telegram: usar send_message com MEDIA:path no body
# O MEDIA:path inline (na resposta do chat) NÃO funciona para este usuário.
# Sempre usar send_message(target="telegram:Gustavo (dm)", message="MEDIA:/path/file")

# Para arquivos HTML: enviar direto com MEDIA:path (Telegram aceita .html)
# Para imagens PNG/JPEG: enviar direto com MEDIA:path

# File delivery from SSH host to Hermes bind mount
# Method 1: Standard (works for most files)
ssh oracle-host 'sudo cp /home/ubuntu/<filename> /home/ubuntu/selfhost/hermes/data/'

# Method 2: Base64 pipe fallback (when bind mount has permission issues)
ssh oracle-host 'sudo cat /tmp/<filename> | base64' 2>/dev/null | base64 -d > /opt/data/<filename>
# NOTE: The file on host must exist at a readable path like /tmp/
# Pre-copy with: ssh oracle-host 'sudo cp /home/ubuntu/<file> /tmp/<file> && sudo chmod 644 /tmp/<file>'

# Method 3: Python exec (when file needs binary extraction)
execute_code("""
import subprocess
result = subprocess.run(['ssh', 'oracle-host', 'sudo cat /tmp/<filename>'],
    capture_output=True, timeout=15)
if result.returncode == 0:
    with open('/opt/data/<filename>', 'wb') as f:
        f.write(result.stdout)
""")
```

## Where agy saves generated images

When agy generates an image (PNG/JPEG), it saves to:
```
~/.gemini/antigravity-cli/brain/<uuid>/<descriptive-name>.png
```

Find recent images:
```bash
ssh oracle-host 'find ~/.gemini/antigravity-cli/brain/ -name "*.png" -mmin -5 2>/dev/null'
```

## Extracting base64 images from existing HTML

When agy embeds images as base64 data URIs in an HTML file, you can extract them later:
```python
import re, base64
with open("file.html") as f:
    html = f.read()
pattern = r'data:image/(?:png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=]{50000,})'
match = re.search(pattern, html)
if match:
    raw = base64.b64decode(match.group(1))
    with open("extracted-logo.png", "wb") as f:
        f.write(raw)
```
