---
name: metricas-financeiras-servico-campo
description: "Use ao estruturar KPIs de serviço técnico de campo."
category: business
type: Orchestrator
timestamp: 2026-10-22T18:20:00Z
---

# Métricas financeiras de serviço técnico de campo

## Quando usar

Cliente cuja receita vem de **hora técnica certificada** (OS, contrato de manutenção, calibração,
ensaio, instalação), com folha como maior custo, ciclo de caixa longo e ERP transacional (OMIE e
similares) — tipicamente 30 a 300 pessoas. É cliente de serviço, não de produto: a métrica que
decide o negócio é **margem de contribuição por OS/contrato**, e a alavanca é **utilização
faturável com qualidade**.

Não serve para métricas de SaaS (MRR/churn/LTV:CAC), nem para valuation (ver `valuation-consultivo`).

## Regra zero — três fatos que mudam o desenho

Estabeleça estes três antes de escolher métrica; sem eles a árvore nasce errada:

1. **O ativo escasso é hora técnica, não capital.** Capacidade vendável = nº de técnicos × horas ×
   utilização. A receita é limitada por isso, não por demanda (quase sempre).
2. **A receita tem naturezas com economias diferentes** — recorrente (contrato com ciclo de
   validade, ex. NR-10/NR-35 de 12 meses), avulsa/corretiva e projeto/instalação. Somar as três num
   "faturamento" único esconde qual metade dá prejuízo.
3. **Ciclo de caixa fragmentado:** OS → medição → NFS-e → boleto → portal do cliente → recebimento.
   Existe **receita executada não faturada** e **fatura não recebida** — duas métricas distintas.

## Nomenclatura travada — os quatro estágios da receita

A mesma palavra designando quatro números diferentes é a causa nº 1 de reunião que não decide. Antes
de qualquer KPI, exija o adjetivo — em todo painel, em toda planilha, em toda fala:

| Estágio | O que é | Dono | Para que serve |
|---|---|---|---|
| **Receita ganha** | contrato assinado, serviço não executado | comercial | prever capacidade, decidir contratação |
| **Receita produzida** | serviço prestado e comprovado | operação | margem, DRE gerencial, comparação com custo |
| **Receita faturada** | nota emitida e aceita | administrativo | medir se o trabalho virou documento a tempo |
| **Receita recebida** | valor creditado | financeiro | prazo, inadimplência, capital de giro |

Regras que decorrem disso:

1. **Receita, sem adjetivo, é receita produzida.** Todas as outras andam sempre adjetivadas. Quando
   alguém diz “a receita caiu”, a primeira pergunta é *qual* — na maioria dos casos caiu o faturamento
   ou o caixa e a operação está intacta, o que muda completamente a decisão.
2. **O valor está nas três distâncias, não nos quatro números**: ganha→produzida = velocidade de
execução; produzida→faturada = receita presa; faturada→recebida = prazo de cobrança. A soma é o ciclo
   total, de contrato assinado a dinheiro em conta.
3. **Só a produzida tira conclusão de desempenho.** Margem, comparação mês a mês e custo por hora se
   apuram em competência; caixa serve para cobrança e capital de giro — nunca no mesmo número.
4. **Parcela não é recorrência.** Recorrência é o formato do **serviço** (cliente recebe de novo no mês
   seguinte, pela mesma obrigação, com renovação esperada), não do boleto. Instalação única em 10
   parcelas é receita avulsa com recebível espalhado — risco de crédito, não previsibilidade. E contrato
   anual pago à vista é recorrente: 1/12 por mês, mesmo com o dinheiro entrando de uma vez.

Exemplo numérico completo (três contratos fictícios, divergência trimestral, quatro jeitos errados de
contar) e a estrutura de painel em cinco pastas com os indicadores nomeados: `references/estagios-receita-e-painel.md`.

## Ordem de execução (não inverter)

1. **Definições** — travar as 5 definições abaixo, por escrito, antes de medir qualquer coisa.
2. **Base mínima** — 6 extrações do ERP: OS (cabeçalho), itens de OS, apontamento de horas,
   contratos, NFS-e/títulos, clientes/equipamentos. Sem isso não existe nada acima.
3. **Conciliação de UM número** — receita do ERP = NFS-e emitida = contábil. Se não fecha, o painel
   não sobe: primeiro concilia.
4. **Árvore** — 4 camadas, no máximo 7 números no topo (fórmulas em
   `references/catalogo-metricas-campo.md`).
5. **Donos e guardrails** — um dono por número; um contra-número por número.
6. **Cadência** — diário/semanal/mensal/trimestral, cada tier com direito de decisão próprio.
7. **Faseamento de 90 dias** — 5 números confiáveis → margem por contrato → painel por segmento →
   forecast e capital de giro.

## As 5 definições que travam o sistema

Se duas pessoas respondem diferente, todos os números desmoronam:

1. **Hora faturável** — inclui deslocamento? espera no cliente? retrabalho? Definir e assinar.
2. **OS concluída** — técnica (serviço executado) vs administrativa (certificado + ART + NFS-e +
   medição no portal). O intervalo entre as duas é **receita presa + risco de conformidade**.
3. **Receita reconhecida** — competência da execução ou emissão da nota (regime de caixa é armadilha
   em serviço).
4. **Custo direto** — folha com encargo, benefício, veículo, ferramenta e EPI; custo real ≈ 1,4× o
   salário. Ratear só o salário faz todo contrato parecer lucrativo.
5. **Contrato ativo** — assinado, vigente e com receita no mês; renovação automática não é receita
   nova.

## Árvore em 4 camadas

- **N1 — Resultado (sócio, mensal):** receita por natureza · margem de contribuição · geração de
  caixa · DSO.
- **N2 — Drivers (diretoria, mensal), no máximo 5:**
  `Receita de serviço = Horas faturáveis × Tarifa média realizada + Peças + Recorrente` ·
  `Recorrente = Contratos ativos × Ticket médio × (1 − churn de contrato)` ·
  `MC% = 1 − (HH + deslocamento + peças + terceiros) / receita` · `Backlog em semanas de capacidade` ·
  `Ciclo de caixa = PMR − PMP + WIP não faturado`.
- **N3 — Folhas operacionais (coordenação, semanal):** utilização faturável, taxa de realização
  (horas faturadas ÷ horas apontadas), first-time fix, retrabalho de 2ª visita, SLA, tempo de ciclo
  da OS, **OS concluídas há >30 dias sem certificado**, WIP > 15 dias, aging de recebíveis.
- **N4 — Unidade de decisão:** margem por segmento, por cliente, por contrato, por família de
  equipamento, por tipo de OS. Sem N4 o painel informa e não decide.

## Guardrails (cada número com seu contra-número)

- Utilização ↑ **vs** SLA / first-time fix ↓ → vender velocidade quebrando a primeira visita.
- Margem ↑ **vs** receita nova ↓ → preço certo, cliente errado.
- Horas faturadas ↑ **vs** horas de segurança/treinamento ↓ → em empresa de NR-10 e trabalho em
  altura, esse par também é risco de vida.
- Faturamento antecipado ↑ **vs** certificado emitido ↓ → faturar sem entregar documento.

Leitura: métrica subindo com seu guardrail caindo por **dois ciclos** é gaming, não melhoria —
escala, não premia.

## Cadência e ritual

- **Diário (coordenação):** fila de OS, técnicos em campo, OS travadas em peça/portal.
- **Semanal (1 página, ≤7 números):** receita da semana vs plano, utilização, first-time fix, OS >30
  dias, faturado não recebido, propostas abertas, WIP.
- **Mensal:** DRE gerencial, margem por segmento/cliente, aging, variação vs orçado.
- **Trimestral:** capacidade vs backlog, mix recorrente, tarifa média, decisão de contratação.

## Pitfalls

- **Transplantar métrica de SaaS/indústria.** MRR, churn de assinatura e LTV:CAC não descrevem
  serviço de campo; margem bruta contábil rateada por hora aponta lucro onde há prejuízo.
- **Começar pelo dashboard.** Painel antes de definição travada e de base conciliada vira três
  números diferentes na mesma reunião — e morre na terceira semana.
- **Confiar no apontamento de horas sem validar.** Apontamento retroativo e grosseiro destrói
  utilização e margem por OS; testar com uma semana de OS reais antes de prometer o indicador.
- **Ignorar acesso restrito.** Cliente que fecha o fluxo financeiro não impede o trabalho: desenhar
  com proxies operacionais (OS, horas, certificados) e pedir ao financeiro só 3 números de topo, em
  vez de tentar abrir o que ele fechou.
- **Medir margem por OS antes de o custo-hora existir.** Média de horas apontadas como base de rateio
  produz margem de mentira; o custo-hora vem antes.
- **Esquecer o vínculo com conformidade.** Em serviço regulado (ensaios, calibração, segurança),
  "OS sem certificado" é ao mesmo tempo receita presa e exposição legal — é o indicador com melhor
  retorno político para começar.
- **Tratar receita avulsa parcelada como recorrente.** Infla a base contratada, faz o negócio parecer
  maior e esconde um recebível que cresce todo mês: a empresa acha que tem cliente que volta quando
  tem cliente que deve. Antes de classificar, aplique os três testes de recorrência do arquivo de
  referência.
- **Cobrar do time um indicador que ele não controla.** Indicador de resultado (receita produzida,
  margem, ciclo total) informa a diretoria e orienta decisão; o que se cobra é o indicador de controle
  da área — operação responde por utilização e receita presa, comercial por conversão e renovação,
  administrativo por prazo de emissão e pendência documental, financeiro por prazo e inadimplência.
  Cobrança sobre número que depende de quatro áreas produz medo, e medo produz número ajustado.
- **Publicar painel sem dono único por indicador.** Quando duas áreas respondem pelo mesmo número,
  nenhuma responde; quando não tem dono, vira decoração.

## Entregável

- Árvore de métricas com dono e cadência por ramo + dicionário de definições + planilha de margem por
  contrato. Material de cliente: **HTML/planilha na identidade da ID** (teal/navy, Neulis Neue +
  Nunito Sans), sem emoji e sem pizza/donut (barras).
- Explicar o critério antes de mostrar o número: cliente de serviço discute definição, não planilha.
- **Peça de estudo para diretoria**: PDF A4 curto (5–6 páginas), didático e encadeado — primeiro
  princípio, os quatro estágios, as regras de medição com exemplo numérico, os painéis com donos, o
  rito semanal e uma nota final de que metas exigem análise retroativa (12 meses; mínimo 3) e sessões
  de planejamento estratégico/tático antes. Sem emoji, sem nota interna, sem gráfico de pizza/donut.
  Produção em `documento-a4-marca-id`.
- Apoio já no acervo (`business/index.md`): `revenue-kpi-framework` (árvore com math reconciliante e
  donos), `variance-analysis` (orçado vs realizado), `revenue-leakage` (receita que vaza),
  `financial-analyst` (forecast, fluxo de 13 semanas), `kpi-dashboard-design` (metodologia divergente
  entre painéis).
