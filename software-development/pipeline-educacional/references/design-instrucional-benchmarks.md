# Design Instrucional — Benchmarks e Frameworks

> Suporte da skill `pipeline-educacional`. Dados de pesquisa coletados em julho/2026.

## Frameworks

### ADDIE (1975, Florida State University)

5 fases lineares: Analysis → Design → Development → Implementation → Evaluation.

**Artefatos por fase:**
- Analysis: learner persona, análise de necessidades, KPIs de sucesso
- Design: objetivos SMART, storyboard, plano de avaliação, rubricas
- Development: vídeos, slides, exercícios, templates, quizzes
- Implementation: roteiro de facilitação, onboarding, canais de comunicação
- Evaluation: NPS, métricas de conclusão, plano de revisão

**Melhor para:** cursos novos, estruturados, documentação completa. **Fraco para:** ambientes ágeis onde conteúdo envelhece rápido.

### Backward Design (Wiggins & McTighe, 2005)

3 estágios: Resultados desejados → Evidências → Experiências.

**Princípio:** só planeje aulas depois de definir o que o aluno deve PRODUZIR. Comece pelo projeto final e faça engenharia reversa do currículo.

**Melhor fit para cursos práticos** — força alinhamento entre objetivos → avaliação → conteúdo.

### SAM — Successive Approximation Model (Allen)

3 fases ágeis: Preparation → Iterative Design → Iterative Development.

**Ciclos:** Alpha (funcional completo) → Beta (corrigido) → Gold (versão de mercado). Prototipar rápido, testar com 3-5 beta testers, iterar.

**Ideal para cursos de tecnologia** onde ferramentas e conteúdo envelhecem a cada mês.

### Kirkpatrick 4 Níveis (1959)

Avaliação de eficácia: Reação → Aprendizagem → Comportamento → Resultados.

**New World Kirkpatrick:** comece pelo Nível 4 (resultados desejados) e faça engenharia reversa. Adicione "drivers" — reforços pós-curso (accountability, follow-up, comunidade).

### Framework Híbrido Recomendado

```
BACKWARD DESIGN  →  SAM (Desenvolvimento)  →  KIRKPATRICK (Avaliação)
(Design curricular)  (Prototipagem ágil)     (Medição de eficácia)
       +                      +                        +
  ADDIE (Documentação e estrutura BASE)
```

---

## Dados de Retenção

| Formato | Taxa de conclusão |
|---|---|
| MOOCs gratuitos | 5–15% |
| Cursos pagos | ~60% |
| Cohort-based | 72% |
| Micro-learning (<2h) | 80%+ |

- 50% dos abandonos ocorrem nas primeiras 2 semanas (ELEARNING INDUSTRY, 2025)
- Vídeos ≤6 min retêm 50% mais engajamento que vídeos longos
- Quizzes a cada 3–5 min aumentam retenção em 40% (SKILLADEMIA, 2025)

---

## Benchmarks de Duração de Conteúdo

| Plataforma | Unidade | Duração |
|---|---|---|
| DeepLearning.AI | Vídeo | 5–15 min |
| Fast.ai | Lição | 90 min |
| Maven | Live session | 90–120 min |
| Coursera | Vídeo | 5–15 min |

**Recomendação:** pílulas de 15–20 min. Vídeos de 2h são o limite superior — risco de baixa retenção.

---

## Equilíbrio Teoria/Prática

| Plataforma | Teoria | Prática |
|---|---|---|
| Maven | 30% | 70% |
| Fast.ai | 20% | 80% |
| DeepLearning.AI | 50% | 50% |
| Coursera | 40% | 60% |

**Padrão ouro:** 70–80% prática. **Mínimo aceitável:** 50%.

---

## Progressão em Níveis (Escadinha)

**Achado:** quase ninguém empacota cursos em trilha integrada de 3 níveis com upsell. É **diferencial competitivo real**.

| Plataforma | Progressão | Integrada? |
|---|---|---|
| DeepLearning.AI | Implícita (Beginner 64 cursos / Intermediate 60) | Não |
| Fast.ai | Part 1 → Part 2 → SolveIt ($500) | Sim |
| Maven (Marily Nika) | AI PM 101 → Advanced → Bootcamp | Upsell manual |
| Maven (James Gray) | Agentic AI for Leaders → Claude Builders | Upsell manual |
| Coursera IBM | 5 cursos sequenciais em Specialization | Sim |

---

## 12 Alavancas de Wes Kao (Maven)

1. Duração (4–6 semanas para cursos profundos)
2. Número de alunos (8–15 primeira turma, 30+ com TAs)
3. Preço (reflete transformação prometida, não horas de conteúdo)
4. Intensidade (mais intensidade = mais transformação)
5. Orientado a projeto (cursos com capstone > cursos só de conteúdo)
6. Interação em grupo (breakout rooms, peer feedback)
7. Envolvimento de coaches (TAs que dão feedback individualizado)
8. Presença do instrutor (nas lives e na comunidade)
9. Qualidade de produção (gravação, slides, materiais)
10. Conteúdo pré-gravado (70% assíncrono / 30% síncrono)
11. Processo seletivo (filtro de entrada aumenta comprometimento)
12. Frequência de turmas (quantas por ano)

---

## ROI de Treinamento (Kirkpatrick-Phillips)

| Tipo de treinamento | ROI típico |
|---|---|
| Treinamento técnico | 150–300% |
| Vendas | 100–350% |
| Liderança | 50–150% |

Apenas **8% das organizações** medem impacto de negócio do treinamento (MCKINSEY, 2025). Medir é diferencial.

---

## Benchmarks de Criadores de Curso

### Maven (maven.com)
- Cohort-based, 4–6 semanas, USD 500–5.000/aluno
- 80% HOW, 20% WHAT. "Super Specific How" (Wes Kao)
- 70% assíncrono, 30% síncrono

### Reforge (reforge.com)
- Frameworks proprietários + artifacts reutilizáveis
- Instrutores = practitioners ativos, não acadêmicos
- Foco B2B (1.000+ empresas)

### Write of Passage (David Perell)
- Bootcamp 5 semanas, promessa aspiracional/transformacional
- Feedback individualizado em <24h
- Garantia de reembolso 14 dias sem perguntas
- 2.000+ alunos, 72 países

### Fast.ai (Jeremy Howard)
- Filosofia top-down: constrói primeiro, teoria depois
- 20% teoria, 80% prática — a mais prática de todas
- Cursos principais gratuitos + SolveIt (USD 500)

### DeepLearning.AI (Andrew Ng)
- 124 cursos, USD 25–30/mês (assinatura)
- Micro-learning 5–15 min por vídeo
- 50% teoria, 50% prática

---

## Plataformas Brasileiras

| Plataforma | Modelo | Preço |
|---|---|---|
| Alura | Assinatura (Netflix de cursos) | R$199/mês (Pro), R$397/mês (Ultra) |
| Hotmart | Marketplace, pagamento único | R$47–500 por curso |

---

## Fontes

- PRECEDENCE RESEARCH. AI in Education Market 2025–2034. https://www.precedenceresearch.com/ai-in-education-market
- ELEARNING INDUSTRY. AI in Education: Key Statistics 2025. https://elearningindustry.com/ai-in-education-key-statistics-trends-2025
- SKILLADEMIA. Online Learning Statistics 2025. https://skillademia.com/statistics/online-learning-statistics/
- WES KAO. Course Mechanics Canvas. https://weskao.com/blog/course-mechanics-canvas
- WES KAO. The Super Specific How. https://weskao.com/blog/super-specific-how
- WIGGINS, G.; MCTIGHE, J. Understanding by Design. 2nd ed. ASCD, 2005.
- ALLEN, M. Leaving ADDIE for SAM. ASTD Press, 2012.
- KIRKPATRICK, D.L.; KIRKPATRICK, J.D. Evaluating Training Programs. 3rd ed. Berrett-Koehler, 2006.
- MAVEN. About. https://maven.com/about
- REFORGE. https://reforge.com
- WRITE OF PASSAGE. https://writeofpassage.com
- FAST.AI. Practical Deep Learning for Coders. https://course.fast.ai
- DEEPLEARNING.AI. https://deeplearning.ai
- ALURA. Planos e Preços. https://www.alura.com.br/planos
