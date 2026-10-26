---
name: contrato-sustentacao-sla
description: "Use ao redigir contrato de sustentação com SLA.

Carregue esta skill ao redigir contrato de sustentação com SLA para cliente da ID: escopo do serviço, níveis de serviço e prazos de resposta, medição, penalidades e renovação — receita recorrente com risco delimitado."
category: legal
type: Orchestrator
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [contrato, sustentação, sla, recorrente, minuta, id-consultoria, drive]
    scopes: [id]
    related_skills: [contratos-justos-id, auxiliar-adm-id, documento-a4-marca-id, id-comunicacao-multiusuario]
timestamp: 2026-10-20T00:00:00Z
---

# Contrato de sustentação com SLA (receita recorrente)

## Quando usar

Sistema/projeto já entregue e aceito e o cliente quer continuar — ou o sócio pede "contrato de
sustentação", "manutenção com SLA de 12 meses", "mensalidade de suporte". É **instrumento novo que
sucede o projeto**, não aditivo dele: o projeto terminava na entrega e na transição.

Para os princípios gerais de contrato da casa (DNA, checklist, o que a ID nunca escreve) use
`contratos-justos-id` — esta skill cobre o **arquétipo recorrente** e o que ele tem de próprio.

## Base de trabalho

1. Ler o **contrato anterior assinado** no Drive e reaproveitar dele: qualificação das partes
   (verbatim, conferindo a razão social no CNPJ), considerandos, PI, confidencialidade, LGPD,
   independência, foro. O que muda é escopo, preço, prazo e nível de serviço.
2. Recolher na fonte o que foi entregue e pago (planilha de contratos, NFS-e, extrato) e o **aceite
   formal** do cliente — ele entra nos considerandos e é o marco que encerra o projeto.
3. Fixar o preço com dado: horas do contrato anterior, custo direto do escopo novo (horas × valor
   da hora + insumos) e delta anual. Preço não se reduz "para ser justo" sem essa conta.
4. **Preço não se inventa.** Pedido de "valor mais justo" sem número é uma pergunta: faça-a com 3–4
   opções ancoradas em dado e diga qual recomenda. Sem resposta, entregue com o valor recomendado e
   **declare a premissa na primeira linha**, oferecendo troca em minutos.

Ambiente dos scripts de Drive/Docs: rode com `venvs/google/bin/python` (o venv que tem
`googleapiclient` — confirme com `-c "import googleapiclient"` antes) e **redirecione a saída para um
arquivo** (`python -u script.py > work/x.log 2>&1`), lendo depois com `read_file`. Saída de script
com chamadas de rede se perde no caminho, e silêncio não significa sucesso.

## Esqueleto das cláusulas

1. Partes + 3 considerandos (plataforma entregue · aceite e transição formal · decisão de manter
   operação com nível de serviço).
2. **Resumo de 1 página**: o que é, quanto, quando, quem faz, o que o cliente entrega, SLA,
   propriedade.
3. **Objeto** com remissão aos anexos de escopo e de SLA, e a frase de que o contrato de projeto
   **não é substituído nem alterado**.
4. **Escopo incluído**: operação assistida (rotinas diárias, integridade dos dados), manutenção
   corretiva com prazos, manutenção evolutiva de **N h/mês não cumulativas**, infraestrutura e
   insumos **na capacidade atual** (nomeie a referência: nº de unidades/volume), suporte aos
   usuários, relatório + reunião mensal.
5. **Fora do escopo**: funcionalidades acima das N horas, integrações novas, ampliação de
   capacidade, migração de nuvem, treinamento de novas turmas, consultoria de captação, recuperação
   por uso indevido ou alteração de terceiros — tudo por proposta prévia + aditivo.
6. **SLA em anexo**: canal oficial e canal de urgência, horário de atendimento em dias úteis,
   severidades com **resposta** e **contorno**, meta de disponibilidade, janela de manutenção,
   medição/relatório e a lista de **exclusões** (força maior, terceiros/APIs/nuvem comunicados,
   alteração do cliente, uso indevido, capacidade não aprovada, rede do cliente, manutenção
   programada, demanda fora de escopo).
7. **Créditos por descumprimento**: percentual por evento fora do prazo com **teto mensal** (ex.: 5%
   por crítico com teto de 20% da mensalidade; 2,5% no alto com teto de 10%), declarados como único
   efeito indenizatório do SLA, sem prejuízo do direito de rescisão.
8. **Vigência**: 12 meses com **renovação automática** por períodos iguais e aviso em contrário de
   60 dias; a sustentação é contínua e não se interrompe por ausência de chamados.
9. **Remuneração**: mensalidade + total do período por extenso, NF até o 5º dia útil, pagamento em
   até 15 dias, Pix com chave CNPJ, reajuste anual pelo IPCA, valores remuneram a integralidade
   (salvo a cláusula de infraestrutura).
10. **Infraestrutura e insumos**: o que a mensalidade cobre (com a capacidade de referência
    explícita) e que **ampliação de capacidade é do cliente**, com custo apresentado e aprovação por
    escrito antes; repasse de reajuste de fornecedor com 30 dias de aviso e comprovação.
11. **Mora e suspensão**: 2% + 1% ao mês e correção; suspensão após 30 dias de atraso com aviso de
    10 dias; suspensão não interrompe a vigência; penalidade **simétrica** para atraso da ID.
12. **PI**: plataforma, código, algoritmos e **as melhorias feitas na vigência** são da ID; licença
    de uso não exclusiva e não transferível ao cliente; dados e relatórios são do cliente;
    preexistentes reservados; vedada comercialização ou sublicença.
13. **Confidencialidade** por 5 anos + dever permanente sobre segredo industrial (Lei 9.279/96, art.
    195, XI), sobrevivendo ao término.
14. **LGPD**: cliente controlador, ID operadora; tratamento só por instrução documentada;
    suboperadores com sigilo; incidente comunicado em 24 h; assistência a titulares; **vedação de
    treinar IA com dado do cliente**; devolução ou eliminação ao término.
15. **Continuidade e saída**: exportação dos dados em formato aberto em até 30 dias, operação
    mantida na transição (remunerada se passar de 30 dias) e **sem retenção de dado como pressão**
    por valor controvertido.
16. **Rescisão**: 60 dias sem justa causa; 30 dias para sanar descumprimento; imediata em violação
    de PI, sigilo ou LGPD; PI, sigilo e dados sobrevivem.
17. **Cessão/sucessão** com anuência prévia; **Relações anteriores**; **Disposições gerais**: aditivo
    por escrito, tolerância não é novação, assinatura eletrônica válida (MP 2.200-2/2001 e Lei
    14.063/2020), foro da Comarca de Aracaju/SE.

## Tabela de severidade (ponto de partida)

| Severidade | Definição | Resposta | Contorno/correção |
|---|---|---|---|
| S1 crítico | plataforma ou função essencial parada, sem contorno | 4 h úteis | 1 dia útil |
| S2 alto | função degradada com alternativa manual, ou risco de perder prazo | 8 h úteis | 3 dias úteis |
| S3 médio | falha não bloqueante (dado, cálculo, tela) | 2 dias úteis | 10 dias úteis |
| S4 baixo | dúvida de uso, ajuste estético, melhoria | 3 dias úteis | próximo ciclo |

Disponibilidade de 99% ao mês; manutenção programada até 4 h com aviso de 48 h. Severidade é
atribuída na abertura, em conjunto; na divergência persistente prevalece a do cliente, com registro
no relatório mensal.

## Página única de avaliação (para os sócios)

O sócio decide pelo que **muda**, não pelo texto das cláusulas. Entregue, junto à minuta, uma página
A4 com o padrão visual da ID (skill `documento-a4-marca-id`), nesta ordem:

1. **Antes × agora** em tabela: escopo, horas, valor, resultado, prazo, nível de serviço.
2. **O que a ID abre mão** — em número: participação de resultado retirada, R$/mês e R$/ano de
   receita, horas de evolução a menos, operação absorvida sem cobrança extra.
3. **O que cobre** e **o que não cobre**, lado a lado.
4. **O que a ID assume de novo**: tabela de severidade, disponibilidade, créditos, penalidade
   simétrica, compromisso de prazo.
5. **Decisões dos sócios**: valor proposto com o custo direto ao lado, data de início, foro,
   conferência de razão social.

Rodapé: documento **interno**, com o link da minuta editável. Vai ao grupo da ID como PDF, com
legenda de 2–3 linhas (receita de envio em `id-comunicacao-multiusuario`).

Render e conferência da página (funciona sem Playwright):

```bash
chromium-browser --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer \
  --virtual-time-budget=4000 --print-to-pdf=peca.pdf file://$PWD/peca.html
pdftoppm -png -r 110 peca.pdf pagina      # e leia pagina-1.png com vision_analyze
```

Conte as páginas do PDF (`pypdf`) **e** olhe o PNG: `overflow:hidden` corta em silêncio. Quando não
couber, encolha **antes** de cortar texto — corpo −0,5 a −1 pt, itens e `td` −0,5 pt, padding de
célula (1,5→1,1 mm), margem entre seções (3,6→2,8 mm), rodapé a 5 mm do pé.

## Padrão visual do contrato (o documento, não só as cláusulas)

O sócio compara a minuta com os contratos **Solution Master** (referência de qualidade da casa):
Google Doc **A4**, **capa** (título + objeto do contrato em page 1, sozinha), **cabeçalho corrido**
em todas as páginas (`Contrato de Prestação de Serviços — <sistema>` / `<Cliente>`) e cláusulas
começando em **PARTES**. Minuta sem isso é lida como "fora do documento padrão", mesmo com o
texto correto.

- **Nunca subir o contrato ao Drive convertendo HTML** (`files().update(media_body=MediaFileUpload(..., 'text/html'))`):
  o Google converte em **US Letter (612×792)**, sem capa e sem cabeçalho. Sintoma exato: `pdfinfo`
  mostra `Page size: 612 x 792 pts (letter)` e a página 1 traz o título colado em `PARTES`.
- **Fix de página**: `documents().batchUpdate` com `updateDocumentStyle`
  (`pageSize{width{unit:'PT',magnitude:595.3},height{...841.9}}` + margens ~72pt) antes de julgar
  paginação.
- **Capa e cabeçalho**: o modelo timbrado em branco da casa é o caminho; não improvisar capa em
  parágrafos soltos (o Docs não reserva a página).

## Página única facilitada (o que acompanha a minuta)

Além da página de avaliação dos sócios, o sócio pede o **contrato inteiro em uma página**
("onepage facilitado"). Regras do dono, na ordem em que ele cobra:

1. **É infográfico, não resumo em texto.** Página densa de parágrafos é devolvida como "confuso"
   mesmo com os números certos. Cada seção leva **ícone de linha**, cada número vira **cartão com
   valor grande + uma linha de explicação**, e todo dado comparativo vira **gráfico de barra**
   (**barra, nunca pizza/donut**; barra = valor relativo ao maior item, com o número absoluto ao
   lado). O que tem começo e fim vira **linha do tempo** (vigência, parcelas).
2. **Todo número se explica em concreto.** "99% de disponibilidade" sozinho é "desconexo": traduza
   na consequência — até ~7 h fora do ar no mês sem sair da meta, fora a manutenção programada e as
   exclusões. O mesmo para prazos ("resposta = primeiro retorno técnico; contorno = sistema no ar").
3. **Item sem obrigação real se declara vazio.** Quando uma cláusula descreve valor que não existe
   (participação de resultado de um contrato em que **não houve captação**), a página diz
   explicitamente **"nada devido — nem a receber, nem a cobrar"**, e a cláusula correspondente da
   minuta precisa ser reescrita ou removida. Deixar a frase "permanecem devidos" na minuta é o que
   faz o sócio ler dívida onde não há.
4. **Ordem das seções:** KPIs → linha do tempo da vigência → quanto custa (barras: parcela anterior ×
   proposta × custo direto interno) → o que acontece quando falha (severidade com prazos + créditos)
   → o que muda em relação ao contrato anterior → dentro/fora do escopo (✓/✗) → o que os sócios
   decidem. Rodapé marcado como **interno** enquanto o destino não for confirmado, com o link da
   minuta editável.

Receita completa (HTML de referência, gráficos, verificação) em
`references/onepage-infografico-contrato.md`. Render sem Playwright: `chromium-browser
--headless=new --disable-gpu --no-sandbox --no-pdf-header-footer --virtual-time-budget=4000
--print-to-pdf=peca.pdf file://$PWD/peca.html`, depois `pdftoppm -png -r 110` e `vision_analyze`
na PNG — a visão pega o que a contagem de páginas não pega (texto invadindo a coluna vizinha,
ícone não desenhado, bloco desalinhado).

## Pitfalls que custam dinheiro

- **Escreva o que sobrevive do contrato anterior — e, quando não houver nada, escreva "nada".**
  Instrumento novo que só descreve o serviço novo apaga a receita que o contrato antigo mandava pagar
  depois do término (participação de resultado sobre captações geradas até X meses do fim, marco
  pendente): cláusula própria citando as cláusulas e a data do contrato anterior, mais a declaração
  de que no período novo aquilo não se aplica. O inverso também vale: se **não houve captação** no
  contrato encerrado, a mesma cláusula tem de dizer que **nada é devido** — cláusula padrão mantida
  com "permanecem devidos" fabrica uma dívida que não existe e trava a leitura dos sócios.
- **Versão = o MESMO arquivo do Drive.** Atualize com
  `files().update(fileId=..., media_body=..., body={"name": "… v2 …"})`; criar um doc v2 com id
  novo quebra todos os links já distribuídos (rodapé do one-pager, mensagem no grupo).
- **Confirme a substituição lendo de volta.** Exporte o texto
  (`files().export(mimeType="text/plain")`) e cheque os **dois lados**: valor novo presente E valor
  antigo ausente. Trocar preço no meio de parágrafo e no total é onde a troca passa batida.
- **Data do documento se confere em DUAS fontes externas independentes** (ex.: o `modifiedTime` que o
  servidor do Drive devolve e um serviço de hora) — um único cabeçalho HTTP `Date` pode vir de cache
  de CDN e errar o dia, e o relógio do container sozinho não decide. Data errada contamina nome do
  arquivo, rodapé do one-pager e cronologia do contrato.
- **Infra acima da capacidade é do cliente**, com custo apresentado e aprovação por escrito antes —
  sem essa cláusula a ID absorve ampliação em silêncio.
- **Horas de evolução não cumulativas**; excedente só por proposta e aditivo.
- **Foro**: Aracaju é o padrão da casa, mas foro já aceito pelo cliente em contrato anterior (comarca
  do órgão ou do parque) é decisão do dono — proponha, não troque sozinho.
- **Razão social**: copie do último instrumento assinado e deixe a conferência no CNPJ como pendência
  explícita (a base já divergiu do contrato: "ID.TEAL Consultoria Organizacional" × "iD.teal
  Consultoria em Gestão Organizacional LTDA").
- **Minuta não vai ao cliente sem ok** do dono; o que circula para avaliação interna é a página única,
  marcada como interna.
