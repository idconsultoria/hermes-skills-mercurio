# Guia de Princípios — Propostas Comerciais (ID Consultoria)

Resultado de deep-research (14/08/2026, 3 agents paralelos, 40+ fontes: HBR, VeraSage/Ron Baker, RAIN Group, Win Without Pitching, Consulting Success, Slideworks, Qwilr, Proposify, Paperbell). Artefatos em disco:

- Guia completo: `/opt/data/Guia_Principios_Propostas_Comerciais.md`
- Template HTML com marca ID: `/opt/data/Modelo_Proposta_Comercial_ID.html` (15 slides, 87 placeholders `{{NOME}}`, fontes/logo/fundos embutidos)
- Dados brutos da pesquisa: `/opt/data/propostas_consultoria_pesquisa.json`, `/opt/data/relatorio_precificacao_consultoria.json`

## Os 12 princípios (resumo)

1. **A proposta é a conclusão do processo, não o começo** — discovery/qualificação antes (fit, orçamento, decisor, prazo); proposta prematura reduz vitória; a decisão se constrói na descoberta (Consulting Success: ~30% → ~70% fechamento ao reordenar).
2. **Estrutura SCR (McKinsey/BCG/Bain)** — Situação → Complicação (custo de NÃO agir) → Resolução. Ordem: Capa → Resumo Executivo (1 pág., **escrito por último**, **com o preço** — "esconder o preço sinaliza desconforto") → Entendimento do desafio → Escopo (com exclusões) → Metodologia/cronograma → ROI antes do preço → Prova social → Investimento → Condições → "Sobre nós" POR ÚLTIMO → Próximos passos. Extensão: 10–15 pág. formal / 4–6 pág. independente / 1–2 recorrente.
3. **Persuasão VTL (Valor → Confiança → Simpatia)** — cada seção deve construir pelo menos um; se não constrói nenhum, corte (The Proposal Lab).
4. **Prova social** — "não prometa, prove"; substanciar em empresa, pessoas, oferta; especificidade vence slogan.
5. **Escopo à prova de escopo creep** — entregáveis verificáveis (formato + aceite + data), exclusões explícitas, responsabilidades do cliente, change order.
6. **Precificação por valor, nunca hora** — hierarquia: hora/diária (pior) < retainer (Pay for Access) < preço fixo por projeto (padrão B2B, nunca horas×taxa, buffer 1,3–1,5x) < value-based (ROI ~5x para o cliente). MVR = piso interno.
7. **Três opções Good-Better-Best** — médio "Recomendado" por design; fences claras; gaps 1,4–1,8x e 2,0–3,0x; efeito decoy direciona para a opção-alvo.
8. **Matemática do desconto** — 10% off ≈ −33% de lucro; desconto só estratégico (em troca de algo); negocie escopo, nunca taxa.
9. **Preço em tabela por linha mapeada a entregáveis** (+35,8% fechamento, Proposify) — nunca só o total ("dá pra baratear?").
10. **Condições explícitas** — validade 14–30 dias ("propostas abertas raramente fecham"), pagamento entrada + marcos, confidencialidade.
11. **Apresente ao vivo + follow-up planejado** — apresentar em reunião (nunca só e-mail); follow-up 3–5 dias e 1–2 dias antes do vencimento; reversão de direção quando o comprador esfria (RAIN Group).
12. **Timing é estratégia** — enviar em até 24h pós-reunião; ~50% das propostas decididas em 24h após abertura; 3+ stakeholders nos 5 primeiros dias = 1,9x mais aceitação; 37% dos deals morrem por falta de fit; personalização > tudo (66% migram por falta dela).

## Template HTML (marca ID)

- 15 slides: Capa (bloco central: logo cliente + divisor + logo ID; título 96; subtítulo 36; meta 4 colunas) → Resumo Executivo (com preço) → Desafio (com "Custo de não agir") → Escopo → Prova → Metodologia → ROI → **Transição teal** (fundo dos slides de transição do deck, título 96) → Investimento (3 tiers GBB + racional + chip de desconto) → Garantia → Condições → Responsabilidades → Sobre a ID → Próximos passos (assinatura) → Final (logo + validade teal `#1AAEBD` + disclaimer).
- Slides padrão: símbolo/mark da ID no canto superior esquerdo, título 60 + subtítulo 24, ícones Lucide-style teal nos títulos de coluna, bullets brancos.
- Logo ID vetorial extraído do deck em `/opt/data/work/minuzzo/logo_id.svg`; mark (sem tagline) em `logo_id_mark.svg`.
