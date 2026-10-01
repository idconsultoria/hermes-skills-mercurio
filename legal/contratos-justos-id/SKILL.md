---
name: contratos-justos-id
description: "Use ao redigir contrato justo que beneficie a ID."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [contratos, minuta, id-consultoria, b2b, risco, lgpd, propriedade-industrial, negociacao]
    related_skills: [direito-empresarial-brasileiro, direito-civil-brasileiro, direito-do-consumidor, analise-contratual, formalizacao-acordo-cliente]
type: Orchestrator
timestamp: 2026-09-30T20:45:00Z
---

# Contratos justos, simples e benéficos à ID Consultoria

## Overview

Skill de **aplicação**: como redigir, pela mão da ID Consultoria, contratos que sejam **justos**
(legais e equilibrados), **simples** (o cliente entende sem advogado) e **muito benéficos à ID**
(preservam o ativo, o caixa e a relação). Não é um skill de direito — é o skill de **como usar
o direito a favor da ID sem virar o cliente contra ela**.

Consome, nesta ordem:
1. `direito-empresarial-brasileiro` — regime, riscos e cláusulas (a lei diz o que é possível).
2. `direito-civil-brasileiro` — parte geral, obrigações, se o caso for civil.
3. `direito-do-consumidor` — se a ponta for consumidor.
4. `analise-contratual` — se a ID estiver sendo subcontratada.
5. `formalizacao-acordo-cliente` — depois, para enviar o formalizado.

**A tese central:** contrato não é trincheira, é **aliança com regras claras**. O desenho que
protege a ID e que o cliente aceita é o que **não** depende de ganhar uma discussão. Aliança
se constrói assim: a ID **diz o preço, o prazo e o risco com clareza**, assume o que é dela,
marca o que não é, e entrega o que prometeu. Cliente que lê contrato simples assina; cliente
que briga no item 5YPE questiona o resto.

## Quando usar / quando não usar

**Use quando:**
- O principal pede "minuta de contrato", "contrato para o cliente X", "formaliza o que
  fechamos", "elabora o contrato do projeto Y".
- Precisa revisar uma minuta existente **antes** de enviar para assinatura.
- Quer **padronizar** a forma como a ID contrata (para não redigir do zero toda vez).
- Precisa saber o que **sempre** entra num contrato da ID e o que é negociável.

**Não use para:**
- Analisar risco de uma minuta **recebida** de cliente → `analise-contratual`.
- Enviar email formalizando acordo → `formalizacao-acordo-cliente`.
- Emitir NFS-e → `emissao-nfse`.
- Questão puramente jurídica sem documento → skills de direito.

## Os sete princípios do contrato justo da ID

Cada princípio responde a uma pergunta que o cliente sempre faz por baixo da mesa.

### 1 · Clareza antes de defesa

Cada cláusula existe porque alguém vai perguntar "e se?" — e a resposta precisa estar escrita.
Escreva a pergunta junto com a resposta, no mesmo parágrafo.

> ❌ "A CONTRATADA não se responsabiliza por terceiros."
> ✅ "A CONTRATADA não responde por indisponibilidade de serviços de terceiros (provedores de nuvem, APIs de terceiros, emissão de certificados digitais, bases oficiais), desde que os tenha comunicado previamente à CONTRATANTE e adotado providências razoáveis para contorná-los."

O segundo custa três linhas e **não é discutido**. O primeiro é curto, genérico e **não protege
nada** — ninguém assina o que é vago.

### 2 · Escopo fechado com exclusão listada

O cliente precisa saber o que **entra** e o que **não entra**. "Escopo fechado + lista do que
fica fora + aditivo com novo preço" é a estrutura que impede scope creep sem soar defensivo.

### 3 · Risco com gatilho, limite e procedimento

Se o risco vai contra a ID, ele precisa de **gatilho** (o evento), **limite** (o teto) e
**procedimento** (como se aplica). Sem os três, é intenção, não cláusula. Ver
`references/dna-contrato-id.md` para a anatomia e `redline-risco-b2b` (skill empresarial) para
o texto pronto.

### 4 · Pago no marco, não na fase

Cada parcela é **um marco entregue**, não um mês que passou. Se o cliente atrasar, o ID para de
mobilizar — e isso está escrito, com data. Não é "o cliente sabe?".

### 5 · Patrimônio primeiro, flexibilidade depois

O ativo da ID é o **método, o know-how, a base reutilizável e o dado**. Cesão expressa do
entregável **após quitação**, reserva de preexistentes, e **vedação de treino de IA** com dado
do cliente. Sem isso, um cliente que recebeu um sistema construído com a base da ID pode, no
futuro, alegar coautoria.

### 6 · Culpa repartida, culpa declarada

Cláusula "ISO" não é justa com ninguém. O cliente é,ITCELLULAR responsável por **dado errado,
acesso indevido, dependência externa**; a ID é responsável por **entrega, prazo (com as
prorrogações acordadas), garantia e segurança (com o que ela controla)**. Declarar isso
escritamente é mais justo — e mais defensável — do que cláusula "a CONTRATADA responde por
tudo".

### 7 · Curto o bastante para ser lido

Contrato que ninguém lê é contrato que ninguém cumpre. Alvo da ID: **8 a 14 páginas** para
projeto de sistema; **4 a 6** para treinamento. Se passar disso, há anexo descritivo.

## O que a ID **nunca** escreve (e por quê)

| Nunca escrever | Por quê | O que escrever no lugar |
|---|---|---|
| Justificativa de preço (custo, margem, "projeto de aprendizagem") | Dá âncora e vira alavanca na próxima rodada | Escopo, prazo, quem executa, quem supervisiona, garantia |
| "Locação de mão de obra" / "fornecimento de profissionais" | Caracteriza errado e cria risco trabalhista e de subordinação | "entrega de resultado nos termos deste contrato", com equipe própria e supervisionada |
| Renúncia genérica a responsabilidade | Não é honesta, não sobrevive e mancha a confiança | Limite de responsabilidade com gatilho e procedimento |
| Multa acima do teto do art. 412 do CC | Risco de nulidade parcial | 2% + 1% a.m. sobre a parcela |
| Confidencialidade de 1 ano em projeto com ativo reutilizável | Enfraquece a proteção real | 5 anos + dever permanente sobre segredo |
| Foro de consumidor quando é B2B | Em B2B, segue a regra da empresa | Foro da Comarca de Aracaju/SE (padrão ID) |
| Jargão sem explicar (ex.: "clawback") | Cliente não entende e não assina | Descrever o efeito em português claro |

## Checklist do "contrato justo" — revisão antes de enviar

### Clareza
- [ ] O cliente lê o resumo de 1 página e entende o que recebe?
- [ ] Cada cláusula negativa tem o seu "e se?" respondido?
- [ ] Não há jargão sem explicação?

### Equilíbrio (o cliente vai achar justo?)
- [ ] A proporção entre obrigações da ID e do cliente é visível?
- [ ] Há alguma cláusula que um advogado do cliente chamaria de abusiva? Reescreva.
- [ ] O cliente tem alguma **saída** legítima (rescisão com aviso, aditivo, rejeição fundamentada)?
- [ ] A garantia da ID sobrevive ao atraso de pagamento? (Sim — é justo e é o contrapeso.)

### Benéfico à ID
- [ ] Entrada cobre custo antes de mobilizar?
- [ ] Cada parcela amarrada a marco entregue?
- [ ] Escopo fechado com exclusão listada e aditivo?
- [ ] Dependência do cliente prorroga prazo automaticamente?
- [ ] PI: cessão expressa + reserva de preexistentes + vedação de treino de IA?
- [ ] LGPD: papel, instruções, incidente 24 h, suboperadores, eliminação?
- [ ] Ausência de aceite tácito, com prazo correndo a favor da ID?
- [ ] Suspensão por atraso de pagamento prevista?
- [ ] Sucessão/mudança de controle com anuência?
- [ ] Segredo industrial com prazo que proteja o ativo?
- [ ] Foro de Aracaju, aditivo por escrito, testemunhas?

### Go/no-go
- [ ] **Duas vias** (se contrato físico).
- [ ] Anexo de escopo assinado.
- [ ] Minuta **não vai** ao cliente sem revisão do principal (gate humano).
- [ ] Versão numerada e com data (não reenviar o mesmo nome).

## Fluxo de trabalho — do combinado ao assinado

1. **Recolher o combinado**: e-mail/proposta/thread, valores, prazos, marcos, quem assina.
   Conferir a fonte (não de memória; ver `formalizacao-acordo-cliente`).
2. **Enquadrar juridicamente** com `direito-empresarial-brasileiro`: empresarial? B2B?
   Registrar a decisão no topo da minuta.
3. **Escolher o desenho**: escopo fechado (projeto) × escopo ágil (backlog) × treinamento.
   Ver `references/arquetipos-contrato-id.md` para qual usar.
4. **Redigir** a minuta com o DNA (`references/dna-contrato-id.md`) + cláusulas prontas da
   skill empresarial.
5. **Checar** com o checklist acima e com `checklist-due-diligence-contratual` (skill
   empresarial).
6. **Entregar ao principal para revisão** (gate humano). Uma coisa de cada vez.
7. **Só depois** gerar o documento final (papel timbrado / PDF) e enviar para assinatura.
8. **Registrar** em [ID] Gestão de Symplexis (aba contratos) e, ao assinar, em
   `1.1.4. Contratos assinados`.

## Redesenhando a experiência do cliente

O contrato é a **primeira entrega** que o cliente recebe da ID — e alguns clientes só
descobrem a qualidade da consultoria quando o leem. Três toques finais que a ID aplica:

- **Resumo de 1 página** antes das cláusulas: o que é, quanto, quando, quem faz, garantias.
- **Anexo de escopo** com o *que está incluído* e *o que não está*, em linguagem de negócio.
- **Assinatura com 2 testemunhas** (recomendado em via física) — o custo é zero e evita
  discussão sobre força probatória.

## Pitfalls da ID (aprendidos em contrato real)

- **Nunca explique a formação do preço no documento.** Vira alavanca. A justificativa fica na
  conversa, por email.
- **Contrato em nome da ID, não em nome do sócio.** CNPJ 54.569.818/0001-59, razão social
  completa, sócio-administrador que assina e tem poderes. Erro aqui é dor de cabeça anos depois.
- **Dois contratos, não um** — quando são duas frentes com marcos e riscos distintos (ex.: um
  sistema + um treinamento). Um contrato misto vira disputa sobre escopo na cobrança.
- **Não deixe case/logo no contrato sem gotten por escrito.** Autorização de case é mais
  valiosa que desconto — e precisa de prazo de resposta do cliente.
- **Nomeie o arquivo com versão e data.** Contrato reenviado sem versão vira ambiguidade de
  assinatura.

## Arquivos desta skill

- `references/dna-contrato-id.md` — a arquitetura do contrato justo da ID: seções padrão,
  anatomia da cláusula, ordem de leitura, com o porquê de cada escolha.
- `references/arquetipos-contrato-id.md` — três arquétipos (projeto de sistema · treinamento ·
  consultoria ágil), com o esqueleto de cada um e quando usar cada.
- Skill de direito: `direito-empresarial-brasileiro` (cláusulas prontas, mapa normativo).
- Skill de análise: `analise-contratual` (quando a ID recebe minuta alheia).
- Skill de envio: `formalizacao-acordo-cliente`.

## Disclaimer

> Minuta elaborada pela equipe da ID Consultoria com apoio de assistente de IA, à luz da
> legislação vigente e da negociação entre as partes. Este documento **não substitui revisão
> jurídica profissional**: recomenda-se a leitura por advogado(a) antes da assinatura,
> especialmente quanto a propriedade intelectual, dados pessoais (LGPD) e tributação. A ID
> recomenda que o cliente, se desejar, submetê-lo ao próprio jurídico.
