---
name: contrato-prestacao-servicos-b2b
description: "Use ao redigir contrato de prestação de serviços B2B."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [contrato, b2b, prestacao-de-servicos, parceiro, aviso-previo, representacao, brasil]
    related_skills: [contratos-justos-id, direito-empresarial-brasileiro, revisao-de-proposta-existente]
type: Orchestrator
timestamp: 2026-11-03T00:00:00Z
---

# Contrato de prestação de serviços B2B — redação operacional

Skill de execução para **escrever o contrato do zero** a partir de uma proposta fechada, quando
o prestador **não é a ID Consultoria** (parceiro/agência que fatura o cliente) ou quando a ID
entrega dentro do pacote de um parceiro. Complementa as skills de direito (que dizem o que é
possível) e `contratos-justos-id` (tom e identidade da ID) — essas são do usuário e não são
editáveis por curadoria; aqui ficam o **esqueleto e as regras de redação**.

## Ordem de trabalho

1. **Fixar a fonte do combinado**: proposta aceita, mensagens e decisões do sócio. Os números do
   contrato são os da proposta **com as correções do dono**, não os da versão antiga.
2. **Qualificar as duas partes com dado verificável** (cartão CNPJ, não memória do nome
   fantasia): razão social, CNPJ, endereço com CEP e quem assina por cada lado.
3. **Checar poderes de representação** antes de tudo (regra abaixo). Marcar `[•]` no que
   depende do cliente (CPF dos signatários, CEP faltante, chave Pix, dia de vencimento,
   data/local) em vez de inventar.
4. **Escolher o desenho** (prestador único × dois contratos independentes × tripartite) e
   registrar a decisão.
5. **Redigir** pelo esqueleto de `templates/contrato-servicos-b2b.md` (13 cláusulas + Anexo I).
6. **Conferir a aritmética** de cada mês contra a proposta e a cronologia de entrega — em
   `execute_code`, nunca de cabeça.
7. **Gerar o documento** na identidade de quem emite e verificar antes de entregar.
8. **Gate humano**: a minuta só sai para assinatura com ok explícito do principal.

## Regras de redação (as que custam dinheiro)

- **Quem negocia não é necessariamente quem assina.** Cruze o CNPJ no quadro societário: se o
  interlocutor do negócio não é sócio/administrador do CNPJ contratante, o contrato **não
  obriga a empresa** sem procuração com poderes específicos anexada. Qualifique pelo
  administrador que assina e sinalize o ponto ao sócio antes de enviar.
- **Sem fidelidade + aviso prévio de 30 dias → remuneração do aviso, não multa.** "Paga
  integralmente as mensalidades relativas ao período dos 30 dias de aviso, os valores vencidos
  e as etapas já entregues". Chamar o mesmo valor de multa abre discussão de teto (art. 412 do
  CC) e de redução equitativa (art. 413).
- **Custo variável de plataforma de terceiro fica fora do preço**: mídia paga direto à Meta
  (conta e cartão do cliente), mensagens/templates da API oficial do WhatsApp cobrados pela
  Meta. O prestador não intermedeia, não recebe, não responde — e o cliente não perde a conta
  de anúncio ao encerrar.
- **Aceite por etapa com prazo curto e silêncio como aceite** (5 dias úteis): sem isso o
  prestador fica refém de aprovação indefinida para faturar o marco entregue.
- **Escopo negativo sempre**, mesmo em versão enxuta: mídia, templates fora da janela de 24 h,
  integração sem acesso, imagens com drone, contratação/substituição de pessoal, garantia de
  volume de vendas ou de resultado comercial.
- **PI em duas faixas**: método, prompts, agentes e bibliotecas ficam do prestador (licença de
  uso na vigência); conteúdo produzido pode ser usado pelo cliente nos canais dele, vedada
  revenda. Vedação explícita de treinar IA com dado do cliente.
- **LGPD**: cliente = controlador, prestador = operador; instruções, incidente em 24 h,
  devolução/eliminação ao término.
- **Ao término**: cessam acessos e manutenção, mas **base de clientes, número de WhatsApp e
  dados ficam com o cliente**; o prestador entrega conteúdos e acessos sob sua gestão. Cláusula
  curta que evita a discussão mais comum na rescisão.
- **Limitação de responsabilidade**: sem garantia de resultado comercial; teto no valor pago
  nos últimos 3 meses; excluídos lucros cessantes e danos indiretos.
- **Reajuste anual** pelo IPCA e mora convencional (2% + 1% a.m.), com suspensão após 15 dias de
  atraso e prazos prorrogados pelo período da suspensão.

## Contrato emitido por terceiro (parceiro que fatura o cliente)

Quando a entrega de uma empresa é embalada no contrato de um parceiro, **o instrumento é do
parceiro**: identidade visual dele, obrigações dele, risco dele. Consequências práticas:

- **Não** usar timbrado, logo ou identidade da empresa que apenas executa parte do escopo; o
  documento leva a marca de quem emite (cores e fontes do parceiro).
- A empresa executora se protege por **instrumento próprio com o parceiro**, que o cliente não
  vê: divisão de frentes, ponto focal e prazo de entrega de material (criativo que atrasa quebra
  a promessa de "processo único"), responsabilidade separada com direito de regresso, não
  abordagem do cliente, sigilo e **mesma data de saída** do contrato principal.
- Se a empresa executora **fatura direto** o cliente, são **dois contratos independentes** com o
  mesmo aviso prévio: evita faturar receita de terceiro (ISS/retenção) e responder por entrega
  alheia. Nesse desenho, o preço se divide por frente e a soma tem de fechar exatamente com a
  proposta que o cliente já viu.

## Entrega do documento

- Gerar em Google Doc na identidade de quem emite (receita e gotchas em `doc-brand-theming`) e
  exportar PDF versionado (`..._v1_<descrição>.pdf`).
- Verificar antes de declarar pronto: nº de páginas A4, fontes embutidas no PDF, quebras de
  página (bloco de assinatura não pode cair sozinho na página seguinte) e o conteúdo de cada
  tabela conferido no JSON do documento.
- Listar na resposta **o que ficou preenchido, o que ficou `[•]` e quais decisões você tomou**
  (aceite tácito, reajuste, teto de responsabilidade, custos de terceiros) para o sócio vetar.

## Pitfalls

1. **Reaproveitar os números da versão anterior da proposta.** O dono muda o desenho (ex.:
   antecipar a segunda implantação para o mês 1) e o contrato tem de refletir isso, inclusive
   dizendo expressamente que a parcela é devida antes da entrega daquela etapa.
2. **Qualificar pelo nome fantasia.** O CNPJ que assina é a razão social; nome fantasia vai como
   nome fantasia.
3. **Assumir que o grupo do cliente é um CNPJ só.** Rede com várias lojas pode ter titulares
   distintos: definir quais estabelecimentos o contrato abrange ou colher anuência dos demais.
4. **Deixar serviço "de brinde" com valor escrito.** Bônus sem preço no documento;
   justificativa de preço é conversa, não cláusula.
5. **Fechar o contrato sem anexo de escopo.** O Anexo I (incluído / não incluído / o que o
   cliente fornece / etapas) é o que evita a discussão na primeira cobrança.

## Arquivos

- `templates/contrato-servicos-b2b.md` — esqueleto completo em markdown (13 cláusulas + Anexo I
  + bloco de assinaturas) pronto para preencher e converter em Google Doc.
- Skills do usuário que complementam: `contratos-justos-id` (DNA e identidade da ID),
  `direito-empresarial-brasileiro` (cláusulas e mapa normativo).
