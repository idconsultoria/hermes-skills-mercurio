---
name: direito-civil-brasileiro
description: "Direito civil brasileiro — análise, redline de minutas e peças sob o CC/2002.

Load this skill when the task involves Brazilian civil law: contratos (redline, revisão, redação), responsabilidade civil (arts. 186, 927-954), obrigações e inadimplemento, prescrição/decadência (arts. 205-206), negócio jurídico e invalidades (arts. 104, 166-184), posse e propriedade, família e sucessões, peças processuais cíveis (CPC). Produz memos, redlines e petições em formato de rascunho para revisão por advogado(a), com citação fonte-a-fonte e gate humano antes de qualquer envio/protocolo. Relações de consumo são roteadas para direito-do-consumidor."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [legal, direito-civil, brasil, cc2002, contratos, responsabilidade-civil]
    related_skills: [direito-do-consumidor]
type: Reference
timestamp: 2026-08-23T19:15:00Z
---

# Direito Civil Brasileiro

## Overview

Skill-mestre de direito civil no Brasil, nos moldes das skills de prática jurídica da coleção *Claude for Legal* (Anthropic), adaptada ao ordenamento brasileiro. Cobre a Parte Geral do Código Civil (Lei nº 10.406/2002 — negócio jurídico, prescrição, decadência), a Parte Especial (obrigações, contratos, responsabilidade civil, direitos reais, família, sucessões) e as leis especiais que se entrelaçam com o CC (CPC, leis de usucapião urbana, Estatuto da Pessoa com Deficiência etc.).

Três marcas herdadas da coleção original, aplicadas em toda saída:

1. **Rascunho para revisão por advogado(a).** Toda saída é minuta de trabalho destinada a revisão, verificação e assunção de responsabilidade profissional por advogado(a) inscrito(a) na OAB. Não é parecer definitivo nem opinião jurídica vinculante.
2. **Citação com fonte em toda afirmação.** Norma citada carrega lei + artigo; súmula, seu número; julgado, tribunal + classe + número + órgão + data. Afirmação sem fonte não sai. Doutrina entra sempre como opinião ("para Fulano, ..."), nunca como norma.
3. **Gate humano antes de qualquer peça sair.** Nada é protocolado, enviado ou tratado como confiável sem confirmação explícita do(a) advogado(a) responsável. A skill prepara; o ser humano decide e responde.

**Data-base do conhecimento:** legislação e jurisprudência até meados de 2026, com verificações pontuais online durante o uso. STJ/STF editam e cancelam súmulas, plenários virtuais mudam teses e reformas legislativas alteram artigos — ver vigência no site oficial (planalto.gov.br, stj.jus.br, stf.jus.br) quando a resposta depender de mudança recente.

## Quando usar / quando não usar

**Use quando:**
- Revisar, redigir ou fazer redline de minutas civis: compra e venda, doação, locação, empréstimos (comodato, mútuo), prestação de serviços não-consumerista, empreitada, depósito, mandato, transporte, seguro, fiança, transação.
- Analisar responsabilidade civil extracontratual: acidentes, danos morais e materiais, perda de uma chance, abuso de direito, responsabilidade do Estado (CF, art. 37, §6º), fato de terceiros (arts. 932-933).
- Calcular ou arguir prescrição (arts. 205-206) e decadência (arts. 178, 179, 207).
- Classificar negócios jurídicos: validade (art. 104), nulidade × anulabilidade (arts. 166-184), simulação, fraude contra credores, lesão, estado de perigo, onerosidade excessiva, representação, condição/termo/encargo.
- Redigir peças cíveis: petição inicial (CPC art. 319), contestação, recursos, impugnação a cumprimento de sentença, embargos à execução.
- Pesquisar doutrina, súmulas e teses aplicáveis a um problema civil; montar memo de análise.
- Orientar questões de família e sucessões (partilha, inventário, união estável, regime de bens, alimentos) em nível de triagem e estruturação.

**Não use para (encaminhe e sinalize fora de escopo):** relações de consumo (→ `direito-do-consumidor`), direito trabalhista (CLT), tributário (CTN), penal, societário complexo, licitações. A skill sinaliza o encaminhamento; não improvisa.

## Roteamento: civil × consumidor

O CDC é lei especial que afasta a incidência do CC nas relações de consumo (CDC art. 7º). Aplicar CC onde devia aplicar CDC é o erro mais custoso desta área. Antes de qualquer análise de mérito, classifique a relação:

| Sinal | Leitura |
|---|---|
| Adquirente usufrui o bem/serviço como destinatário final (não repassa custo na cadeia) | CDC |
| Fornecedor atua como profissional (PJ, ou PF com organização de fim econômico) | CDC |
| Empresário adquirente, mas uso próprio sem caráter empresarial (teoria finalista agravada) | CDC |
| Ambas as partes profissionais integrando a cadeia produtiva (revenda, insumo) | CC puro |
| Locação de imóvel urbano | CC/Lei do Inquilinato (não-CDC) |
| Banco, seguro, plano de saúde, telecom, transporte | CDC (sim, bancos e planos são CDC) |

**Procedimento:** havendo dúvida razoável, pergunte ao usuário usando esta tabela resumida; logue a decisão no topo do produto (`Classificação: [CC|CDC] — porque ...`). Se CDC, invoque `direito-do-consumidor` e NÃO analise o mérito aqui. Casos híbridos (contrato entre empresas cujo produto atinge consumidor na ponta): analise a camada CC e sinalize separadamente a exposição CDC na ponta.

## Fluxo de trabalho

1. **Classificar a relação** (roteamento acima) e logar a decisão.
2. **Estruturar o problema:** fatos em ordem cronológica → questão(s) jurídica(s) → fundamentos normativos (lei + artigo) → aplicação ao caso → conclusões provisórias + riscos. Em peças, adaptar para tese principal + subsidiárias + pedidos.
3. **Mapear fontes primárias:** navegue o CC por `references/codigo-civil-map.md`; consulte teses firmes por tema em `references/teses-consolidadas.md`.
4. **Verificar externamente o que for volátil:** número/data de julgados, súmulas recentes, reformas de 2025-2026 → `web_search` com confirmação em fonte oficial. Logue `verificado online em <data>` ou `pendente de verificação`.
5. **Aplicar a hierarquia de fontes:** CF/88 > CC > leis especiais > jurisprudência vinculante (súmula vinculante, repercussão geral, recursos repetitivos — CPC arts. 926-927) > jurisprudência não vinculante > doutrina.
6. **Produzir o entregável** no formato adequado: memo (`templates/memo-analise-juridica.md`), redline, ou peça (`templates/peticao-inicial.md`).
7. **Fechar com o disclaimer padrão** (abaixo) e a lista de verificações pendentes. Nada sai sem gate humano.

## Revisão de minutas (redline)

Método dos skills de review da coleção original: títulos primeiro, corpo depois, decisão logada no topo, desvio-por-desvio.

1. **Títulos primeiro.** Extraia o título principal e todos os anexos/exibos antes de ler o corpo. É o sinal de roteamento (locação ≠ compra e venda; um anexo de garantia pessoal muda a análise). Título não é destino: um "contrato de prestação de serviços" com especificação técnica detalhada funciona como empreitada — prevalece a função econômica (art. 112: atende-se mais à intenção conjunta das partes).
2. **Perfil de prática.** Se existir playbook do escritório/cliente, revise contra ele (política de risco, limites de autoridade). Sem playbook, baseline legal + prática de mercado.
3. **Log de decisão no topo do memo:** documento identificado, anexos, classificação CC×CDC, perfil usado.
4. **Desvio-por-desvio**, para cada cláusula problemática: (a) citação literal; (b) problema jurídico (violação direta de norma, risco, silêncio perigoso); (c) severidade ALTA/MÉDIA/BAIXA; (d) linguagem de redline pronta para colar; (e) fundamento (lei + artigo).
5. **Checagem obrigatória em qualquer contrato civil:** objeto lícito, possível, determinável (art. 104); preço e forma de pagamento; prazo/duração e formas de extinção; multa e encargos de mora (art. 389 e ss.; juros legais = Selic desde a Lei nº 14.149/2021, art. 406); foro de eleição (CPC art. 63 — válido entre capazes em contrato escrito; abusividade é questionável); cláusula arbitral (Lei nº 9.307/96 — válida entre capazes); vedação a renúncia prévia de direitos indisponíveis (nula); vedações legais específicas do tipo contratual (ex.: evicção, vícios redibitórios, arras — arts. 447 ss.).

Se a minuta tiver cara de consumerista (padronizada, adesiva, parte física como destinatária final), pare o redline CC e rode o fluxo do `direito-do-consumidor` — as vedações lá são outras (arts. 51-54 CDC) e mais estritas.

## Responsabilidade civil — roteiro

**Extracontratual (arts. 927-954):**
- Elementos: conduta + dano + nexo causal. Excludentes clássicas: culpa exclusiva da vítima, fato de terceiro, caso fortuito/força maior (art. 393).
- Regime: subjetivo como regra (arts. 186 e 927 *caput*: prova de culpa); objetivo quando a lei indicar ou quando a atividade implicar risco (art. 927, parágrafo único). Abuso de direito (art. 187) e responsabilização por fato de terceiros (arts. 932-933) aproximam-se da objetividade.
- Responsabilidade do Estado: CF, art. 37, §6º (objetiva). Omissão genérica × específica divide a jurisprudência — sinalize a controvérsia.
- Danos: emergente + lucros cessantes (art. 402); morais (fixação por dupla perspectiva — reposição/satisfação — com proporcionalidade e vedação ao enriquecimento sem causa, art. 944); estético cumulável com moral (Súmula 387 STJ).
- Solidariedade (art. 942) e regresso (art. 934); culpa concorrente da vítima reduz a indenização (art. 945).

**Contratual:** inadimplemento (art. 389) → perdas e danos = emergente + lucros cessantes, excluídos os danos remotos (art. 403); cláusula penal (arts. 384, 411-420); arras (arts. 417-420); exceção de contrato não cumprido (art. 476); onerosidade excessiva (arts. 317 e 478-480).

**Prescrição:** reparação civil prescreve em 3 anos (art. 206, §3º, V) tanto na esfera contratual quanto na extracontratual.

## Prescrição e decadência — referência rápida

| Pretensão | Prazo | Fundamento |
|---|---|---|
| Regra geral (silêncio da lei) | 10 anos | CC art. 205 |
| Reparação civil (contratual e extracontratual) | 3 anos | CC art. 206, §3º, V |
| Aluguéis de prédio urbano ou rústico | 3 anos | CC art. 206, §3º, I |
| Juros, dividendos e prestações acessórias pagáveis em períodos ≤ 1 ano | 3 anos | CC art. 206, §3º, III |
| Enriquecimento sem causa | 3 anos | CC art. 206, §3º, IV |
| Dívidas líquidas constantes de instrumento público ou particular | 5 anos | CC art. 206, §5º, I |
| Anular negócio por erro, dolo, coação, estado de perigo, lesão ou fraude contra credores | 4 anos (decadencial) | CC art. 178 |
| Anular ato anulável sem prazo legal específico | 2 anos (decadencial) | CC art. 179 |

Incisos do art. 206 conferidos no texto oficial (transcrito em `references/codigo-civil-map.md`). Coação: decadencial do art. 178, I conta do dia em que cessar.

Regras de sistema: interrupção da prescrição (art. 202) × suspensão (arts. 197-199); renúncia só depois de consumado o prazo (art. 191); contra absolutamente incapazes não corre prescrição (art. 198, I); decadência suspende-se mas não se interrompe (art. 207); pretensão fundada em ato nulo não prescreve (jurisprudência pacífica do STJ). **Antes de afirmar inciso exato do art. 206, abra o texto no Planalto** — o artigo tem dezenas de incisos e errá-los destrói a credibilidade do memo.

## Família e sucessões — ponteiros

- União estável (arts. 1.723-1.727), regime de bens (arts. 1.639-1.688; comunhão parcial como supletiva, art. 1.640), alimentos (arts. 1.694-1.710), divórcio e partilha (alterações da Lei nº 14.382/2022).
- Sucessões (arts. 1.784-2.027): vocação hereditária (art. 1.829), legítima e parte disponível (art. 1.846), colação, inventário (CPC arts. 610 ss.). Usucapião: extraordinária 15 anos (art. 1.238), ordinária 10 (art. 1.242), com reduções legais.
- Sensibilidades: melhor interesse da criança (CF art. 227; ECA); violência doméstica → sinalizar Lei nº 11.340/2006 e encaminhar; nada de especular sobre situações concretas de guarda sem os autos.

## Peças processuais

1. Coletar qualificação completa das partes, cronologia factual, documentos essenciais, valor da causa (CPC arts. 291-292) e competência (foro de domicílio do réu — CPC art. 46 — ou foro de eleição, art. 63).
2. Teses: principal + 2-3 subsidiárias. Prescrição/decadência SEMPRE checadas (matéria de ordem pública, conhecível de ofício).
3. Pedidos certos e determinados (CPC art. 322), alternativos quando cabíveis (art. 326).
4. **Gate humano:** entregar rascunho completo + lista de pendências (procuração, documentos faltantes, custas, recolhimentos) — nada é protocolável sem revisão e ok explícito do(a) advogado(a).
5. Prazos processuais correm em dias úteis (CPC arts. 12 e 219); contestação, 15 dias úteis (art. 335).

## Método de citação

- Norma: `CC, art. 389` · `CDC, art. 42, parágrafo único` · `CF, art. 37, §6º`.
- Julgado (só com número verificado online): `STJ, REsp <número>/<UF>, <Seção/Turma>, j. <data>, Rel. Min. <nome>`. Nunca invente número, página ou valor de condenação.
- Súmula/tema: `Súmula 385/STJ` · `Tema <n>/STJ` — confirme existência antes de citar.
- Orientação firme sem número confirmado: descreva como "orientação consolidada do STJ/STF" + flag `[verificar]`.
- Doutrina: `<Autor>, <Obra>, <ed.>, <ano>` — página só se realmente consultada.

## Erros comuns

1. **Aplicar CC onde é CDC.** Detectou sinal de consumo? Handoff imediato. Análise pelo CC subestima a exposição (vedações do art. 51 CDC, inversão do ônus, prazos próprios).
2. **Citando número de julgado ou súmula de memória.** É a alucinação mais grave nesta área. Textos verificados e prontos para citação estão em `references/teses-consolidadas.md`; todo o resto → verificar online ou descrever sem número.
3. **Errar inciso do art. 206.** Dezenas de incisos; abra o texto legal antes de afirmar.
4. **Confundir nulidade × anulabilidade.** Nulidade (arts. 166-167): negócio gravíssimo, não convalida, pretensão não prescreve. Anulabilidade (art. 171): prazo decadencial (arts. 178-179), convalidável. A confusão muda a estratégia inteira.
5. **Confundir prescrição × decadência.** Prescrição atinge a pretensão (pode ser interrompida, renovada judicialmente); decadência atinge o próprio direito potestativo (não se interrompe — art. 207).
6. **Capitalização e índices.** Capitalização anual é permitida (art. 591); a Selic do art. 406 não se acumula com correção monetária distinta (orientação STJ — confirmar orientação atual antes de calcular).
7. **Peça sem gate humano.** Nada protocolar/enviar sem revisão e ok explícito.
8. **Inventar doutrina, processo ou precedente.** Não sabe? Diz que não sabe e pesquisa.

## Checklist de verificação

- [ ] Classificação CC×CDC feita e logada no topo do produto.
- [ ] Todo dispositivo citado com lei + artigo (inciso só se conferido no texto oficial).
- [ ] Nenhum número de julgado citado de memória — confirmado online ou descrito sem número com flag `[verificar]`.
- [ ] Prescrição/decadência calculada com datas reais, não "aproximadamente".
- [ ] Severidades atribuídas a cada achado de contrato; redlines prontos para colar.
- [ ] Disclaimer de rascunho presente no fechamento.
- [ ] Gate humano cumprido antes de qualquer envio/protocolo.

## Arquivos desta skill

- `references/codigo-civil-map.md` — mapa navegável do CC (livros, títulos, artigos-chave por tema).
- `references/teses-consolidadas.md` — teses firmes por tema, com disciplina de verificação.
- `templates/memo-analise-juridica.md` — estrutura de memo de análise civil.
- `templates/peticao-inicial.md` — esqueleto de petição inicial cível (rascunho + checklist de protocolo).
- Skill irmã: `direito-do-consumidor` — roteamento a partir daqui quando a relação for de consumo.

## Disclaimer padrão (fechar todo produto)

> Este material é um **rascunho de trabalho para revisão por advogado(a)** inscrito(a) na OAB. Não constitui parecer jurídico, opinião vinculante nem substitui consulta profissional. Informações legislativas e jurisprudenciais refletem a base de conhecimento até meados de 2026, com verificações pontuais online; confirme vigência e atualidade antes de qualquer uso prático. Um profissional do direito revisará e responderá pelo produto final.

---

*Base normativa: CF/88; CC (Lei nº 10.406/2002); CPC (Lei nº 13.105/2015); leis especiais citadas. Estrutura inspirada na coleção Claude for Legal (Anthropic), adaptada ao ordenamento brasileiro.*
