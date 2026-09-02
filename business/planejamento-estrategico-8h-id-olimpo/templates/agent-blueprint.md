# Agent Blueprint — 1 Processo → 1 Time de Agentes (Olimpo/Capitolino)

> 1 página por processo. Preencher na Sessão 2, Bloco 3 (20' por processo). Total: 3 páginas.

## Processo: [Nome — ex: "Geração de proposta comercial"]

**Escolha:** Impacto [alto/médio] × Esforço [baixo/médio] | Volume: [ex: 12/mês] | Horas/mês liberadas: [ex: 16h]

### SIPOC enxuto (5')

| | Conteúdo |
|---|---|
| **S**uppliers | [quem fornece input — ex: Sheets Symplexis, Drive, cliente] |
| **I**nputs | [dados de entrada — ex: briefing, tabela de preços] |
| **P**rocess (3–5 passos) | 1. [passo] → 2. [passo] → 3. [passo] → 4. [human-in-loop] → 5. [entrega] |
| **O**utputs | [entrega — ex: PDF proposta + email] |
| **C**ustomers | [quem recebe — ex: lead, sócio revisor] |

### Blueprint do Agente

| Campo | Definição |
|---|---|
| **Papel** | [Olimpo = executor autônomo / Capitolino = orquestrador multi-agente] |
| **Ferramentas** | [APIs, Drive, Delfos, Sheets, WhatsApp, Inter, nfelib] |
| **Inputs estruturados** | [ex: JSON do briefing, linha da planilha] |
| **Outputs** | [ex: PDF, linha em Sheets, mensagem WhatsApp] |
| **Regra de decisão** | [ex: "se valor < R$10k, envia direto; se > R$10k, pede aprovação"] |
| **Human-in-loop** | [onde humano aprova — ex: "Gustavo aprova proposta antes de enviar"] |
| **Métrica de sucesso** | [ex: "proposta em <2h, 0 retrabalho em 80% dos casos"] |
| **Dono técnico** | [Nome] + prazo piloto: [data] |
| **Crawl-Walk-Run** | Crawl: [piloto baixo risco] → Walk: [integra ERP/CRM] → Run: [autonomia cross] |

### Riscos deste agente (pré-mortem)

| Risco | Mitigação | Dono |
|---|---|---|
| [ex: LGPD — dados cliente expostos] | [ex: anonimizar antes do agente] | [Nome] |
| [ex: bloqueio IP] | [ex: rotação via Olimpo (IP residencial)] | [Nome] |

---
*Blueprint gerado em [data] — Sessão 2. Próximo passo: implementar até [data] e medir [métrica].*
