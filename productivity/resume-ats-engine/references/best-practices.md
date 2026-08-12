# Best Practices de Currículo — consolidado de Harvard Career Services, r/EngineeringResumes, The Tech Resume Inside Out (Gergely Orosz), Tech Interview Handbook e repos-fontes (dabydat, ResumeSkills, varunr89, ComposioHQ, claude-office-skills)

## Estrutura de seções (ordem por senioridade e área)

**Para tecnologia/engenharia (3+ anos):**
1. Nome & Contato (centralizado, no corpo — NUNCA em header/footer)
2. **Skills (primeiro!)** — recrutador escaneia stack nos primeiros 5 segundos
3. Experience (ordem cronológica reversa)
4. Projects (se relevantes)
5. Education (no fim)

**Para estudantes/júnior:** Education sobe para o topo (depois do contato).
**Para gestão/consultoria/executivo:** Professional Summary (2-3 linhas) primeiro, depois Experience; Skills agrupadas por competência (não stack).

## Contato (formato ATS-safe)

```
NOME
email@x.com | (11) 99999-9999 | Cidade/UF | linkedin.com/in/usuario | github.com/usuario
```
- URLs sem "https://" e sem prefixo "Email:"/"LinkedIn:" (ou só "LinkedIn:" como rótulo limpo)
- Sem endereço completo — cidade/estado basta
- Um e-mail profissional; sem caracteres especiais

## Bullets — fórmula XYZ (Google) / STAR condensado / CAR

**XYZ:** "Accomplished [X] as measured by [Y] by doing [Z]" → na prática: **Verbo de ação (passado) + O quê + Contexto técnico/domínio + Impacto mensurável**.

- RUIM: "Responsible for developing web applications"
- BOM: "Developed fintech web applications for credit management and card issuance using React and NestJS under Hexagonal Architecture and DDD"
- BOM c/ métrica: "Reduced deployment time by 75% (4h → 1h) by implementing CI/CD pipeline with GitHub Actions"

**STAR condensado em bullet:** "Revitalized underperforming sales team through training and commission restructure, improving quota attainment from 65% to 92% (+$1.8M revenue)"

**CAR (alternativa):** Challenge → Action → Result, ex.: "Reduced customer churn (C) via proactive outreach program (A), retaining 85% of at-risk accounts worth $500K ARR (R)"

Regras:
- Máx. 5-6 bullets por cargo; os mais relevantes à vaga primeiro (reordenar, não reescrever tudo)
- Sempre que possível métrica real; sem número, estime com `~` e sinalize ("~40%") ou deixe `[INFORMAR]` — NUNCA invente número
- Sem pronomes (I, my, we / eu, meu, nós)
- Sem ponto final no fim do bullet (não são frases)
- Descreva o **domínio**: indústria (fintech, healthtech), tipo de dado (PII, financeiro), usuários (B2B/B2C), impacto de negócio
- 1 métrica por bullet é suficiente; 2-3 bullets com métrica por cargo já é forte

## Power verbs (EN)

- **Leadership:** Led, Directed, Managed, Coordinated, Mentored, Championed, Established, Launched
- **Achievement:** Achieved, Delivered, Exceeded, Improved, Increased, Reduced, Optimized, Streamlined, Accelerated
- **Technical:** Developed, Engineered, Implemented, Architected, Automated, Migrated, Deployed, Scaled, Integrated
- **Communication:** Collaborated, Presented, Negotiated, Authored, Documented, Trained, Facilitated

## Power verbs (PT)

- **Liderança:** Liderei, Coordenei, Gerenciei, Orientei, Liderava, Implantei, Lancei
- **Conquista:** Alcancei, Entreguei, Superei, Melhorei, Aumentei, Reduzi, Otimizei, Acelerei
- **Técnico:** Desenvolvi, Implementei, Arquitetei, Automatizei, Migrei, Implantei, Escalonei, Integrei
- **Comunicação:** Colaborei, Apresentei, Negociei, Documentei, Treinei, Facilitei

**Evitar clichês:** spearheaded, orchestrated, utilized, leveraged, results-driven, dynamic, innovative, "paixão por tecnologia".

## Formatação ATS-rígida (currículo é SEMPRE formal)

- Fonte: Calibri ou Arial — corpo 10.5-11pt, nome 16pt, headings 11.5pt bold
- Margens: 0.75" todos os lados; line spacing 12-13pt
- **Single column; sem tabelas de layout, sem caixas de texto, sem imagens/logos/ícones, sem gráficos, sem cards, sem cores de fundo**
- Headers de seção padrão: "Experience"/"Professional Experience", "Skills", "Projects", "Education", "Certifications" (nunca "Minha Jornada", "Caixa de Ferramentas")
- Datas: "2021 – Present" (en dash com espaços); formato MM/YYYY consistente
- Datas à direita na mesma linha do cargo (tab right); bullets não ultrapassam as datas
- Bullets simples: • ou - (padrão)
- Arquivo: .docx ou .pdf (texto, não imagem); nome: "Nome_Sobrenome_Curriculo.pdf"
- 1 página (<10 anos de exp), 2 páginas máx (sênior/executivo)

## Idioma

- Currículo no idioma da vaga (vaga em PT → PT; em EN → EN)
- Termos técnicos permanecem em inglês mesmo em currículo PT (backend, CI/CD, Scrum)
- NUNCA tradução literal entre versões — cada versão natural no seu idioma
- PT: verbos de ação no pretérito perfeito (Desenvolvi, Implementei, Liderei)
- EN: US English para vagas americanas

## Checklist antes de exportar (herdado do dabydat)

**Formato:**
- [ ] Nome em uma linha (max 16pt), sem truncar
- [ ] Single column, sem tabelas/gráficos/ícones/cards/cores de fundo
- [ ] Calibri/Arial, corpo ≥10.5pt, preto
- [ ] Espaçamento equilibrado (nem apertado, nem esparso)
- [ ] Datas com en dash (–) e espaços; alinhadas à direita
- [ ] URLs texto puro, sem cor/underline, sem "https://"

**Conteúdo:**
- [ ] Sem pronomes (I, my / eu, meu)
- [ ] Todo bullet começa com verbo de ação no passado
- [ ] Nenhum bullet termina com ponto final
- [ ] Todo cargo descreve o DOMÍNIO (indústria, sistema, sensibilidade de dado)
- [ ] Métricas onde possível (dígitos: "8", não "oito")
- [ ] Tecnologias no cargo E na seção de skills
- [ ] Sem verbos supérfluos/clichês; sem adjetivos vazios
- [ ] Títulos de seção padrão
- [ ] Datas consistentes com "Present"
- [ ] Ordem cronológica reversa
- [ ] Zero erro de ortografia/gramática
- [ ] Sem jargão interno indecifrável

**Entrega:**
- [ ] PDF gerado a partir do DOCX final
- [ ] PDF é texto (verificado — script da skill valida com pypdf)
- [ ] Contagem de páginas confere (1-2)
- [ ] Links funcionam
- [ ] .docx E .pdf entregues
