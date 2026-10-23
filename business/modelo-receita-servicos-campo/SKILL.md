---
name: modelo-receita-servicos-campo
description: "Use ao modelar receita de serviço técnico de campo."
version: 1.0.0
author: Hermes (co-criada com Gustavo Mello, ID Consultoria — 22/10/2026)
license: MIT
metadata:
  hermes:
    tags: [receita, kpi, servicos-de-campo, competencia, caixa, painel, consultoria]
    category: business
    related_skills: [revenue-kpi-framework, revenue-reporting, revenue-leakage, financial-analyst, variance-analysis, documento-a4-marca-id]
    projects: [solution-master]
type: Orchestrator
timestamp: 2026-10-22T00:00:00Z
priority: high
---

# Modelo de receita de serviço técnico de campo

Carregue esta skill quando precisar desenhar, explicar ou auditar o modelo de receita de uma empresa que vende **tempo de gente certificada** (técnico que vai ao cliente, executa e assina laudo/certificado): manutenção de equipamentos, ensaios elétricos, calibração, telecom, medical, safety — 40 a 100 pessoas, ticket por OS/contrato, ciclo de caixa longo, cliente grande e/ou público.

Não usar para SaaS de assinatura nem produto de prateleira — a aritmética é outra.

## Primeiro princípio (a conta-mãe)

O que a empresa vende é tempo de gente certificada. Duas consequências:

1. **A receita tem teto físico**, não de demanda: `receita de serviço = técnicos × horas disponíveis × % faturável × preço da hora`.
2. **O custo é gente** — folha + encargo + benefício + veículo + ferramenta + EPI. Não há matéria-prima para comprar mais barato.

Toda métrica é um pedaço dessa conta. Se a receita cai, é **um** dos quatro termos — sem a decomposição, a discussão vira "mercado".

## Os quatro estágios (nomenclatura travada)

Nunca dizer "receita" sozinho. Quatro palavras, sempre:

| Estágio | O que é | O que NÃO é | Dono |
|---|---|---|---|
| **Receita ganha** | contrato assinado, não executado = backlog | receita, lucro | comercial |
| **Receita produzida** | serviço prestado (competência) — **a única receita de verdade**, entra em margem/DRE | caixa | operações |
| **Receita faturada** | nota emitida + medição = direito de cobrar | receita, caixa | administrativo-financeiro |
| **Receita recebida** | dinheiro na conta | receita | administrativo-financeiro |

**O valor não está nos quatro valores — está nas três distâncias:**

- ganha → produzida = velocidade de execução (backlog andando ou parado)
- produzida → faturada = **receita presa** (serviço feito, documento não saiu)
- faturada → recebida = prazo de cobrança / DSO
- ganha → recebida = **ciclo de caixa inteiro** (dias entre assinar e receber)

## Temporalidade (onde os erros custam mais caro)

- **Margem, utilização, custo da hora, produtividade → competência.** Comparar receita que caiu em outubro com a folha de outubro compara trabalho de agosto com custo de outubro: número inventado.
- **Prazo, aging, saldo, "o que posso pagar" → caixa.**
- **Nunca misturar os dois no mesmo indicador.**
- **Contrato entrega 1/12 por mês**, no mês em que o serviço foi prestado (não no mês da assinatura, não no mês da nota).
- **Teste do critério:** somados os 12 meses, a receita reconhecida iguala o valor do contrato. Competência não muda o total, distribui.
- **Contrato encerrado:** a fração para no mês em que o serviço parou → o degrau para baixo é a perda de recorrência, visível na competência.
- **Cobrança trimestral/anual:** faturamento em bloco não significa perda de recorrência. A recorrência é propriedade do contrato, não do calendário da nota.
- **Faturado além do entregue = obrigação** (receita antecipada), não lucro. O espelho: **executado não faturado = receita presa**.
- **Parcela ≠ recorrência.** Parcelamento é formato do boleto (financiamento de recebível); recorrência é formato do serviço. Contrato avulso em 10× não é recorrente; contrato anual pago à vista **é** recorrente (1/12 por mês, caixa antecipado).
- **Imposto:** o regime de apuração (Simples, emissão vs recebimento) não muda a análise de margem — confirmar com a contabilidade, nunca escolher regime para "pagar menos no mês".

## Os quatro painéis (cada um com UM dono)

Máximo 4–6 indicadores por painel.

- **Visão geral — direção.** As quatro receitas, ciclo de caixa e as médias de tempo entre estágios. É o painel de leitura da reunião semanal.
- **Comercial — receita ganha.** Contratos/propostas ganhas, conversão, ticket médio, ciclo de venda, backlog em semanas de capacidade.
- **Operações — receita produzida.** Utilização faturável (horas faturáveis ÷ disponíveis), realização (horas faturadas ÷ apontadas), custo da hora técnica, margem de contribuição por contrato/segmento, retrabalho e primeira visita, OS > 30 dias sem certificado.
- **Administrativo-financeiro — faturada e recebida.** Faturamento no mês, receita presa (produzida − faturada), faturado não recebido, aging, DSO.

**Guardrails (pares anti-gaming):** utilização ↑ contra primeira visita/SLA ↓; preço realizado ↑ contra receita nova ↓; horas faturadas ↑ contra horas de treinamento/segurança ↓.

## Propriedade e justiça na cobrança

- **Um dono por indicador** (nunca dois — dono compartilhado é dono nenhum).
- **Cobra-se pelo que a pessoa controla.** Indicador de resultado informa a direção; indicador de controle é o que se cobra do time. Utilização é do operacional, preço realizado é do comercial, resultado consolidado é da direção.
- Cada dono entrega o seu número **mês a mês**.

## Rito

- **Reunião semanal de operação** com todas as equipes olhando os números antes de discutir o problema.
- Leitura mensal por dono; trimestral para decisão de estrutura (contratar técnico, entrar/sair de segmento, reajustar tabela).
- **Metas exigem processo anterior:** análise de dados retroativos + sessões breves de planejamento estratégico/tático. Nunca definir meta por decreto no documento — registrar a nota.

## Pitfalls

1. **Painel de 20 indicadores** — 4–6 por painel, 7 no topo. Mais que isso ninguém orienta.
2. **Contar o contrato inteiro na assinatura** — mês glorioso seguido de meses vazios; comissão sobre receita que não existe.
3. **Usar o caixa como receita** — comemora calendário de boletos; decide contratação em cima de erro de data.
4. **Ratear só salário no custo da hora** — todo contrato parece lucrativo; o custo real é salário × encargos + benefícios + veículo + ferramenta + EPI.
5. **Sem fechamento mensal não existe competência** — OS aberta há dois meses corrompe a receita do mês. "OS > 30 dias em aberto" é requisito de confiabilidade, não só controle operacional.
6. **Julgar contrato pelo mês isolado** — mês serve de alarme, acumulado serve de veredito.
7. **"Receita" sem qualificador** na boca de diretor gera meia hora de reunião discutindo o que cada um quis dizer.

## Referências

- `references/exemplo-numerico.md` — três contratos fictícios mostrando os quatro estágios, o efeito da cobrança trimestral e os quatro modos de errar. Material didático para guia/treinamento.
- `revenue-kpi-framework` — árvore de KPIs com math reconciliante; `revenue-reporting` — narrativa e cadência; `revenue-leakage` — vazamento e recuperável.
