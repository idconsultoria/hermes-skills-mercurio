---
name: figuras-em-documento-pdf
description: "Use ao inserir prints de app em PDF: captura e recorte."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [figura, print, screenshot, pdf, a4, recorte, qr, verificacao]
    category: productivity
    related_skills: [html-pdf-fidelity, documento-a4-marca-id, padrao-dataviz-id, revisao-entrega-cliente]
type: Orchestrator
timestamp: 2026-10-23T00:00:00Z
---

# Figuras e prints dentro de documento PDF

## Quando usar

A peça descreve um sistema que **existe** (painel, protótipo, tela de app) e você quer levar a tela para dentro do
PDF. Complementa `html-pdf-fidelity` (render) e `documento-a4-marca-id` (marca A4); aqui está o caminho da captura
até a figura fechada.

## Regras que valem sempre

- **Print é prova, não enfeite.** A figura só entra quando o texto já afirma algo e a imagem mostra aquilo acontecendo.
- **Recorte carrega contexto.** Inclua o título/cabeçalho da tela. Recorte só do miolo (uma fileira de cartões) vira
  fragmento solto: o leitor não sabe que página está vendo.
- **Prefira a tela que prova um mecanismo** (nomenclatura, fórmula, fonte do dado, regra de negócio) à tela que só
  mostra movimento. Ficha de indicador com definição + fórmula + regra + fonte vale mais que tabela de origem.
- **Legenda diz o que a figura prova**, em uma linha, numerada. Não descreva o que já se vê.
- **Dado fictício leva rótulo visível** na captura e na legenda.
- **Link de protótipo**: endereço em texto discreto **e** QR, para abrir no celular durante a conversa.
- **A borda do recorte se decide por pixel, não por visão.** Medida manda.

## Receita

1. **Servir a cópia local** do app (`python3 -m http.server <porta> --bind 127.0.0.1`, em background).
2. **Capturar em 2x** com o Chromium headless: `--force-device-scale-factor=2`, `--hide-scrollbars`,
   `--window-size=1240,<altura>`, `--screenshot=<png>`, URL com a rota por hash.
3. **Estado interativo** (modal, aba, tooltip): copiar a página para `_shot-*.html` com um clique automático em
   `window.load` + `setTimeout`, capturar com `--virtual-time-budget=6000`, apagar o temporário no fim.
4. **Conferir que a captura é a versão publicada**: MD5 de `index.html`, `app.js`, `data.js`, `styles.css` local
   contra o deploy.
5. **Recortar em um vão em branco**: `scripts/faixas_de_tinta.py <png> --de A --ate B` lista faixas com tinta e vãos;
   corte o vão, com 4–10 px de folga da última tinta.
6. **Verificar**: última linha da imagem sem tinta (limiar `<200`) e zoom 3x da faixa dos últimos 120 px lido com visão.
7. **Embutir em JPEG q≈90** em base64, largura em mm (154–168 mm ocupa a coluna; `width:100%` come a página),
   `margin:... auto`, legenda com a mesma largura.
8. **Fechar a página**: contar páginas do PDF e medir a faixa de tinta na base da última página. Se estourou, reduza a
   **largura das figuras em mm** antes de cortar texto.

Receita detalhada, com comandos e seletores: `references/captura-e-recorte.md`.

## Pitfalls

1. **Medidor de folga que anda na árvore de caixas não conta imagem.** Depois de inserir figura, o slack que o script
   imprime é falso: confirme pela contagem de páginas do PDF e pela faixa de tinta na base da página.
2. **A visão ancora no recorte que ela já viu.** Depois de mostrar um recorte com resto de card, ela afirma que o resto
   continua ali mesmo com a imagem limpa. Confirme por pixel e refaça o zoom de uma faixa isolada antes de "corrigir"
   um corte que já está certo.
3. **Resto do bloco seguinte na base é o defeito mais visível.** Corte na borda inferior do card (linha + ícones), não
   logo depois da última palavra: sobra de título ou sombra cortada ao meio salta aos olhos.
4. **Modal tem fundo escurecido**: recorte 4 px **dentro** do retângulo claro do modal; senão o PDF ganha um bloco
   preto em volta da figura.
5. **PNG 2x triplica o PDF.** Converta para JPEG na hora de embutir.
6. **Bloco de QR não use flex**: tabela de duas células (QR à esquerda, rótulo/URL/descrição à direita) renderiza igual
   em WeasyPrint e em Chromium.
7. **Não empilhe figuras grandes para "usar a página".** Duas figuras + texto + bloco de link fecham uma A4;
   três não fecham e o corte recai sobre o texto, que é o que o leitor precisa.

## Antes de entregar

- [ ] Cada figura prova uma afirmação que o texto já faz
- [ ] Recorte com título da tela, bordas limpas medidas por pixel
- [ ] Legenda numerada, curta, e dado fictício rotulado
- [ ] Largura em mm conferida; página fecha acima do rodapé
- [ ] QR apontando para o endereço certo
