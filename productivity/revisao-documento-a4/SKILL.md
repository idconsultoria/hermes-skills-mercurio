---
name: revisao-documento-a4
description: "Use ao revisar documento A4 já aprovado (layout e registro)."
category: productivity
type: Orchestrator
timestamp: 2026-10-22T00:00:00Z
related_skills: [documento-a4-marca-id, html-to-pdf-chromium, html-pdf-fidelity, elaboracao-proposta-comercial]
---

# Revisar documento A4 já aprovado

## Quando usar

O usuário aprovou um documento em PDF/HTML e volta com ajustes: *"está 90% bom, mude o tom e
ajuste a capa e a tipografia, preserve as ilustrações"*. Também vale para a primeira renderização de
qualquer documento de marca em A4 montado com páginas de altura fixa.

**Não usar para:** montar o documento do zero (aí é `documento-a4-marca-id` ou
`elaboracao-proposta-comercial`) nem para trocar o motor de render (ver seção 3).

## 1. Editar o gerador, nunca o HTML final

O documento aprovado sai de um script (`build_*.py`) que monta as `<section class="page">` e inlina
fontes/SVGs. **Edite o script.** Editar o HTML final quebra a reprodutibilidade: a próxima revisão
perde o histórico e as ilustrações aprovadas viram texto solto no meio do arquivo.

- Preserve tudo o que o usuário elogiou — diagramas SVG, tabelas de referência, identidade de
  capacidade, os desenhos. Enxugue texto em volta, nunca o desenho.
- **Meça a altura, não a impressão.** A skill irmã `revisao-entrega-cliente` traz
  `scripts/medir-overflow-weasyprint.py`: percorre a árvore de caixas do WeasyPrint e reporta, página
  por página, quantos mm o conteúdo passa do topo do rodapé. É a checagem que fecha o assunto:
  contagem de páginas e inspeção visual não substituem.
- **Arquivo único.** Ao final, um só PDF e um só HTML com nome que corresponde ao título do
  documento; apague as versões anteriores do diretório para não entregar o arquivo errado.

## 2. O estouro invisível (o erro que custa a entrega)

Documento de marca usa `.page{width:210mm;height:297mm;overflow:hidden}` com rodapé em
`position:absolute`. Consequência: **texto a mais não cria página nova nem gera aviso — ele passa
por baixo do rodapé e desaparece.**

- A contagem de páginas não detecta. Um documento pode continuar com as mesmas 7 páginas e ter três
  páginas com o último parágrafo impresso sobre o rodapé.
- **Verifique a base de CADA página, como imagem — depois de medir.** `pdftoppm -png -r 100 -f N -l N`
  e inspeção visual perguntando uma coisa só: *"o texto colide com a linha do rodapé? há conteúdo
  cortado nos últimos 20%?"*. Uma chamada por página, explícita; "parece bom" em visão panorâmica já
  deixou colisão passar.
- **O medidor tem três detalhes que, errados, acusam overflow em página boa:** `.page` usa
  `box-sizing:border-box`, então `box.height` é a caixa de **conteúdo** (~260 mm num A4 com padding
  19/18 mm) e comparar com `position_y + height` acusa tudo; o limite real é o **topo da caixa
  `.foot`** (absoluta); e é preciso pular a **subárvore inteira** do rodapé — os `span` internos não
  carregam a classe e viram "último elemento" de toda página.
- **Depois de cada edição, não só no fim.** Uma frase acrescentada em página já cheia custa 10-30 mm.
  Meça, corte, meça de novo.
- **Encolher prosa é a alavanca preferida.** Mexer em padding global conserta uma página e desalinha
  as outras.
- **Orçamento de prosa por página:** ao acrescentar um bloco, conte com ~3 linhas de folga. Acima
disso, vai estourar.
- **Corte sem perder conteúdo: fundir parágrafos.** Juntar dois parágrafos elimina a margem entre
  eles (~4,5 mm ≈ 2 linhas) e mantém todas as frases. É o primeiro recurso; encurtar o parágrafo
  vizinho é o segundo; apagar texto aprovado é o último.
- **Mexeu em duas páginas, confira as duas.** O que saiu de uma pode ter estourado a anterior.

## 3. Renderizar: renderer local para arquivo local

Ladder, do mais fiel ao mais simples — confira o primeiro caminho existente e não cace binários:

```bash
ls /opt/data/.playwright/                     # Chromium compartilhado do proot, se presente
python3 -c "import weasyprint; print(weasyprint.__version__)"   # alternativa local
```

WeasyPrint 70 renderiza fielmente documento de marca A4: `@font-face` base64, flexbox, SVG inline,
tabela e rodapé absoluto. Perde gradiente, `background-clip`, chip com sombra e float.

```bash
python3 -c "from weasyprint import HTML; HTML(filename='Doc.html', base_url='.').write_pdf('Doc.pdf')"
pdfinfo Doc.pdf | grep -E 'Title|Pages'      # páginas têm que bater com o desenho
pdftoppm -png -r 100 Doc.pdf pg              # PNG por página para a inspeção da seção 2
```

**Arquivo local renderiza local.** A ferramenta `browser_exec` executa o navegador fora deste
filesystem: `file://` daqui volta `ERR_FILE_NOT_FOUND` e `127.0.0.1` volta `ERR_CONNECTION_REFUSED`.
Ela serve para site externo e para o que estiver publicado.

Confira também os metadados: `Title` do PDF precisa ser o título novo do documento, não o antigo.

## 4. Mudar o registro para proposta

Pedido frequente: *"mude o tom para proposta e declare uma intenção"*. O que muda é o registro, não
o rigor.

- **Uma intenção, declarada uma vez**, ancorada no que se sabe até ali: *diante do nosso
  entendimento até então da realidade da empresa, acreditamos que … é o projeto com maior potencial
  de retorno para …*. Repetir a mesma frase transforma convicção em refrão.
- **Ecos distribuídos, cada um com consequência nova:** o que se propõe instalar, o que se recomenda
  adotar como padrão, o que se propõe deixar de fora, como a implantação começa, o encerramento que
  retoma a abertura explicitamente. Cinco ou seis pontos, nenhum repetindo outro.
- **Postura sem adjetivo de venda:** zero superlativo solto, zero promessa numérica, zero prazo ou
  ganho afirmado sem dado. Autoridade vem da precisão.
- **Honestidade de escopo sem nota de escopo.** Se o trabalho não examinou dados do cliente, isso
  não vira aviso na capa: entra como "diante do nosso entendimento até então" e como a etapa que
  falta (linha de base antes de metas). O leitor conclui sozinho — e a nota de escopo sai, se ele
  pedir para sair.
- **Título e rótulo dizem proposta.** Título `Proposta de …`; `Modelo de …` soa material didático e
  enfraquece o posicionamento. Atualize o `<title>`, os metadados do PDF e o nome do arquivo juntos.
- **Nunca reproduza literalmente a frase-exemplo do usuário.** Quando ele escreve "algo como …",
  aquilo é direção, não redação — a tarefa é escrever melhor que o rascunho dele, mantendo a tese.
- **Não nomeie frameworks de gestão no corpo** (PDCA e afins), mesmo quando o raciocínio do documento
  é exatamente esse ciclo. Absorva na prosa: a medida vira meta, a meta vira ação, a ação vira nova
  medida. Nome próprio de método soa manual, não diagnóstico.
- **O eixo do impacto precisa estar certo.** "Medir" raramente justifica um projeto; o que justifica
  é a gestão sobre a medida — rito, meta realista e ação de área. Se a abertura promete medição, ela
  está fraca.

## 5. Ajustes visuais que o usuário pede por nome

- **Ordem das logos:** a marca da casa primeiro à esquerda, divisor, depois a do cliente. Ambas com
  peso visual equilibrado — logo pequeno ao lado de grande parece erro de montagem.
- **Equilíbrio de logos se mede, não se adivinha.** Meça a **tinta** de cada arquivo: PNG com
  `Image.open(p).convert('RGBA').split()[-1].getbbox()`; SVG rasterizando com
  `cairosvg.svg2png(bytestring=...)` e aplicando o mesmo `getbbox()`. Calcule a fração de tinta sobre
  a caixa (uma marca com 62%, outra com 91%) e **iguale a altura da tinta** — as alturas de CSS ficam
  desiguais de propósito. Se a tinta está centrada na própria caixa nos dois arquivos,
  `align-items:center` já dá centros coincidentes; não invente `translateY`.
- **Ao crescer as marcas, suba o `padding-top` da capa na mesma proporção** — logo grande colado na
  borda faz a página parecer soterrada, e o pedido seguinte do usuário será reduzir de novo.
- **Rótulo de fase** ("estudo preliminar"): quando o usuário pede para aumentar, é o overline da
  capa que muda (≈9,5 pt, caixa alta, `letter-spacing` de 2,5 px). Não confunda com o rodapé.
- Ilustrações, diagramas e tabelas aprovados ficam intocados; o pedido de "ajuste visual" nunca
autoriza refazer o desenho.

## 6. Quando o pedido é hierarquia, fórmula e vocabulário

- **Proeminência pedida ("dê destaque a estes, os outros com menos"):** duas densidades na mesma
  tabela longa — destaque (corpo maior, contraste pleno, linhas espaçadas) para os que abrem a
  leitura; apoio (corpo menor, cinza mais claro, entrelinha comprimida, cabeçalho de grupo por área)
  para os demais. Diga na prosa que a hierarquia é **de uso, não de importância**, senão parece
  depreciação do indicador secundário.
- **Fórmula:** nome do total e o sinal `=` na primeira linha, fatores na segunda. Uma linha corrida
  com o total no fim é ilegível em A4.
- **Tabela de composição:** quando o usuário pede "como cada item compõe cada linha", ponha a soma
  dentro da célula (parcelas em corpo menor, total em destaque abaixo) e escreva o parágrafo que
  explica de onde vem a oscilação. Sem esse parágrafo, a célula composta vira quebra-cabeça.
- **Vocabulário trocado se confere no PDF, não no gerador:**
  `pdftotext Doc.pdf - | grep -c '<termo antigo>'` tem de dar `0`. Renomear conceito em documento
  longo sempre deixa resíduo em título de tabela, rodapé ou texto de apoio.

## Checklist

- [ ] Ajustes feitos no gerador (`build_*.py`), não no HTML final
- [ ] Ilustrações e tabelas aprovadas preservadas
- [ ] `pdfinfo` com contagem de páginas igual ao desenho
- [ ] `scripts/medir-overflow-weasyprint.py` (na skill irmã `revisao-entrega-cliente`) rodado: nenhuma página com excesso positivo
- [ ] Base de **cada** página inspecionada como imagem, sem colisão com o rodapé
- [ ] Logos com altura de tinta igualada e centros coincidentes
- [ ] Vocabulário trocado verificado no PDF (`grep -c` = 0)
- [ ] Metadados e nome do arquivo com o título novo
- [ ] Versão anterior removida do diretório
- [ ] Intenção declarada uma vez e ecoada com consequência nova (quando o registro é proposta)
