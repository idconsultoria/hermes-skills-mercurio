# Mermaid → PNG transparente com mmdc + headless_shell do Hermes

Pipeline validado (CFP IA, ago/2026): renderizar blocos ` ```mermaid ```` (flowcharts) de documentos
markdown como PNG para inserção em Google Docs. Mesma classe do BPMN → imagem: diagrama em código/XML →
renderização via headless browser. Fundo **transparente** + escala **2x**.

## Requisitos

- **mmdc** (mermaid-cli) em `/opt/data/mmdc`:
  ```bash
  mkdir -p /opt/data/mmdc && cd /opt/data/mmdc && npm init -y >/dev/null 2>&1
  npm install @mermaid-js/mermaid-cli --no-audit --no-fund --ignore-scripts
  ```
  `--ignore-scripts` evita o postinstall do puppeteer (baixa Chrome x64 quebrado em ARM64 e falha sem
  `unzip` instalado no container). O executável do browser vem do puppeteer-config.
- **Browser: usar o headless_shell do próprio Hermes** — nunca instalar/remover chromium no host:
  ```
  /opt/hermes/.playwright/chromium_headless_shell-1234/chrome-linux/headless_shell
  ```
  É ARM64 nativo e funciona (Chromium 151). O chrome x64 do cache do puppeteer (`~/.cache/puppeteer/...`)
  dá `Exec format error` em ARM.
  ⚠️ **O chromium snap do oracle-host é INFRA COMPARTILHADA** (IAF PDF, outras skills/sessões) — NUNCA
  rodar `snap remove`/instalar browser no host (erro real ago/2026: `sudo snap remove chromium` quebrou
  outra sessão). Se precisar de browser no host, usar o já existente (`/snap/bin/chromium`).

## puppeteer-config.json (salvar em /opt/data/mmdc/)

```json
{
  "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
  "executablePath": "/opt/hermes/.playwright/chromium_headless_shell-1234/chrome-linux/headless_shell"
}
```

## Renderizar

```bash
cd /opt/data/mmdc
node_modules/.bin/mmdc -i input.mmd -o output.png -b transparent -s 2 -p puppeteer-config.json
```

- `-b transparent` → PNG RGBA com canal alfa (conferir pixel do canto = (0,0,0,0)).
- `-s 2` → escala 2x (~192 DPI efetivo) — texto nítido no Docs mesmo ampliado.
- Flowchart alto (784×2876 a 1x) vira ~784×5752 a 2x; dimensionar proporcionalmente ao inserir.

## Pitfalls

1. **Aspas simples dentro de labels quebram o parser mermaid.** Remover/trocar as aspas internas antes
   de renderizar. Parênteses `(Igor)` dentro de label também quebram — envolver o label em aspas duplas
   externas e limpar caracteres internos.
2. **`--puppeteerConfig` não existe como flag.** A flag é `-p <arquivo.json>`.
3. **Falta `unzip` no container** → postinstall do puppeteer falha; `--ignore-scripts` contorna.
4. **Validar mermaids após editar docs**: rodar o mmdc em cada bloco extraído (sem modificar o .md) para
   pegar sintaxe quebrada — Pi Cost fez isso automaticamente ao atualizar fluxos (ago/2026).
5. **Screenshot do chromium snap do host NÃO serve para validar visual** (AppArmor bloqueia CSS →
   ícones gigantes, sem header) — usar o browser do Hermes para julgar visual.

## Integração com md-to-gdoc (Google Docs)

O conversor `md-to-gdoc.py` (skill google-workspace) detecta blocos ` ```mermaid ```` e insere a imagem
via `insertInlineImage`: renderiza PNG transparente 2x → upload no Drive → torna público → insert com
`objectSize` dimensionado (máx ~550pt largura / ~700pt altura, proporcional). Os arquivos `.md` do repo
permanecem SOMENTE texto; a imagem só entra no espelho do Google Docs (preferência explícita do usuário
CFP IA: "os .md devem continuar contendo apenas textos").
