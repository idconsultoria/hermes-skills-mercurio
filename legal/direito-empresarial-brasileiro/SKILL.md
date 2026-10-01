---
name: direito-empresarial-brasileiro
description: "Use ao revisar/redigir contrato B2B sob direito brasileiro."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [legal, direito-empresarial, brasil, llc, lindb, contratos-b2b, lgpd, propriedade-industrial, compliance, risco]
    related_skills: [direito-civil-brasileiro, direito-do-consumidor, contratos-justos-id]
type: Reference
timestamp: 2026-09-30T20:15:00Z
---

# Direito Empresarial Brasileiro

## Overview

Skill de prática em **direito empresarial brasileiro**: o regime das relações entre empresas —
societário, contratual B2B, alocação de risco, propriedade intelectual, dados e compliance.
Irmã de `direito-civil-brasileiro` e `direito-do-consumidor`, e completa a série:

- **civil** cobre o direito comum e a relação pessoa-a-pessoa;
- **consumidor** cobre a relação de consumo (CDC, lei especial);
- **empresarial** cobre a relação entre empresas e o exercício profissional da atividade —
  é o trilho em que a consultoria de gestão e a prestadora de serviços operam.

Nos moldes das skills de prática jurídica da coleção *Claude for Legal* (Anthropic),
adaptados ao ordenamento brasileiro. Três marcas herdadas, aplicadas em toda saída:

1. **Rascunho para revisão por advogado(a).** Toda saída é minuta de trabalho destinada a
   revisão e assunção de responsabilidade profissional por advogado(a) inscrito(a) na OAB.
2. **Citação com fonte em toda afirmação.** Norma citada carrega lei + artigo; súmula, seu
   número; julgado, tribunal + classe + número + órgão + data. Afirmação sem fonte não sai.
3. **Gate humano antes de qualquer peça sair.** Nada é assinado, protocolado ou enviado sem
   ok explícito do(a) advogado(a) responsável e do principal da ID Consultoria.

**Data-base:** legislação e jurisprudência até meados de 2026, com verificações pontuais
online durante o uso. LINDB, reforma tributária (EC 132/2023, LC 214/2025), julgados do
STJ e decisões da ANPD mudam — confirme vigência em fonte oficial quando a resposta depender
de mudança recente.

## Quando usar / quando não usar

**Use quando:**
- Qualificar e redigir contrato **entre empresas** (B2B): prestação de serviços, consultoria,
  desenvolvimento de software/sistemas, empreitada, licença, SaaS, agência.
- Analisar **alocação de risco**: quem responde por dependência externa, por dados do
  cliente, por força maior, por variação de custo, por atraso de terceiros, por resultado.
- Questões **societárias operacionais**: LLC e LINDB, quotas, administração, poderes de
  representação, cessão de quotas, mudança de controle, responsabilidade dos sócios.
- **Propriedade intelectual** em entrega a cliente: titularidade de software, cessão de
  direitos autorais, reserva de componentes preexistentes, marca, segredo industrial.
- **LGPD em contexto B2B**: controlador × operador, suboperadores, transferência
  internacional, direitos do titular, incidente de segurança.
- **Compliance**: Lei 12.846/2013, due diligence de parceiro, canal de denúncia, cláusulas
  de integridade.
- **Insolvência**: o que acontece com os contratos quando uma parte entra em recuperação
  judicial ou falência (Lei 11.101/2005).
- **Redline de minuta empresarial** com a ID na posição de contratado ou contratante.

**Não use para (encaminhe e sinalize fora de escopo):**
- Relação de consumo → `direito-do-consumidor`.
- **Trabalhista** (CLT, SST, eSocial, jornada, estágio, prestação pessoal): sinalize que a
  questão é trabalhista e que a ID, como empregadora dos próprios devs em formação, tem
  exposição própria a Mapa. A skill não cobre e não improvisa.
- **Tributário** de plano (CTN, Simples/MEI, IBS/CBS, ISS, retenção): encaminhe a
  contabilidade.
- **Societário complexo** (S.A. aberta, M&A, due diligence de aquisição) e **licitações
  públicas** (Lei 14.133/2021): sinalize e encaminhe.
- **Civil comum** não incidente de relação empresarial (família, sucessões, posse):
  → `direito-civil-brasileiro`.

## Roteamento: empresarial × consumidor × civil × trabalhista

O erro mais caro é enquadrar errado. Antes de qualquer análise de mérito, classifique:

| Sinal | Leitura |
|---|---|
| Ambas as partes são empresas e uma usa o serviço no próprio processo produtivo | **Empresarial** (CC/LLINDB) |
| Contratante é empresa e o objeto é insumo, serviço ou sistema integrado à sua operação | **Empresarial** |
| Destinatário final é consumidor e a empresa é fornecedor profissional | **Consumidor** → `direito-do-consumidor` |
| Prestador é profissional liberal (médico, advogado) sem promessa de resultado | Regra: fora do CDC |
| Prestador é liberal **com promessa de resultado** | CDC aplica-se — verificar tese vigente |
| Contratante PJ mas uso não empresarial, sem caráter de insumo | CDC por finalista agravada (jurisprudência) |
| Relação one-off entre PF, ocasional, sem profissionalidade | **Civil** → `direito-civil-brasileiro` |
| Contrato de emprego, estágio ou prestação pessoal à própria empresa | **Trabalhista** (CLT) — sinalize |

**Caso híbrido B2B com consumidor na ponta:** a camada CC/empresarial rege a relação entre
as empresas; a exposição CDC existe só na ponta, se o produto chegar ao consumidor. Analise
a camada empresarial e sinalize separadamente a exposição da ponta. O contrato empresarial
pode(validamente/internalizar o risco sobre o que for entregue ao consumidor — isso é
**alocação contratual de risco**, não renúncia a direito de terceiro.

**Procedimento:** havendo dúvida razoável, pergunte usando esta tabela; logue no topo do
produto `Enquadramento: [EMPRESARIAL | CONSUMIDOR | CIVIL | TRABALHISTA] — porque...`. Se não
for empresarial, invoque a skill irmã e **NÃO** analise o mérito aqui.

## Fluxo de trabalho

1. **Enquadrar a relação** e logar a decisão no topo do produto.
2. **Identificar o regime contratual material:** prestação de serviços (CC arts. 594-626) ×
   empreitada (arts. 610-626) × licença × suprimento de tecnologia × atípico (art. 425).
   Título não é destino: prevalência da função econômica e da intenção conjunta (CC art. 112;
   art. 421-A, IV-V para interpretação).
3. **Mapear as fontes primárias:** CC navegável em `references/mapa-normas-empresarial.md`
   (arts. transcritos verbatim); demais leis com número e artigo.
4. **Verificar externamente o que for volátil:** LINDB alterada, reforma tributária, súmulas e
   temas repetitivos, decisões da ANPD → `web_search` em fonte oficial (planalto.gov.br,
   stj.jus.br, gov.br/anpd). Logue `verificado online em <data>` ou `pendente de verificação`.
5. **Aplicar a hierarquia de fontes:** CF/88 > CC/LLINDB > leis especiais (CDC, LGPD, PI,
   Lei 12.846, Lei 11.101) > jurisprudência vinculante (súmula, RE repetitivo — CPC arts.
   926-927) > jurisprudência não vinculante > doutrina.
6. **Produzir o entregável:** memo de contrato empresarial, redline desvio-por-desvio,
   cláusula de risco pronta para colar, ou checklist de due diligence contratual.
7. **Fechar com disclaimer + pendências + gate humano.**

## Regime contratual B2B — o que muda em relação ao civil comum

**a) Autonomia contratual reforçada (Lei 13.874/2019).** O art. 421 impõe a **função social**
do contrato; o parágrafo único acrescenta **intervenção mínima e excepcionalidade da revisão
contratual**; o art. 421-A presume os contratos civis e empresariais **paritários e
simétricos** até que haja elemento concreto que justifique afastar a presunção, e determina
que: as partes podem estabelecer **parâmetros objetivos** de interpretação e de revisão; a
**alocação de riscos definida pelas partes deve ser respeitada e observada** (inciso II); e a
revisão contratual só ocorre **de maneira excepcional e limitada** (inciso III).

Consequência prática: em contrato B2B bem redigido é mais forte **consensualizar** a alocação
de risco do que tentar sustenta-la contra ela. Redline que trate risco como "cláusula abusiva"
entre empresas é, na maior parte das vezes, juridicamente frágil — o caminho é **reescrever**
o risco com gatilho, limite e procedimento.

**b) Boa-fé na execução (CC art. 422).** Vale na conclusão **e na execução**. Se a obrigação
for positiva e líquida e tiver termo, mora é **de pleno direito** (art. 397), sem interpelação.

**c) Resolução × onerosidade excessiva.** A parte lesada pode pedir resolução (art. 475) ou
exigir o cumprimento, sempre com perdas e danos. Em contrato de execução continuada ou
diferida, circunstância extraordinária e imprevisível pode justificar resolução por
onerosidade excessiva (art. 478), evitada por ajuste equitativo (art. 479). A exceção do
contrato não cumprido (art. 476) exige **prévio cumprimento da própria obrigação** — cláusula
de lay-off mal redigida vira arma contra o ID.

**d) Cláusula penal (arts. 409-413).** Pode incidir sobre a inexecução total, sobre cláusula
especial ou sobre a mora. Para mora, o credor tem **arbítrio** de exigir a pena *juntamente*
com o desempenho da obrigação (art. 411). O valor da penalidade **não pode exceder o da
obrigação principal** (art. 412); é reduzida equitativamente pelo juiz se a obrigação foi
cumprida em parte (art. 413). Verificar o teto antes de redigir.

**e) Mora e juros.** Mora (arts. 389 e 395): perdas e danos + juros + atualização monetária +
honorários. Juros legais = **taxa referencial da Selic deduzido o índice de atualização**
(art. 406, redação Lei 14.905/2024), com piso zero (art. 406, §3º). Na prática B2B,
**convencionar** multa e juros costuma ser melhor que litigar a aplicação do legal.

**f) Forma e assinatura.** Contrato empresarial é negócio jurídico: exige objeto lícito,
possível, determinado ou determinável e agente capaz (CC art. 104); a forma não é essencial
salvo lei específica (art. 107). Assinatura eletrônica vale — MP 2.200-2/2001, art. 10, §2º,
e MP 14.063/2020.

**g) Cessão e sucessão do contrato.** **Cessão de crédito** é livre (CC art. 286), salvo
oposição da natureza, lei ou convenção. **Cessão da posição contratual NÃO existe
automaticamente** — depende de **consentimento da outra parte**. Logo: mudança de controle
do cliente, aquisição do cliente ou sucessão empresarial exigem **cláusula de anuência /
continuidade**. Sem ela, o contrato pode não acompanhar o cliente. Ponto de falha frequente.

**h) Insolvência (Lei 11.101/2005).** Créditos contra a massa têm classes e efeitos
próprios; a garantia real pesa. Ponto prático: em entrega de sistema, exigir **pagamento da
etapa entregue** e não aceitar suspensão por aperto financeiro do cliente — cláusula de não
suspensão por inadimplemento do cliente.

## Propriedade intelectual em entrega a cliente (roteiro)

- **Direitos de autor (Lei 9.610/1998).** Podem ser transferidos total ou parcialmente
  (art. 49). **Transmissão total e definitiva só mediante estipulação contratual escrita**
  (art. 49, II); sem ela, o prazo máximo é de 5 anos (art. 49, III). Cessão sempre por
  escrito e ** presume-se onerosa** (art. 50). Os direitos **morais são inalienáveis e
  irrenunciáveis** (art. 27). → Em projeto por escopo fechado, cliente que pagou por "código
  100% do cliente" entendeu propriedade: **escreva cessão expressa**, não deixe implícita.
- **Obra por encomenda**: verificar a redação vigente no texto oficial (ver
  `references/mapa-normas-empresarial.md`, sinalizada) antes de citar artigo específico.
- **Componentes preexistentes** (framework, biblioteca, boilerplate, base interna do ID,
  templates de design): **pertencem ao ID**. Sem ressalva, o cliente pode alegar
  co-propriedade de base reutilizada em outro cliente — risco de vazar o ativo do ID. Esta
  ressalva é **essencial** em contrato de desenvolvimento.
- **Segredo industrial (Lei 9.279/1996, art. 195, XI).** Crime usar, sem autorização,
  conhecimentos, informações ou dados confidenciais utilizáveis na indústria, comércio ou
  prestação de serviços, acessados por relação contratual, **mesmo após o término do
  contrato**. A cláusula contratual de confidencialidade é a medida razoável de proteção
  que sustenta a pretensão em caso de disputa.

## LGPD em contrato B2B (roteiro)

- **Papéis (art. 5º, VI-VII):** **controlador** = quem decide sobre o tratamento;
  **operador** = quem trata em nome do controlador. Se o ID trata dados do cliente
  (documentos de colaboradores, fotos, credenciais), o ID é **operador** e age **segundo as
  instruções do controlador** (art. 39) — por isso o contrato **precisa** conter as
  instruções, o descritivo de tratamento e a lista de subprocessantes.
- **Medidas de segurança (art. 46):** dever de ambos; observadas desde a concepção do
  produto (art. 46, §2º).
- **Incidente:** a comunicação à ANPD e aos titulares é dever do **controlador** (art. 48),
  em prazo razoável, com conteúdo mínimo dos incisos I-VI. No contrato, definir **janela de
  notificação interna** (ex.: 24 h) e dever de cooperação do operador.
- **Transferência internacional (art. 33):** exige hipótese legal; a cláusula contratual
  padrão (inciso II, "a") é a base usual.
- **Direitos do titular (art. 18):** o operador deve assistir o controlador a atender.
- **Vedação de uso para treino de IA:** dado do cliente não alimenta modelo do ID nem de
  terceiro sem base legal e autorização — cláusula **explícita e não-negociável** da ID.

## Checklist de risco para relação empresarial

- **Quem executa e como é revisado.** Desenvolvimento por pessoas em formação exige
  **coordenação, supervisão e revisão técnica contratadas**, com termo de confidencialidade
  individual e restrição de acesso ao ambiente do projeto.
- **Objeto:** escopo fechado, com **fase e marco de aceite**; silêncio do cliente não é
  aceite tácito.
- **Dependência externa** (API, provedor, base legal, terceiro): risco do cliente se o ID
  comunicar impedimento e adotar contingência.
- **PI:** cessão do entregue (após quitação) + reserva de preexistentes + segredo.
- **LGPD:** papel definido, instruções, suboperadores, incidente em janela curta, vedação de
  treino de IA, transferência internacional.
- **Pagamento:** entrada antes do custo; marco como gatilho; **sem aceite tácito**; mora
  convencional; **suspensão por inadimplemento do cliente**; cobrança por etapa entregue.
- **Multa:** drafting de mora respeitando o teto do art. 412.
- **Mudança de controle / sucessão:** cláusula de anuência.
- **Rescisão:** aviso, proporcional por etapa entregue, e **consequência sobre garantia e
  mensalidade** — enunciar.
- **Independência:** não é locação de mão de obra; é entrega de resultado.
- **Foro:** foro de eleição entre partes capazes em contrato escrito é válido (CPC art. 63).

## Hierarquia de fontes

CF/88 > CC/LLINDB > leis especiais (CDC, LGPD, Lei 9.610, Lei 9.609, Lei 9.279, Lei 12.846,
Lei 11.101) > jurisprudência vinculante (súmula, RE repetitivo) > jurisprudência não
vinculante > doutrina.

## Erros comuns

1. **Aplicar o regime empresarial a relação de consumo** — handoff imediato.
2. **Tratar cláusula de alocação de risco como abusiva entre empresas.** No direito
   empresarial a presunção é de simetria (art. 421-A) e a alocação pactuada deve ser
   respeitada (inciso II). O redline certo é **reescrever**, não nulificar.
3. **Redigir multa acima do teto** (art. 412) ou cumular multa + conversão + honorários de
   forma que o conjunto exceda razoavelmente a obrigação — risco de redução judicial.
4. **Deixar a PI implícita.** "Cliente é dono do sistema" sem cessão expressa; e
   **esquecer de reservar componentes preexistentes** — o ID perde parte da própria base.
5. **Não prever mudança de controle/sucessão.** Cessão de posição contratual exige
   consentimento; sem cláusula, o contrato pode não acompanhar o cliente.
6. **Papel de LGPD trocado.** ID como controlador quando é operador (ou o inverso) — a
   obrigação recai sobre a parte errada.
7. **Operador sem instrução documentada** age fora do art. 39 — é o ID, não o cliente, que
   está em mora.
8. **Confundir LGPD com segredo.** Dado pessoal tem regime próprio (incidente, direitos do
   titular, sanção administrativa); informação confidencial de negócio é outra coisa.
9. **Citar número de julgado ou súmula de memória.** Alucinação mais grave desta área;
   só com texto conferido.
10. **Peça sem gate humano.**

## Checklist de verificação

- [ ] Enquadramento (empresarial × consumidor × civil × trabalhista) logado no topo.
- [ ] Regime contratual identificado com fundamento.
- [ ] Todo dispositivo citado com lei + artigo; inciso só se conferido em texto oficial.
- [ ] Nenhuma súmula/julgado citado sem verificação online (não confirmados ficam
      `[verificar]`).
- [ ] Risco alocado **por cláusula com gatilho, limite e procedimento** — não por silêncio.
- [ ] PI: cessão do entregue + reserva de preexistentes + confidencialidade.
- [ ] LGPD: papéis, instruções, incidente (janela), vedação de treino de IA.
- [ ] Pagamento: gatilhos, mora dentro do teto, sem aceite tácito, sem suspensão por
      inadimplemento do cliente.
- [ ] Disclaimer de rascunho no fechamento; pendências listadas.
- [ ] Gate humano antes de qualquer assinatura/protocolo.

## Arquivos desta skill

- `references/mapa-normas-empresarial.md` — mapa do regime empresarial: CC arts. transcritos
  verbatim, LINDB, LGPD, PI, compliance, insolvência; teses com disciplina de verificação.
- `references/redline-risco-b2b.md` — padrão de redline desvio-por-desvio e cláusulas de
  risco prontas para colar (alocação, gatilho, teto, procedimento).
- `templates/memo-contrato-empresarial.md` — estrutura de memo de contrato B2B.
- `templates/checklist-due-diligence-contratual.md` — checklist de due diligence antes de
  assinar.
- Skills irmãs: `direito-civil-brasileiro`, `direito-do-consumidor`.
- Skill de aplicação: `contratos-justos-id` (como redigir contrato justo, simples e benéfico
  à ID a partir destas três).

## Disclaimer padrão (fechar todo produto)

> Este material é um **rascunho de trabalho para revisão por advogado(a)** inscrito(a) na OAB.
> Não constitui parecer jurídico, opinião vinculante nem substitui consulta profissional.
> Informações legislativas e jurisprudenciais refletem a base de conhecimento até meados de
> 2026, com verificações pontuais online; confirme vigência e atualidade antes de qualquer uso
> prático. Um profissional do direito revisará e responderá pelo produto final.

---

*Base normativa: CF/88; CC (Lei nº 10.406/2002); LLINDB (Lei nº 13.303/2016); CPC (Lei nº
13.105/2015); LGPD (Lei nº 13.709/2018); Lei nº 9.610/1998; Lei nº 9.609/1998; Lei nº
9.279/1996; Lei nº 12.846/2013; Lei nº 11.101/2005; CDC (Lei nº 8.078/1990). Estrutura
inspirada na coleção Claude for Legal (Anthropic), adaptada ao ordenamento brasileiro.*
