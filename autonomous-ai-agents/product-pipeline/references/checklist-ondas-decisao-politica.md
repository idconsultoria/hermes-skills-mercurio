# Execução de checklist pré-lançamento em ondas + política de decisão 🔴/🟢

> Padrão validado em 14/08/2026 (projeto Zera/CFP IA, Onda 1–3). Quando existe um
> checklist pré-MVP em planilha (aba "Tarefas em tabela") com status por tarefa,
> executá-lo em **ondas** (agrupamentos por domínio e dependência) em vez de tarefa a
> tarefa, com **política de decisão explícita** aprovada pelo usuário.

## Estrutura da execução em ondas

1. **Ler o checklist real da planilha** (Sheets API, aba `Tarefas em tabela`): status,
   responsável, pts, **dependências** (coluna "Dependências" lista IDs).
2. **Agrupar em ondas por domínio + dependência** (ex.: Onda 1 backend → Onda 2 frontend →
   Onda 3 bot → Onda 4 infra → Onda 5 QA → Onda 6 LGPD → Onda 7 docs). Cada onda tem
   IDs, pts e deps explícitos.
3. **Separar o que é executável sozinho** (responsável = Gustavo, deps satisfeitas) do que
   depende do parceiro (Igor) — as tarefas bloqueadas NÃO travam as ondas independentes.
4. **Cada onda = ciclo product-pipeline completo:** Pi best gera code-tasks (gap analysis
   contra o código real — às vezes o checklist está DESATUALIZADO e a tarefa já existe!)
   → Pi cost executa em lotes (background, sem timeout) → agy revisa (print-mode flags)
   → correção Pi best max (MESMA sessão) → documentação Pi cost max → commit.
5. **Atualizar a planilha a cada onda fechada** (status → CONCLUIDO; contar progresso).

## Política de decisão 🔴/🟢 (documento `product/management/politica-decisao.md`)

Antes de qualquer execução, o usuário aprova uma política de quando PARAR e perguntar:

- 🔴 **REVISÃO OBRIGATÓRIA (parar e perguntar):** tecnologia crítica não especificada
  (lib/framework novo fora da Base Técnica/PRD/ADRs), princípios de design do projeto,
  forma de implementação de funcionalidade crítica (auth, motor, LLM, LGPD), custo
  recorrente (provedor pago novo), deploy produção, mudança de escopo.
- 🟢 **EXECUÇÃO DIRETA:** implementação dentro de decisão já tomada, correções mecânicas,
  QA/verificação, documentação técnica, infra staging/CI, atualização da planilha, commits.
- **Regra de ouro:** reversível com esforço pequeno → executa; difícil de reverter ou
  afeta custo/usuário/contrato público → pergunta; dúvida genuína → pergunta.
- **Checkpoints agrupados:** decisões 🔴 pendentes são apresentadas EM LOTE ao usuário
  (tabela de opções + recomendação), não uma a uma.

### Implementação da política

- Documento canônico: `product/management/politica-decisao.md` com tabela D1..Dn de
  decisões estruturais e status (decidida/pendente).
- **Cada prompt de Pi (best/cost/best max/cost max) DEVE carregar a política** e instruir:
  "🔴 → PARE e reporte (decisão, opções, recomendação, impacto); 🟢 → execute direto; ao
  final declare 'Política: nenhuma 🔴' OU liste as 🔴."
- Decisões estruturais viram **ADR** (ex.: `adr-018-frontend-separado-prototipo.md`) —
  o Pi best as cita como "decisões já tomadas, não redecidir".
- O AGENTS.md do repo ganha uma linha apontando que todo prompt de Pi deve carregar a
  política.

### Lições reais

- **Gap analysis do Pi best é ouro:** o checklist da planilha pode dizer "não iniciado"
  quando o código JÁ tem a feature (ex.: auth JWT completo da Task-004). O Pi best lê o
  código real e reporta o gap honesto — evita reimplementar.
- **Pi best PAROU sozinho nas 🔴** (ex.: D12 auth frontend, D4 persistência do bot) —
  não decidiu por suposição, reportou tabela de opções. O orquestrador faz relay ao
  usuário com `clarify` (opções em choices, recomendação em texto).
- **Terminologia de produto é decisão do usuário** (ex.: "usuário vê 'conversas', nunca
  'sessões'") — registrar em ADR e aplicar em copy/UI; não é decisão técnica.
- **Mudança de escopo assumida pelo usuário** (ex.: bot vira canal do núcleo em vez de
  SQLite) — registrar como ADR e reescrever as code-tasks retomando a MESMA sessão do
  Pi best (`pi --session`), nunca sessão nova.
