---
name: html-deck-to-pptx
description: "Use ao converter deck HTML em PPTX editável (1920x1080)."
category: productivity
type: ToolIntegration
timestamp: 2026-09-13T00:00:00Z
---

# Deck HTML → PPTX totalmente editável

**Quando:** o cliente aprovou um deck HTML/PDF e agora quer editar no PowerPoint (mexer em valores, texto, reordenar). **Quando não:** se ele só vai apresentar, entregue o PDF; se quer fidelidade absoluta, avise antes que a métrica de fonte do Office difere e o resultado é ~95% fiel, não pixel-perfect.

**Contrato da entrega:** todo texto em caixa de texto real (editável), tabelas nativas do PowerPoint, cartões/selos/badges como formas nativas; fundo (gradiente + orbs) e ícones SVG entram como imagem. Entregar `.pptx` + o PDF renderizado a partir do `.pptx` (é o que se audita).

## Pipeline

1. **Ferramentas (uma vez por máquina).** python-pptx; LibreOffice Impress (`soffice`) para renderizar o PPTX de volta em PDF e conferir; fontes de marca instaladas em `/root/.fonts` + `fc-cache -f` — sem elas o LibreOffice substitui a fonte e a conferência visual mente (receita de download Fontshare/Google + conferência de fidelidade em `references/fontes-de-marca-render.md`). Se `uv pip install` falhar com *failed to hardlink ... Operation not permitted*, use `UV_LINK_MODE=copy`; se depois o pacote importar como namespace (`unknown location`, sem `__init__.py`), baixe a wheel do PyPI e extraia com `zipfile.ZipFile(w).extractall('libs')`, rodando com `PYTHONPATH=$PWD/libs`.
2. **Extrair geometria** do deck no Chromium/CDP → `deck_geo.json`. Nunca deduza tamanho de fonte, cor, raio, sombra ou posição lendo o CSS: só o valor medido no navegador serve. Receita completa em `references/cdp-geometry-extraction.md`.
3. **Rasterizar** (a) o fundo de cada slide (`.bg`: gradiente + orbs desfocados) e (b) cada `<svg>` como PNG transparente. Aproximar orb de `radial-gradient` com oval sólido fica visivelmente errado.
4. **Emitir o PPTX** com python-pptx, 1 slide por `<section>` do deck. Receitas de XML/tabela/texto em `references/pptx-emitter-recipes.md`.
5. **Verificar em loop:** `soffice --headless -env:UserInstallation=file:///tmp/lo_profile --convert-to pdf` → `pdfinfo` (nº de páginas = nº de slides) → `pdftoppm -r 150 -png` → compor lado a lado **referência aprovada | conversão** (PIL) → auditar com visão, slide a slide. Nunca entregue com base em conferência pontual: os defeitos que importam (texto duplicado, selo sumido, tabela inundada, rodapé cortado) aparecem em slides específicos.

## Regras que não podem ser violadas

- **Reconstrua nativo; não converta por rota pronta.** Importar o PDF no LibreOffice/Office gera uma caixa de texto por linha e nada de estrutura — não é o que "editável" significa.
- **Um bloco de texto por "inline formatting context".** Emita texto apenas de elementos *blockish* (block/flex/grid/list-item/table/inline-block/inline-flex) que não tenham descendentes blockish, juntando os filhos inline como *runs*. Filtrar só por "elemento com texto" duplica títulos e preços: o `<span>` interno é emitido de novo.
- **`<br>` vira nova linha do parágrafo**, não some — título de capa de duas linhas vira frase colada se for ignorado.
- **`background-clip: text`** (texto com gradiente) — não emita a caixa (vira barra sólida horrorosa) e use a primeira cor do gradiente como cor do run.
- **Borda só nos lados existentes.** 4 lados → contorno; 1–3 lados → retângulo fino preenchido por lado. Contornar a caixa inteira desenha moldura falsa (típico em rodapé com `border-top`).
- **Alpha nunca se perde**, em caixas e em células de tabela: `rgba(2,145,144,.05)` vira verde sólido se o alpha for descartado, e a tabela inteira inunda de cor escura.
- **Célula herda fundo** do `<tr>` e depois do `<table>` quando o `<td>` é transparente — senão o cabeçalho perde o fundo.
- **Texto:** uma linha (h ≤ 1,75×font-size) → `word_wrap=False`, âncora MIDDLE e caixa alguns px maior; multi-linha → `word_wrap=True`, deslocar `(line-height − font-size)/2` para baixo (o CSS distribui *half-leading* em cima e embaixo; o PowerPoint joga o espaço abaixo) e dar ~12 px de folga de largura para não quebrar linha a mais.
- **Pseudo-elementos com `content` são invisíveis ao DOM.** Selo do tipo `.plan.recommended::before{content:"RECOMENDADO"}` some — meça a largura com `canvas.measureText` + `padding` e posicione com `left/top` computados + matriz de `transform`.
- **`box-shadow` → `a:outerShdw`**, senão os cartões ficam chapados ao lado da referência.
- **Ordem das formas:** fundo → caixas → selos → logos/imagens → ícones → tabelas → textos. Texto por último para ficar por cima.
- **Fontes de marca não se embutem** pelo python-pptx: mantenha os nomes reais (Clash Display / Hanken Grotesk na BiotechSe) e **entregue os arquivos das fontes junto**, avisando que sem instalá-las o Office substitui.
- **Nunca faça `str.replace('token_curto', texto_longo)` no HTML do deck.** `'X'` casa dentro de `translateX(-50%)` e corrompe a regra CSS silenciosamente (o selo sai descentralizado e sobra lixo dentro do `<style>`). Use substituição ancorada/palavra inteira e, depois, `grep` do texto injetado.
- **Tamanho final:** fundos rasterizados levam o `.pptx` a ~8 MB. É aceitável; diga isso na entrega em vez de degradar o fundo sem avisar.

## Preferências do cliente (ID / BiotechSe)

- Entrega visual conferida com screenshot + visão e contagem de páginas antes de dizer "pronto"; zero emoji e zero nota interna no material do cliente.
- Arquivo nomeado com versão (`..._v5_apresentacao.pptx`) e salvo em `/opt/mercurio-data/deliverables/`.
- Ao achar defeito no material já aprovado (typo no rodapé, selo descentralizado por CSS corrompido), corrija na fonte e avise o sócio, oferecendo regerar o PDF também — não conserte escondido nem replique o erro.
- Fale em linguagem de negócio com Maxwell/Cleverton/Tácio ("montei o PPT", "conferi slide a slide"); ferramenta e infraestrutura só com o Gustavo.

## Reuso

Os scripts desta classe ficaram em `/opt/mercurio-data/work/proposta_famosa/`: `extrair_geo.py` (HTML → JSON), `rasterizar_fundos.py`, `rasterizar_svgs.py`, `gerar_pptx.py` (JSON → PPTX). O JSON é a interface entre eles: adapte os extratores para um deck novo e reaproveite o emissor inteiro.
