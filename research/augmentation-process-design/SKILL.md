---
name: augmentation-process-design
description: "Design, research and curadoria de soluções de augmentação de processos com IA — aumento de capacidade humana, não automação.

Load this skill when the user wants to research, catalog or design solutions that augment (not automate) human work with AI. Covers the granular solution concept, the A/B × I/II/III taxonomy, the PME-friendly bias, the operational analytics niche, and the delivery format (index + solucoes/ folder with YAML frontmatter)."
category: research
type: Research
timestamp: 2026-06-28T05:11:55Z
---

# Augmentation Process Design

> Skill para **pesquisar, catalogar e desenhar** soluções de augmentação de processos com IA. O foco é **augmentação** (amplificar talento humano) — não automação (substituir).

---

## Conceito Central: Solução Granular

**Definição de "solução"** (corrigida pelo usuário após interpretação errada inicial):

> Uma **alteração isolada e replicável** dentro de um processo. É a menor unidade que, **se aplicada sozinha, já entrega um ganho mensurável de produtividade**.

**Implicação direta:** cases grandes devem ser decompostos em soluções granulares. Exemplos:
- Case Allianz Nemo (7 agentes) = **7 soluções distintas** (uma por agente)
- Case Harvey (análise contratos + DD + drafting) = **pelo menos 3 soluções**
- Case McKinsey Lilli = **N soluções** (pesquisa, tone of voice, CaseAI, etc.)

**Critério de granularidade:** se um agente humano consegue **aprender e aplicar a alteração de forma independente** (mesmo que complementada por outras), ela é uma solução candidata. Se ela só faz sentido combinada com outras no mesmo fluxo, é uma etapa de uma solução maior, não uma solução.

---

## Taxonomia Oficial

### Por Categoria (escopo da mudança)

| Categoria | Definição |
|-----------|-----------|
| **A. Reengenharia do processo** | Processo inteiro é repensado do zero, com IA embutida na estrutura. Workflow fundamentalmente alterado. |
| **B. Otimização do processo** | Etapas específicas dentro de um processo existente são aumentadas com IA. Estrutura geral permanece, partes são otimizadas. |

### Por Tipo (papel da IA)

| Tipo | Definição |
|------|-----------|
| **I. Agente de IA** | Etapa/subprocesso sob responsabilidade da IA. Inputs e outputs claros, meios semi-estruturados. IA age com autonomia dentro do escopo. |
| **II. Assistente de IA** | IA executa ao lado de um humano, amplificando a produtividade. O humano continua responsável pela decisão final. |
| **III. Automação** | Automação tradicional ou LLM muito simples substitui etapa humana ou de outro sistema. Sem ambiguidade, regras claras. |

### Notação compacta

Use `categoria·tipo` no frontmatter e nas listagens. Ex: `A·I` (reengenharia com agente), `B·II` (otimização com assistente).

---

## Diretrizes de Mix (do usuário)

Quando o usuário pedir uma **pasta de referências / catálogo**, siga o mix:

- **~60-70% soluções simples/práticas** — baixo esforço de implantação, sem equipe de engenharia pesada, plug-and-play ou low-code
- **~10-20% soluções focadas em análise de dados** — dashboard, BI, query em linguagem natural, visualização, exploração de dados
- **~10-20% soluções enterprise/transformação maior** — reengenharias completas, multi-agent, governança

**Sinais de "solução simples/prática":** download + signup em < 5 min, free tier ou US$ 10-50/mês, no-code, deploy em horas, ganha valor sem customização pesada.

**Sinais de "enterprise/transformação":** requer equipe de implementação, investimento significativo, meses de rollout, métricas em escala de milhares de pessoas.

---

## Metadados YAML Padrão (cada arquivo .md de solução)

Todo arquivo de solução individual deve ter frontmatter YAML com:

```yaml
---
id: identificador-kebab-case-unico
titulo: Descrição clara da alteração (verbo + objeto)
case_pai: Nome do case maior (se aplicável)
categoria: A ou B
tipo: I, II ou III
setor: Setor de aplicação
porte_empresa: PME | Enterprise | Qualquer
ferramentas: [Ferramenta 1, Ferramenta 2]
fonte: URL da fonte primária
data_pesquisa: AAAA-MM-DD
human_in_the_loop: sim | não | parcial | configurável
ganho_principal: Métrica principal com delta
processo_original: "Como era antes (1-2 frases)"
processo_augmentado: "Como ficou depois (1-2 frases)"
---
```

**Campos opcionais:** `ganho_secundario`, `complexidade_implementacao`, `custo_estimado`.

---

## Formato de Index Enxuto

O `index.md` do catálogo deve ser **só listagem**. Não incluir:
- Instruções de "como usar"
- Padrões observados
- Próximas pesquisas recomendadas
- Templates para adicionar soluções
- Estatísticas extras além do total

**Formato aceito pelo usuário:**

```markdown
# Índice de Soluções — [Tema]

> Cabeçalho curto com data e origem.

**Categorias:** A — ... | B — ...
**Tipos:** I — ... | II — ... | III — ...
**Marcadores:** 🌱 simples/prática | 📊 análise de dados

---

## Soluções documentadas

- `id-da-solucao` — Título curto (categoria·tipo)
- `outra-solucao` — Outra descrição (categoria·tipo) 🌱
- ...

---

**Total: N soluções.** 🌱 = X simples/práticas. 📊 = Y de análise de dados.
```

**Regras para listagem:**
- Um item por linha começando com backtick-id
- Marcadores 🌱/📊 inline no item
- Categoria·tipo entre parênteses ao final
- Nada de tabelas — só lista com `-`
- Ordem alfabética por ID

---

## Fontes Recomendadas por Tipo de Solução

### Para cases enterprise de augmentação
- McKinsey Insights (`mckinsey.com/capabilities`)
- BCG Henderson Institute (`bcg.com/publications`)
- Deloitte Insights (`deloitte.com/us/en/insights`)
- HBR (Harvard Business Review)
- HBS Working Papers (`hbs.edu/ris/Publication Files`)

### Para cases de produtividade
- Granola Blog, Otter.ai, Reclaim.ai, Lindy, Superhuman — case studies nos sites oficiais
- Fathom, tl;dv, Fireflies — para transcrição

### Para cases de análise de dados
- Julius AI, Power BI Blog, ThoughtSpot Case Studies
- Metabase, Hex, Preset, Observable — open source
- ChartGen, Blink — para PMEs

### Para cases de vendas/outbound
- Clay Customers (`clay.com/customers/[empresa]`)
- HubSpot, Salesforce Einstein — case studies

### Para cases jurídicos
- Harvey.ai (Allen & Overy foi o pioneer)
- Law Society Gazette, Legal Futures

### Para cases de seguros/saúde
- McKinsey Alliances, Mayo Clinic, Abridge

---

## Workflow de Pesquisa para Catálogo

1. **Definir tema e escopo** com o usuário
2. **Confirmar o conceito de "solução granular"** antes de começar a escrever arquivos
3. **Confirmar o mix desejado** (simples/práticas vs enterprise vs dados)
4. **Disparar subagentes paralelos** via `delegate_task` se o escopo permitir, OU fazer pesquisa direta com `web_search` + `web_extract`
5. **Para cada case identificado**, decompor em soluções granulares (não manter o case inteiro como 1 solução)
6. **Validar cada solução** tem: fonte primária, métricas mensuráveis, processo antes/depois, replicabilidade
7. **Gerar arquivos .md individuais** com frontmatter YAML
8. **Gerar index.md enxuto** (só listagem, nada mais)
9. **Compactar em tar.gz** para entrega via Telegram

---

## Pitfalls Conhecidos

⚠️ **Não classificar o case inteiro como 1 solução.** O usuário corrigiu isso explicitamente. Case com N subprocessos = N soluções distintas, cada uma com seu ID próprio.

⚠️ **A granularidade é regra do catálogo, não da ideação para clientes.** O conceito de "solução granular e isolável" se aplica ao repositório de referências (catálogo de soluções documentadas). Na ideação para clientes (ex: pipeline de aumentação de processos), vale pensar tanto em soluções pontuais quanto sistêmicas — reengenharias completas que abrangem múltiplos nós, otimizações multi-etapa, e soluções interdependentes são válidas. Não aplicar a restrição de isolabilidade fora do contexto do catálogo.

⚠️ **Index não é lugar para instruções.** Após a listagem, colocar padrões, templates, "como usar" foi explicitamente rejeitado. Index = só listagem.

⚠️ **Não super-representar enterprise.** O usuário pediu mix 60-70% simples/práticas. Tools como Clay, Julius, Granola, Fathom, Lindy, Reclaim, Metabase, ThoughtSpot, Power BI devem ter presença forte.

⚠️ **Não negligenciar análise de dados.** O usuário pediu nicho explícito de "IA para controle e visualização de dados operacionais". Dedicar 10-20% do catálogo a isso.

⚠️ **Tamanho de cada .md deve ser curto.** 0.5-1.5KB por solução. Foco no que importa: processo antes, processo depois, ganho, replicabilidade. Nada de ensaios.

---

## Template de Cada Arquivo de Solução

```markdown
---
[frontmatter YAML]
---

## O que muda

[1-2 frases descrevendo a alteração concreta na etapa/processo]

## Implementação prática (opcional, breve)

[2-3 frases sobre como foi feito]

## Quem pode replicar

[1-2 frases sobre em que contextos essa solução se aplica]
```

**Não precisa mais que isso.** Cada arquivo é uma referência rápida, não um whitepaper.

---

## Histórico de Atualizações

- **2026-06-19** — Adicionado pitfall: granularidade é regra do catálogo, não da ideação para clientes. Soluções sistêmicas e multi-nó são válidas em contextos de consultoria.
- **2026-06-18** — Skill criada após correção do usuário sobre conceito de "solução granular" e taxonomia A/B × I/II/III. Mix 60-70% simples/práticas + 10-20% análise de dados. Formato de index enxuto (só listagem).
