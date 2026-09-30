---
name: proposta-sergipetec-documento
description: "Use when a proposta é do SergipeTec (órgão público)."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [proposta, sergipetec, parque-tecnologico, contratacao-publica, PD&I, parecer, HTML, PDF]
    related_skills: [analise-contratual, html-to-pdf-chromium, elaboracao-proposta-comercial, auxiliar-adm-id]
    scopes: [id]
type: Orchestrator
timestamp: 2026-09-29T23:30:00Z
---

# Proposta do SergipeTec para órgão público (P,D&I)

Propostas endereçadas por órgão público ao **Sergipe Parque Tecnológico** não são propostas da ID:
são documento institucional do Parque (o proponente é o SergipeTec), no formato **documento A4** — não no
deck escuro da marca ID. O que passa pelo crivo é a **PGE/assessoria jurídica do órgão**, então o
documento precisa atender ao art. 72 da Lei nº 14.133/2021 antes de ser elegante.

## Quando usar

- "Reescreva/refaça a proposta da SEMAC / do Parque / do TJSE".
- Proposta em que o contratado é o **SergipeTec** (OS sem fins lucrativos, art. 75, XV) e a ID/parceiros
  aparecem como empresas residentes que executam.
- Resposta a **parecer técnico** de órgão público (devolução de proposta).

## Identidade e pipeline

Tokens herdados dos currículos institucionais do Parque (mesma família visual em todo documento):

```
--navy:#09182b  --blue:#0048FE  --green:#00d084  --mint:#7bdcb5
--ink:#1c2536   --muted:#5b6879 --line:#e3e8ef   --bg:#f7fafc
fonte: "Segoe UI",Roboto,"Helvetica Neue",Arial  ·  logo: sergipetec-logo.png (topo esquerdo)
@page A4 · margens 11,5mm 12,5mm 10,5mm 12,5mm · corpo 8,4–9,3pt
```

Caminho que funciona:

1. Escrever o documento em **partes** (`part1.html` com `<head>+CSS`, `part2..4.html` só conteúdo) e
   concatenar num `build.py`. O build envolve a primeira `<tr>` de cada tabela em `<thead>` e o resto em
   `<tbody>` — isso faz o cabeçalho repetir quando a tabela quebra de página.
2. Renderizar com o Chromium compartilhado:
   `CHROMIUM=/opt/data/.playwright/chromium-1117/chrome-linux/chrome` + `--headless=new --no-sandbox
   --disable-gpu --disable-dev-shm-usage --no-pdf-header-footer --print-to-pdf=...`.
3. Medir: `pdfinfo` (páginas) e `pdftotext -f N -l N | wc -c` por página. Página cheia ≈ **4.200–4.500
   caracteres** nessa densidade; abaixo de ~1.500 é página órfã e está errada.
4. Conferir com visão: `pdftoppm -png -r 110` e `vision_analyze` nas páginas-chave (capa, tabelas grandes,
   última). A visão pega o que a contagem não pega: rodapé solto, assinatura flutuando, capa poluída.

## Orçamento de páginas (o que custa tempo)

O cliente limita o número de páginas; a ID entrega menos. Iterar sempre nesta ordem:

1. **Densidade** (corpo 8,4→9,3pt, `line-height` 1,28→1,40, margens) — resolve a maior parte sem cortar conteúdo.
2. **Quebras forçadas** só onde valem (capa, seção-símbolo). Cada quebra forçada desperdiça de 0,3 a 1 página.
3. **Conteúdo** por último.

Pitfalls que queimam rodada:
- `break-inside:avoid` na **tabela inteira** cria buracos: mantenha a regra só em `<tr>` e deixe a tabela quebrar.
- Rodapé com "página N" digitado à mão fica errado a cada re-render e aparece no meio do texto quando o
  fluxo muda — não numere página dentro do HTML.
- Última página com menos de ~2.000 caracteres significa que o bloco de assinatura não coube: reduza o
  material anterior em ~700–900 caracteres ou agrupe o fecho.

## Estrutura narrativa que passou pela validação

Raciocínio encadeado, cada seção respondendo à anterior: capa enxuta (sem nota interna longa) → resumo
com 3 números-chave → por que agora (o fenômeno, a janela, o recorte territorial) → o que se contrata
(natureza P,D&I + delimitação negativa) → como se entrega (ciclos) → o painel principal especificado →
os módulos → quem executa (vínculos) → propriedade/continuidade/custos de operação → riscos →
investimento e composição → declarações → próximos passos → assinatura.

## Modelo comercial: ciclos de 3 semanas

Exigência recorrente de órgão de controle: **sem pagamento antecipado** (art. 145) e **parcela vinculada a
aceite**, com a última após a homologação.

- Divida a implantação em **7 ciclos de 3 semanas** (`valor total ÷ 7`, ex.: R$ 153.753,25 → R$ 21.964,75).
- Cada ciclo fecha em três atos: **demonstração → entrega usável → aceite formal** (5 dias úteis, com
  vedação expressa de aceite tácito). Sem aceite, não há faturamento.
- O cliente **prioriza a ordem dos ciclos** a cada fechamento — isso não muda valor nem prazo e responde
  à demanda de "priorização da própria secretaria".
- Eixos continuados (consultoria, sustentação) ficam **mensais e em linha própria** quando o cliente assim
  decide; o ano 2 em **instrumento próprio**, para não virar contrato continuado por inércia.

## Ordem de trabalho: especificação ANTES da proposta (não depois)

Erro real cometido na proposta SEMAC: escrever a seção de painéis e só depois produzir a
especificação interna de UI/UX. O documento sai defensável, mas a especificação vira validação
retroativa em vez de fonte — e o que ela descobre de novo não entra no documento.

**Sequência correta:**

1. Especificar os painéis (blocos, funções, estados de tela, gatilhos, microcopy, fluxos, métricas).
2. **Derivar** a seção da proposta da especificação — só o nível de clareza que o cliente lê.
3. Auditar o inverso antes de entregar: varrer a especificação por conceito e conferir se cada um
   aparece na proposta; o que sobrar é decisão consciente de manter interno, não esquecimento.

O que a auditoria do caso real pegou e a proposta não tinha — itens que todo documento de painel
deve carregar:

- **Estado dos dados na tela**: o que acontece quando uma fonte atrasa (número permanece com a data
  do último dado, aviso de fonte atrasada, resto da tela operando; nada em branco, nada sem data).
- **Integridade das fontes** como entregável verificável (última carga, falhas e pendências por fonte).
- **Métrica de adoção** na avaliação de impacto (taxa de recomendações validadas ou recusadas com
  justificativa pelos órgãos) — mede uso real, não acesso.

Checar também por sinônimo antes de concluir que falta: "ficha do indicador" costuma estar no texto
como "rastro de origem"; "limiar" como "limites de gatilho".

## Composição de custos (exigência estrita)

O parecer costuma cobrar "planilha de composição de custos"; a norma aplicável (IN 05/2017) vale para
**dedicação exclusiva de mão de obra**, que não é o caso. O que o órgão pede, literalmente: perfis, horas,
valores unitários, custos indiretos, deslocamentos — **não** linha de lucro.

- Monte por **perfil × horas × valor-hora**, com indiretos, administrativos e tributos embutidos no
  valor-hora, e faça o **total quadrar exatamente** com o valor de contrato.
- Nunca exponha a margem como linha nem use a planilha interna de custo da ID no documento do cliente.
- Parta da planilha interna para calibrar horas e faça os valores finais "soarem razoáveis" (valor-hora de
  especialista sênior na ordem de R$ 130–240).

## Anexos (padrão)

- **Anexo A — Atendimento ao parecer**: item a item, em duas tabelas (condicionantes da conclusão e
  observações técnicas), com "onde consta" e a lista de documentos a apresentar na instrução processual.
  Entregar **separado**, não dentro da proposta.
- **Anexo B — Glossário**: fixa o vocabulário técnico que o parecer apontou como ambíguo (ex.: "80+ modelos",
  anomalias, horizontes, indicadores).
- **Anexo C — Currículos** (já existem em PDF institucional do Parque).
- **Especificação de painéis** — trabalho **interno**, fora do documento entregue: o cliente cobra que a
  proposta traga a especificação só no nível de clareza correto, com o detalhe (blocos, estados, funções,
  microcopy, fluxos, métricas de UX) guardado para a equipe. Wireframe em HTML → PNG (1440×1080) com
  `--screenshot` serve para alinhar internamente sem expor rascunho.

## Ponto sensível: vínculo da equipe

Quando a execução envolve empresas residentes, o parecer ataca "intermediação de terceiros". O argumento
que sustenta: a atuação por **ecossistema de inovação é admitida desde que coordenação institucional,
responsabilidade técnica e governança fiquem com o Parque** (é o que diz o parecer jurídico do próprio
Parque). Na prática, deixe explícito por integrante: **pesquisador contratado pelo Parque** × **sócios de
empresas residentes**, com a comprovação documental listada no Anexo A.

## Verificação

- [ ] `pdfinfo` confere e o número de páginas está dentro do orçamento pedido.
- [ ] Nenhuma página abaixo de ~2.000 caracteres (sem órfã).
- [ ] Somas da composição quadram com os valores de contrato.
- [ ] `vision_analyze` nas páginas-chave: sem corte, sem sobreposição, sem capa poluída.
- [ ] Zero nota interna, zero emoji, zero rodapé com numeração manual.
- [ ] Anexo A cobre todos os itens da conclusão do parecer.
