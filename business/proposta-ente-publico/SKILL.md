---
name: proposta-ente-publico
description: "Use ao elaborar proposta/documento para órgão público.

Carregue esta skill quando o cliente for órgão público (secretaria, Defesa Civil, autarquia) — documento A4 light-mode com frentes de demanda, escopo e exclusões explícitas, sem preço, no padrão da referência canônica aprovada."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [proposta, ente-publico, orgao-publico, documento-de-solucoes, frentes-de-demanda, A4, HTML, PDF, light-mode, escopo, escopo-exclusoes]
    related_skills: [proposta-sergipetec-documento, elaboracao-proposta-comercial, html-to-pdf-chromium, revisao-entrega-cliente, auxiliar-adm-id, organizacao-drive-id]
    scopes: [id]
type: Orchestrator
timestamp: 2026-10-09T21:30:00Z
---

# Documento de soluções / proposta para ente público

Quando o cliente é **órgão público** (Defesa Civil, secretaria, prefeitura, autarquia), a peça
não é o deck escuro de vendas da ID: é um **documento A4 em light mode**, denso e institucional,
que descreve **frentes de demanda** com escopo escrito, entregas por fase e exclusões explícitas.
Quem lê são servidores e, depois, o jurídico/controle interno do órgão — o documento precisa ser
**defensável antes de ser elegante**.

**Referência canônica desta skill:** `assets/referencia-ID-Solucoes-Defesa-Civil-SE-v1.2.pdf`
(8 páginas A4, 5 frentes, aprovada pelo Tácio em 08/10/2026) e o HTML-fonte em
`templates/documento-solucoes-A4-base.html`. **Toda nova entrega sai nesse padrão** — mesma
grade, mesma ordem de seções, mesmo tom. O conteúdo muda; a forma não.

## Roteamento (não errar o dono da peça)

| Situação | Skill |
|---|---|
| ID entrega soluções a órgão público (esta situação) | **proposta-ente-publico** (esta) |
| Proponente é o **SergipeTec**; a ID aparece como empresa residente | `proposta-sergipetec-documento` |
| Cliente privado (deck de marca + minuta de contrato) | `elaboracao-proposta-comercial` |
| Cliente privado específico já com identidade própria | `proposta-biotechse` e afins |

Não misturar: a peça pública **não** leva preço (ver gate abaixo), **não** leva deck de marca e
**não** leva minuta de contrato.

## As dez regras da peça

1. **Escopo escrito antes de começar.** Cada frente traz, obrigatoriamente, os quatro blocos:
   *o que o órgão descreveu* · *o que é possível construir* · *o que o órgão fornece* ·
   *não incluído nesta frente*. Frente sem os quatro não entra no documento.
2. **"Não incluído" é o que dá credibilidade.** Toda frente declara o que fica fora — inclusive
   o que o órgão pediu implicitamente (Libras, app offline, modelo preditivo, equipamento,
   integração com terceiros). Escopo sem exclusão é escopo que o órgão vai cobrar depois.
3. **"A avaliar" nunca é entregável.** Item marcado como `a avaliar` é evolução possível,
   dimensionada junto à equipe técnica na etapa de calibração — o documento diz isso na cara,
   não no rodapé.
4. **Não reconstruímos o que o Estado já tem.** Se uma base, painel ou sistema já existe ou está
   em implantação em outra frente do Estado, a solução **nasce acoplada a ele**. Duplicar
   estrutura pública é duplicar gasto — e é o argumento que mais defende a ID no controle interno.
5. **Nunca nomear projeto interno de outro cliente.** Quando o que o órgão pede é exatamente o que
   outro projeto da casa (ex.: Odigeí/El Niño/SEMAC) já entrega, o texto fala em "outra iniciativa
   do Estado" e recorta a camada que é própria do órgão (ex.: a camada **operacional** — alerta,
   acionamento, resposta registrada —, não a duplicação de fontes).
6. **Sem preço nesta fase.** O documento de soluções vai sem valor, sem pacote e sem "a partir de".
   Preço e pacotes são **internos, sob Gate 1, com a Fortuna** — não vão ao órgão. Verificar com
   `grep` por `R$` antes de entregar (zero ocorrências).
7. **A dor vem do órgão, não da nossa cabeça.** O bloco *o que o órgão descreveu* reproduz o que
   foi dito na reunião/ata — sem inventar dado, sem dramatizar, sem número que ninguém apurou.
8. **Uma frente entra primeiro.** O documento sempre propõe começar por **uma** entrega em produção
   (prova o método, mede indicador antes/depois) e escalar por fases homologadas. Cinco sistemas
   simultâneos ocupam a equipe do órgão em cinco decisões ao mesmo tempo — e o documento diz por quê.
9. **Tom institucional, não comercial.** Frases completas, zero superlativo, zero emoji, zero
   exclamação, zero nome de método proprietário. Quem escreve é a instituição falando do trabalho.
10. **Nada de placeholder no PDF final.** Sem `{{}}`, sem "a definir", sem nota interna, sem
    comentário de rascunho — a peça sai como se fosse impressa e protocolada.

## Estrutura canônica (8 páginas A4)

| Pág. | Seção | O que carrega |
|---|---|---|
| 1 | **Capa** | Logo ID (SVG, esquerda) + marca/logotipo do órgão (direita) · eyebrow `DOCUMENTO DE SOLUÇÕES` · título "Soluções para a <órgão>" + `em` "o que é possível construir" · lede de 1 parágrafo · 3 pills (órgão · mês/ano · versão). Capa enxuta: sem nota interna, sem sumário. |
| 2 | **01 Sumário executivo** | 4 indicadores (frentes · tipos de entrega · etapas de método · **1 frente entra em produção primeiro**) + 3 blocos curtos (*O que este documento é* / *Como a ID entrega* / *Onde começar*) + nota sobre o que o documento **não** faz. |
| 2–3 | **02 Como a ID trabalha** | 5 compromissos que valem para qualquer frente: escopo escrito antes de começar · entrega por fases homologadas (aceite formal) · com gente dentro (conhecimento fica com o órgão) · dados/automação/educação na mesma casa · não reconstruímos o que o Estado já tem (bloco largo). |
| 3 | **03 As N frentes, em uma vista** | Matriz frentes × 4 tipos de entrega (painel/plataforma · atendimento automatizado · registro em campo · conteúdo e formação) com marcadores incluída/parcial/a avaliar, legenda, **barra empilhada** com a contagem ("13 de 20 entregas incluídas · 5 parciais · 2 a avaliar") e nota de que *a avaliar* não é entregável fechado. |
| 3–6 | **04 As frentes, uma a uma** | Uma frente por bloco (`FRENTE n` + título + subtítulo operacional) com os quatro blocos da regra 1. Frente com risco de duplicidade ganha uma **consideração honesta** (`.honest`) antes do quadro. |
| 6–7 | **05 Como um projeto começa e evolui** | 4 etapas em fluxo: calibração e priorização → primeira entrega em produção → expansão das frentes → operação assistida e transferência. Nota: por que começar por uma frente e não por todas. |
| 7 | **06 Serviços que acompanham as frentes** | Sustentação e evolução · formação das equipes · acompanhamento técnico continuado · documentação como entregável. |
| 8 | **07 O que definimos juntos na primeira conversa** | 8 pontos que dependem da equipe técnica do órgão para virarem escopo (fontes de dados, limiares, modelos preditivos, governança dos dados, bases já existentes, funcionamento sem internet, acessibilidade e idiomas, integrações) + bloco **Próximo passo** + rodapé institucional de fecho. |

Detalhamento, microcopy palavra a palavra e como derivar cada bloco: `references/estrutura-e-microcopy.md`.

## Design system (herdado da referência)

```
--navy #0a1929   --ink #0a1a30   --ink-2 #41566b   --ink-3 #7b8c9c
--teal #4AC6D3   --teal-deep #1AAEBD   --line #dbe4ec
--bg #ffffff     --bg-2 #f5f8fa (cartões)   --bg-3 #eef3f6 (notas)
"Não incluído": #a8603f   ·  marcador 'a avaliar': borda #d2a24a
fontes: 'Neulis Neue' 700 (títulos, OTF embutido) + 'Nunito Sans' (corpo, woff2 embutido)
@page A4 · margem 11mm 12mm · corpo 10.4pt / line-height 1.58
capa em sangria: margin:-11mm -12mm; width:210mm; height:297mm
```

Componentes já prontos no template (não recriar): `.cover` · `.sec-head`/`.sec-num` ·
`.stats`/`.stat` · `.exec` · `.grid2`/`.comp`(`.wide`) · `.matrix` + `.dot.I/.P/.A` + `.legend`
+ `.barchart`/`.seg` · `.frente`/`.blk`/`.blk.nao`/`.entrega` · `.honest` · `.flow`/`.etapa` ·
`.serv` · `.pontos`/`.todo` · `footer.doc` · `section.closing`.

> **Decisão em aberto (não inventar):** a referência usa o teal `#4AC6D3`. Existe um teal
> histórico `#14b8a6` na identidade. Manter `#4AC6D3` (é o da peça aprovada) e **só trocar o
> token** se o sócio decidir — nunca misturar os dois no mesmo documento.

Iconografia: ícones de linha SVG inline (viewBox 0 0 24 24, `stroke="currentColor"`, `stroke-width="1.7"`),
herdando a cor via CSS. Nunca emoji, nunca ícone preenchido, nunca clipart.

## Pipeline

**Passo 1 — Contexto.** Reunir as frentes de demanda como o órgão as apresentou (ata, gravação,
documento do cliente), o nome oficial do órgão, a marca/logotipo em PNG (capa + rodapé) e o
recorte territorial. Sem as frentes de demanda não há documento — não inventar frente para
fechar número.

**Passo 2 — Ficha por frente (antes de escrever HTML).** Para cada frente, preencher os quatro
blocos da regra 1 mais o subtítulo operacional e o tipo de entrega (para a matriz). É a parte
que decide a qualidade: a dor vem do órgão, as exclusões vêm do que **não** é nosso escopo, e o
"a avaliar" fica separado do incluído.

**Passo 3 — Números e matriz.** Contar entregas (incluída/parcial/a avaliar) direto da matriz;
os 4 indicadores do sumário executivo saem desses números e precisam **bater** com a barra
empilhada. Somar no papel, não de cabeça.

**Passo 4 — Escrever o HTML editando o template.** Copiar
`templates/documento-solucoes-A4-base.html` para o diretório de trabalho e **editar como agente**
(trocar frentes, textos, logos, versão, mês). O conteúdo da base é o exemplo Defesa Civil: ele é
referência de forma e tom, não retrato final. Nomear o arquivo
`ID-Solucoes-<Orgao>-<UF>-vX.Y.html`.

**Passo 5 — Render + verificação.** `scripts/render_doc.cjs` (Playwright, A4, rodapé numerado
pelo Chromium) e `scripts/checar_paginas.sh` (densidade por página, página órfã, `R$`).
Depois: `pdftoppm -png -r 110` e **olhar** capa, matriz, uma frente e o fecho antes de declarar pronto.

**Passo 6 — Entrega e arquivamento.** PDF + HTML versionados (nunca reutilizar nome) em
`/opt/mercurio-data/entregas/<cliente>/` e no Drive, na pasta do cliente sob `4.3.1. Odigeí`.
O documento vai ao órgão; a circulação interna é revisão dos sócios.

### Quando o órgão pedir versão com preço

Aí é outro documento, e não se improvisa: seguir `proposta-sergipetec-documento` para o que o
controle interno cobra — composição de custos por perfil × horas × valor-hora (sem linha de lucro,
indiretos embutidos, total quadrando com o contrato), **sem pagamento antecipado**, parcelas
vinculadas a aceite formal e fases homologadas. O documento de soluções continua sendo a base de
escopo; a versão com preço é a camada comercial que se acrescenta depois do Gate 1.

## Pitfalls

- **Preço vazando.** Antes de entregar, `pdftotext` + `grep "R\$"` no PDF. Zero ocorrências.
- **Rodapé digitado à mão.** A numeração de página sai do Chromium (`displayHeaderFooter`), nunca
do HTML — numeração manual quebra a cada re-render e aparece no meio do texto.
- **Página órfã.** `break-inside:avoid` no bloco grande cria buracos: proteger só `<tr>` e os
  cartões internos, com `break-after:avoid` no cabeçalho. Cada quebra forçada custa 0,3–1 página.
- **Capa poluída.** Capa é marca + título + lede + pills. Nota interna e sumário vão para o miolo.
- **Matriz que não fecha.** Pontos da matriz ≠ barra empilhada ≠ indicadores do sumário é o erro
  que um servidor pega primeiro. Conferir a soma.
- **Prometer tecnologia que o órgão não tem.** Sem sensores, sem link de dados, sem app offline
  "de graça": isso é *o órgão fornece* ou *não incluído* — nunca "possível construir".
- **Nomear outro cliente/iniciativa do Estado.** Quebra a isolação e cria conflito de interesse
  aparente.
- **Emoji / nota interna / comentário de rascunho** na entrega do cliente. Zero.

## Verificação (antes de dizer pronto)

- [ ] `pdfinfo` conferido, páginas dentro do orçamento (referência: 8).
- [ ] `checar_paginas.sh` sem página abaixo do piso (referência: ~1.400 caracteres).
- [ ] Toda frente com os quatro blocos + subtítulo operacional.
- [ ] Números do sumário = matriz = barra empilhada.
- [ ] Zero `R$`, zero `{{`, zero "a definir", zero emoji.
- [ ] Rodapé numerado pelo Chromium; nenhuma numeração manual no HTML.
- [ ] Páginas-chave vistas em imagem (capa, matriz, uma frente, fecho): sem corte, sem sobreposição.
- [ ] Arquivo nomeado com versão, salvo em `entregas/<cliente>/` e no Drive do cliente.

## Arquivos desta skill

- `assets/referencia-ID-Solucoes-Defesa-Civil-SE-v1.2.pdf` — a entrega de referência (padrão-ouro).
- `assets/preview-p1.png` · `assets/preview-p3.png` · `assets/preview-p8.png` — prévias das páginas-chave.
- `templates/documento-solucoes-A4-base.html` — HTML-fonte da referência, com CSS, fontes e logos embutidos.
- `references/estrutura-e-microcopy.md` — blueprint seção a seção + microcopy padrão.
- `references/render-e-verificacao.md` — geometria de página, rodapé, checagem de densidade.
- `scripts/render_doc.cjs` — render A4 com rodapé numerado (Playwright/Chromium compartilhado).
- `scripts/checar_paginas.sh` — densidade por página, página órfã, varredura de `R$`.
