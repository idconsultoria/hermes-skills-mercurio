# Caso real: Minuta TJSE × SergipeTec (ago/2026)

Análise de contrato administrativo sob a ótica da **ID Consultoria (subcontratada da SergipeTec)**. Checklist com numeração de cláusulas e IDs dos documentos no Drive para reprocessamento futuro.

## Contexto

- **Contrato:** TJSE (CONTRATANTE) × Sergipe Parque Tecnológico — SergipeTec (CONTRATADA, OS sem fins lucrativos), por **contratação direta art. 75, XV, Lei 14.133/2021**.
- **Objeto:** Plataforma de Inteligência de Dados para Mutirões Judiciais e Gestão de Custas Processuais — motor de cálculo, parcelamento em até 6x, conciliação bancária (Banese), integração SEFAZ/CEDA sobre dívida ativa não tributária (~R$ 22,3M nominais; projetados R$ 30–40M). Mutirão de conciliação até novembro.
- **Papel da ID:** subcontratada/parceira técnica da SergipeTec. Empresa: **ID.TEAL CONSULTORIA EM GESTAO ORGANIZACIONAL LTDA, CNPJ 54.569.818/0001-59**, sócio-admin Gustavo Alexandre Souza Mello (36%), capital R$ 20.000.

## Documentos no Drive (IDs)

- MINUTA CONTRATO Nº TJSE vs.2 — `1CG_cD_vwHFNgqZ0yj6fOi9yefDZL3b-KkSttGSfZQ7A` (mod. 06/08/2026)
- Plano de Trabalho — Sergipetec — `1R8PCezBW8QtjHA1g4Qi6fZulxJkIBQ62IesN3Uqx3bM`
- Proposta de Plano de Trabalho — SergipeTec — `1Kbd8ryzbZB_Q1ZpOAOEgM-gg77sghG1lokyj3buSjis`
- Contrato Social ID.TEAL (PDF) — `1P6bnftUuhJgO9PrsBAqZ83jtjySDYLSp`
- Documentos de Cadastro ID no SergipeTec — `12hOVSAK4SCg5MHv1deKQWYtBiBIxr5yzBVDOsbQKQhk`
- Declaração de Natureza Exclusiva (EAI / ArtemisHub) — `1WX_zJ3t77mqn8h1ekWb6k7CmvRAYJZvj5__0zt6mEx4`

## Achados-chave por cláusula

| # | Cláusula | Risco para a ID |
|---|---|---|
| 19 | Subcontratação | Veda o núcleo (desenvolvimento principal, arquitetura, engenharia de dados, gestão, sustentação principal, segurança). Só acessória c/ autorização prévia + composição de custos (19.2.III) + não esvaziar capacidade. **O escopo da ID É o núcleo vedado.** |
| 18 | Execução direta | 18.4: contratada executa diretamente a parcela principal; 18.1: 13 competências obrigatórias. |
| 9–11 | Preço/pagamento | Por produto aceito (6 produtos, 15–90 dias); sem aceite tácito (10.8); 30 dias pós-ateste (11.3); sem antecipação (11.6); preço inclui tudo (9.6) → capital de giro 90–120 dias. |
| 20 | LGPD | Papéis a definir (20.2); **proibido treinar IA com os dados (20.6.V)**; IA exige autorização formal (20.7); incidente 24h (20.9); confidencialidade por profissional (20.5). |
| 21 | Propriedade intelectual | Código novo → TJSE sem custo (21.2/21.3); componentes preexistentes ficam com a ID só se identificados antes (21.5). |
| 22/25 | SLA/sanções | 99,5% disponibilidade; crítico 1h/4h; multas 0,5%/dia (10% limite), 10%/15% inexecução; multa por incidente de dados (25.3.IV). |
| 8 | Vigência | 24 meses (implantação 90 dias + sustentação 21 meses); prorrogável (8.5). |
| 23 | Dependências externas | Escudo: não responde por indisponibilidade de terceiros (SEFAZ/Banese) se comunicar + contingência (23.2). |
| 28 | Integridade | Vedado parente até 3º grau de dirigente (28.3); ID é residente do SergipeTec — documentar relação prévia. |

## Divergência central

**Minuta: 24 meses, valores em branco `[VALOR]`.** **Plano de trabalho: 12 meses de faturamento** (R$ 9.600/sprint + R$ 5.200/mês ≈ R$ 88.400/ano + banco de 800h × R$ 220/h). Precificar pelo contrato real, não pelo plano.

## Alertas societários

- ID.TEAL **não tem CNAE de desenvolvimento de software (62.01-5)** — objeto social (85.99-6/04 treinamento, 62.04-0/00 consultoria TI, 70.20-4/00 gestão) pode não cobrir o núcleo; avaliar alteração contratual.
- Contrato interno ID ↔ SergipeTec deve ser **escopo fixo/resultado** (nunca locação de mão de obra — minuta insiste em "sem dedicação exclusiva", 1.3.II e 4.1).

## Formato de entrega aprovado

Resumo executivo no chat (riscos numerados, bullets) + arquivo `.md` completo via `MEDIA:` — tabelas/comparações estruturadas nunca inline entre mensagens (preferência registrada do usuário).
