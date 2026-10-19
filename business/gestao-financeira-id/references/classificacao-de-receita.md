# Classificação de transações e receita (Gestão Financeira ↔ Symplexis)

Depth para decidir **onde** uma transação entra e **como reconhecer** o que ela é. As regras
de quando lançar (pré-condição de projeto existente, transferência entre contas da ID) estão
no SKILL.md; aqui fica o mapa das colunas, o vocabulário e os valores observados.

## Aba `transações` (Gestão Financeira) — 20 colunas

| Col | Campo |
|---|---|
| A | `#` (numeração) |
| B | `Status` |
| C | `ID Transação` (base64 do Inter — copiar inteiro) |
| D | `Data` |
| E | `Valor` |
| F | `Centro de Custo` |
| G | `Projeto` |
| H | `Dimensão` |
| I | `Categoria` |
| J | `Sub-categoria` |
| K | `Descrição refinada` |
| L | `Descrição no extrato` |
| M | `Anexos` |
| N | `Pasta de anexos` |
| O | `pasta_de_anexos_url` |
| P | `Mês de competência` |
| Q/R/S | Composição no Lucro Líquido / no EBITDA / no OPEX ou LB |
| T | `Racional da IA` |

**F–K vazias e status `A processar` = transação recém-chegada da automação, ainda não
classificada.** É o estado normal de um crédito de ontem — não é erro nem "já registrado".

Vocabulário de `Status`: `A processar` · `Anexos pendentes` · `Processada` ·
`Processada por IA`.

A GF classifica; a Symplexis espelha por IMPORTRANGE na aba `_transações` — a mesma transação
aparece nas duas planilhas com o mesmo `ID Transação` (confira por esse campo, não por valor).

## Valores de classificação observados

- **Receita de cliente:** F `Receita` · G `<Cliente> - <Contrato> - <Symplexi>` (exatamente o
  rótulo de `__projetos`) · H `Recebimento` · I `Faturamento` · J `Parcela de contrato`
  (ou `Parcela/Serviço Adic.` quando valor/escopo diferem do previsto em contrato).
- **Imposto:** F `Receita` · G `Gestão Interna` · I `Imposto` · J `Simples Nacional`.
- **Projeto não identificado:** G `Projeto a Identificar` (por vezes `<Cliente> - Projeto a
  Identificar`) — sinaliza crédito de cliente sem contrato correspondente na Symplexis. Não é
  classificação final: é o marcador de que falta cadastro.
- **Centros de custo válidos** (aba `parâmetros`, coluna `centros de custo`): `Ferramentas`,
  `Pessoas`, `Comercial`, `Operação`, `Receita`, `Gestão`, `Marketing`, `Lucro`. A coluna
  `projetos` da mesma aba é o catálogo aceito — projeto fora dela não entra em relatório.

## Detectar transferência entre contas da mesma titular

`CCI_detalhes_PIX` traz, por transação, os campos que decidem:
`nomePagador`, `cpfCnpjPagador`, `nomeEmpresaPagador`, `descricaoPix`, `endToEndId`,
`chavePixRecebedor`, `nomeRecebedor`.

- `cpfCnpjPagador` = CNPJ da própria ID **e** `nomeEmpresaPagador` = `NU PAGAMENTOS - IP` ⇒
  o crédito veio de outra conta da ID (Nubank → Inter): a perna do Inter é **transferência
  interna**, e a venda real está descrita em `descricaoPix` (ex.: venda de vaga de curso a PF).
- `CCI_extrato` mostra só `título` e o nome do pagador — para saber *o que* foi a operação é
  preciso o detalhe em `CCI_detalhes_PIX`.

## Inventário: dizer se algo "está na planilha de Symplexis"

Abas que respondem a pergunta (última linha de cada grade é o corte real):

| Aba | O que é |
|---|---|
| `symplexis` | frentes de entrega — uma linha por symplexi (`SM3-1`), com consultor, prazo, horas, entregáveis |
| `contratos` | iD (ex. `SM2`), rótulo, cliente, status, valor total, data de assinatura, oferta |
| `recebimentos` | **uma linha por parcela**; `Data efetuada` é fórmula que resolve pelo `iD.Transação` |
| `clientes` | cadastro de empresas (contato principal, e-mail, telefone) |
| `consultores` | pessoas alocáveis |
| `__projetos` | catálogo `iD.contrato / cliente / contrato / symplexi / detalhado` |
| `_transações` | espelho da `transações` da Gestão Financeira (IMPORTRANGE) |
| `Tabela dinâmica 1`, `conexões`, `sankey_*` | visões derivadas — não são fonte |

**Não existe aba de turmas, alunos ou vendas a pessoa física.** Venda de curso a PF não cabe
no modelo contrato/parcela (o `recebimentos` resolve cliente/contrato por VLOOKUP) — ausência
nessas abas significa ausência, não "linha escondida": confirme com `find` antes de dizer que
está, e relate a ausência em vez de fabricar cadastro.
