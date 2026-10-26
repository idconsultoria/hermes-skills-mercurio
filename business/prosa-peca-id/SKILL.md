---
name: prosa-peca-id
description: "Use ao escrever ou revisar prosa de peça da ID."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [escrita, prosa, voz, humanizer, pt-br, peca, cliente, id]
    related_skills: [documento-a4-marca-id, elaboracao-proposta-comercial, revisao-entrega-cliente]
type: Reference
timestamp: 2026-10-22T00:00:00Z
---

# Prosa de peça da ID

## Quando usar

Antes de redigir (ou ao revisar) qualquer texto que sai com a marca da ID: documento de cliente,
estudo, guia, proposta, seção de apresentação. O objetivo não é texto bonito — é o diretor entender
na primeira leitura e confiar no número.

Se a peça é um PDF A4 com a identidade visual, combine com `documento-a4-marca-id` (marca e
template) e volte aqui para a prosa. A verificação final de página, espaçamento e renderização está
em `references/verificacao-da-peca.md`. Se a peça vai levar print de tela (painel, protótipo, app),
a receita de captura, recorte e verificação da figura está em `figuras-em-documento-pdf`.

## Ordem de trabalho

1. **Carregue a voz certa.** O acervo do perfil Fama guarda os guias por sócio com as medidas de
   ritmo e vocabulário de cada um: `profiles/fama/workspace/marca/guias-de-escrita/` e o método em
   `profiles/fama/skills/conteudo-id/guia-de-escrita-founder-id/SKILL.md`. Escrever de memória sobre
   o estilo erra na forma.
2. **Escolha o registro e não troque no meio da peça.** Documento de diretoria: impessoal e direto
   ("é preciso distinguir", "em termos práticos"). Peça curta e conversacional: "a gente", "você",
   "repara". Misturar os dois é o defeito mais visível.
3. **Monte o esqueleto antes de escrever a frase:** cena concreta → fato incomum com número e fonte →
   objeção na voz de quem lê → resposta em uma linha → teste ou distinção que o leitor aplica
   sozinho → fecho curto. Sem cena, a peça é aforismo.
4. **Escreva com definição motivada.** Nenhum termo entra antes de o problema que ele resolve ter
   aparecido. Definição que chega antes da motivação é decorada, não aprendida.
5. **Rode a conferência mecânica** (seção abaixo) e leia em voz alta.
6. **Entregue a prévia e diga o que mudou** em poucas linhas. Se algum elemento depende de terceiro
   (link, print, painel), entregue sem ele e enriqueça depois — não segure a peça inteira.

## Ritmo

- Frase curta e cadência regular: mediana de 10 a 15 palavras, sem alternar registro a cada
  parágrafo.
- Travessão é caro: um punhado por peça no máximo, quase sempre separando rótulo de título. Para o
  resto, vírgula, dois-pontos ou ponto final.
- Negrito só em nome de termo, rótulo e sigla. Negrito mecânico a cada parágrafo é tell de máquina.
- Uma ideia por parágrafo. Em documento para diretoria, cada página tem que sobreviver a uma
  leitura de trinta segundos.

## As cinco proibições de construção

Violar uma reprova a peça, por bem escrita que esteja.

1. **Antítese de correção** ("isso não é X, é Y"). No máximo **uma** por peça, e só depois de a
   objeção ter sido escrita na voz do leitor. Nunca na abertura. A exceção legítima tem alguém
   respondendo dentro do texto; a que reprova não tem.
2. **Abertura por crença que ninguém vê** — "a maioria não sabe", "quase ninguém percebe", "poucas
   empresas". Abra pelo fato observável ou pela cena.
3. **Objeção de cortina** — "pode-se argumentar que… porém, como vimos…". A objeção entra inteira, na
   fala de quem lê, e ganha argumento de verdade.
4. **Fecho que resume** — "em resumo", "como vimos", "o caminho é claro". Volte à frase da abertura,
   dê um passo curto e pare.
5. **Eufemismo de marketing e frase de manual** — transformação digital, revolução, solução
   inovadora, ecossistema, sinergia, escalabilidade, disruptivo, "é importante notar", "vale
   ressaltar", "no cenário atual", "em um mundo onde".

## Tells de IA em português

Travessão em série · negrito mecânico · regra de três forçada · lista com cabeçalho em negrito
seguido de dois-pontos · fragmento dramático de duas ou três palavras fechando o parágrafo ·
pergunta retórica respondida na frase seguinte · variação elegante (sinônimos ciclando para o mesmo
objeto) · aspas curvas · emoji · conclusão otimista genérica · **paralelismo negativo em série**
("e não X", "não é X, e sim Y" repetido a cada seção) · **antítese de espelho** ("não existe para X.
Existe para Y") · **meta-comentário de tabela** ("cada célula mostra de onde vem o valor") ·
**aforismo de fecho** ("um painel restrito e utilizado supera um painel completo e ignorado").

Varredura dos dois primeiros, que são os que mais aparecem em documento técnico:

```python
print('e não', len(re.findall(r'e não [a-zçãéíóú]+', txt)))
print('espelho', re.findall(r'não existe para [^.]+\.[^.]*Existe para', txt))
```

Uma ocorrência de cada é conteúdo (distinção de conceito); três ou mais é tique de escrita.

Conferência mecânica no HTML/markdown gerado, antes de fechar a peça:

```python
import re, html
src = open('peca.html').read()
txt = html.unescape(re.sub(r'<[^>]+>', ' ', src))
print('travessões', txt.count('—'))
print('negritos', src.count('<b>'))
print('antíteses', re.findall(r'não é [^.<]{3,60}\.? é [^.]{3,80}', txt))
print('resumos', re.findall(r'[Ee]m resumo|[Cc]omo vimos|[Oo]u seja', txt))
print('eufemismo', re.findall(r'crucial|pivotal|vale ressaltar|cenário atual|ecossistema', txt, re.I))
```

Leia cada "não é" que aparecer: negação comum fica; antítese de correção só uma na peça.

## Registro de proposta — intenção declarada

Peça que propõe algo (proposta, estudo preliminar, plano de implantação) não é só descrição: declara
uma intenção e a sustenta até o fim. Regras:

- **Uma intenção por peça**, na abertura, ancorada no que se sabe — "do que compreendemos da
  realidade da empresa até aqui" — nunca em fato que não foi levantado nem em dor presumida.
- **Distribua, não repita.** A intenção volta em dois ou três pontos de decisão, cada vez com
  formulação diferente e peso maior, e o fecho a retoma pelo nome ("é por isso que sustentamos a
  recomendação da abertura"). A mesma frase repetida em cada seção é excesso e o leitor percebe.
- **Texto do interlocutor: pauta por padrão, literal quando ele anunciar literal.** Pedido genérico
  ("melhore a escrita", "dê seu melhor") autoriza reescrever no registro da peça preservando a tese.
  Quando ele avisa que vai ditar o trecho ("escreva literalmente", "é assim que você deve escrever"),
  entre com o texto dele inteiro, na ordem dele, sem encurtar e sem trocar registro; corrija apenas
  erro de digitação e diga numa linha o que corrigiu. Trocar o registro nesse modo é o defeito mais
  caro: ele já revisou a frase e vê a versão dele voltar diferente.
- **Absorver ideia sem nomeá-la.** Quando ele pede para não citar o conceito ("não cite o método,
  absorva a ideia"), escreva o mecanismo em linguagem de trabalho — medida, meta, ação, nova medida —
  sem nome próprio em nenhuma página, e confira a ausência com busca no texto final.
- **Modelo, não diagnóstico, e sem causa inventada.** Peça escrita sem examinar dado do cliente não
  afirma o que vai bem ou mal na operação dele e não enuncia causa ("a receita não muda por falta de
  gestão"). Declare na abertura que nenhum dado foi examinado e o que o documento é: um modelo de
  acompanhamento. Causa é conclusão de diagnóstico, e diagnóstico exige dado.
- **Postura se sustenta em consequência, não em adjetivo:** sem superlativo solto, sem promessa
  numérica, sem "revolucionário". A força vem de dizer o que a proposta substitui ou destrava.
- Cada ponto de posicionamento entra em um lugar em que já existe assunto para ele (recomendação de
  nomenclatura na seção de nomenclatura, escopo do painel na seção do painel). Posicionamento em
  seção própria vira discurso e é o primeiro lugar em que o leitor desiste.
- **A seção do rito é a que convence; trate-a como prova, não como fecho.** Mostre a cadência em
  tabela ou desenho — anual define metas gerais, tático desce para a meta de cada setor e de cada
  página do painel, semanal foca ações com responsável e prazo — e feche com o ciclo medida → meta →
  ação → nova medida. Duas páginas no máximo; o desenho substitui a enumeração em prosa em vez de
  repeti-la. É o trecho que responde "isto dá resultado ou é exercício intelectual?", e é onde o
  documento ganha ou perde a decisão.
- **Cadência se apresenta de baixo para cima.** Abra pelo ritmo mais curto — o semanal que já roda e
  converte número em ação, com pergunta concreta ("qual técnico está subutilizado, em qual
  modalidade, e por quê") — e só depois suba para mensal, trimestral e anual. Quem lê precisa ver o
  mecanismo funcionando antes de ver o organograma de reuniões; ordem anual → semanal parece
  cronograma e não gestão.
- **O que depende de decisão futura vai no fim, e com escala pequena.** Definição de metas não é
  projeto: diga que os indicadores já existem nas bases da empresa, que basta uma análise
  retrospectiva do histórico e duas reuniões (diretoria, depois gerentes) e desenhe as três etapas
  em passo a passo numerado. Esforço com cara de longo é o que trava a aprovação do modelo.
- **Renomear o total é reenquadrar, não recalcular.** Ao trocar o nome de um resultado ("teto de
  receita" → "receita do período"), a fórmula fica igual e muda a moldura: os fatores passam a ser
  alavancas acionáveis. Na mesma rodada, ajuste o rótulo, o título da seção que o apresenta e a
  definição de cada fator; e varra a peça pela palavra antiga até zero ocorrências — resíduo em outro
  parágrafo contradiz a nova moldura.

## Nomenclatura e sigla

- **Sigla só depois do nome por extenso**, e só depois de o conceito ter sido apresentado:
  "Taxa de Utilização Faturável (TUF)". Sigla antes da definição faz o leitor desistir.
- Prefira o nome em português; mantenha a sigla inglesa apenas quando for o nome de mercado.
- Uma nomenclatura por peça, declarada no começo e usada sem variação. Dois nomes para a mesma coisa
  fazem o leitor procurar uma diferença que não existe.
- Quando a peça padroniza vocabulário do cliente, declare a regra em uma frase e cumpra em todas as
  páginas.

## Pitfalls

1. **"A prosa ficou desagradável" quase sempre é o mesmo diagnóstico:** antítese em série, travessão
   decorativo e negrito a cada parágrafo. Corrija nessa ordem antes de reescrever conteúdo.
2. **Não reescreva a peça inteira por um problema de construção.** Troque as frases que carregam o
   vício e preserve o que já está claro; o cliente reconhece o texto e compara.
3. **Prosa mais solta ocupa mais página.** Se o pedido era "peça pequena", ganhe espaço cortando
   indicador e seção, não apertando entrelinha — aperto é o que ele vê primeiro.
4. **Não anuncie o que o texto vai fazer** ("vamos ver agora", "o caminho deste guia") em texto
   corrido; sumário só quando a peça tem seções de verdade.
5. **Dado de cliente fictício precisa de rótulo visível** ("dados fictícios para demonstração").
   Sem o rótulo, o número inventado vira informação e volta como cobrança.
6. **Parágrafo de posicionamento novo costuma duplicar o que já está no fecho ou na seção vizinha.**
   Antes de acrescentar, procure a mesma ideia no documento; cortar a duplicata resolve página
   apertada melhor do que apertar entrelinha, e evita dizer duas vezes a mesma coisa com palavras
diferentes.

## Antes de entregar

- [ ] Cada definição aparece depois do problema que a motiva
- [ ] No máximo uma antítese, e depois da objeção
- [ ] Nenhum "em resumo", nenhum "quase ninguém", nenhum eufemismo de marketing
- [ ] Se a peça é proposta: intenção declarada uma vez, retomada sem repetição literal
- [ ] Siglas com nome por extenso na primeira ocorrência
- [ ] Conferência mecânica rodada e números conferidos
- [ ] Leu em voz alta e não travou
