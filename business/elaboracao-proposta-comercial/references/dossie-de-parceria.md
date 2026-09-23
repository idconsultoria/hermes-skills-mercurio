# Dossiê de parceria (variante sem conteúdo comercial)

Pedido típico: "apresentar o que fazemos para um possível parceiro, **sem** proposta comercial — preço fica para a reunião presencial". Mesmo modelo/identidade da proposta, mas sem investimento, condições, validade ou prazos comerciais.

## Estrutura que funcionou (13 páginas, 1 slide = 1 página)
capa co-branded (logo do parceiro em box branco) · Quem somos em uma página · Por que IA, por que agora · O que fazemos na prática · Quem já confiou · Nosso método · Impacto que já entregamos · **carteira de produtos** (era o slide "Investimento — Opções", reaproveitado) · Garantia & Compromisso · O que cada lado coloca na mesa (era "Responsabilidades") · Sobre a ID · Próximos Passos · contracapa.

Números só com lastro (portfolio.md, site, KB) — nunca inventar; o bloco comercial vira frase explícita de "conversa adiada para a reunião presencial".

## Como editar o template
1. Copiar `templates/modelo_proposta.html` para o diretório de trabalho e substituir os placeholders por script (mapa completo em `references/placeholders.md`); conferir ao fim que não sobrou nenhum `{{...}}`.
2. Remover o slide "Condições Comerciais": achar `<h2>Condições Comerciais</h2>` e cortar de `rfind('<section')` até `find('</section>')`.
3. Reaproveitar o slide "Investimento — Opções" como carteira: trocar `{{OPCAO_n_NOME}}`/`{{OPCAO_n_VALOR}}` (o valor em R$ vira **nível**, ex. "Nível iniciante"), adaptar a flag "Recomendado", reescrever `<p class="ration">` e apagar o `<div class="chip">` do pacote.
4. Logo do parceiro: baixar do site deles e embutir como data URI; em slide escuro, adicionar `style="background:#fff;padding:10px 16px;border-radius:10px"` no `<img class="logo-cliente">` e remover o `<span class="logo-cliente-ph">`.

## Armadilhas (custam uma rodada cada)
- **Substituição em cascata:** a ordem importa. Ao trocar `{{CLIENTE_NOME}}` globalmente, frases como "destinada exclusivamente a {{CLIENTE_NOME}}" ficam sem artigo — corrigir as frases longas **antes** da troca global.
- **`<h3>` e `<h4>` têm SVG inline antes do texto.** Patch ancorado em `<h3>Texto</h3>` falha; ancorar em `Texto</h3>`.
- Placeholders duplicados que não casam não são erro se o slide foi removido — mas cheque a lista de "não encontradas" para separar cascata de defeito.

## Render e verificação
- Chromium local: `/opt/data/.playwright/chromium-1117/chrome-linux/chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --virtual-time-budget=30000 --no-pdf-header-footer --print-to-pdf=saida.pdf file:///caminho.html`.
- O template **não tem `@page`**: injetar antes de `</head>` → `@page { size: 1920px 1080px; margin: 0 }` + `html,body{margin:0}` (senão saem páginas Letter e o slide é cortado).
- Verificação (não há pdftoppm/pypdf na imagem): `uv venv /tmp/pdfv && uv pip install --python /tmp/pdfv/bin/python pymupdf` → contar páginas, extrair o texto de cada página (prova de que nenhuma saiu em branco) e rasterizar para conferir com `vision_analyze` (capa, slide mais denso e o de contato).
- `Page.captureScreenshot` via CDP neste host sai preto/em branco — usar a rasterização do PDF para inspeção visual.
- Conferir também que não sobrou preço/validade: `grep` por `R$`, `Investimento`, números do tarifário (cuidado com falsos positivos em coordenadas de SVG).
