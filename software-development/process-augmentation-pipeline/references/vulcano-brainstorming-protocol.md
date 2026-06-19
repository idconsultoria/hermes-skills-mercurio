# Protocolo Vulcano para Brainstorming (Etapa 2)

> **Referência do `process-augmentation-pipeline`**
> Execução validada no Sergipetec (Junho 2026) — 7 clusters, 14 engramas, 130 soluções

## Objetivo

Transformar o Vulcano de ferramenta de "validação superficial" (2 chamadas, nota 1.2/10) em **motor de profundidade arquitetural** (7+ chamadas, nota 7.2/10). O protocolo garante que cada cluster do grafo causal receba pelo menos 2 engramas de referência com extração ativa antes da ideação.

---

## Protocolo Passo a Passo

### Passo 1 — Para cada cluster, executar vulcano_context

```
vulcano_context(query="<descrição do cluster em português>", max_tokens=2500)
```

**Regra:** 1 chamada por cluster. Se o cluster tiver > 12 nós, considerar 2 chamadas com queries complementares.

**O que NÃO fazer:** pular clusters "menos importantes". A execução do Sergipetec mostrou que clusters com baixa cobertura do vault (Comunicação, Cultura) são exatamente os que mais precisam de expansão — pular só piora a lacuna.

### Passo 2 — Extrair a Ficha de Engrama

Para CADA engrama retornado, extrair ATIVAMENTE 4 campos:

| Campo | O que extrair | Exemplo (DocuWare) |
|-------|--------------|---------------------|
| **Arquitetura** | Etapas, componentes, fluxo de dados, decisões de design | "4 etapas — captura → classificação → extração → indexação. Active learning realimenta o modelo" |
| **Métricas de ganho** | Números concretos: % redução, horas economizadas, R$ | "Redução de 70-85% no tempo de processamento. De 2-5 min/doc para 10-30 seg" |
| **Armadilhas** | Onde a solução falha, edge cases, erros comuns de implementação | "Amostra de treinamento mal preparada. Subestimar variedade de layouts. Automatizar sem validação humana para dados financeiros" |
| **Onde NÃO aplicar** | Perfil de organização/processo contraindicado | "Volume < 500 docs/mês — custo de implementação não se paga. Sem ECM implantado. Documentos altamente não estruturados" |

**Regra:** Extração ATIVA, não leitura passiva. A diferença entre "li o engrama" e "preenchi a ficha" é a diferença entre uma solução genérica ("criar um dashboard") e uma solução arquitetural ("dashboard conversacional com agente que traduz perguntas em português para queries, usando Google Sheets como data warehouse — inspirado no PowerBI MCP").

### Passo 3 — Propor soluções com citação de engrama

Cada solução deve conter o campo `Referência:` citando o(s) engrama(s) que a inspiraram.

**Formato:**
```
### S-001 · Nome da Solução
- **Categoria × Tipo:** B·I
- **Nós alvo:** DOR-JUR-42, DOR-ASP-09
- **Referência:** DocuWare ECM + Notion Enterprise Search
- **Descrição:** ...
- **Mecanismo de ganho:** ...
```

**Métrica de qualidade:** > 80% das soluções devem (a) citar um engrama, (b) demonstrar adaptação ao contexto real (pessoas, processos, códigos de nó específicos). Na execução Sergipetec, 92% atenderam.

### Passo 4 — (Opcional) Comparação qualitativa

Quando há um baseline anterior (brainstorming sem Vulcano), gerar `analise-qualitativa-original-vs-vulcano.md` com 7 dimensões:

1. Distribuição Categoria × Tipo
2. Mecanismo de ganho explícito (% com métrica concreta)
3. Arquitetura de solução (% com padrão de implementação)
4. Adaptação ao contexto real (% com pessoas/processos reais)
5. Armadilhas identificadas (% com riscos)
6. Inovação (% que adapta vs. replica)
7. Completude (% soluções detalhadas vs. "em elaboração")

---

## Verificação de Qualidade

Ao final da Etapa 2, verificar:

```bash
# 1. Número de engramas consultados ≥ número de clusters
grep -c "Referência:" etapa-2-brainstorming/propostas-solucoes.md

# 2. Pelo menos 1 solução cita engrama por cluster
grep -c "vulcano_context" <log da sessão>

# 3. Matriz Categoria × Tipo soma 130 (ou o número-alvo)
# 4. Distribuição I+II ≥ 30% do total (sinal de profundidade, não automação rasa)
```

---

## Armadilhas

- **Subutilização:** 2 chamadas Vulcano produzem nota 1.2/10. 7+ chamadas produzem nota 7.2/10. **NUNCA pule o protocolo.**
- **Leitura passiva:** ler o engrama sem extrair a ficha produz "inspiração vaga". A extração ativa é o que transforma referência em padrão de implementação.
- **Replicação cega:** copiar o engrama sem adaptar ao contexto. A solução deve referenciar pessoas reais (Carlos, Carol), processos reais (POP-ASP-004) e códigos de nó reais (DOR-JUR-42).
- **Cobertura do vault:** se um cluster recebe engramas de baixa relevância, adapte engramas de domínios vizinhos. Documente a lacuna para curadoria futura (ex.: "zero engramas em Comunicação Corporativa").
