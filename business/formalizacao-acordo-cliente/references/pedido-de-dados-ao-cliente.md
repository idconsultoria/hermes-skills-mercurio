# Pedir dados ao cliente para fechar o documento

Quando o documento (contrato, termo, proposta) depende de dados que só o cliente tem, a entrega
não para: o documento sai com marcadores visíveis e o pedido vai junto, pronto para uso.

## Marcadores no documento

Use marcadores angulares visíveis no corpo — `«RAZÃO SOCIAL», «CNPJ», «ENDEREÇO COMPLETO»,
«Nome do representante legal»` — em vez de deixar a cláusula em branco ou inventar dado. Eles são
acháveis por busca e substituíveis por `replaceAllText` quando a resposta chegar, sem regerar o
arquivo.

## Lista de pendências separada, em duas classes

Nunca misture o que é do cliente com o que é decisão da ID:

- **Só o cliente informa** — razão social, CNPJ, endereço da sede, qualificação completa de quem
  assina (nome, nacionalidade, estado civil, profissão, RG/órgão emissor, CPF), e-mail oficial para
  comunicações.
- **Decisão da ID** — vigência, multa, data de assinatura. Essas não se pergunta ao cliente; vai ao
  principal.

## O pedido sai em bloco copiável (WhatsApp)

O principal é quem repassa o pedido. Entregue um **único bloco de código** com a marcação do
WhatsApp (`*negrito*`), numerado, pedindo exatamente os campos que faltam e fechando com a
promessa do próximo passo ("assim que me mandar, preencho e envio para assinatura"). Nada de
lista em markdown solta nem de pedido redigido como parágrafo de conversa: ele copia, cola e envia.

## Dados da ID não se pedem — vêm de contrato canônico

A qualificação da ID já está em contrato assinado. Copie do parágrafo da CONTRATADA de um contrato
recente: **iD.teal Consultoria em Gestão Organizacional LTDA**, nome fantasia ID Consultoria e
Treinamento, CNPJ 54.569.818/0001-59, sede na Rua Manoel Espírito Santo, nº 165, Sala 02, Bairro
Grageru, Aracaju/SE, CEP 49.025-440, assinando Gustavo Alexandre Souza Mello, Sócio-Administrador,
RG 369.746-76 – SSP/SE, CPF 076.429.105-09; comunicações por **contato@idconsultoria.ai**.

## Ao receber as respostas

Aplique por `replaceAllText` no doc já existente (mecânica em `edicao-incremental-de-gdoc`) e
renomeie o arquivo com versão nova — não reenvie o mesmo nome, o cliente precisa saber qual versão
está assinando.
