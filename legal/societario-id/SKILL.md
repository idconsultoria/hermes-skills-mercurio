---
name: societario-id
description: "Use ao responder sobre contrato social e sócios da ID."
category: legal
type: Method
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [societario, contrato-social, quotas, retirada, exclusao, jucese, id-consultoria]
    scopes: [id]
    related_skills: [contratos-justos-id, auxiliar-adm-id, direito-empresarial-brasileiro]
timestamp: 2026-10-20T00:00:00Z
---

# Societário da ID — contrato social, quotas e movimentação de sócios

## Quando usar

Qualquer pergunta de sócio sobre a **própria sociedade**: retirada, exclusão, cessão de quotas,
entrada de novo sócio, alteração contratual, pró-labore, distribuição de lucros, acordo de sócios,
registro na JUCESE — ou o genérico "o que o contrato social diz sobre X".

Não é redação de contrato com cliente (isso é `contratos-justos-id`) nem revisão de minuta recebida
(`analise-contratual`).

## Onde o documento está — e qual versão vale

- No Drive da ID existe um Google Doc `Contrato Social - iD.teal` que é **minuta com campos em
  branco** (sede, CNAE, data). **Não é a versão vigente** — usá-la produz resposta com cláusulas que
  não existem e sem os números reais.
- A versão que vale é o **PDF assinado** (`Contrato Social assinado`), 8 páginas, arquivado na JUCESE.
  Busque por `name contains 'contrato social'` com o token `admin@idconsultoria.ai`.
- **Extraia o texto com `pdftotext -layout arquivo.pdf saida.txt`** e leia o `.txt`: o `read_file`
  recusa PDF como binário nesse host, e OCR não é necessário quando o PDF tem camada de texto.
- Procure **alterações contratuais posteriores** (`name contains 'alteração'`, `JUCESE`) antes de
  responder. Cuidado: há no Drive uma "IV Alteração Contratual" de **outra empresa** (SERVICES) —
  conferir a razão social no cabeçalho do PDF antes de citar.
- O **Acordo de Sócios** citado na cláusula décima **prevalece sobre o contrato social**: nenhuma
  transferência de quotas ou exclusão pode ir contra ele, e ato em desconformidade é nulo. Se ele
  não estiver localizável, dizer isso explicitamente ao sócio como primeira pendência — nunca
  responder como se o contrato social fosse a palavra final.

## Retirada por vontade própria — procedimento, na ordem

1. O sócio pode se retirar **a qualquer tempo e por vontade própria** porque o prazo de duração é
   indeterminado (cláusula quarta + art. 1.029 do CC). Não precisa de justa causa.
2. **Notificação formal e escrita aos demais sócios, com 60 dias de antecedência**, informando a data
   da saída **e contendo proposta de venda das quotas ou de liquidação** (cláusula nona, I).
3. Nos **30 dias seguintes à notificação**, os sócios que ficam podem optar pela **dissolução da
   sociedade** em vez de seguir com a saída (art. 1.029, parágrafo único). O contrato não afastou
   esse direito — avise.
4. **Apuração dos haveres** pela fórmula da **cláusula oitava**, que o parágrafo único dela manda
   aplicar a qualquer resolução em relação a um sócio:
   `valor econômico = 3 × lucro líquido apurado nos últimos 12 meses` e
   `valor da quota = valor econômico ÷ total de quotas`. Pagamento em **até 24 meses**, parcelas
   sucessivas, corrigidas por índice oficial — o contrato afasta os 90 dias do art. 1.031, §2º, e
   disposição contratual em contrário é válida.
5. **Havendo ou não acordo sobre o valor**, o sócio retirante assina a alteração do contrato social
   em até **30 dias contados do fim dos 60** (cláusula nona, II). A saída não fica refém da
   negociação do valor — diga isso ao sócio, é o ponto que ele mais teme.
6. Registro da alteração na **JUCESE**, com redução do capital na proporção da quota, salvo se os
   remanescentes suprirem o valor (art. 1.031, §1º).

## Como ler o instrumento (regras que evitam resposta errada)

- A cláusula nona, I, manda liquidar "de acordo com o critério estabelecido na cláusula nona" —
  **referência circular**: o critério está na **oitava**. Cite a oitava e sinalize o defeito; é a
  fresta que o advogado do outro lado explora. Corrigir na próxima alteração.
- Sem cláusula específica de cessão, aplica-se o **art. 1.057** (oposição de titulares de mais de
  1/4 do capital; eficácia a partir da averbação). Com Acordo de Sócios, vale o acordo.
- **Não há cláusula de não concorrência pós-saída.** Concorrência desleal aparece apenas como causa
  de **exclusão** (cláusula nona, parágrafo segundo), não como restrição depois de sair.
- Deliberações: reunião de sócios com aviso de 7 dias, ata assinada; as matérias do parágrafo
  segundo da cláusula sétima exigem instrumento escrito.
- **Os percentuais de quota não são conhecimento permanente.** Leia a cláusula quinta do instrumento
  vigente em cada resposta; qualquer retrato em skill ou memória pode estar velho.

## Artigos — só citar com o texto conferido

Conferido no texto oficial (Planalto, `l10406compilada.htm`):

- **1.029** — retirada: prazo indeterminado → notificação aos demais com 60 dias; prazo determinado →
  justa causa provada judicialmente; parágrafo único: 30 dias para os demais optarem pela dissolução.
- **1.031** — quota liquidada pelo montante realizado, com base na situação patrimonial em balanço
  especialmente levantado, **salvo disposição contratual em contrário**; §1º redução do capital
  salvo suprimento pelos demais; §2º pagamento em 90 dias, salvo acordo ou estipulação.
- **1.057** — cessão de quota na omissão do contrato; oposição de mais de 1/4 do capital.
- **1.077** — retirada do **dissidente** em modificação do contrato, fusão ou incorporação, em 30
  dias. Não confundir com a saída voluntária.

Não citar número de artigo de memória: reler o trecho no Planalto (browser, `document.body.innerText`
+ busca do artigo) antes de escrever.

## Pitfalls

- **Ler a minuta em Google Docs em vez do PDF assinado** → resposta com cláusulas inexistentes e sem
  capital, quotas, sede e CNAE reais. Sempre o assinado.
- **Não procurar alteração posterior** → quadro societário desatualizado. Diga de qual instrumento e
  de que data você leu.
- **Ignorar o Acordo de Sócios** → resposta incompleta e possivelmente contrária ao documento que
  prevalece.
- **Confundir 1.029 com 1.077** → a segunda só existe em modificação/fusão/incorporação.
- **Responder como parecer jurídico.** O produto é leitura do instrumento + procedimento; a minuta da
  notificação, a alteração contratual e a memória de cálculo vão para revisão de advogado antes de
  qualquer uso.

## Entregável

Resposta em bullets no chat (o sócio lê no celular): procedimento **numerado na ordem em que
acontece**, prazos em negrito, e no fim os **defeitos e pendências** do instrumento. Ofereça, como
próximo passo, a minuta da notificação de retirada e a memória de cálculo dos haveres.
