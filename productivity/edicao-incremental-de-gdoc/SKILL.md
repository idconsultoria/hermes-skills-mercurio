---
name: edicao-incremental-de-gdoc
description: "Use when editar/versionar um Google Doc existente."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [google-docs, drive, edicao, versao, replaceAllText, documento-institucional]
    related_skills: [google-workspace, google-docs-formatting, elaboracao-proposta-comercial]
    scopes: [id]
type: Orchestrator
timestamp: 2026-09-30T06:00:00Z
---

# Editar e versionar um Google Doc existente sem danificar

Vale para qualquer documento que **já vive no Drive** e é revisado por outra pessoa: propostas, anexos,
minutas, relatórios, atas. O documento pode ter capa desenhada, cabeçalho/rodapé institucional, campos de
numeração e edições feitas pelo cliente — reconstruir apaga tudo isso, e uma reconstrução interrompida
deixa o documento vazio.

## Regra de ouro

**Substitua texto; não reconstrua.** `replaceAllText` troca só a cadeia pedida: estrutura, estilos,
imagens, rodapé e link ficam intactos. Reconstruir (delete + reinserção) é o último recurso, e só em
cópia nova.

## Procedimento de edição

1. **Leia o texto ATUAL do Doc** e extraia dele as cadeias exatas a substituir. Nunca use o rascunho local
   como fonte: o cliente edita o documento em paralelo.
2. Monte os pares `antes → depois` e **confirme que cada `antes` existe** antes de enviar — um par que não
   casa é erro de leitura, não um no-op inofensivo.
3. Aplique em lote (`replaceAllText` com `containsText.matchCase: true`, ~20 requisições por chamada) e
   confira `occurrencesChanged` de cada requisição.
4. **Para acrescentar** conteúdo, reescreva uma frase existente em vez de inserir parágrafo novo: sem
   deslocamento de índice e nada a recalcular. O texto novo **herda o estilo do trecho casado**, então
   nunca inclua marcadores de markdown no `replaceText`.
5. **Confirme a integridade depois**: contagem de linhas e de tabelas idêntica à de antes, páginas dentro
   do teto pedido e conferência visual (screenshot + visão) das páginas alteradas.

Detalhe de valor repetido em vários lugares (preço, prazo, número de ciclos): troque em TODOS os pontos
— resumo, tabelas, composição, fecho — e confira por busca. Uma sobra vira contradição dentro do mesmo
documento, e é o tipo de erro que o cliente encontra antes de você.

## Versão nova no mesmo padrão visual da anterior

1. `drive.files().copy(fileId=MODELO, body={"name": ..., "parents": [PASTA]})` — a cópia carrega capa
   desenhada (inclusive o objeto gráfico que a API reporta como elemento não suportado), cabeçalho,
   rodapé e estilos nomeados. Criar do zero perde tudo.
2. Leia o **DNA do modelo** em vez de supor: `documentStyle` (pageSize A4 = 595×842pt, margens),
   `namedStyles` (fonte/tamanho/cor por estilo nomeado), runs dos primeiros elementos (a capa costuma ter
   fonte própria, ex. Montserrat 10/28pt em branco e verde sobre bloco navy), `tableCellStyle`
   (`backgroundColor`, `padding*`) e `inlineObjects` (tamanho do logo).
3. `pdffonts` no PDF exportado confirma quem é o corpo e quem é a capa — é a evidência mais rápida.
4. Ao reaplicar tipografia, **restrinja por índice**: o fim da capa é o `sectionBreak` seguinte ao
   primeiro elemento; estilize só `startIndex >= capa_fim`. Passar estilo no documento inteiro reescreve os
   runs da capa e mata o visual dela.

## Preferências do principal (valem sempre)

- Pedido de versão nova significa **mesma aparência da anterior** (capa, fontes, tamanhos, tabelas) — não
  um documento novo com as mesmas palavras.
- **Alterações pontuais**: "não mexa no que já está correto". Ajustar valor ou frase não justifica
  reconstruir nada.
- Se ele está editando o Doc em paralelo, **o texto vem do Doc vivo**.
- **Quando a automação for arriscada, entregue a lista de edição** (onde → de → para, por seção/tabela) em
  vez de executar. Depois de uma automação ter mexido no que não devia, ele prefere editar à mão com o
  roteiro na frente.
- Antes de mexer, **diga o método** em uma frase ("só substituição de texto; nada é apagado ou
  reconstruído"). A pergunta "dá para fazer sem danificar?" é sobre confiança, não sobre técnica.

## Pitfalls

- **Usar o conversor md-to-gdoc com `--doc-id` para atualizar um doc existente.** Ele apaga todo o corpo
  (`deleteContentRange [1, end-1]`) e a capa vai junto; e re-rodar sobre doc já mexido falha com
  `deleteParagraphBullets: Index N must be less than the end index of the referenced segment` — porque o
  índice de inserção é rastreado localmente e passa do fim quando o corpo é curto. Como o delete roda
  antes da reinserção, a execução que falha deixa o documento sem conteúdo. Use o conversor só em doc novo
  ou cópia recém-feita, em uma passada só.
- **Passar estilo no documento inteiro.** Reescreve os runs da capa (título de 28pt vira corpo de 11pt) e o
  documento perde a identidade — restrinja por índice, sempre.
- **Extrair Doc → markdown sem mesclar runs de negrito adjacentes.** Dois runs em negrito em sequência
  viram `****` no meio do texto e quebram o markdown.
- **Confiar na contagem de páginas do seu render.** O Google Docs pagina diferente do HTML/PDF local: meça
  exportando o Doc para PDF e conte `pdfinfo`, não presuma.
- **Prometer campo de numeração no rodapé.** Não existe `insertPageNumber` na API (só `insertPageBreak`):
  "Página X de Y" só sai de doc-modelo que já traga o campo ou de dois cliques no Docs — diga isso ao
  usuário em vez de prometer.

## Verificação

- [ ] Pairs aplicados com `occurrencesChanged` > 0 onde deveria haver troca.
- [ ] Contagem de linhas/tabelas igual à de antes da edição.
- [ ] Valores repetidos conferidos por busca (nenhuma sobra contraditória).
- [ ] PDF exportado do Doc conferido: páginas dentro do teto e páginas alteradas vistas em imagem.
- [ ] Capa, cabeçalho e rodapé intactos (abrir o PDF e olhar a página 1).
- [ ] Link do Doc inalterado (edição feita no mesmo arquivo, não em cópia paralela).

## References

- `references/api-docs-receitas.md` — receitas de API: laço de `replaceAllText`, leitura do doc com
  estrutura, negrito por correspondência de markdown, recuperação de conteúdo por revisão do Drive,
  criação de rodapé em duas chamadas.
