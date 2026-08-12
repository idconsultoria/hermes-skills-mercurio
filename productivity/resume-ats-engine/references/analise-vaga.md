# Análise de Vaga — extração de requisitos, match score e concorrência

## Passo 1 — Extrair e categorizar requisitos

Divida o JD em 3 níveis (herdado do ComposioHQ + ResumeSkills):

**P1 — Obrigatórios (deal-breakers):** anos de experiência, stack obrigatória, formação exigida, certificações exigidas, inglês obrigatório, "must have".
**P2 — Importantes (fortemente desejados):** "preferred", "nice to have" forte, stack secundária, domínio específico.
**P3 — Bônus:** diferenciais, "plus", conhecimentos que agregam.

Também extraia:
- **Soft skills enfatizadas** (comunicação, liderança, colaboração) — devem ecoar em bullets
- **Termos de domínio/indústria** (fintech, healthtech, LGPD, ARR, compliance)
- **Sinais de senioridade** (mentoria, arquitetura, cross-team, ownership)
- **Sinais de concorrência** (ver Passo 4)

## Passo 2 — Match score (pré-design)

```
Match% = (P1 cobertos × 0.7) + (P2 cobertos × 0.2) + (P3 cobertos × 0.1)

Ex.: 8/10 P1 (80%), 3/5 P2 (60%), 1/4 P3 (25%)
→ (0.80×0.7) + (0.60×0.2) + (0.25×0.1) = 0.56 + 0.12 + 0.025 = 70.5%
```

**Interpretação (faixas do ResumeSkills/job-description-analyzer):**
- 90-100% = Overqualified (risco de flight) — avisar
- 75-89% = Excelente fit → aplicar forte
- 60-74% = Bom fit → aplicar com cover letter forte
- 50-59% = Stretch → aplicar só se apaixonado
- <50% = Subqualificado → repensar (a menos que o usuário queira mesmo assim)

## Passo 3 — Gap analysis

Para cada requisito faltante, classifique:
- **Critical gap:** deal-breaker (ex.: exige 5 anos em linguagem X, usuário nunca usou)
- **Major gap:** significativo mas endereçável (ex.: faltam certificações → dá para obter; falta domínio do setor → dar para enfatizar setores adjacentes)
- **Minor gap:** fácil de cobrir (ex.: ferramenta parecida com outra que já domina)

No currículo: **downplay** gaps menores (não destacar o que não tem), **transfer** experiência análoga (ex.: outro setor com mesmas regulamentações), **nunca fabricar**.

## Passo 4 — Estimativa de concorrência da vaga

Classifique o nível de disputa esperado (fatores ponderados, use o que souber; se a vaga for URL, pesquise a empresa):

| Fator | Baixa concorrência | Alta concorrência |
|---|---|---|
| Senioridade | Sênior/lead/especialista nicho | Júnior/trainee |
| Stack | Nicho (mainframe, Rust embarcado, COBOL) | Genérica (React/Node, SQL/Excel, marketing digital) |
| Empresa | Média/pequena, desconhecida, setor desvalorizado | Tech conhecida, unicórnio, FAANG-like, gov premium |
| Modalidade | Presencial obrigatório em cidade pequena | Remoto amplo / hibrido flexível |
| Salário | Abaixo do mercado | Acima do mercado (attracts talent) |
| Volume do JD | "vaga única", específica | "várias vagas", "time em expansão" |
| Postagem | Antiga (pipeline já andou) | Recente (fila cheia chegando) |

**Níveis:** Muito Alta (500+ candidatos típicos) · Alta (200-500) · Média (50-200) · Baixa (<50).

Para estimar o **percentil do candidato**: cruze a nota final da avaliação (E1-E7) com o nível de disputa e o perfil típico:
- Nota ≥8.5 em disputa média/alta → top 5-10%
- Nota 7.5-8.4 → top 10-25%
- Nota 6.5-7.4 → meio do pelotão (25-50%)
- Nota <6.5 → abaixo da mediana; aplicar só com ajustes ou se a vaga for stretch intencional

## Verdict final

- **Aplicar forte** — nota ≥7.5 e sem critical gaps
- **Aplicar com ajustes** — nota 6.5-7.4 ou major gaps endereçáveis; executar as top-5 ações do relatório antes de enviar
- **Repensar** — nota <6.5 ou critical gap; dizer claramente e sugerir vaga-alvo diferente (sem enrolação)
