# Template de Solução — Arquivo .md Individual

> Cada arquivo documenta **uma alteração isolada e replicável** que produziu ganho mensurável de produtividade. O frontmatter YAML é obrigatório; as 5 seções do corpo são o padrão validado.

## Frontmatter YAML

```yaml
---
id: slug-identificador-unico
titulo: Descrição clara da alteração isolada
case_pai: Nome do case maior (ex: "Allianz Nemo")
categoria: A  # A = reengenharia do processo inteiro | B = otimização de etapas
tipo: I       # I = agente IA (etapa autônoma, I/O claros)
              # II = assistente IA (co-piloto, humano decide)
              # III = automação (substitui etapa humana)
setor: Seguros  # Setor de aplicação
porte_empresa: Enterprise  # Enterprise | PME | Variado | Qualquer
ferramentas:
  - Ferramenta 1
  - Ferramenta 2
fonte: URL da fonte primária
data_pesquisa: AAAA-MM-DD
human_in_the_loop: sim  # sim | não | parcial
ganho_principal: Métrica principal (ex: "-99% tempo de claim")
processo_original: "Como era antes — descrição do fluxo manual."
processo_augmentado: "Como ficou depois — descrição do fluxo augmentado."
---
```

## Body Sections (120-200 linhas totais)

### ## Contexto

**3 parágrafos obrigatórios:**

1. **A Organização** — porte, setor, receita, número de funcionários, contexto da empresa/instituição onde a solução foi aplicada. Por que ela buscou IA? Qual o histórico?

2. **O Problema** — gargalo específico que a solução veio resolver. Incluir números sempre que disponíveis: volume (ex: "2M transações/dia"), tempo ("7-30 dias"), custo, taxa de erro, satisfação. Descrever como era o processo antes e por que era insustentável.

3. **A Abordagem Escolhida** — por que essa solução específica, quais alternativas foram consideradas (e descartadas, e por quê). Qual o princípio de design? (ex: "digital-first, presencial por exceção")

### ## A Solução em Detalhe

**3 subseções:**

1. **Fluxo Operacional** — o que o agente/assistente/automação FAZ, etapa por etapa (numerado). Incluir como o input chega, como é processado, qual a saída. Ser específico.

2. **Arquitetura Técnica** — quais modelos LLM, quais integrações (APIs, CRMs, ERPs), fluxo de dados, infraestrutura (cloud, on-premise, edge). Se relevante: latência, volume processado, modelo de deployment.

3. **Interface Humano-Máquina** — como o humano interage com o sistema: o que a IA faz autonomamente, onde o humano decide, como o handoff ocorre, qual o papel do humano no loop. (É de validação? Revisão? Exceção? Supervisionamento?)

### ## Resultados Obtidos

**Métricas concretas** (usar bullets ou tabela):

- Tempo economizado (absoluto e percentual)
- Custo reduzido
- Volume processado
- Qualidade/satisfação (CSAT, NPS, acurácia)
- Adoção (% de uso)

**Impactos qualitativos** (1-2 parágrafos):
- O que mudou na rotina das pessoas
- Que novas atividades ficaram possíveis
- Como a organização mudou com a solução

> 📌 **Nunca invente números.** Use os dados do frontmatter como âncora. Para valores não disponíveis, escreva "estimado em" ou "relatado em".

### ## Como Replicar

**4 subseções obrigatórias:**

**Pré-requisitos** (bullets): dados necessários, integrações, treinamento, buy-in de stakeholders, infraestrutura, time.

**Implementação Passo a Passo** (numerado, 8-10 etapas):
1. Etapa 1
2. Etapa 2
...

**Ferramentas e Custos Aproximados** (tabela):

| Componente | Ferramentas | Custo/mês |
|---|---|---|
| LLM | GPT-4o, Claude | US$ X |
| Infraestrutura | Cloud | US$ Y |
| Time | N pessoas | US$ Z |

**Armadilhas Comuns** (5-8 itens com mitigação):
- **Armadilha**: descrição
  **Mitigação**: como evitar

### ## Onde Seria Relevante

**3 subseções:**

**Cenários Recomendados** — em que tipos de organização/setor/processo essa solução brilha. Perfil ideal (volume mínimo, maturidade digital, porte).

**Onde NÃO Aplicar** — contra-indicações explícitas. Quando o custo não justifica o benefício. Quando a solução quebra.

**Variações do Padrão** (bullets, 4-8):
- Variação 1 — descrição
- Variação 2 — descrição
- ...

## Exemplo de Arquivo Completo

Ver `expansion-pipeline.md` no diretório references desta skill para o pipeline de geração em massa (subagentes, paralelismo, verificação de qualidade).
