---
name: direito-do-consumidor
description: "Direito do consumidor brasileiro (Lei 8.078/90 — CDC) — revisão de contratos e peças.

Load this skill when the task involves Brazilian consumer law: relações de consumo e enquadramento (arts. 2º-4º), práticas e cláusulas abusivas (arts. 39, 51-54), publicidade e oferta (arts. 30, 36-38, 48-49), cobrança indevida e negativação (arts. 42-43, 71), vício/defeito/acidente de consumo (arts. 12-20), responsabilidade objetiva com inversão do ônus da prova (art. 6º, VIII), relações bancárias e superendividamento (Lei 14.181/2021) e Juizados Especiais. Produz memos, redlines e petições em rascunho para revisão por advogado(a), com citação fonte-a-fonte e gate humano antes de qualquer envio."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [legal, cdc, direito-do-consumidor, brasil, juizados, clausulas-abusivas]
    related_skills: [direito-civil-brasileiro]
type: Reference
timestamp: 2026-08-23T19:20:00Z
---

# Direito do Consumidor (CDC)

## Overview

Skill de prática em direito do consumidor brasileiro, irmã de `direito-civil-brasileiro` e referenciada por ela como roteiro obrigatório para relações de consumo. Nos moldes das skills de prática jurídica da coleção *Claude for Legal* (Anthropic), adaptada ao CDC — Lei nº 8.078/1990 — e à sua jurisprudência consolidada (STJ responde pela uniformização).

Mesmas três marcas herdadas:

1. **Rascunho para revisão por advogado(a).** Toda saída é minuta para revisão, verificação e assunção de responsabilidade profissional. Não é parecer nem opinião vinculante.
2. **Citação com fonte em toda afirmação.** Lei + artigo; súmula + número; julgado verificado online antes de citar número/data.
3. **Gate humano antes de qualquer peça sair.** Nada é protocolado, enviado ou tratado como confiável sem ok explícito do(a) advogado(a).

**Data-base:** legislação e jurisprudência até meados de 2026, com verificações pontuais online durante o uso.

## Quando usar / quando não usar

**Use quando:**
- Enquadrar uma relação como de consumo ou não (arts. 2º-3º; teoria finalista e finalista agravada).
- Revisar contratos de adesão e contratos padronizados (arts. 54); identificar cláusulas abusivas (arts. 51-53) e práticas abusivas (art. 39); redigir redline.
- Analisar vícios de qualidade (arts. 18-20), defeito/acidente de consumo (arts. 12-17), fato do produto × vício.
- Cobrança indevida, duplicidade de cobrança, negativação indevida, dano moral por inscrição irregular (arts. 14, 42, 43, §2º; Súmula 479/STJ).
- Bancário: tarifas abusivas, capitalização, superendividamento (Lei nº 14.181/2021, arts. 54-A ss.), revisão contratual.
- Publicidade enganosa/abusiva (arts. 30, 36-38), venda porta a porta/domicílio (art. 49), coleta de dados do consumidor (art. 43, §3º-§5º).
- Peças: ação no JEC (Lei nº 9.099/95, até 40 salários mínimos sem advogado; acima disso com), ação ordinária, recurso inominado; defesa de fornecedor.
- Triagem de demandas em massa (padrão de conduta repetido pelo fornecedor → estratégia de teses padronizadas).

**Não use para:** relação entre empresas integrando cadeia produtiva sem destinatária final (→ `direito-civil-brasileiro`), trabalhista, tributário, penal (exceto sinalizar crimes previstos no CDC arts. 66-72, p.ex. art. 71 — cobrança vexatória, que é penal e civil ao mesmo tempo).

**Nota LGPD:** tratamento de dados pessoais é regido pela Lei nº 13.709/2018; o CDC toca no tema (art. 43 §§3º-5º, cadastro do consumidor) mas não o substitui. Se a questão for núcleo LGPD, sinalize que a análise completa exige trilho próprio (a skill trabalha a interface CDC+LGPD, ex.: vazamento de dados como acidente de consumo).

## Fluxo de trabalho

1. **Enquadrar a relação** — consumidor × fornecedor × produto/serviço (arts. 2º-3º). Empresário pode ser consumidor (finalista agravada). Logue o enquadramento no topo do produto.
2. **Identificar o regime material:** vício (arts. 18-20 — responsabilidade por correção/substituição/restituição, independe de culpa) × defeito/acidente (arts. 12-17 — responsabilidade objetiva por danos causados) × práticas/cláusula abusiva (arts. 39, 51) × publicidade (arts. 36-38).
3. **Mapear fontes primárias:** CDC navegável em `references/cdc-map.md`; jurisprudência sumulada e temas repetitivos em `references/jurisprudencia-chave.md`.
4. **Verificar externamente o volátil:** números de julgados, temas recentes, mudanças regulatórias (CMN/BACEN, ANATEL, ANVISA) — `web_search` em fonte oficial; logue data da verificação ou flag `[verificar]`.
5. **Calcular o que for calculável:** prazos decadenciais/prescricionais próprios do CDC (tabela abaixo), valor da causa, multas do art. 42, parágrafo único (repetição do indébito em dobro).
6. **Produzir entregável:** memo, redline, ou petição (`templates/memo-consumidor.md`, `templates/peticao-jec.md`).
7. **Fechar com disclaimer + pendências + gate humano.**

## Enquadramento — decisões rápidas

| Situação | Enquadramento | Fundamento |
|---|---|---|
| PF compra celular para uso próprio | Consumidor | CDC art. 2º |
| ME compra insumo para revender | Não é consumidor | finalista clássica |
| ME compra computador para uso administrativo | Consumidor (jurisprudência) | finalista agravada |
| Fornecedor PJ de app, banco, loja | Fornecedor | CDC art. 3º |
| Profissional liberal (médico, advogado) | Regra: fora do CDC; exceção se prometer resultado | CDC art. 14, §4º |
| Profissional liberal promete resultado (ex.: cirurgia estética com promessa) | CDC aplica-se | jurisprudência — verificar tese vigente |
| Compra entre particulares (PF→PF, ocasional) | Fora do CDC | sem profissionalidade |
| Plataforma/marketplace | Responsabilização do intermediador em discussão no STJ — confirmar tese vigente | verificar |

Regra de log: `Enquadramento: [CDC | não-CDC] porque ...` no topo de todo memo/peça.

## Vício × defeito × abuso — decidir o regime

| Fato típico | Regime | Artigos | Prazo |
|---|---|---|---|
| Celular novo com tela com defeito | **Vício** (qualidade/quantidade) | art. 18 | 30 dias impróprio/não durável... ver tabela de prazos |
| Carro novo com problema crônico na direção | Vício (aparente/de fácil constatação) | arts. 18, 26 | ver prazos |
| Airbag não dispara e fere o motorista | **Acidente/defeito** | arts. 12-17 | prescrição 5 anos (art. 27) |
| Medicamento com efeito colateral não avisado | Defeito (falha de informação) | arts. 6º, III, 9º, 31, 12 | art. 27 |
| Banco cobra tarifa não pactuada | Prática abusiva | art. 39 | prescrição comum |
| Contrato com foro de eleição contra consumidor | Cláusula abusiva (nula) | art. 51 | nulidade de pleno direito |
| Propaganda com preço que a loja não honra | Publicidade enganosa (vincula) | arts. 30, 37 | — |

**Vício aparente × oculto:** aparente/de fácil constatação — 30 dias (produto/serviço não durável) / 90 dias (durável), contados da entrega efetiva ou término da execução (art. 26, *caput* e §1º); vício oculto — prazo conta-se do momento em que ficar evidenciado o defeito (art. 26, §3º). Obstam a decadência: reclamação comprovadamente formulada junto ao fornecedor até a resposta negativa (art. 26, §2º, I) e instauração de inquérito civil até seu encerramento (art. 26, §2º, III — o inciso II foi vetado).

## Cláusulas abusivas — checklist do art. 51

Nulas de pleno direito, entre outras (art. 51 — incisos conferidos no texto oficial):
- impossibilitar, exonerar ou atenuar a responsabilidade do fornecedor por vícios, ou implicar renúncia/disposição de direitos (I) — entre PJ, a lei admite limitação de indenização em situações justificáveis;
- subtrair ao consumidor a opção de reembolso da quantia paga (II);
- transferir responsabilidades a terceiros (III);
- impor obrigações iníquas que coloquem o consumidor em desvantagem exagerada ou ofendam a boa-fé/equidade (IV; presunções do §1º, I-III);
- estabelecer inversão do ônus da prova em prejuízo do consumidor (VI);
- determinar a utilização compulsória de arbitragem (VII);
- permitir variação unilateral de preço (X), cancelamento unilateral sem simetria (XI), cobrança dos custos de ressarcimento sem simetria (XII) ou modificação unilateral de conteúdo/qualidade (XIII);
- condicionar ou limitar o acesso ao Judiciário (XVII, incluído pela Lei nº 14.181/2021).
- Foro de eleição diferente do domicílio do consumidor não está listado no art. 51, mas é combatido pela jurisprudência — o CDC dá o foro ao consumidor no art. 101, I.

Redline padrão: para cada cláusula abusiva → citação literal + fundamento (artigo + inciso conferido no Planalto) + severidade + linguagem substitutiva compatível com contrato de adesão (art. 54: interpretação mais favorável ao consumidor; cláusulas ambiguas prevalecem na leitura menos onerosa — art. 47).

## Prazos do CDC — tabela de trabalho

| Situação | Prazo | Natureza | Fundamento |
|---|---|---|---|
| Vício aparente, produto não durável | 30 dias | decadencial | art. 26, I |
| Vício aparente, produto/serviço durável | 90 dias | decadencial | art. 26, II |
| Vício oculto | conta da data em que o defeito ficar evidenciado | decadencial | art. 26, §3º |
| Reclamação comprovada junto ao fornecedor | obsta a decadência até a resposta negativa | impedimento | art. 26, §2º, I |
| Acidente de consumo (defeito) | 5 anos | prescricional | art. 27 |
| Fato do serviço com dano (ex.: queda de agência) | 5 anos | prescricional | art. 27 |
| Repetição de indébito (cobrança sem causa) | 10 anos (CC art. 205, aplicado por analogia — orientação dividida; confirmar) | prescricional | CC art. 205 |
| JEC: recurso inominado | 10 dias | processual | Lei 9.099/95, art. 42 |

⚠️ O texto integral do art. 26 — incluindo os incisos vetados — está transcrito em `references/cdc-map.md` (extraído do texto oficial). Consulte-o em vez de citar incisos de memória; a mesma regra vale para o art. 51.

## Indébito e dano moral — parâmetros

- **Repetição em dobro**: cobrança indevida gera repetição do indébito "por valor igual ao dobro do que pagou **em excesso**, acrescido de correção monetária e juros legais", salvo engano justificável (art. 42, parágrafo único — texto conferido). Não é dobro do total pago, salvo se tudo foi indevido.
- **Negativação indevida**: dano moral *in re ipsa* quando não há inscrição legítima preexistente (regra da Segunda Seção; a exceção está na Súmula 385/STJ — texto em `references/jurisprudencia-chave.md`); exclusão do cadastro após pagamento integral em 5 dias úteis (Súmula 548/STJ).
- **Parâmetros de fixação**: dupla perspectiva (reposição + satisfação), proporcionalidade, vedação ao enriquecimento sem causa; valores variam por região e gravidade — nunca cite "valor médio" inventado; pesquise orientação atual quando o caso exigir quantum.
- **Bancário**: capitalização em periodicidade inferior à anual exige previsção expressa (MP 2.170-36/2001, art. 5º — conferir norma vigente); tarifas só as pactuadas e autorizadas (Resoluções CMN — conferir lista vigente); superendividamento: Lei 14.181/2021 acrescentou arts. 54-A ss. (crédito responsável, repactuação).

## Publicidade e oferta

- Oferta vincula (art. 48): preço, prazo, condições anunciadas devem ser honradas; erro de sistema/preço errado na vitrine digital → analisar caso a caso (engano justificável × vinculação).
- Publicidade enganosa (art. 37, §1º) × abusiva (§2º); **burden-shift**: cabe ao fornecedor provar a veracidade da publicidade (art. 38) — invertido por lei.
- Informação prévia e adequada sobre produto/serviço (arts. 6º, III, e 31): dados essenciais disponíveis antes da compra.
- Telemarketing/comércio eletrônico: direito de arrependimento em 7 dias (art. 49) para compras fora do estabelecimento comercial, inclusive online; devolução imediata + frete por conta do fornecedor.

## Juizados Especiais Cíveis — operação

- Valor da causa: até 40 SM o processo tem as regras simplificadas dos JECs (orientação oral, dispensado técnico); acima disso, a lei exige advogado (Lei 9.099/95, art. 9º). Duplo grau: recurso inominado em **10 dias** (art. 42).
- Foro do domicílio do autor/consumidor ou onde prestado o serviço (art. 4º da Lei 9.099/95).
- Fluxo de petição: template `templates/peticao-jec.md` (enquadramento + fatos + direitos violados + pedidos + valor + prova).
- Prova: inversão do ônus quando verossimilhante ou hipossuficiente (CDC art. 6º, VIII); documentos: notas fiscais, prints com URL/data, extratos, protocolos de atendimento, gravações lícitas (participante da conversa — pacífico no STF/STJ — verificar).
- **Gate humano:** rascunho completo + pendências (procuração, documentos, custas conforme tabela do tribunal) — nada protocolar sem ok explícito.

## Hierarquia de fontes

CF/88 (arts. 5º, XXXII; 170, V) > CDC > leis especiais consumeristas > normas regulamentares (CMN/BACEN/ANATEL/ANVISA etc., dentro de suas competências) > jurisprudência vinculante (súmulas, temas repetitivos do STJ) > jurisprudência não vinculante > doutrina.

## Erros comuns

1. **Confundir vício com defeito.** Vício = o produto/serviço não funciona ou tem qualidade inadequada (arts. 18-20, prazos curtos do art. 26); defeito = o produto/serviço funciona mas causa dano além do esperado (arts. 12-17, prescrição de 5 anos). A confusão troca prazo e regime de responsabilidade.
2. **Aplicar prazos do CC no CDC.** O CDC tem prazos próprios (arts. 26-27) e eles vencem primeiro; usar o CC subestima o risco de perda do prazo.
3. **Afirmar inciso do art. 26 ou do art. 51 de memória.** Armadilha clássica — abra o texto oficial.
4. **Esquecer a inversão legal da publicidade** (art. 38): quem prova a verdade da propaganda é o fornecedor.
5. **Dano moral automático.** Nem todo dissabor gera dano moral (STJ repele o "dissabor cotidiano"); caracterize o ultraje à esfera extrapatrimonial, não apenas transtorno.
6. **Citando número de julgado de memória.** Só com texto/número conferidos (ver `references/jurisprudencia-chave.md`); senão descrever a orientação com flag `[verificar]`.
7. **Peça sem gate humano** — nada protocolar/enviar sem revisão e ok explícito do(a) advogado(a).
8. **Inventar quantum, tarifa, índice ou precedente.** Pesquisa antes de afirmar.

## Checklist de verificação

- [ ] Enquadramento CDC×não-CDC feito e logado no topo.
- [ ] Regime identificado: vício / defeito / abuso / publicidade — com prazos corretos calculados com datas reais.
- [ ] Todo artigo citado com lei + artigo; inciso só se conferido no texto oficial.
- [ ] Nenhum número de julgado/súmula citado de memória sem verificação online.
- [ ] Redlines de cláusulas abusivas com linguagem pronta para colar.
- [ ] Disclaimer presente no fechamento; pendências listadas.
- [ ] Gate humano cumprido antes de qualquer envio/protocolo.

## Arquivos desta skill

- `references/cdc-map.md` — mapa navegável do CDC por título/capítulo + artigos-chave.
- `references/jurisprudencia-chave.md` — súmulas e teses firmes do STJ por tema, com disciplina de verificação.
- `templates/memo-consumidor.md` — estrutura de memo de análise consumerista.
- `templates/peticao-jec.md` — esqueleto de petição inicial para Juizados Especiais Cíveis.
- Skill-mãe: `direito-civil-brasileiro` — roteamento para cá em toda relação de consumo.

## Disclaimer padrão (fechar todo produto)

> Este material é um **rascunho de trabalho para revisão por advogado(a)** inscrito(a) na OAB. Não constitui parecer jurídico, opinião vinculante nem substitui consulta profissional. Informações refletem a base de conhecimento até meados de 2026, com verificações pontuais online; confirme vigência e atualidade antes de qualquer uso prático. Um profissional do direito revisará e responderá pelo produto final.

---

*Base normativa: CF/88 (art. 5º, XXXII; art. 170, V); CDC (Lei nº 8.078/1990); Lei nº 9.099/1995; Lei nº 14.181/2021; normas CMN/BACEN citadas. Estrutura inspirada na coleção Claude for Legal (Anthropic), adaptada ao ordenamento brasileiro.*
