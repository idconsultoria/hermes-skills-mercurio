# Rubrica de Avaliação — nota 0-10 por eixo, justa e com evidência

**Regra de ouro:** toda nota deve vir com evidência citável ("E2=6 porque 1 de 5 bullets do cargo atual tem métrica"). Nota sem evidência é opinião — não entregar.

## Eixos e pesos

| Eixo | Peso | O que mede |
|---|---|---|
| E1 Match com a vaga | 25% | Cobertura de P1/P2/P3, keywords exatas e sinonímia, linguagem do JD |
| E2 Impacto e quantificação | 20% | Qualidade dos bullets: XYZ/STAR, métricas, power verbs, sem clichês |
| E3 Estrutura e ATS | 15% | Single column, headers padrão, fonte, margens, PDF texto, 1-2 páginas |
| E4 Conteúdo e completude | 15% | Lacunas de info crítica, profundidade de domínio, placeholders |
| E5 Posicionamento e senioridade | 10% | Fala a língua do nível da vaga (prova de liderança/arquitetura p/ sênior) |
| E6 Escaneabilidade | 10% | 5-segundo scan: título, stack, anos de exp visíveis; hierarquia |
| E7 Idioma e apresentação | 5% | Gramática, sem pronomes/períodos, en dash, URLs limpas, consistência |

**Nota final = E1×0.25 + E2×0.20 + E3×0.15 + E4×0.15 + E5×0.10 + E6×0.10 + E7×0.05**

Escala da nota final: 9.0+ excelente · 8.0-8.9 forte · 7.0-7.9 bom · 6.0-6.9 regular · <6.0 fraco.

## Âncoras por eixo (o que é nota 10, 7, 4)

### E1 — Match (25%)
- **10:** 100% dos P1 com termo exato do JD, ≥80% P2/P3 cobertos, linguagem espelhada, sem stuffing
- **7:** ~80% P1, ~50% P2/P3, maioria com termo exato
- **4:** <50% P1, keywords genéricas, muito "quase" sem termo do JD
- Desconto por keyword stuffing artificial (parece lista, não experiência)

### E2 — Impacto e quantificação (20%)
- **10:** ≥70% dos bullets com métrica real, todos XYZ/STAR, power verbs variados, zero clichê
- **7:** ~50% com métrica, maioria com verbo forte, 1-2 clichês
- **4:** bullets de dever ("Responsible for...", "Ajudei com..."), quase nada mensurável
- Métricas inventadas → nota máxima 4 neste eixo (integrity cap)

### E3 — Estrutura e ATS (15%)
- **10:** single column, headers padrão, Calibri/Arial ≥10.5, margens 0.75", contato no corpo, PDF texto, 1 página (jun/mid) ou 2 (sênior), **sem cards/cores/decoração (currículo é formal)**
- **7:** 1-2 desvios menores (fonte 9pt, margem 0.5")
- **4:** tabelas/colunas, imagens, cards, header com contato, 3+ páginas, PDF imagem

### E4 — Conteúdo e completude (15%)
- **10:** contato completo (inclui telefone), todo cargo com domínio e períodos, sem placeholders
- **7:** 1-2 lacunas menores (falta certificação, período aproximado)
- **4:** placeholders críticos, cargo sem contexto de domínio, buracos de tempo sem explicação
- Informação que o usuário tinha e não deu (não é culpa da skill) também desconta aqui — o relatório lista o que falta

### E5 — Posicionamento e senioridade (10%)
- **10:** prova explícita do nível (sênior: arquitetura, mentoria, cross-team, ownership; júnior: potencial, aprendizado rápido, projetos)
- **7:** sinais presentes mas implícitos
- **4:** currículo "júnior" para vaga sênior (ou vice-versa), sem evidência do nível

### E6 — Escaneabilidade (10%)
- **10:** em 5s acha cargo atual, stack, anos de exp; skills no topo (tech); hierarquia clara; bullets curtos (≤2 linhas)
- **7:** 2-3 segundos extras para achar a stack
- **4:** texto corrido, paragrafão, bullets de 4 linhas, seções escondidas

### E7 — Idioma e apresentação (5%)
- **10:** zero erro, sem pronomes, sem ponto final em bullets, en dash, URLs limpas, datas consistentes
- **7:** 1-2 erros menores
- **4:** erros de português/inglês, "Responsible for" repetido, formatação inconsistente

## Análise de concorrência e competitividade (parte 2 do relatório)

Use `references/analise-vaga.md` Passo 4:
1. **Nível de disputa esperado** (Muito Alta/Alta/Média/Baixa) + 2-3 fatores que justificam
2. **Percentil estimado do candidato** (top 5%, 10-25%...) cruzando nota final × disputa
3. **Vantagens competitivas reais** do candidato (o que ele tem que o típico concorrente não tem — citar do input)
4. **Desvantagens** (gaps) e se são críticas para a vaga
5. **Verdict**: Aplicar forte / Aplicar com ajustes / Repensar (faixas do analise-vaga.md)

## Modelo do relatório `avaliacao.md`

```markdown
# Avaliação — [Nome] × [Cargo] @ [Empresa]

## Nota final: X.X/10 — [rótulo da escala]

| Eixo | Nota | Peso | Ponderado | Justificativa (evidência) |
|---|---|---|---|---|
| E1 Match com a vaga | 8.5 | 25% | 2.13 | 4/5 P1 cobertos... |
| ... | | | | |

## Concorrência esperada da vaga
- Nível: [Muito Alta/Alta/Média/Baixa] — fatores: ...
- Perfil típico de quem disputa: ...

## Competitividade do currículo
- Percentil estimado: top X%
- Vantagens: ...
- Desvantagens/gaps: ...

## Pontos fortes
## Pontos fracos
## Top-5 ações para subir a nota (priorizadas por impacto × esforço)
1. ...
```

**Entrega:** arquivo .md via MEDIA (o usuário rejeita tabela inline quebrada no WhatsApp) + resumo 4-5 linhas no chat.
