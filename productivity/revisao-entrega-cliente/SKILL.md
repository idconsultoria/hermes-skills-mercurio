---
name: revisao-entrega-cliente
description: "Use ao revisar/polir entrega de cliente antes de apresentar."
trigger: Pedido para revisar, auditar, dogfoodar, polir ou opinar sobre um artefato antes de entregar/apresentar ao cliente (documento de processo, especificação operacional, diagrama, deck, site publicado, PDF).
related_skills: [reunioes-diarizadas, identidade-visual-id]
type: Orchestrator
timestamp: 2026-09-21T12:00:00Z
---

# Revisão de entrega ao cliente

Revisar é **ler e reportar**, não consertar. O material pertence ao cliente e ao dono do projeto: aponta-se o problema, pergunta-se o que fazer, e só então se altera — item por item, com OK explícito.

## Quando usar

- "Revise esses documentos, estão completos?"
- "Algo que você adicionaria?"
- Conferência final de peça que vai a cliente (especificação, diagrama, proposta, PDF).

## Procedimento

### 0. Confirmar o recebimento do lote antes de executar

Pedido de revisão costuma chegar como lote (várias imagens + lista de correções). Responda
primeiro **confirmando o que chegou**: quantas imagens, quais são (nome/tamanho/hora) e quais
pontos foram entendidos — e só então execute. Imagem que veio sem descrição automática ainda pode
ser lida do cache local; diga o que falta em vez de presumir que o lote está completo.

### 1. Inventariar e medir antes de opinar

Liste os arquivos com tamanho e estrutura (`wc -l -c`; cabeçalhos). Diga o que está lá — o inventário já mostra se algo prometido não veio (o pacote pode ter 2 arquivos e faltar o terceiro). Se o material chegou compactado, extraia para pasta própria antes de ler.

### 2. Verificar que a peça **abre** de verdade

Peça visual não se julga pela descrição do autor: conte os elementos. Em SVG/HTML de diagrama, confirme `viewBox`, nº de tarefas e nº de gateways e **compare com o texto que o acompanha**. Contagem que não bate = trecho cortado ou peça de outra versão.

### 3. Conferir imprimibilidade (o erro mais silencioso)

- Fator de escala = largura útil da página ÷ largura do canvas; multiplique o corpo da fonte. Abaixo de ~6pt a peça não serve impressa.
- Canvas fixo em px **sem `@media print`** cai em 1 página A4: canvas de 3740px dá fator ~0,16 → corpo de 11,5px vira ~1,8pt. Saída: paisagem pré-dimensionada, tiling em páginas, ou exportar PNG/PDF em resolução nativa.

### 4. Conferir identidade da ID

Peça de cliente sai em teal `#14b8a6` + navy `#0a1929`, Neulis Neue nos títulos e Nunito Sans no corpo. Cor de template genérico (azul de sistema, roxo de dashboard) destoa da marca — aponte.

### 5. Cruzar artefato × decisão registrada

O erro que mais custa: o documento está bonito e **contradiz o que foi decidido**. Compare nomes de dono/supervisor, metas numéricas, papéis e prazos com a última decisão registrada (ata, base de conhecimento). Divergência **se reporta e se pergunta** — não se resolve por conta própria.

### 6. Entrega viva (site/deploy): conferir o que o cliente vai abrir, não o que o repo diz

Quando a entrega é um site publica­do, o artefato **vivo** é o que será apresentado — e ele
pode estar atrás (ou à frente) do repositório. Antes de dizer "está pronto":

1. **Monte o inventário de URLs.** Extraia do histórico de sessões/notas **todas** as URLs
de deploy já publicadas para o projeto. Protótipo com dados mockados e versão final
convivem no ar, com nomes parecidos: apresentar o protótipo é o erro caro.
2. **Compare vivo × fonte de verdade por hash**, não por tamanho: baixe `index.html`, os
JS/CSS de entrada e um asset pesado do domínio e compare o `sha256` com o HEAD do repo
(conteúdo raw do GitHub). Byte-idêntico = publica o HEAD; diferente = deploy velho — avise
antes da reunião, não durante.
3. **Teste os assets, não só a home.** Home 200 não garante HDR/GLB/áudio: um asset 404
quebra a cena 3D na frente do cliente.
4. **Escopo contratual × artefato vivo.** Percorra a lista de entregáveis do contrato e
confirme cada um **dentro do artefato a ser apresentado**. É comum a etapa que virou
entregável depois existir só no repo/Drive, em HTML separado que nunca foi publicado.
5. **Rastreie a entrega formal.** Pasta do Drive (existe? está em trashed? tem subpasta por
entregável?), thread do Gmail (enviada? reencaminhada? respondida?). A data do último item
da thread é a resposta para "em que pé está a entrega".

Receitas de comando (hash vivo×repo, pasta/thread, URLs de deploy):
`references/entrega-viva-verificacao.md`.

Medição de contraste sobre cena 3D/canvas (cena clara simulada + leitura no pixel):
`scripts/contraste-cena-clara.py`.

**Pitfall:** o README do repo desatualiza em relação ao artefato (conta telas/etapas de
uma versão antiga). O artefato manda; README é pista, não fonte.

**Pitfall:** o clone local que existia quando a peça foi feita pode não existir mais na
máquina. Confirme o caminho antes de prometer "rodo local" — e trate o remoto como fonte
única.

**Apresentação presencial com rede incerta:** sirva a cópia local do site
(`python3 -m http.server 8098 --directory <...>/<pasta-do-site>`) em vez de depender do
domínio público — site com ES modules/importmap **não** abre por `file://`. Passe sempre
`--directory`: sem ele o `http.server` serve o diretório de trabalho errado e devolve 404 em
tudo, o que parece site quebrado. Teste home + JS/CSS de entrada + um asset pesado antes de
dizer que está pronto para apresentar.

### 6b. Polir a entrega viva antes de apresentar (auditar com prova, não a olho)

Revisar e **consertar** a peça que o cliente vai abrir, iterando até ficar apresentável — cada
item abaixo só se encerra com evidência medida:

1. **Contraste WCAG AA medido por script, não por impressão visual.** Percorra os nós de texto
compondo o fundo efetivo (rgba sobre rgba, base = fundo do body) e multiplicando a **opacidade
de todos os ancestrais**; compare com 4,5:1 (3:1 para ≥24px / ≥18,66px bold). Sem compor
opacidade de ancestrais você acusa como falha o que está apenas escondido por design (tela
inativa, animação de entrada) e perde as falhas reais embutidas em token
(`--text-muted` escuro demais, `opacity: .55` numa linha de tabela, tag pintada com o tom escuro
da própria paleta).
2. **Conte elementos visíveis por tela depois de cada navegação.** Tela com entrada dirigida por
scroll passa no audit e fica invisível para o visitante; navegação por menu/aba/âncora costuma
deixar a tela em branco até o próximo scroll. Imprima `visíveis/total` por tela — inclusive na
primeira carga.
3. **Todo controle tem que produzir efeito observável.** Clique e meça a mudança (URL, download,
estado, texto). CTA sem handler, botão cujo listener se perdeu e link de contato incompleto
(e-mail sem TLD) são comuns em página montada por template string.
4. **Paleta única e zero emoji.** `grep` o CSS/JS por cores que não pertencem à paleta da casa
(indigo/dourado/verde/roxo herdados de um esquema anterior) — inclusive em `::selection`,
sombre de legenda e regra de impressão. Página reusada de um relatório antigo costuma trazer
cor e emoji próprios: alinhe antes de publicar.
5. **Fallback de recurso ausente em vez de tela preta.** Se o carregamento depende de uma
capacidade do navegador (WebGL, câmera, codec), teste com a capacidade ausente e exija que o
conteúdo apareça mesmo assim, com prazo máximo — overlay de carregamento que só sai quando a
cena carrega é o pior modo de falha de um site de apresentação.
6. **Artefato publicado é o que conta.** Depois de corrigir, publique e revalide **no domínio**
(hash dos assets, contraste, controles) — correção só no clone local não chegou ao cliente. Se
o projeto de deploy vive em outra conta/escopo, isso é bloqueio a escalar, não a ignorar
(ver `dns-dominios-id`).

7. **Bug de posicionamento: suspeite dos dados antes do render.** Item no lugar errado (bolinhas
fora das regiões, marcadores amontoados num canto, coluna vazia) costuma vir da derivação do
**dado**, não do desenho: reproduza fora do navegador a função que calcula a posição (mesmo
hash/índice/cluster) e confira item a item contra a geometria de origem — no caso real,
`parseInt('S-005'.slice(1))` = `-5` jogava todas as soluções na mesma região, o que parecia bug de
3D. Cobertura medida (N de N dentro da área certa) é o que autoriza dizer "corrigido".
8. **Meça layout em movimento com cuidado.** `offsetLeft`/`getBoundingClientRect` já carregam o
**transform aplicado**: derivar o passo de um carrossel a partir deles faz o trilho andar menos a
cada clique e sobra um vão à esquerda. Calcule o passo por índice (largura de layout + gap) e, ao
medir logo depois de um clique, espere a transição terminar (ou leia
`getComputedStyle(...).transform`) — medir no meio da animação inventa um bug que não existe. Se a
capacidade do navegador não existe no ambiente (WebGL), diga explicitamente o que **não** foi
verificado visualmente e o que foi verificado por medição.

9. **Contraste sobre cena 3D/canvas: o audit por CSS não vê o fundo real — meça no pixel.** O audit
compositor de fundo lê **só o DOM** (ancestrais), então texto apoiado sobre um canvas/WebGL claro
passa no script e mesmo assim falha na frente do cliente. Teste de estresse: injete uma camada
clara atrás do conteúdo (`position:fixed; inset:0;` com `z-index` acima do canvas e abaixo do
conteúdo), capture o screenshot e calcule o contraste **local** por caixa de elemento (percentis
2%/98% de luminância; percentil largo dilui glifo fino). Script pronto e re-rodável:
`scripts/contraste-cena-clara.py`.

   A causa dominante não é falta de sombra: é **fundo translúcido** (`rgba(...,0.55)` de card,
   chip ou pill) que, composto sobre cena clara, clareia e derruba o texto. Correção por tipo de
elemento: rótulo pequeno e todo controle (botão, link de fecho, linha de contato) recebem
**fundo próprio escuro** (alpha ≥0,8, em chip/pill); parágrafo solto sobre a cena fica em cor
**primária** com sombra **densa e curta** (blur grande não protege glifo pequeno); e cards/rodapés
translúcidos escurecem (mesma regra do fundo próprio).

   Rode o teste em **todas** as telas, não só na reclamada — as telas não citadas costumam trazer o
   mesmo defeito (eyebrow, título riscado e rodapé de cobertura foram achados assim). Reporte
   antes/depois **por elemento** com a razão medida.

10. **Ajuste por altura de tela (16:9 · 1366×768) — a media query precisa vencer a cascata.** Regra
escrita no `base.css` perde para a regra do CSS da tela carregado **depois**: o arquivo muda, o
layout não, e parece que "o ajuste não pegou" (ou que é cache). Diagnóstico correto: leia
`getComputedStyle` do elemento (padding, fonte) — valor ainda no original significa **cascata**,
não cache (distinga os dois baixando o asset **servido** e `grep`ando o marcador novo: arquivo servido
atualizado + DOM antigo = cache do navegador, desative-o no CDP ou use perfil/porta novos; arquivo
servido antigo = você editou outro caminho). Conserto: um stylesheet de ajustes carregado **por último** (`<link>` depois de todos)
ou a media query dentro do próprio CSS da tela.

   Overflow vertical com `justify-content:center` corta **topo e base ao mesmo tempo**; o estado é
`scrollHeight` da tela > `innerHeight`. Trate como conteúdo que não cabe (reduza escala vertical:
padding do card, tamanho de lista, altura do rodapé), não como bug de estilo. Meça depois em
**todas** as resoluções que interessam (1280×720, 1366×768, 1440×900, 1920×1080) e não só na citada.

11. **Rótulo de navegação sob demanda; rolagem interna com sinal.** Duas convenções de site de
apresentação que o cliente cobra explicitamente:

   - O **nome da cena** aparece **no hover** e, **no clique, por ~1,8s**, e some — **nunca fixo no
item ativo** (a sidebar já marca a posição). Implementação: CSS só em `:hover`/`:focus-visible`
mais uma classe transitória (`.mostra-rotulo`) aplicada no clique e removida por timer; manter a
regra `.is-active` mostrando o rótulo é exatamente o que o cliente rejeita.
   - Card cujo dossiê é mais alto que a caixa **rola por dentro**: sem sinal, o fim do texto lê como
conteúdo cortado. Marque com classe quando `scrollHeight > clientHeight` (+4px de tolerância) e
mostre **fade no rodapé + dica curta** ("role para ver o restante") apenas nesses cards.

12. **Caber não é estar bom: orçamento vertical e hierarquia do fecho em 16:9.** Tela com
`scrollHeight == innerHeight` pode ainda estar sufocada — o que se mede é a **fatia** que o bloco de
conteúdo ocupa. Em 1366×768, bloco de 702px em 768px (título de 4-5 linhas = 41% da altura) é
reprovado mesmo sem corte: alvo é bloco ≤ ~60% da altura, com ≥15% de respiro em cima e embaixo.

- Reduza **tamanho e medida**: encolher a fonte não diminui o número de linhas — o `max-width` em
 `ch` é quem manda na quebra. Aumente a medida (ex.: de 14ch para 20-24ch) junto com o clamp para o
 título cair de 4-5 para 2 linhas. Contagem de linhas = `altura / lineHeight`, medida, não olhada.
- Ritmo constante: o mesmo gap entre todos os blocos (eyebrow → título → parágrafo → CTA → links →
 contato) evita o "degrau" que o cliente lê como aglomerado.
- Hierarquia: **uma** ação principal (pill com glow) e os secundários rebaixados a link de texto
 sublinhado, com mais espaço antes da linha de contato. Empilhar pílulas de mesmo peso polui a
 escolha e é cobrado como feio.

Medição re-rodável do orçamento vertical (fatia do bloco, linhas do título, ritmo dos gaps e
respiro topo/base, por tela e por resolução, com exit code de gate):
`scripts/orcamento-vertical-tela.py`.

PDF que o próprio site oferece (botão "Exportar PDF"): regras e armadilhas em
`references/exportacao-pdf-no-proprio-site.md` — `color-mix()` invalida o html2canvas,
`windowWidth/Height` gera página em branco, carrossel precisa empilhar no modo impresso.

### 7. Reportar em quatro blocos

1. **O que está completo** — diga primeiro e com honestidade; na maioria dos casos a maior parte está boa, e começar pelo defeito queima credibilidade.
2. **Lacunas por tema**, cada uma com o motivo prático de importar (não só "falta seção X").
3. **Conflitos a confirmar com o dono**, em bloco separado, pedindo a resposta.
4. **Sugestões numeradas**, pedindo OK antes de tocar em qualquer arquivo.

Checklists temáticos (diagrama de processo, especificação operacional, renderização/impressão,
documento no timbrado gerado a partir de markdown): `references/checklists-revisao.md`.

## Pitfalls

- **"Já que estou aqui, vou corrigir"** — alterar material do cliente sem OK é o pior erro possível neste trabalho, mesmo quando a correção é óbvia e a divergência é factual.
- **Opinar sem abrir a peça.** Renderize/leia e conte elementos; impressão visual de descrição de terceiro não é revisão.
- **Julgar layout sem testar a conversão.** SVG estilizado só por custom property CSS (`var(--x)`) vira mancha preta em conversor que não é navegador — a variável não resolve e o default do SVG é preto. Para PDF, cor literal no SVG (atributo `fill` ou `<style>` interno com hex) ou geração pelo próprio navegador.
- **Ignorar dependência de rede.** Fonte por `<link>` do Google Fonts = tipografia perdida offline; em peça arquivável, embuta ou defina fallback.
- **Supor que a ferramenta está instalada porque o gerenciador de pacotes disse sim.** Confirme com um render real (ou screenshot de HTML trivial) antes de construir o fluxo em cima dela — sucesso de instalação não prova binário funcional.
- **Avaliar diagrama de processo só pela estética.** Gate sem ramo "não/reprovado" não é gate; ciclo de melhoria prometido no texto sem seta de retorno no desenho é lacuna; e SVG desenhado à mão rotulado "BPMN 2.0" não abre em bpmn.io/Camunda nem versiona diff.
- **Confundir ausência com falha.** Artefato que não existe no pacote é lacuna de conteúdo; artefato que existe e está incompleto é lacuna de profundidade. Separe os dois ao reportar.
- **Re-depurar defeito que já foi corrigido.** Print ou relato com um elemento que a correção
removeu (rótulo antigo, painel translúcido, cor fora da paleta) quase sempre é **build/URL antiga**.
Baixe o JS/CSS **servido** pelo domínio que a pessoa abriu e `grep` pelo marcador que a correção
eliminou: se o marcador existe, o assunto é qual URL abrir — não re-corrigir. Alias manual do
Vercel **não acompanha** deploy novo: cada `vercel --prod` cria URL nova e as URLs amigáveis
seguem apontando para o deploy anterior até rodar `vercel alias set` de novo (uma vez por alias).
- **Tratar print recortado como prova de truncamento.** Texto cortado no meio da palavra em close-up
pode ser o recorte do próprio print. Meça no DOM antes de mexer no CSS: `scrollHeight`/`clientHeight`
do item e folga entre a última linha e a borda do container. Se o dado não cabe (texto longo demais),
quer dizer outra coisa que clipping.
- **Crédito à leitura de imagem: layout sim, string pequena não.** A crítica visual é boa em apontar
aglomerado, desequilíbrio, hierarquia — e também erra: texto pequeno em caixa alta/mono é mal lido e
volta como "typo" que não existe. Todo typo alegado se confere no DOM/fonte antes de mexer. Em
compensação, **revise a redação** da peça viva (concordância, verbo faltando): erro de texto no
artefato do cliente é achado de revisão, não detalhe.

## Verificação

- [ ] Inventário completo do pacote, com tamanhos, antes de qualquer juízo.
- [ ] Peça visual aberta/contada, com números conferidos contra o texto que a acompanha.
- [ ] Imprimibilidade e identidade conferidas.
- [ ] Cruzamento com a decisão registrada feito; conflitos isolados para confirmação.
- [ ] Nenhum arquivo alterado; sugestões numeradas e submetidas à aprovação.
- [ ] Entrega viva: vivo × repo comparado por hash e **todos** os entregáveis do contrato
  localizados no artefato a ser apresentado.
- [ ] Entrega viva polida: contraste AA medido por script, `visíveis/total` por tela, cada
  controle com efeito observável, paleta única (sem cor herdada de esquema antigo, sem emoji),
  fallback quando falta a capacidade do navegador — e a versão corrigida revalidada **no domínio**
  publicado.
- [ ] Contraste medido também **com cena clara simulada atrás do conteúdo** (texto sobre canvas/3D),
  em todas as telas, com antes/depois por elemento (`scripts/contraste-cena-clara.py`).
- [ ] Ajuste por altura de tela conferido por `getComputedStyle` (a regra venceu a cascata) e
  nenhuma tela com `scrollHeight` > `innerHeight` nas resoluções combinadas.
- [ ] Tela que cabe mas ocupa >60% da altura com respiro <15% em cima/embaixo também é reprovada:
  conte as linhas do título (`altura / lineHeight`) e meça a fatia do bloco de conteúdo.
- [ ] Defeito "já corrigido" reclamado de novo: marcador da correção `grep`ado no asset servido pelo
  domínio que a pessoa abriu, e aliases do deploy re-apontados após o último `--prod`.
- [ ] Documento de texto gerado (roteiro, checklist, relatório, plano): **gate de integridade
  rodado** — contagem por seção, sequência e contaminação de alfabeto:
  `python3 roteiro-de-qualificacao/scripts/scan-integridade-texto.py ARQUIVO.md`. O vazamento de
  caractere de outro alfabeto e a pontuação duplicada são **invisíveis na leitura** e aparecem na
  frente do cliente; ao corrigir, reescrever a **linha inteira** e revalidar a estrutura depois.
- [ ] Retorno em quatro blocos (completo / lacunas / conflitos / sugestões).
