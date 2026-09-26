---
name: brand-design-system-html
description: "Design system de marca de cliente em HTML.

Load this skill when you need to build a client's visual identity as an HTML design system — brand manual, color system, typography, and liquid glass."
version: 1.0.0
author: Mercúrio
category: business
type: Template
timestamp: 2026-09-01T12:00:00Z
tags: [html, design-system, branding, identidade-visual, marca, paleta, tipografia, liquid-glass]
trigger_phrases: ["design system", "design system oficial", "guia de identidade", "system da marca", "paleta oficial", "manual da marca", "tipografia da marca", "style guide cliente", "identidade visual do cliente", "liquid glass"]
---

# Brand Design System em HTML (identidade de marca de cliente)

Montar um design system / guia de identidade **de um cliente** (não da ID nem do Hermes)
entregue como página HTML navegável. Caso real de referência: **Biotechse** (biotech agroindustrial,
sócio Tácio) — ver `references/biotechse-brand.md` para os fatos exatos da marca.

## Quando ativar
- O usuário manda um **manual da marca** (PDF) e/ou imagem de **sistema de cores** e pede o
  "design system oficial".
- Pediu usar referências visuais de outro DS do cliente (ex.: "Aethereum do Artemis") e uma
  lib de ícones específica (ex.: **Solar Icons**).

## Fluxo
1. **Coletar fontes da marca**: manual (PDF — normalmente é *image-driven*, sem camada de texto,
   então extraia o texto (vazio) e **renderize cada página com pymupdf → PNG** e leia com
   vision_analyze página a página). Pegue também a imagem do sistema de cores e qualquer arte/branding.
2. **Extrair a paleta oficial** (hex/RGB/CMYK) direto do manual via visão. Guarde os fatos num
   `references/<cliente>-brand.md` para reaproveitar.
3. **Extrair o conteúdo de marca**: slogan, manifesto, conceito do símbolo, lockup do logo
   (wordmark + sufixo acentuado), aplicações (fundos claro/escuro, símbolo isolado), tipografia.
   ⚠️ Manuais de marca costumam ser **conceituais/aplicativos** — frequentemente NÃO têm malha de
   construção numérica nem área-de-proteção com medidas. Documente a área mínima como **regra
   operacional** (ex.: margem = altura do símbolo) e **nunca invente um grid que não existe**.
4. **Tipografia — verificar que a fonte REALMENTE carrega** (seção crítica, ver Pitfalls).
5. **Auditoria de contraste** antes de entregar (ver seção).
6. **Entregar como HTML versionado** (`<cliente>-design-system-v<N>.html`), nunca reutilizando nome.

## Tipografia — o erro clássico (fonte que "parece outra")
Quando o usuário diz "parece que entrou foi a Bricolage" / "não carrega a Tomato", o problema é:
- **Fonte licenciada não está em CDN gratuito.** Verifique SEMPRE com `curl` no CSS do CDN se o
  `@font-face` da família retornou (ex.: Fontshare/Google). Se a família não existir lá, o navegador
  **silenciosamente cai num fallback** que muda o desenho — e o usuário percebe "outra fonte".
- Fontes comerciais (ex.: **Tomato Grotesk**, The Designers Foundry / ex-Grilli Type) → **self-host**:
  declare `@font-face` apontando para `assets/fonts/<nome>-<peso>.woff2`, crie `assets/fonts/README.md`
  listando os arquivos exatos esperados, e use um **proxy gratuito rotulado** (ex.: Hanken Grotesk)
  na stack até os arquivos licenciados chegarem. **NÃO hotlink de sites de "download grátis".**
- Fontes gratuitas (ex.: **Clash Display**, Fontshare/Indian Type Foundry) → CDN ok.
- **Fonte de marca já embutida num HTML aprovado: extrair, não caçar no disco.** Quando não há
  arquivo de fonte local mas existe um HTML aprovado com `@font-face` em base64, rodar
  `scripts/extrair_fontes.py <template.html> <pasta_de_fontes>` e referenciar
  `url('./fonts/<familia>-<peso>-<estilo>.<ext>')` — o Chromium resolve relativo igual ao
  `file://` e o pacote sobrevive ao zip. Na ID o par canônico (Neulis Neue Bold + Nunito Sans 400)
  vive em `business/elaboracao-proposta-comercial/templates/modelo_proposta.html`; serve tanto
  para identidade de cliente quanto para documento da casa (POP, relatório, carta) que precise
  sair com a tipografia da ID. Preferir isso a `find` no sistema inteiro, que é lento e costuma
  não achar nada.
  **Segundo vetor de extração: qualquer HTML *já renderizado* da casa que use a tipografia da ID**
  (um painel, um relatório, uma carta exportada) carrega as fontes embutidas em base64 e serve
  de fonte canônica sem depender do Drive. O truque é o regex que pega os dois formatos:
  ```python
  re.findall(r'@font-face\s*\{[^}]*\}', html, re.S)   # não use @font-face\{ — o espaço importa
  re.search(r"url\(data:font/(otf|woff2);base64,([A-Za-z0-9+/=]+)\)", bloco)
  ```
- **Antes de declarar a tipografia resolvida, teste a COBERTURA DE GLIFOS, não o nome da família.**
  Uma fonte pode carregar o nome certo (`fc-scan` devolve `Nunito Sans 12pt ExtraLight 12pt`)
  e ainda assim faltar `ã`, `ç`, `R$`, `×` ou `·` — o que quebra exatamente o texto de marca
  (R$ na tabela de preços é o caso mais comum). Parseie `%{charset}` do `fc-query` e teste as
  letras e os símbolos que o documento realmente usa, incluindo acentuação portuguesa completa:
  ```bash
  fc-query --format "%{charset}" fonte.ttf | # expande os pares hex->caracteres
  # verifica: á à â ã é ê í ó ô õ ú ü ç Á É Í Ó Ú Ç $ 0-9 × · — º ª
  ```
  Se faltar glifo e a fonte "irmã" de mesmo desenho estiver disponível (Nunito ↔ Nunito Sans,
  Hanken Grotesk ↔ Hanken), use a irmã **declarando a diferença no relatório de entrega** — o
  usuário decide se a aproximação basta.
- Confirme **pesos oficiais**: título pode ser 400/500, e "negrito em texto" pode ser o **ExtraBold**
  da família (ex.: Tomato 800), não um bolder sintético.

## Auditoria de paginação (PDF multi-página, antes de entregar)

Relatório HTML→PDF com N páginas falha por **espaço morto**, não por estética. Meça, não julgue
pelo olho: com `pymupdf`, para cada página, some o `y1` de todos os spans e subtraia da altura
útil; o que sobra é espaço morto. Regras:

- **Alvo: menos de ~20 mm livres no rodapé de cada página.** Acima disso, a página está furada.
- **Página com >80 mm livres** = conteúdo atômico grande demais (um cartão que não cabe) sendo
  empurrado inteiro. Solva em duas frentes: permitir quebra interna do bloco
  (`page-break-inside: auto` + `page-break-after: avoid` nos títulos/dd, para não deixar órfão de
  cabeçalho) **e** reordenar seções para o bloco grande não abrir a página.
- **A tabela grande é a melhor âncora final.** Mova-a para antes das seções curtas: ela preenche
  a página inteira, evita a página órfã do fim e (bônus) é o que o leitor consulta por último.
- `thead { display: table-header-group }` + `tr { page-break-inside: avoid }` repetem o cabeçalho
  da tabela e impedem que uma linha se parta ao meio.
- Ajuste tipográfico é o último recurso, nesta ordem: padding de célula → line-height → corpo.
  Nunca encolher texto abaixo de ~8.4pt em tabela: o leitor é humano, não o medidor de margem.

## Auditoria de contraste (fazer ANTES de entregar)
Calcule **WCAG programaticamente** para cada par texto/fundo realmente usado no sistema:
- AA normal = **4.5:1**; AA grande = **3.0:1** (≥24px ou ≥18.66px bold).
- Falhas comuns em design system de marca:
  - **Cinza de apoio** (ex. `#5a5a5a`) em textos pequenos (0.72–0.86rem) sobre **glass translúcido
    colorido** — passa o número mas fica ilegível; **escureça** (ex. `#414141`) e remova `opacity`
    que reduz contraste em texto pequeno.
  - **Cor primária da marca usada como cor de texto** (ex. teal `#029190` ~3.2:1 sobre off-white)
    → para texto use o **tom escuro/derivado** da marca (teal-deep), primária só p/ ícones/elementos.
  - **Branco sobre botão na primária** (~3.8:1) → aprofunde o gradiente do botão (partida mais escura).
- Ref. (Biotechse): charcoal `#2d2d2d` sobre cream/off-white = **11–12:1** (AAA); neutros de apoio ≥8:1.

## Identidade no layout
- Incorpore **motivos orgânicos do manual** como SVG divider (linhas DNA/folha em gradiente da marca)
  e o símbolo da marca no rodapé/nav.
- Wordmark com **sufixo acentuado** (ex. "Biotech**se**" em mint) e assinatura do cliente.
- **Liquid glass** (se o cliente usa): glassmorfismo **colorido** e flutuante (gradiente teal→mint
  ~10–16%, 3 orbs de blur que flutuam, borda superior clara + brilho interno), não glass neutro opaco.

## Entrega
- Arquivo versionado `v<N>` e `assets/fonts/` junto quando houver fonte licenciada.
- **Todo link de documento num artefato entregue é verificado antes do envio, um a um.** Confirme
  por API que o ID existe, tem o nome que você citou no texto e **não está na lixeira**
  (`trashed`); documento superado que ainda aparece na busca é o erro mais comum aqui — pesquise
  pelo nome exato e escolha a versão **vigente**, não a primeira que sai. No PDF, confira que os
  links saíram clicáveis (`page.get_links()` lista os `uri` do render).
- **Texto longo em português: escrever o HTML em pedaços, nunca de uma vez.** Um `write_file` de
  25 KB de texto corrido introduz vocabulário de outro idioma no meio (verbo em espanhol no lugar
  do substantivo) sem erro de sintaxe — passa pelo `html.parser` e só aparece na leitura. Gere por
  seções com `patch`, e rode um grep de termos do idioma errado antes de renderizar; verbos
  curtos (`el`, `com`, `para`, `que`) são falso-positivo — mire nos **substantivos e adjetivos**
  da língua errada.
- Se não der para renderizar visualmente (browser sem headless / localhost bloqueado), valide por
  Python: tags balanceadas (html.parser), `@font-face` presentes, todos os hex da paleta no arquivo.

## Pitfalls
- Não assumir que o manual tem grid/área-de-proteção; se não tem, diz isso e padroniza.
- Não fabricar a tipografia da marca; confirmar pesos e nomes (verificar via CDN + usuário).
- Não entregar texto/"palavras" onde o usuário espera HTML visual — sempre página HTML.

## Browser policy — Mercúrio proot

- **Renderer local** (HTML→PDF, screenshots, Mermaid, BPMN, p5.js e decks): usar a única cópia ARM64 do Chromium em `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`.
- **Runtime Playwright:** `/opt/mercurio-data/node_modules/playwright`; cache: `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Não instalar outro Chromium/Puppeteer por perfil; não usar caches antigos ou browsers remotos.
- **Sites externos com internet:** usar a ferramenta `browser_exec` para navegação, interação, extração e verificação visual.
